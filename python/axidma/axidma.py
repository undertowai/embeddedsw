import sys
import ctypes as ct

sys.path.append('../misc')

from dts import Dts
from make import Make

class AxiDma:
    def __init__(self, libPath):
        self.lib = ct.CDLL(libPath)

    def startTransfer(self, DevName, addr, len):
        fun = self.lib.XDMA_StartTransfer

        status = fun(ct.c_char_p(DevName.encode('UTF-8')), int(addr), int(len))
        assert status == 0

    def reset(self, DevName):
        fun = self.lib.XDMA_Reset

        status = fun(ct.c_char_p(DevName.encode('UTF-8')))
        assert status == 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('{}: Usage'.format(sys.argv[0]))
        exit()

    libPath = Make().makeLibs('axidma')

    id = int(sys.argv[1])
    numDmaPerIP = int(8)

    ipName ='stream_to_mem_{}_axi_dma_{}'.format(int(id/numDmaPerIP), int(id%numDmaPerIP))
    devName = Dts().ipToDtsName(ipName)

    dma = AxiDma(libPath)

    dma.startTransfer(devName, 0, 4096)
    dma.reset(devName)

    print('Pass')