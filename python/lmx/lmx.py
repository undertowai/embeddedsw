import sys
import ctypes as ct
import numpy as np
from numpy.ctypeslib import ndpointer

from TICS import read as TICSread

sys.path.append('../misc')

from dts import Dts
from make import Make

class Lmx2820:
    RO_REGS = [71, 72, 73, 74, 75, 76, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122]

    LOCKED_REG = 74
    LOCKED_BITS = [14, 15]
    RF_DATA_READ_BIT = 0x80

    def __init__(self, ipName):
        libPath = Make().makeLibs('spi')
        self.devName = Dts().ipToDtsName(ipName)
        self.lib = ct.CDLL(libPath)

    def getRegIndex(self, regs, id):
        for i, d in enumerate(regs):
            if ((d >> 16) & 0x7f) == id:
                return i
        raise Exception()

    def getBits(self, a, bounds):
        bits = np.unpackbits(a.view(dtype=np.uint8), bitorder='little')
        bits = bits[bounds[0]:bounds[1]+1]
        bits = np.packbits(bits, bitorder='little')
        return bits[0]

    def isPllLocked(self, regs):
        i = self.LOCKED_REG
        ld = self.getBits(regs[i:i+1], [14, 15])
        return ld == 0x2

    def setMuxOut(self, regs):
        i = self.getRegIndex(regs, 0)
        regs[i] = regs[i] & (~(1 << 2))

    def writeData(self, data):
        fun = self.lib.SpiSendData

        status = fun(ct.c_char_p(self.devName.encode('UTF-8')), int(0), int(3), ct.c_void_p(data.ctypes.data), int(data.size))
        assert status == 0

    def readData(self, data):
        fun = self.lib.SpiRecvData

        status = fun(ct.c_char_p(self.devName.encode('UTF-8')), int(0), int(3), ct.c_void_p(data.ctypes.data), int(data.size), self.RF_DATA_READ_BIT)
        assert status == 0

    def checkConfig(self, expData, gotData):
        for i, d in enumerate(expData):
            #Mask data bits
            if i not in self.RO_REGS:
                if (expData[i] & 0xffff) != gotData[i]:
                    raise Exception("Data doesn't match: i={} : exp={}, got={}".format(i, hex(expData[i]), hex(gotData[i])))

    def loadTICS(self, ticsFilePath):
        return TICSread(ticsFilePath)

    def config(self, ticsFilePath):
        expData = self.loadTICS(ticsFilePath)

        gotData = np.empty(expData.size, dtype=np.uint32)
        self.setMuxOut(expData)
        self.writeData(expData)
        self.readData(gotData)

        expData = np.flip(expData, 0)

        self.checkConfig(expData, gotData)

        if not self.isPllLocked(gotData):
            raise Exception('PLL is not locked')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('{}: Usage'.format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]

    lmx = Lmx2820('axi_quad_spi_0')
    lmx.config(ticsFilePath)
    print("Pass")