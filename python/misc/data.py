

import sys
import ctypes as ct
import numpy as np

sys.path.append("../misc")

from make import Make

class DataProc:
    def __init__(self, libName):
        libPath = Make().makeLibs(libName)
        self.lib = ct.CDLL(libPath)

    def dwellAvg(self, ddr_offset, samples_in_unit, integrator_depth, dwell_offset):
        fun = self.lib.dwell_avg

        dwell = np.empty(samples_in_unit, dtype=np.int32)
        dwell_ptr = ct.c_void_p(dwell.ctypes.data)

        status = fun(dwell_ptr,
                     int(ddr_offset>>32),
                     int(ddr_offset & 0xffffffff),
                     int(dwell_offset),
                     int(samples_in_unit),
                     int(integrator_depth) )

        assert status == 0
        return dwell