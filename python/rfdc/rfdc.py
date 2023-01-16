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

    def init_clk104_External(self, lmk_data, lmx_rf1_data, lmx_rf2_data):
        fun = self.lib.RFDC_Init_Clk104_External

        print(f'lmk_data.size={lmk_data.size}')

        status = fun(
            ct.c_void_p(lmk_data.ctypes.data) if lmk_data is not None else None,
            int(lmk_data.size) if lmk_data is not None else 0,

            ct.c_void_p(lmx_rf1_data.ctypes.data) if lmx_rf1_data is not None else None,
            int(lmx_rf1_data.size) if lmx_rf1_data is not None else 0,

            ct.c_void_p(lmx_rf2_data.ctypes.data) if lmx_rf2_data is not None else None,
            int(lmx_rf2_data.size) if lmx_rf2_data is not None else 0
        )
        assert status == 0

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
        
        status = fun(int(self.adc), int(self.dac), int(self.adc_ref), int(self.dac_ref))
        assert status == 0


if __name__ == "__main__":
    rfdc = Rfdc("rfdc2")
    # rfdc.init_clk104()
    # rfdc.restart()
    freq = rfdc.getSamplingFrequency()
    print(freq)

    print("Pass")
