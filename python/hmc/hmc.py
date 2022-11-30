import sys
import ctypes as ct

sys.path.append('../misc')

from dts import Dts
from make import Make


class HMC63xx:
    def __init__(self, ipName):

        libPath = Make().makeLibs('hmc63xx')
        devName = Dts().ipToDtsName(ipName)

        self.libPath = libPath
        self.devName = devName
        self.lib = ct.CDLL(self.libPath)

        self.GpioInit()

    def GpioInit(self):
        fun = self.lib.HMC63xx_GpioInit
        status = fun(self.devName.encode('UTF-8'))

        assert status == 0

    def IfGain_6300(self, ic, val):
        fun = self.lib.HMC6300_SetIfGain

        status = fun(ct.c_char_p(self.devName.encode('UTF-8')), int(ic), val)
        assert status == 0


    def __CheckDefConfig_6300(self, ic):
        fun = self.lib.HMC6300_CheckConfig

        status = fun(ct.c_char_p(self.devName.encode('UTF-8')), int(ic))
        if status != 0:
            raise Exception("Failed to config 6300 ic={}, status={}".format(ic, status))

    def DefaultConfig_6300(self, ic):
        fun = self.lib.HMC6300_SendDefaultConfig

        status = fun(ct.c_char_p(self.devName.encode('UTF-8')), int(ic))
        assert status == 0

        self.__CheckDefConfig_6300(ic)

    def PrintConfig_6300(self, ic):
        fun = self.lib.HMC6300_PrintConfig

        status = fun(ct.c_char_p(self.devName.encode('UTF-8')), int(ic))
        assert status == 0

    def __CheckDefConfig_6301(self, ic):
        fun = self.lib.HMC6301_CheckConfig

        status = fun(ct.c_char_p(self.devName.encode('UTF-8')), int(ic))
        if status != 0:
            raise Exception("Failed to config 6301 ic={}, status={}".format(ic, status))

    def DefaultConfig_6301(self, ic):
        fun = self.lib.HMC6301_SendDefaultConfig

        status = fun(ct.c_char_p(self.devName.encode('UTF-8')), int(ic))
        assert status == 0

        self.__CheckDefConfig_6301(ic)

    def PrintConfig_6301(self, ic):
        fun = self.lib.HMC6301_PrintConfig

        status = fun(ct.c_char_p(self.devName.encode('UTF-8')), int(ic))
        assert status == 0

    def Reset(self):
        fun = self.lib.HMC63xx_Reset

        status = fun(ct.c_char_p(self.devName.encode('UTF-8')))
        assert status == 0



if __name__ == "__main__":

    hmc = HMC63xx('spi_gpio')

    for i in range(8) :
        hmc.DefaultConfig_6300(i)

    for i in range(8) :
        hmc.DefaultConfig_6301(i)

    hmc.Reset()

    print('Pass')