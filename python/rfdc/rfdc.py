import sys
import ctypes as ct
import numpy as np

sys.path.append('../misc')

from make import Make

class Rfdc:

    def __init__(self, libName):
        libPath = Make().makeLibs(libName)
        self.lib = ct.CDLL(libPath)

    def init(self):
        fun = self.lib.RFDC_Init

        status = fun()
        assert status == 0

if __name__ == "__main__":
    rfdc = Rfdc('rfdc2')
    rfdc.init()

    print("Pass")