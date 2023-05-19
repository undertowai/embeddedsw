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
from player import DacPlayer

class Test_Sanity_1(TestSuite):

    def __init__(self, config_path):
        TestSuite.__init__(self, config_path)
        self.player = DacPlayer()
        self.rx_to_bram_map = {0:0, 1:0, 2:0, 3:0, 4:1, 5:1, 6:1, 7:1}
        self.rx_to_bram_channel_map = {0:[0, 1], 1:[2, 3], 2:[4, 5], 3:[6, 7], 4:[0, 1], 5:[2, 3], 6:[4, 5], 7:[6, 7]}

    def compare_data(self, got, exp):
        print(f'got.size={got.size}, exp.size={exp.size}')
        for i, s in enumerate(exp):
            if s != got[i]:
                print(f'Sample missmatch i={i}')
                print(f'got = {got[i:i+64]}')
                print(f'exp = {exp[i:i+64]}')
                assert False

    def getBramData(self, rxn):
        bram_id = self.rx_to_bram_map[rxn]
        dac_channel = self.rx_to_bram_channel_map[rxn]

        bramI = self.player.decompose_buf(bram_id, dac_channel[0])[0]
        bramQ = self.player.decompose_buf(bram_id, dac_channel[1])[0]

        bramTileNum = self.getStreamSizeSamples() // bramI.size

        bramI = np.tile(bramI, bramTileNum)
        bramQ = np.tile(bramQ, bramTileNum)
        return (bramI, bramQ)

    def proc_cap_data_raw(self, area, dtype=np.int16):
        for rxn in self.rx:
            a = area[rxn]

            aI, sI = a["I"]
            aQ, sQ = a["Q"]

            print(f'[RAW] Iteration: rxn={rxn}')

            I = self.xddr_read(aI, sI, dtype)
            Q = self.xddr_read(aQ, sQ, dtype)

            bramI, bramQ = self.getBramData(rxn)

            assert np.array_equal(I, bramI)
            assert np.array_equal(Q, bramQ)

    def proc_cap_data_integrated(self, area, dtype=np.int16):
        for rxn in self.rx:
            a = area[rxn]

            aI, sI = a["I"]
            aQ, sQ = a["Q"]

            wDwellWindow = self.getDwellWindowPeriods()
            print(f'[INTEGRATED] Iteration: rxn={rxn}')

            I = self.xddr_read(aI, sI, dtype)
            Q = self.xddr_read(aQ, sQ, dtype)

            I = self.integrator.do_integration(I)
            Q = self.integrator.do_integration(Q)

            #Must be zeros

            assert not I.any()
            assert not Q.any()

    def run_test(self):
        rx_dma_map = self.map_rx_to_dma_id(self.rx)

        self.adc_dac_sync(False)
        self.start_dma(rx_dma_map)

        area = self.start_dma(rx_dma_map)
        self.adc_dac_sync(True)

        sleep(self.calc_wait_time_ms() / 1000)

        self.integrator.do_check_errors(self.rx)

        if self.isIntegrationEnabled():
            self.proc_cap_data_integrated(area)
        else:
            self.proc_cap_data_raw(area)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <config.json path>")
        assert False

    config_path = sys.argv[1]

    test = Test_Sanity_1(config_path)

    for i in range(test.num_iterations):
        print(f'Iteration {i}')
        test.run_test()