import sys
import ctypes as ct

from misc.dts import Dts
from misc.make import Make
from misc.mlock import MLock


class HMC63xx(MLock):
    def __init__(self, ipName):

        libPath = Make().makeLibs("hmc63xx")
        devName = Dts().ipToDtsName(ipName)

        reg = Dts().readPropertyU32(ipName, "reg")
        self.addr = (reg[0] << 32) | reg[1]
        self.size = (reg[2] << 32) | reg[3]

        self.libPath = libPath
        self.devName = devName
        self.lib = ct.CDLL(self.libPath)

        self.devNamePtr = ct.c_char_p(self.devName.encode("UTF-8"))

    @MLock.Lock
    def GpioInit(self):
        fun = self.lib.HMC63xx_GpioInit
        status = fun(self.devNamePtr)

        assert status == 0

    @MLock.Lock
    def IfGain_6300(self):
        fun = self.lib.HMC6300_SetIfGain

        status = fun(self.devNamePtr, int(self.ic), self.val)
        assert status == 0

    @MLock.Lock
    def RVGAGain_6300(self):
        fun = self.lib.HMC6300_SetRVGAGain

        status = fun(self.devNamePtr, int(self.ic), self.val)
        assert status == 0

    @MLock.Lock
    def Power_6300(self):
        fun = self.lib.HMC6300_Power

        status = fun(self.devNamePtr, int(self.ic), 0x1 if self.pwup == True else False)
        assert status == 0

    def __RMW_6300(self, ic, i, val, mask):
        fun = self.lib.HMC6300_RMW

        status = fun(self.devNamePtr, int(ic), i, val, mask)
        assert status >= 0
        return status

    @MLock.Lock
    def RMW_6300(self):
        mask = (1 << (self.bp[1] + 1)) - 1
        mask = mask >> self.bp[0]

        assert self.val <= mask

        val = self.val << self.bp[0]
        mask = 0xFF ^ (mask << self.bp[0])

        return self.__RMW_6300(self.ic, self.i, val, mask)

    def __CheckDefConfig_6300(self, ic):
        fun = self.lib.HMC6300_CheckConfig

        status = fun(self.devNamePtr, int(ic))
        if status != 0:
            raise Exception("Failed to config 6300 ic={}, status={}".format(ic, status))

    @MLock.Lock
    def DefaultConfig_6300(self):
        fun = self.lib.HMC6300_SendDefaultConfig

        status = fun(self.devNamePtr, int(self.ic))
        assert status == 0

        self.__CheckDefConfig_6300(self.ic)

    @MLock.Lock
    def PrintConfig_6300(self):
        fun = self.lib.HMC6300_PrintConfig

        status = fun(self.devNamePtr, int(self.ic))
        assert status == 0

    def __CheckDefConfig_6301(self, ic):
        fun = self.lib.HMC6301_CheckConfig

        status = fun(self.devNamePtr, int(ic))
        if status != 0:
            raise Exception("Failed to config 6301 ic={}, status={}".format(ic, status))

    @MLock.Lock
    def DefaultConfig_6301(self):
        fun = self.lib.HMC6301_SendDefaultConfig

        status = fun(self.devNamePtr, int(self.ic))
        assert status == 0

        self.__CheckDefConfig_6301(self.ic)

    @MLock.Lock
    def PrintConfig_6301(self):
        fun = self.lib.HMC6301_PrintConfig

        status = fun(self.devNamePtr, int(self.ic))
        assert status == 0

    def __RMW_6301(self, ic, i, val, mask):
        fun = self.lib.HMC6301_RMW

        status = fun(self.devNamePtr, int(ic), i, val, mask)
        assert status >= 0
        return status

    @MLock.Lock
    def RMW_6301(self):
        mask = (1 << (self.bp[1] + 1)) - 1
        mask = mask >> self.bp[0]

        assert self.val <= mask

        val = self.val << self.bp[0]
        mask = 0xFF ^ (mask << self.bp[0])

        return self.__RMW_6301(self.ic, self.i, val, mask)

    @MLock.Lock
    def SetAtt_6301(self):
        fun = self.lib.HMC6301_SetAtt

        status = fun(self.devNamePtr, int(self.ic), self.i, self.q, self.att)
        assert status == 0

    @MLock.Lock
    def IfGain_6301(self):
        fun = self.lib.HMC6301_SetIfGain

        status = fun(self.devNamePtr, int(self.ic), self.val)
        assert status == 0

    def LNAGain_6301(self, ic, gain):
        i = int(8)
        maxGain = 0x3
        assert gain <= maxGain

        gain = maxGain - gain

        self.RMW_6301(ic=ic, i=i, val=gain, bp=[3, 4])

    def ReadReg_6300(self, ic, i):
        return self.RMW_6300(ic=ic, i=i, val=0x0, bp=[0, 7])

    def ReadTemp_6300(self, ic):
        # enable temperature sensor
        self.RMW_6300(ic=ic, i=3, val=0x1, bp=[0, 0])
        self.RMW_6300(ic=ic, i=10, val=0x0, bp=[0, 0])
        temp = self.ReadReg_6300(ic, 27)
        tempC = ((85 - (-40)) * temp) / 0x1F
        return int(tempC)

    @MLock.Lock
    def Reset(self):
        fun = self.lib.HMC63xx_Reset

        status = fun(self.devNamePtr)
        assert status == 0


if __name__ == "__main__":

    hmc = HMC63xx("spi_gpio")

    limit = 1

    hmc.GpioInit()
    for i in range(limit):
        # hmc.DefaultConfig_6300(ic=i)
        hmc.PrintConfig_6300(ic=i)
        # hmc.DefaultConfig_6300(ic=i)
        hmc.PrintConfig_6301(ic=i)

    hmc.Reset()

    print("Pass")
