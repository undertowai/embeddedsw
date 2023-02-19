import os
import mmap
import numpy as np

class sequencer():

    reg_defs = { 'capture count': 0,
                 'current capture': 1,
                 'symbol cycles': 4,
                 'current symbol': 5,
                 'symbol integrations': 8,
                 'current integration': 9,
                 'dwell times': 12,
                 'current dwell time': 13,
                 'offset time': 16,
                 'current offset time': 17,
                 'loopback enable': 64 }

    def __init__(self, base: int) -> None:
        # Open raw dev mem 
        f = os.open("/dev/mem", os.O_RDWR)
        assert (f != None)

        print("Mapping at %08x\n", base)

        self.m = mmap.mmap(f,mmap.PAGESIZE,mmap.MAP_SHARED,mmap.PROT_WRITE|mmap.PROT_READ, offset=base)
        assert (self.m != None)

        self.regs = np.frombuffer(self.m, np.uint32, mmap.PAGESIZE >> 4)
        print(self.regs[0])


    def SetReg(self, offset: int, val: int) -> None:
        self.regs[offset] = val

    def DumpRegs(self) -> None:
        print ("-----")
        for k,v in self.reg_defs.items():
            d = self.regs[v]
            print(" %20s: \t%08x" % (k, d))

    def __del__(self) -> None:
        if (self.m != None):
            self.m.close()
        

if __name__ == "__main__":

    # Danger - fix to use __symbol__ interface
    s = sequencer(int("b0004000",16))
    s.DumpRegs()
    s.SetReg(0,128)
    s.DumpRegs()