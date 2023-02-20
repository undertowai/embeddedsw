import os
import mmap
import numpy as np

class capture():

    def __init__(self, base: int, size: int) -> None:
  
        print("DAC Capture Mapping at %08x" % base)

        size = (size // mmap.PAGESIZE) * mmap.PAGESIZE
        self.size = size >> 2 # size of int32
        print(self.size, size)

        f = os.open("/dev/mem", os.O_RDWR, os.O_SYNC)

        assert (f != None)

        self.m = mmap.mmap(f, size, flags=mmap.MAP_SHARED, prot=mmap.PROT_WRITE|mmap.PROT_READ, offset=base)

        # Create 16 channel buffers 
        self.channels = np.frombuffer(self.m, dtype=np.int32, count=self.size, offset=0).reshape(16,-1)

if __name__ == "__main__":

    c = capture(int('b1000000', 16), 1024*1024)

    print(c.channels[0][0:128])

    c.channels[0][1] = 1
    c.channels[15][1] = 2

    print(c.channels[0][0:128])
    print(c.channels[15][0:128])
