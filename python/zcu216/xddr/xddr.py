import sys
import numpy as np
import ctypes as ct
import mmap

sys.path.append("../misc")

from dts import Dts
from make import Make

class Xddr:
    def __init__(self, ipName):
        reg = Dts().readPropertyU32(ipName, "reg")

        self.address = (reg[0] << 32) | reg[1]
        self.length = (reg[2] << 32) | reg[3]

        libPath = Make().makeLibs('misc')
        self.lib = ct.CDLL(libPath)

    def test(self, addr, size):
        fun = self.lib.ddr_test

        addr += self.address
        status = fun(int((addr>>32) & 0xffffffff), int(addr & 0xffffffff), int(size))
        assert status == 0

    def clear(self, addr, size):
        fun = self.lib.ddr_zero

        addr += self.address
        status = fun(int((addr>>32) & 0xffffffff), int(addr & 0xffffffff), int(size))
        assert status == 0

    def read(offset, length, dtype=np.uint8):
        with open("/dev/mem", "r+b") as f:
            mm = mmap.mmap(
                fileno=f.fileno(),
                length=length,
                flags=mmap.MAP_SHARED,
                prot=mmap.PROT_READ | mmap.PROT_WRITE,
                access=mmap.ACCESS_READ | mmap.ACCESS_WRITE,
                offset=offset,
            )

            data = mm[:length]
            mm.close()
            return np.frombuffer(data, dtype=dtype)

    def capture(self, offset, length):
        return Xddr.read(offset, length)

    def base_address(self):
        return self.address

    def size(self):
        return self.length


if __name__ == "__main__":

    print('Performing DDR test')

    ddr0 = Xddr("ddr4_0")
    ddr1 = Xddr("ddr4_1")

    ddr0.test(0x0, 0x1000000)
    ddr1.test(0x0, 0x1000000)


    print("Pass")
