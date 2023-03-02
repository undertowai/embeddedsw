import sys
import ctypes as ct

sys.path.append("../misc")

from dts import Dts
from make import Make
from mlock import MLock


class AxiDma(MLock):
    def __init__(self, libName):
        libPath = Make().makeLibs(libName)
        self.lib = ct.CDLL(libPath)
        self.numDmaPerIP = 8

    def devIdToIpName(self, devId):
        ipName = "stream_to_mem_{}_axi_dma_{}".format(
            int(devId / self.numDmaPerIP), int(devId % self.numDmaPerIP)
        )
        devName = Dts().ipToDtsName(ipName)
        return devName

    @MLock.Lock
    def startTransfer(self):
        fun = self.lib.XDMA_StartTransfer

        status = fun(
            ct.c_char_p(self.devName.encode("UTF-8")),
            int(self.addr) >> 32,
            int(self.addr) & 0xFFFFFFFF,
            int(self.len),
        )
        assert status == 0

    def __to_c_array(self, dtype, data):
        arr = (dtype * len(data))()
        arr[:] = data
        return arr

    @MLock.Lock
    def startTransferBatched(self):
        fun = self.lib.XDMA_StartTransferBatched

        name_arr = []
        addr_arr = []
        size_arr = []

        for d, n, a, s in self.dmaBatch:
            name_arr.append(n.encode("UTF-8")), addr_arr.append(a), size_arr.append(s)

        name_arr = self.__to_c_array(ct.c_char_p, name_arr)
        addr_arr = self.__to_c_array(ct.c_uint64, addr_arr)
        size_arr = self.__to_c_array(ct.c_uint64, size_arr)

        status = fun(
            name_arr,
            addr_arr,
            size_arr,
            len(name_arr),
            int(0)
        )

        assert status == 0

    @MLock.Lock
    def reset(self):
        fun = self.lib.XDMA_Reset

        status = fun(ct.c_char_p(self.devName.encode("UTF-8")))
        assert status == 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("{}: Usage".format(sys.argv[0]))
        exit()

    id = int(sys.argv[1])

    dma = AxiDma("axidma")

    dma.startTransfer(devName=dma.devIdToIpName(id), addr=0x48_0000_0000, len=4096)
    dma.reset(devName=dma.devIdToIpName(id))

    print("Pass")
