import sys
from test import TestSuite
from time import sleep
import zmq
import pickle
import time
import numpy as np
import collections

from inet import Inet

sys.path.append("../misc")
sys.path.append("../xddr")
from xddr import Xddr

class Test_Streaming(TestSuite):
    def __init__(self, port):
        TestSuite.__init__(self)

    def proc_cap_data(self, area, sn, txn, freq, fs, dtype=np.int16):
        iq_data = []

        print(area)
        for rxn in self.rx:
            a = area[rxn]
            addrI, sizeI = a["I"]
            addrQ, sizeQ = a["Q"]

            I = self.xddr_read(addrI, sizeI, dtype)
            Q = self.xddr_read(addrQ, sizeQ, dtype)
            iq_data.append((I, Q))

        self.publish(sn, txn, fs, freq, self.rx, iq_data)

    @TestSuite.Test
    def run_test(self):
        samplingFreq = self.rfdc.getSamplingFrequency()

        sn = self.sn
        iter_count = 0
        cap_ddr_offset = 0x0

        rx_dma_map = self.map_rx_to_dma_id(self.rx)

        self.setup_hmc([], self.rx)

        while iter_count < self.num_iterations:
            
            print("*** Running Iteration : sn={}, rx={}".format(sn, self.rx))

            self.adc_dac_sync(False)

            area = self.start_dma(rx_dma_map, cap_ddr_offset, self.capture_size)

            self.adc_dac_sync(True)

            sleep(self.calc_capture_time(self.capture_size))

            self.proc_cap_data(area, sn, 0, 0, samplingFreq)

            sn += 1
            iter_count += 1

        self.shutdown_hmc()


if __name__ == "__main__":

    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <num_iterations> <current sn> <config.json>")
        assert False

    num_iterations = int(sys.argv[1])
    sn=int(sys.argv[2])
    config_path = sys.argv[3]

    test = Test_Streaming(Inet.PORT)
    
    test.load_config(config_path)

    test.run_test(
        num_iterations=num_iterations,
        sn=sn
    )
