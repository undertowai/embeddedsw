import sys
import ctypes as ct
import numpy as np

sys.path.append("../misc")

from make import Make
from mlock import MLock


class Rfdc(MLock):
    def __init__(self, libName):
        libPath = Make().makeLibs(libName)
        self.lib = ct.CDLL(libPath)

    def init_clk104(self):
        fun = self.lib.RFDC_Init_Clk104

        status = fun()
        assert status == 0

    @MLock.Lock
    def restart(self):
        fun = self.lib.RFDC_Restart

        status = fun()
        assert status == 0

    @MLock.Lock
    def getSamplingFrequency(self):
        fun = self.lib.RFDC_GetSamplingFreq

        freq = fun()
        assert freq > 0

        return int(freq * 1_000_000)
    
    @MLock.Lock
    def setRFdcMTS(self):
        fun = self.lib.RFdcMTS
        
        status = fun(int(self.adc), int(self.dac))
        assert status == 0


if __name__ == "__main__":
    rfdc = Rfdc("rfdc2")
    # rfdc.init_clk104()
    # rfdc.restart()
    freq = rfdc.getSamplingFrequency()
    print(freq)

    print("Pass")
