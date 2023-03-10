import os
import numpy as np
import time
import zmq
import json
from json import JSONEncoder

from zcu216.rfdc.rfdc_clk import RfdcClk
from zcu216.axi.gpio import AxiGpio

from zcu216.v2.player import player as V2Player
from zcu216.v2.capture import capture as V2Capture
from zcu216.v2.sequencer import sequencer as V2Sequencer    

class TestV2():

    def __init__(self):
        self.AxiGpio = AxiGpio("axi_gpio");
        self.RfdcClk = RfdcClk()

        self.RfdcClk.init_clk104(lmk_path="zcu216/rfdc/configs/LMK_300MHz_RefClk_Out.txt")
        self.RfdcClk.setup_rfdc()
        self.RfdcClk.setup_mts()

        print("Test init done\n")
        return None

if __name__ == "__main__":

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.setsockopt(zmq.SNDHWM, 2)
    socket.bind("tcp://*:5555")

    # Ugly mess - replace with symbol lookup in /proc
    p = V2Player(int('b2000000',16), 512*1024)
    c = V2Capture(int('b1000000', 16), 1024*1024)
    s = V2Sequencer(int("b0100000",16))

    #
    # Load static
    #
    d = np.load("/home/petalinux/jiwoo.npy")
    fr = np.squeeze(np.real(d).astype(np.int16), axis=-1)
    fi = np.squeeze(np.imag(d).astype(np.int16), axis=-1)

    test = TestV2()

    p.channels[0] = fr 
    p.channels[1] = fi 

    # Run a capture
    for i in range(0,1000):
    
        s.StartSequencer(captures=1,
                         symbol_samples=4096,
                         integrations=4000,
                         dwells=0,
                         offset=4,
                         loopback=int("0000",16))
       
        # Wait for sequencer to finish
        while (s.SequencerRunning()):
            pass

        # send binary data 16 channels of int32 with implicit shape (16,16384)
        # receive with 
        #      m = socket.recv()
        #      channels = np.frombuffer(m, dtype=np.int32).reshape((16,-1))
        socket.send(np.ascontiguousarray(c.channels))

        print("Iteration %d" % i)

    exit(0)


