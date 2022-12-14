

import sys
import ctypes as ct
import numpy as np
import os
import mmap

sys.path.append('../misc')

from dts import Dts

class Xddr:
    def __init__(self, ipName):
        reg = Dts().readPropertyU32(ipName, 'reg')

        self.address = (reg[0] << 32) | reg[1]
        self.length = (reg[2] << 32) | reg[3]

    def capture(self, offset, length):
        #TODO: mmap should not allocate memory ?
        data = []
        with open('/dev/mem', 'r+b') as f:
            mm = mmap.mmap(fileno=f.fileno(),
                                length=length,
                                flags=mmap.MAP_SHARED,
                                prot=mmap.PROT_READ | mmap.PROT_WRITE,
                                access=mmap.ACCESS_READ | mmap.ACCESS_WRITE,
                                offset=offset)

            data = mm[:length]
            mm.close()
            return np.frombuffer(data, dtype=np.uint8)

    def base_address(self):
        return self.address

if __name__ == "__main__":

    ddr = Xddr('ddr4_0')

    #ddr.capture('cap0.bin', 0x48_0000_0000, 0x1000)

    print("Pass")