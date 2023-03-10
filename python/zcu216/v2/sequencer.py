import os
import mmap
import numpy as np

class sequencer():

    CAPTURE_COUNT='capture count'
    CURRENT_CAPTURE='current capture'
    SYMBOL_CYCLES='symbol cycles'
    CURRENT_SYMBOL='current symbol'
    SYMBOL_INTEGRATION='symbol integrations'
    CURRENT_INTEGRATION='current integration'
    DWELL_TIMES='dwell times'
    CURRENT_DWELL_TIME='current dwell time'
    OFFSET_TIME='offset time'
    CURRENT_OFFSET_TIME='current offset time'
    LOOPBACK_ENABLE='loopback enable'

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

        print("Mapping at %08x\n" % base)

        self.m = mmap.mmap(f,mmap.PAGESIZE,mmap.MAP_SHARED,mmap.PROT_WRITE|mmap.PROT_READ, offset=base)
        assert (self.m != None)

        self.regs = np.frombuffer(self.m, np.uint32, mmap.PAGESIZE >> 4)

    def StartSequencer(self,
                       captures: int,
                       symbol_samples: int,
                       integrations: int,
                       dwells: int,
                       offset: int,
                       loopback: int = 0
                       ) -> None:
        
        # Sanity check based on hardware configuration
        assert (symbol_samples <= 4096)
        assert (integrations   <= 32768)
        assert (offset         <= symbol_samples * 4)

        # First disable sequencer
        self.regs[self.reg_defs['capture count']] = 0

        # Clear state
        self.regs[self.reg_defs['current capture']] = 0
        self.regs[self.reg_defs['current symbol']] = 0
        self.regs[self.reg_defs['current integration']] = 0
        self.regs[self.reg_defs['current dwell time']] = 0
        self.regs[self.reg_defs['current offset time']] = 0

        self.regs[self.reg_defs['symbol cycles']] = symbol_samples
        self.regs[self.reg_defs['symbol integrations']] = integrations
        self.regs[self.reg_defs['dwell times']] = dwells
        self.regs[self.reg_defs['offset time']] = offset
        self.regs[self.reg_defs['loopback enable']] = loopback

        # and finally start 
        self.regs[self.reg_defs['capture count']] = captures

    def SequencerRunning(self) -> bool:
        return self.regs[self.reg_defs['capture count']] != self.regs[self.reg_defs['current capture']]

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