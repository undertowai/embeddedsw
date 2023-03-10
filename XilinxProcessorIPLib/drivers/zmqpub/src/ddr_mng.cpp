

#include "ddr_mng.hpp"

void DdrMng::ddrAreaToVector(DdrMng::MemVec &ddrMap,
            uint32_t *ddrIdArray,
            uint64_t *dmaAddrArray,
            uint64_t *dmaLenArray,
            uint32_t dmaNumInst) {

    for (int i =0; i < dmaNumInst; i++) {
        ddrMap[ddrIdArray[i]].push_back( {dmaAddrArray[i], dmaLenArray[i]} );
    }
}

std::tuple<uint64_t, uint64_t>
DdrMng::getDdrBounds(DdrMng::MemVec &ddrMap, uint32_t ddr) {
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

DdrMng::DdrMng (void) {
    this->ddr_map_v.clear();
    this->fd = -1;
}

int
DdrMng::ddrMap(DdrMng::IqData &iq_data_v,
            uint32_t *ddrIdArray,
            uint64_t *dmaAddrArray,
            uint64_t *dmaLenArray,
            uint32_t dmaNumInst) {

    DdrMng::MemVec ddrMap;
    this->ddrAreaToVector(ddrMap, ddrIdArray, dmaAddrArray, dmaLenArray, dmaNumInst);
    this->fd = ddr_map_start();

    for (const auto &[k, v]: ddrMap) {
        auto bound = this->getDdrBounds(ddrMap, k);
        char *ptr = (char *)ddr_map(this->fd, std::get<0>(bound), std::get<1>(bound));
        auto ptr_old = ptr;

        if (ptr == nullptr) {
            ddr_map_finish(this->fd);
            return -1;
        }

        for (auto t: v) {
            auto addr = std::get<0>(t);
            auto len = std::get<1>(t);

            iq_data_v.push_back( {ptr, len});
            ptr += len;
        }
        this->ddr_map_v.push_back({ptr_old, ptr-ptr_old});
    }
    return 0;
}

int
DdrMng::ddrUnmap (void) {
    for (auto &[addr, len]: this->ddr_map_v) {
        ddr_unmap(addr, len);
    }
    ddr_map_finish(this->fd);
    return 0;
}
