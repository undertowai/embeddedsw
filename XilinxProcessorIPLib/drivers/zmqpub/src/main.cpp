#include <iostream>
#include <stdint.h>
#include <chrono>
#include <thread>
#include <vector>

#include "zmq.hpp"
#include "main.h"

extern "C" {
    int XDMA_StartTransferBatched(const char **dmaNameArray,
                                uint64_t *dmaAddrArray,
                                uint64_t *dmaLenArray,
                                uint32_t dmaNumInst,
                                uint32_t debug);

    int AXI_Gpio_Set(const char *gpioName, uint32_t val, uint32_t val2);

    int ddr_read(void **ptr, uint64_t addr, uint32_t size);
    void ddr_read_finish(int fd);
};

std::string sync_gpio_name;
bool debug;
uint32_t fs;

int MainLoopInit_cpp (const char *port,
                    const char *topic,
                    const char *_sync_gpio_name,
                    uint32_t _fs,
                    uint32_t _debug)
{
    sync_gpio_name = _sync_gpio_name;
    fs = _fs;
    debug = _debug ? true : false;
    ZmqInit(port, topic);

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
    return 0;
}

int MainLoop_cpp (const char **dmaNameArray,
                uint64_t *dmaAddrArray,
                uint64_t *dmaLenArray,
                uint32_t dmaNumInst,
                uint32_t waitTimeMs,
                uint32_t txn,
                uint32_t *rxn,
                uint32_t rxn_len)
{

    std::vector<void *> iq_data_v(rxn_len*2);
    std::vector<uint32_t> iq_data_size_v(rxn_len*2);
    std::vector<int> fd(rxn_len*2);
    std::vector<uint32_t> rxn_v;
    void *ptr;

    rxn_v.assign(rxn, rxn+rxn_len);

    if (debug) {
        std::cout << "MainLoop parameters:" << std::endl;
        std::cout << "dmaNumInst=" << dmaNumInst << std::endl;
        std::cout << "waitTimeMs=" << waitTimeMs << std::endl;
        std::cout << "rx channels num=" << rxn_len << std::endl;
    }
    debug = false;

    uint32_t sn = 0;
    while (true) {

        std::cout << "Running iteration " << sn  << std::endl;

        AXI_Gpio_Set(sync_gpio_name.c_str(), 0x0, 0x0);
        XDMA_StartTransferBatched(dmaNameArray, dmaAddrArray, dmaLenArray, dmaNumInst, uint32_t(debug));
        XDMA_StartTransferBatched(dmaNameArray, dmaAddrArray, dmaLenArray, dmaNumInst, uint32_t(debug));

        AXI_Gpio_Set(sync_gpio_name.c_str(), 0xff, 0x0);

        std::chrono::milliseconds timespan(waitTimeMs);
        std::this_thread::sleep_for(timespan);

        for (int i = 0; i < rxn_len*2; i++) {
            if (debug) {
                std::cout << "Reading memory : rxn=" << i/2 << "; addr=" << (void *)dmaAddrArray[i] << "; size=" << (void *)dmaLenArray[i] << std::endl;
            }
            fd[i] = ddr_read(&ptr, dmaAddrArray[i], dmaLenArray[i]);
            iq_data_v[i] = ptr;
            iq_data_size_v[i] = dmaLenArray[i];
        }

        ZmqPublish(sn, txn, rxn_v, fs, iq_data_v, iq_data_size_v);
        sn++;

        for (int i = 0; i < rxn_len*2; i++) {
            ddr_read_finish(fd[i]);
        }
    }
    return 0;
}