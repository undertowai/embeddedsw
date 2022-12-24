import sys
from time import sleep
import ctypes as ct
import numpy as np

from .TICS import read as TICSread

from misc.dts import Dts
from misc.make import Make
from misc.mlock import MLock


class Lmx2820(MLock):
    RO_REGS = [71, 72, 73, 74, 75, 76, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122]

    LOCKED_REG = 74
    LOCKED_BITS = [14, 15]
    RF_DATA_READ_BIT = 0x80

    def __init__(self, ipName):
        libPath = Make().makeLibs("spi")
        self.devName = Dts().ipToDtsName(ipName)
        self.lib = ct.CDLL(libPath)
        self.devNamePtr = ct.c_char_p(self.devName.encode("UTF-8"))

    def __getRegIndex(self, regs, id):
        for i, d in enumerate(regs):
            if ((d >> 16) & 0x7F) == id:
                return i
        raise Exception()

    def __getBits(self, a, bounds):
        if type(a) is np.ndarray:
            a = a.view(dtype=np.uint8)

        bits = np.unpackbits(a, bitorder="little")
        bits = bits[bounds[0] : bounds[1] + 1]
        bits = np.packbits(bits, bitorder="little")
        return bits[0]

    def __isPllLocked(self, regs):
        i = self.LOCKED_REG
        ld = self.__getBits(regs[i : i + 1], [14, 15])
        return ld == 0x2

    def __setMuxOut(self, regs):
        i = self.__getRegIndex(regs, 0)
        regs[i] = regs[i] & (~(1 << 2))

    def __writeData(self, data):
        fun = self.lib.SpiSendData

        status = fun(
            self.devNamePtr,
            int(0),
            int(3),
            ct.c_void_p(data.ctypes.data),
            int(data.size),
        )
        assert status == 0

    def __readData(self, data):
        fun = self.lib.SpiRecvData

        status = fun(
            self.devNamePtr,
            int(0),
            int(3),
            ct.c_void_p(data.ctypes.data),
            int(data.size),
            self.RF_DATA_READ_BIT,
        )
        assert status == 0

    def __checkConfig(self, expData, gotData):
        for i, d in enumerate(expData):
            # Mask data bits
            if i not in self.RO_REGS:
                if (expData[i] & 0xFFFF) != gotData[i]:
                    raise Exception(
                        "Data doesn't match: i={} : exp={}, got={}".format(
                            i, hex(expData[i]), hex(gotData[i])
                        )
                    )

    def __loadTICS(self, ticsFilePath):
        return TICSread(ticsFilePath)

    def __waitLock(self, data):
        self.__readData(data)

        wait_lock = 0
        while not self.__isPllLocked(data):
            print("LMX2820: Waiting PLL locked...")
            sleep(1)
            self.__readData(data)

            wait_lock += 1
            if wait_lock >= 10:
                raise Exception("PLL is not locked")

    @MLock.Lock
    def config(self):
        expData = self.__loadTICS(self.ticsFilePath)

        gotData = np.empty(expData.size, dtype=np.uint32)
        self.__setMuxOut(expData)
        self.__writeData(expData)
        self.__readData(gotData)

        expData = np.flip(expData, 0)

        self.__checkConfig(expData, gotData)
        self.__waitLock(gotData)

    @MLock.Lock
    def writeReg(self):
        fun = self.lib.SpiWriteReg
        data = (self.reg << 16) | self.val
        status = fun(self.devNamePtr, int(0), int(3), data)
        assert status == 0

    @MLock.Lock
    def readReg(self):
        fun = self.lib.SpiReadReg
        status = fun(self.devNamePtr, int(0), int(3), self.reg, self.RF_DATA_READ_BIT)
        assert status >= 0
        return status

    def dumpRegs(self):
        for i in range(123):
            reg = self.readReg(reg=i)
            print("reg %d = %x" % (i, reg))

    def readLockedReg(self):
        reg = self.readReg(reg=self.LOCKED_REG)
        ld = (reg >> 14) & 0x2
        return ld == 0x2

    def power_reset(self, pwup, reset):
        r = 0x0
        p = 0x0 if pwup else 0x1
        reset = reset << 1
        self.writeReg(reg=r, val=p | reset)


if __name__ == "__main__":

    lmx = Lmx2820("axi_quad_spi_0")
    if len(sys.argv) == 2:
        ticsFilePath = sys.argv[1]
        lmx.config(ticsFilePath=ticsFilePath)

    print("locked= %d" % lmx.readLockedReg())
    lmx.dumpRegs()
    print("Pass")
