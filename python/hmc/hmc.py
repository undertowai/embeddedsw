import sys
import ctypes as ct

sys.path.append('../misc')

from dts import Dts
from make import Make


class HMC63xx:
    def __init__(self, ipName):

        libPath = Make().makeLibs('hmc63xx')
        devName = Dts().ipToDtsName(ipName)

        reg = Dts().readPropertyU32(ipName, 'reg')
        self.addr = (reg[0] << 32) | reg[1]
        self.size = (reg[2] << 32) | reg[3]

        self.libPath = libPath
        self.devName = devName
        self.lib = ct.CDLL(self.libPath)

        self.devNamePtr = ct.c_char_p(self.devName.encode('UTF-8'))

    def GpioInit(self):
        fun = self.lib.HMC63xx_GpioInit
        status = fun(self.devNamePtr)

        assert status == 0

    def IfGain_6300(self, ic, val):
        fun = self.lib.HMC6300_SetIfGain

        status = fun(self.devNamePtr, int(ic), val)
        assert status == 0

    def RMW_6300(self, ic, i, val, mask):
        fun = self.lib.HMC6300_RMW

        status = fun(self.devNamePtr, int(ic), i, val, mask)
        assert status == 0

    def __CheckDefConfig_6300(self, ic):
        fun = self.lib.HMC6300_CheckConfig

        status = fun(self.devNamePtr, int(ic))
        if status != 0:
            raise Exception("Failed to config 6300 ic={}, status={}".format(ic, status))

    def DefaultConfig_6300(self, ic):
        fun = self.lib.HMC6300_SendDefaultConfig

        status = fun(self.devNamePtr, int(ic))
        assert status == 0

        self.__CheckDefConfig_6300(ic)

    def PrintConfig_6300(self, ic):
        fun = self.lib.HMC6300_PrintConfig

        status = fun(self.devNamePtr, int(ic))
        assert status == 0

    def __CheckDefConfig_6301(self, ic):
        fun = self.lib.HMC6301_CheckConfig

        status = fun(self.devNamePtr, int(ic))
        if status != 0:
            raise Exception("Failed to config 6301 ic={}, status={}".format(ic, status))

    def DefaultConfig_6301(self, ic):
        fun = self.lib.HMC6301_SendDefaultConfig

        status = fun(self.devNamePtr, int(ic))
        assert status == 0

        self.__CheckDefConfig_6301(ic)

    def PrintConfig_6301(self, ic):
        fun = self.lib.HMC6301_PrintConfig

        status = fun(self.devNamePtr, int(ic))
        assert status == 0

    def RMW_6301(self, ic, i, val, mask):
        fun = self.lib.HMC6301_RMW

        status = fun(self.devNamePtr, int(ic), i, val, mask)
        assert status == 0

    def Reset(self):
        fun = self.lib.HMC63xx_Reset

        status = fun(self.devNamePtr)
        assert status == 0



if __name__ == "__main__":

    hmc = HMC63xx('spi_gpio')

    limit = 8

    hmc.GpioInit()
    for i in range(limit):
        hmc.DefaultConfig_6301(i)
        hmc.DefaultConfig_6300(i)

    hmc.Reset()

    print('Pass')