import sys
import ctypes as ct
import numpy as np
from numpy.ctypeslib import ndpointer

from TICS import read as TICSread

from time import sleep

class SharedObject:
    def __init__(self, libPath, devName):
        self.libPath = libPath
        self.devName = devName

        self.__loadSo()

    def __loadSo(self):
        self.lib = ct.CDLL(self.libPath)


class Lmx2820(SharedObject):
    RO_REGS = [71, 72, 73, 74, 75, 76, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122]

    LOCKED_REG = 74
    LOCKED_BITS = [14, 15]
    RF_DATA_READ_BIT = 0x80

    def __init__(self, libPath, devName):
        super().__init__(libPath, devName)

    def getBitMask(self, bits):
        mask = 0x0
        for i in range(bits[0], bits[1]+1, 1):
            mask |= 1 << i
        return mask

    def getMaskedVal(self, reg, bits):
        mask = self.getBitMask(bits)
        reg = (reg & mask) >> bits[0]
        return reg

    def getRegIndex(self, regs, id):
        for i, d in enumerate(regs):
            if ((d >> 16) & 0x7f) == id:
                return i
        raise Exception()

    def getPllStatus(self, regs):
        i = self.LOCKED_REG
        return self.getMaskedVal(regs[i], self.LOCKED_BITS)

    def getVCOstate(self, regs):
        i = self.LOCKED_REG
        return self.getMaskedVal(regs[i], [2, 4])

    def getVCO_CAPCTRL(self, regs):
        i = self.LOCKED_REG
        return self.getMaskedVal(regs[i], [5, 12])

    def getMUTEpin(self, regs):
        i = 77
        return self.getMaskedVal(regs[i], [8, 8])

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


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('{}: Usage'.format(sys.argv[0]))
        exit()

    libPath = sys.argv[1]
    devName = sys.argv[2]
    ticsFilePath = sys.argv[3]

    #TODO:
    devName = devName.split('/')[2].split('@')
    devName = devName[1] + '.' + devName[0]

    lmx = Lmx2820(libPath, devName)

    expData = TICSread(ticsFilePath)

    gotData = np.empty(expData.size, dtype=np.uint32)
    lmx.setMuxOut(expData)
    lmx.writeData(expData)
    lmx.readData(gotData)

    expData = np.flip(expData, 0)
    for i, d in enumerate(expData):
        #Mask data bits
        if i not in lmx.RO_REGS:
            if (expData[i] & 0xffff) != gotData[i]:
                print("Data doesn't match: i={} : exp={}, got={}".format(i, hex(expData[i]), hex(gotData[i])))
                raise Exception

    LD = lmx.getPllStatus(gotData)
    print("PLL Locked : {}".format(LD == 0x2))
    print("VCO {}".format(lmx.getVCOstate(gotData)))
    print("VCO_CAPCTRL {}".format(lmx.getVCO_CAPCTRL(gotData)))
    print("MUTE Polarity {}".format(lmx.getMUTEpin(gotData)))
