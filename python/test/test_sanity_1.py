import sys
from test import TestSuite
from time import sleep
import zmq
import pickle
import time
import numpy as np

from inet import Inet

sys.path.append("../misc")
sys.path.append("../xddr")
sys.path.append("../dac")
from xddr import Xddr
from data import DataProc
from player import DacPlayer

class Test_Sanity_1(TestSuite):
    def __init__(self):
        TestSuite.__init__(self)
        self.data_proc = DataProc('misc')
        self.player = DacPlayer()

    def check_cap_data(self, got, exp, offset_samples, assert_on_failure=True):
        got = got[offset_samples:]

        for i, s in enumerate(got):
            s_exp = exp[i%exp.size]
            if s != s_exp:
                print(got[i:i+32])
                print(exp[i:i+10])
                assert not assert_on_failure

            p = '- \\ | /'.split()[int(i/self.dwell_samples) % 4]
            print(f'\r{p}', end='')
        print()

    def proc_cap_data(self, area, dtype=np.int16):
        #Note: Only RX0, RX4 (I, Q) has loopback enabled so far
        a0 = area[0]
        a4 = area[4]

        aI, sI = a0["I"]
        aQ, sQ = a0["Q"]
        I0 = Xddr.read(aI, sI, dtype)
        Q0 = Xddr.read(aQ, sQ, dtype)

        aI, sI = a4["I"]
        aQ, sQ = a4["Q"]
        I4 = Xddr.read(aI, sI, dtype)
        Q4 = Xddr.read(aQ, sQ, dtype)

        bramI0 = self.player.decompose_buf(0, 0)[0]
        bramQ0 = self.player.decompose_buf(0, 1)[0]

        bramI4 = self.player.decompose_buf(1, 0)[0]
        bramQ4 = self.player.decompose_buf(1, 1)[0]

        print('Checking data sequence:')

        offset_samples = self.hw.HW_AXIS_DELAY_SAMPLES + 40
        self.check_cap_data(I0, bramI0, offset_samples)
        self.check_cap_data(Q0, bramQ0, offset_samples)

        self.check_cap_data(I4, bramI4, offset_samples)
        self.check_cap_data(Q4, bramQ4, offset_samples)

        #print('Checking data averaging:')

        #I = self.data_proc.dwellAvg(addrI, self.dwell_samples, self.dwell_num, offset_samples)
        #Q = self.data_proc.dwellAvg(addrQ, self.dwell_samples, self.dwell_num, offset_samples)

        #self.check_cap_data(I, bramI, 0, assert_on_failure=False)
        #self.check_cap_data(Q, bramQ, 0, assert_on_failure=False)

    @TestSuite.Test
    def run_test(self):
        print('Running Sanity #1: Check Data coherence using SW loopback')

        rx_dma_map = self.map_rx_to_dma_id(self.rx)

        for txn in self.tx:

            self.adc_dac_sync(False)

            area = self.start_dma(rx_dma_map, self.cap_ddr_offset, self.capture_size)

            self.adc_dac_sync(True)

            sleep(self.calc_capture_time(self.capture_size))

            self.proc_cap_data(area)



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <config.json path>")
        assert False

    config_path = sys.argv[1]

    test = Test_Sanity_1()

    test.load_config(config_path)

    for i in range(10):
        test.run_test()
