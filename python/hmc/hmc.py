import sys
import ctypes as ct

sys.path.append('../misc')

from dts import Dts
from make import Make


class HMC63xx:
    def __init__(self, libPath, devName):
        self.libPath = libPath
        self.devName = devName
        self.lib = ct.CDLL(self.libPath)

    def DefaultConfig_6300(self, ic):
        fun = self.lib.HMC6300_SendDefaultConfig

        status = fun(ct.c_char_p(self.devName.encode('UTF-8')), int(ic))
        assert status == 0

    def PrintConfig_6300(self, ic):
        fun = self.lib.HMC6300_PrintConfig

        status = fun(ct.c_char_p(self.devName.encode('UTF-8')), int(ic))
        assert status == 0

    def Reset(self):
        fun = self.lib.HMC63xx_Reset

        status = fun(ct.c_char_p(self.devName.encode('UTF-8')))
        assert status == 0



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('{}: Usage'.format(sys.argv[0]))
        exit()

    libPath = Make().makeLibs('hmc63xx')

    ipName ='spi_gpio'
    devName = Dts().ipToDtsName(ipName)

    ic = sys.argv[1]

    hmc = HMC63xx(libPath, devName)

    hmc.DefaultConfig_6300(ic)
    hmc.PrintConfig_6300(ic)
    hmc.Reset()

    print('Pass')