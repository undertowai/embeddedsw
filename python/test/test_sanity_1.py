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

    def check_cap_data(self, data, exp, offset_samples):
        data = data[offset_samples:]

        for i, s in enumerate(data):
            s_exp = exp[i%exp.size]
            if s != s_exp:
                print(data[i-10:i+10])
                print(f'Missmatch at {i}: exp={s_exp} != {s}')
                assert False

            p = '- \\ | /'.split()[int(i/self.dwell_samples) % 4]
            print(f'\r{p}', end='')
        print()

    def proc_cap_data(self, area, dtype=np.int16):
        #Note: Only RX0 (I, Q) has loopback enabled so far
        loopback_rx_id = 0

        a = area[loopback_rx_id]

        addrI, sizeI = a["I"]
        addrQ, sizeQ = a["Q"]
        I = Xddr.read(addrI, sizeI, dtype)
        Q = Xddr.read(addrQ, sizeQ, dtype)

        bramI = self.player.decompose_buf(0, 0)[0]
        bramQ = self.player.decompose_buf(0, 1)[0]

        print('Checking data sequence:')

        offset_samples = 24
        self.check_cap_data(I, bramI, offset_samples)
        self.check_cap_data(Q, bramQ, offset_samples)

        print('Checking data averaging:')

        #TODO : fix & uncomment
        #I = self.data_proc.dwellAvg(addrI, self.dwell_samples, self.dwell_num, offset_samples)
        #Q = self.data_proc.dwellAvg(addrQ, self.dwell_samples, self.dwell_num, offset_samples)

        #self.check_cap_data(I, bramI, 0)
        #self.check_cap_data(Q, bramQ, 0)

    @TestSuite.Test
    def run_test(self):
        print('Running Sanity #1: Check Data coherence using SW loopback')

        cap_ddr_offset = 0x0

        rx_dma_map = self.map_rx_to_dma_id(self.rx)

        for txn in self.tx:

            self.adc_dac_sync(False)

            area = self.start_dma(rx_dma_map, cap_ddr_offset, self.captureSize)

            self.adc_dac_sync(True)

            sleep(self.calc_capture_time(self.captureSize))

            self.proc_cap_data(area)



if __name__ == "__main__":  
    tx = [0]
    rx = [0, 1, 2, 3]

    test = Test_Sanity_1()
    dwell_samples = 64 * 1024
    dwell_num = 2
    captureSize = dwell_samples * dwell_num * test.hw.BYTES_PER_SAMPLE

    test.set_loobback(True)

    test.run_test(
        captureSize=captureSize,
        tx=tx,
        rx=rx,
        dwell_samples=dwell_samples,
        dwell_num=dwell_num
    )
