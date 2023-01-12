

import sys
import ctypes as ct
import numpy as np

sys.path.append("../misc")

from make import Make

class DataProc:
    def __init__(self, libName):
        libPath = Make().makeLibs(libName)
        self.lib = ct.CDLL(libPath)
        
    def dwellAvg(self, ddr_offset, dwell_samples, dwell_num, dwell_offset):
        fun = self.lib.dwell_avg
        
        dwell = np.empty(dwell_samples, dtype=np.int32)
        dwell_ptr = ct.c_void_p(dwell.ctypes.data)

        status = fun(dwell_ptr,
                     int(ddr_offset>>32),
                     int(ddr_offset & 0xffffffff),
                     int(dwell_offset),
                     int(dwell_samples),
                     int(dwell_num) )
        
        assert status == 0
        return dwell
        
