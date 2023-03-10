#pragma once

#include <iostream>
#include <stdint.h>
#include <chrono>
#include <thread>
#include <vector>
#include <map>

extern "C" {
    int ddr_map_start(void);
    void *ddr_map(int fd, uint64_t addr, uint32_t size);
    int ddr_unmap(void *ptr, uint64_t len);
    void ddr_map_finish(int fd);
};

class DdrMng {

public:
using MemVec = std::map<uint32_t, std::vector< std::tuple<uint64_t, uint64_t> > >;
using IqData = std::vector< std::pair<void *, uint32_t> >;

private:
    int fd;
    std::vector< std::pair<void *, uint64_t> >ddr_map_v;

    void ddrAreaToVector(DdrMng::MemVec &ddrMap,
                uint32_t *ddrIdArray,
                uint64_t *dmaAddrArray,
                uint64_t *dmaLenArray,
                uint32_t dmaNumInst);

    std::tuple<uint64_t, uint64_t>
    getDdrBounds(DdrMng::MemVec &ddrMap, uint32_t ddr);

public:

    DdrMng (void);

    int ddrMap(DdrMng::IqData &iq_data_v,
                uint32_t *ddrIdArray,
                uint64_t *dmaAddrArray,
                uint64_t *dmaLenArray,
                uint32_t dmaNumInst);

    int ddrUnmap (void);
};