#include <iostream>
#include <stdint.h>
#include <chrono>
#include <thread>
#include <vector>
#include <map>

#include "zmq.hpp"
#include "main.h"

extern "C" {
    int XDMA_StartTransferBatched(const char **dmaNameArray,
                                uint64_t *dmaAddrArray,
                                uint64_t *dmaLenArray,
                                uint32_t dmaNumInst,
                                uint32_t debug);

    int XDMA_InitBatched(void **dma_inst_pool, const char **inst_names, uint32_t num_inst);
    int XDMA_FinishBatched(void *dma_inst_pool, uint32_t num_inst);
    int XDMA_StartTransferBatched_NoMetal(void *dma_inst_pool, uint64_t *addr, uint64_t *len, uint32_t num_inst, uint32_t debug);

    int AXI_Gpio_Init_NoMetal(void **ptr, const char *DevName);
    int AXI_Gpio_Finish_NoMetal(void *ptr);
    int AXI_Gpio_Set_NoMetal(void *ptr, uint32_t val, uint32_t val2);

    int ddr_map_start(void);
    void *ddr_map(int fd, uint64_t addr, uint32_t size);
    int ddr_unmap(void *ptr, uint64_t len);
    void ddr_map_finish(int fd);

    int _metal_init (void);
    void metal_finish (void);
};

bool debug;
uint32_t fs;
void *dma_inst_pool;
void *gpio_sync_ptr;
uint32_t dma_inst_num;
int ddr_map_fd;
std::vector< std::pair<void *, uint64_t> >ddr_map_v;

int MainLoopInit_cpp (const char *port,
                    const char *topic,
                    const char *sync_gpio_name,
                    uint32_t _fs,
                    uint32_t _debug)
{
    fs = _fs;
    debug = _debug ? true : false;
    ZmqInit(port, topic);
    _metal_init();
    if (AXI_Gpio_Init_NoMetal(&gpio_sync_ptr, sync_gpio_name)) {
        return -1;
    }

    ddr_map_v.clear();
    dma_inst_pool = nullptr;
    dma_inst_num = 0;
    ddr_map_fd = -1;

    if (debug) {
        std::cout << "Port : " << port << std::endl;
        std::cout << "Topic : " << topic << std::endl;
        std::cout << "MainLoopInit done" << std::endl;
    }
    return 0;
}

int MainLoopDestroy_cpp (void)
{
    ZmqDestroy();
    XDMA_FinishBatched(dma_inst_pool, dma_inst_num);
    AXI_Gpio_Finish_NoMetal(gpio_sync_ptr);

    for (auto &[addr, len]: ddr_map_v) {
        ddr_unmap(addr, len);
    }
    ddr_map_finish(ddr_map_fd);
    metal_finish();
    return 0;
}

using DDR_map_t = std::map<uint32_t, std::vector< std::tuple<uint64_t, uint64_t> > >;

void mapDdr(DDR_map_t &ddrMap,
            uint32_t *ddrIdArray,
            uint64_t *dmaAddrArray,
            uint64_t *dmaLenArray,
            uint32_t dmaNumInst) {

    for (int i =0; i < dmaNumInst; i++) {
        ddrMap[ddrIdArray[i]].push_back( {dmaAddrArray[i], dmaLenArray[i]} );
    }
}

std::tuple<uint64_t, uint64_t>
getDdrBounds(DDR_map_t &ddrMap, uint32_t ddr) {
    auto &vec = ddrMap[ddr];
    uint64_t lowAddr = std::numeric_limits<uint64_t>::max(), hiAddr = 0;

    for (auto t: vec) {
        if (lowAddr > std::get<0>(t)) {
            lowAddr = std::get<0>(t);
        }
        if (hiAddr < std::get<0>(t) + std::get<1>(t)) {
            hiAddr = std::get<0>(t) + std::get<1>(t);
        }
    }
    return { lowAddr, hiAddr - lowAddr };
}

template <typename T>
void tstamp(T &t_start, std::string id)
{
    auto t_end = std::chrono::high_resolution_clock::now();
    double elapsed_time_ms = std::chrono::duration<double, std::milli>(t_end-t_start).count();

    std::cout << "Time taken for " << id << " :" << elapsed_time_ms << std::endl;
    t_start = t_end;
}

int MainLoop_cpp (uint32_t *ddrIdArray,
                const char **dmaNameArray,
                uint64_t *dmaAddrArray,
                uint64_t *dmaLenArray,
                uint32_t dmaNumInst,
                uint32_t waitTimeMs,
                uint32_t txn,
                uint32_t *rxn,
                uint32_t rxn_len)
{

    uint32_t stream_num = rxn_len*2;
    std::vector<void *> iq_data_v;
    std::vector<uint32_t> iq_data_size_v;
    std::vector<uint32_t> rxn_v;
    uint32_t sn = 0;

    dma_inst_num = dmaNumInst;

    rxn_v.assign(rxn, rxn+rxn_len);

    if (XDMA_InitBatched(&dma_inst_pool, dmaNameArray, dmaNumInst)) {
        return -1;
    }

    if (debug) {
        std::cout << "MainLoop parameters:" << std::endl;
        std::cout << "dmaNumInst=" << dmaNumInst << std::endl;
        std::cout << "waitTimeMs=" << waitTimeMs << std::endl;
        std::cout << "rx channels num=" << rxn_len << std::endl;
    }

    DDR_map_t ddrMap;
    mapDdr(ddrMap, ddrIdArray, dmaAddrArray, dmaLenArray, dmaNumInst);
    ddr_map_fd = ddr_map_start();

    for (const auto &[k, v]: ddrMap) {
        auto bound = getDdrBounds(ddrMap, k);
        char *ptr = (char *)ddr_map(ddr_map_fd, std::get<0>(bound), std::get<1>(bound));
        auto ptr_old = ptr;

        if (ptr == nullptr) {
            ddr_map_finish(ddr_map_fd);
            return -1;
        }

        for (auto t: v) {
            auto addr = std::get<0>(t);
            auto len = std::get<1>(t);

            iq_data_v.push_back(ptr);
            iq_data_size_v.push_back(len);
            ptr += len;
        }
        ddr_map_v.push_back({ptr_old, ptr-ptr_old});
    }

    while (true) {

        if (debug) std::cout << "Running iteration " << sn  << std::endl;

        auto t_start = std::chrono::high_resolution_clock::now();

        if (AXI_Gpio_Set_NoMetal(gpio_sync_ptr, 0x0, 0x0)) {
            return -1;
        }

        if (XDMA_StartTransferBatched_NoMetal(dma_inst_pool, dmaAddrArray, dmaLenArray, dmaNumInst, uint32_t(debug))) {
            return -1;
        }

        if (XDMA_StartTransferBatched_NoMetal(dma_inst_pool, dmaAddrArray, dmaLenArray, dmaNumInst, uint32_t(debug))) {
            return -1;
        }

        if (AXI_Gpio_Set_NoMetal(gpio_sync_ptr, 0xff, 0x0)) {
            return -1;
        }

        std::chrono::milliseconds timespan(waitTimeMs);
        std::this_thread::sleep_for(timespan);

        if (debug) tstamp(t_start, "Start DMA");

        ZmqPublish(sn, txn, rxn_v, fs, iq_data_v, iq_data_size_v);

        if (debug) tstamp(t_start, "ZmqPublish");
        sn++;
    }

    std::cout << "!!!!!!!! MainLoop_cpp : unexpected path #1" << std::endl;
    return 0;
}