import os
import mmap
import numpy as np

class player():

    def __init__(self, base: int, size: int) -> None:
  
        print("DAC Player Mapping at %08x" % base)

        size = (size // mmap.PAGESIZE) * mmap.PAGESIZE
        self.size = size >> 1 # size of int16
        print(self.size, size)

        f = os.open("/dev/mem", os.O_RDWR, os.O_SYNC)

        assert (f != None)

        self.m = mmap.mmap(f, size, flags=mmap.MAP_SHARED, prot=mmap.PROT_WRITE|mmap.PROT_READ, offset=base)

        # Create 16 channel buffers 
        self.channels = np.frombuffer(self.m, dtype=np.int16, count=self.size, offset=0).reshape(16,-1)
        print(self.channels.shape)

if __name__ == "__main__":

    p = player(int('b2000000',16), 512*1024)
    p.channels[0] = ((np.sin(np.linspace(start=0,stop=2*np.pi,num=16384)) * 100.0)).astype(np.int16)
    p.channels[1] = ((np.cos(np.linspace(start=0,stop=2*np.pi,num=16384)) * 100.0)).astype(np.int16)

    print(p.channels[0][0:16384:100])
    print(p.channels[1][0:16384:100])
