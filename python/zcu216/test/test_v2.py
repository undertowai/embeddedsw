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

        self.RfdcClk.setup_rfdc()

        print("Test init done\n")
        return None

if __name__ == "__main__":

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.setsockopt(zmq.SNDHWM, 2)
    socket.bind("tcp://*:5555")

    test = TestV2();

    # Ugly mess - replace with symbol lookup in /proc
    p = V2Player(int('b2000000',16), 512*1024)
    c = V2Capture(int('b1000000', 16), 1024*1024)
    s = V2Sequencer(int("b0100000",16))

    # load a sin wave in each channel
    for ch in range(0,16):
        p.channels[ch] = ((np.sin(np.linspace(start=0,stop=5*2*np.pi,num=16384))) * 32767).astype(np.int16)

    # Run a capture
    for i in range(0,1):
        s.StartSequencer(captures=1,symbol_samples=16384,integrations=4000,dwells=1,offset=0)
       
        # Wait for sequencer to finish
        while (s.SequencerRunning()):
            pass

        # Copy out capture data
        channel_data = c.channels

        np.save("channel_data.npy", channel_data)

        print("Iteration %d" % i)

    exit(0)


