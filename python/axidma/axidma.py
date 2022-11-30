import sys
import ctypes as ct

sys.path.append('../misc')

from dts import Dts
from make import Make

class AxiDma:
    def __init__(self, libName):
        libPath = Make().makeLibs(libName)
        self.lib = ct.CDLL(libPath)
        self.numDmaPerIP = 8

    def devIdToIpName(self, devId):
        ipName ='stream_to_mem_{}_axi_dma_{}'.format(int(devId/self.numDmaPerIP), int(devId%self.numDmaPerIP))
        devName = Dts().ipToDtsName(ipName)
        return devName

    def startTransfer(self, DevName, addr, len):
        fun = self.lib.XDMA_StartTransfer

        status = fun(ct.c_char_p(DevName.encode('UTF-8')), int(addr) >> 32, int(addr) & 0xffffffff, int(len))
        assert status == 0

    def reset(self, DevName):
        fun = self.lib.XDMA_Reset

        status = fun(ct.c_char_p(DevName.encode('UTF-8')))
        assert status == 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('{}: Usage'.format(sys.argv[0]))
        exit()

    id = int(sys.argv[1])

    dma = AxiDma('axidma')

    dma.startTransfer(dma.devIdToIpName(id), 0x48_0000_0000, 4096)
    dma.reset(dma.devIdToIpName(id))

    print('Pass')