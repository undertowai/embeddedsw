import os
import mmap
import numpy as np

class player():

    def __init__(self, base: int, size: int) -> None:
  
        print("DAC Player Mapping at %08x" % base)

        size = (size // mmap.PAGESIZE) * mmap.PAGESIZE
        self.size = size >> 1 # size of int16
        print(self.size)

        f = os.open("/dev/mem", os.O_RDWR)
        m = mmap.mmap(f, size, flags=mmap.MAP_SHARED, prot=mmap.PROT_WRITE|mmap.PROT_READ, offset=base)
        
        # Create 16 channel buffers 
        self.channels = np.frombuffer(m, dtype=np.int16, count=self.size, offset=0).reshape(16,-1)


if __name__ == "__main__":

    p = player(int('b2000000',16), 512*1024)

    print(p.channels[0:128])
