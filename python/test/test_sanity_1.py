import sys
from test import TestSuite
from time import sleep
import zmq
import pickle
import time
import numpy as np
import random

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
        self.rx_to_bram_map = {0:0, 1:0, 2:0, 3:0, 4:1, 5:1, 6:1, 7:1}
        self.rx_to_bram_channel_map = {0:[0, 1], 1:[2, 3], 2:[4, 5], 3:[6, 7], 4:[0, 1], 5:[2, 3], 6:[4, 5], 7:[6, 7]}

    def check_cap_data(self, got, exp, assert_on_failure=True):
        for i, s in enumerate(got):
            s_exp = exp[i%exp.size]
            if s != s_exp:
                print(f'Missmatch at {i}')
                print(got[i:i+32])
                print(exp[i:i+10])
                assert not assert_on_failure

            p = '- \\ | /'.split()[int(i/self.dwell_samples) % 4]
            print(f'\r{p}', end='')
        print()

    def proc_cap_data(self, area, dtype=np.int16):
        for rxn in self.rx:
            a = area[rxn]

            aI, sI = a["I"]
            aQ, sQ = a["Q"]

            wDwellSize = 3
            wDwellOffsetMax = self.dwell_num - wDwellSize
            wDwellOffsetMin = 0
            wDwellOffset = random.randint(wDwellOffsetMin, wDwellOffsetMax)
            print(f'Iteration: rxn={rxn}, window offset={wDwellOffset}')

            hwOffsetSamples = 40

            wOffset = self.dwell_samples * wDwellOffset + hwOffsetSamples
            wSize = self.dwell_samples * wDwellSize

            I = self.xddr_read(aI, sI, dtype)[wOffset:wOffset+wSize]
            Q = self.xddr_read(aQ, sQ, dtype)[wOffset:wOffset+wSize]

            bram_id = self.rx_to_bram_map[rxn]
            dac_channel = self.rx_to_bram_channel_map[rxn]
            bramI = self.player.decompose_buf(bram_id, dac_channel[0])[0]
            bramQ = self.player.decompose_buf(bram_id, dac_channel[1])[0]

            bramI = np.tile(bramI, wDwellSize)
            bramQ = np.tile(bramQ, wDwellSize)

            assert np.array_equal(I, bramI)
            assert np.array_equal(Q, bramQ)

            #self.check_cap_data(I, bramI)
            #self.check_cap_data(Q, bramQ)

            #print('Checking data averaging:')

            #I = self.data_proc.dwellAvg(addrI, self.dwell_samples, self.dwell_num, offset_samples)
            #Q = self.data_proc.dwellAvg(addrQ, self.dwell_samples, self.dwell_num, offset_samples)

            #self.check_cap_data(I, bramI, 0, assert_on_failure=False)
            #self.check_cap_data(Q, bramQ, 0, assert_on_failure=False)

    @TestSuite.Test
    def run_test(self):
        print('Running Sanity #1: Check Data coherence using SW loopback')

        rx_dma_map = self.map_rx_to_dma_id(self.rx)

        self.adc_dac_sync(False)
        area = self.start_dma(rx_dma_map, self.cap_ddr_offset, self.capture_size)
        #self.xddr_clear_area(area)
        self.adc_dac_sync(True)

        sleep(self.calc_capture_time(self.capture_size))

        self.proc_cap_data(area)

    @TestSuite.Test
    def warm_up(self):
        """
        This function is needed to fill FIFO's so, offset are applied correctly
        """
        print('Warming up...')

        rx_dma_map = self.map_rx_to_dma_id(self.rx)

        self.start_dma(rx_dma_map, self.cap_ddr_offset, self.capture_size)
        self.adc_dac_sync(True)
        sleep(self.calc_capture_time(self.capture_size))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <config.json path>")
        assert False

    config_path = sys.argv[1]

    test = Test_Sanity_1()

    test.load_config(config_path)

    test.warm_up()
    for i in range(10):
        print(f'Iteration {i}')
        test.run_test()
