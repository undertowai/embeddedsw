import sys
import ctypes as ct
import numpy as np
from numpy.ctypeslib import ndpointer

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
    if len(sys.argv) != 4:
        print('{}: Usage'.format(sys.argv[0]))
        exit()

    libPath = sys.argv[1]
    devName = sys.argv[2]
    ic = sys.argv[3]

    #TODO:
    devName = devName.split('/')[2].split('@')
    devName = devName[1] + '.' + devName[0]


    hmc = HMC63xx(libPath, devName)

    hmc.DefaultConfig_6300(ic)
    hmc.PrintConfig_6300(ic)
    hmc.Reset()