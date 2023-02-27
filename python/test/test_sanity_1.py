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
from data import DataProc
from player import DacPlayer

class Test_Sanity_1(TestSuite):

    def __init__(self, config_path):
        TestSuite.__init__(self, config_path)
        self.data_proc = DataProc('misc')
        self.player = DacPlayer()
        self.rx_to_bram_map = {0:0, 1:0, 2:0, 3:0, 4:1, 5:1, 6:1, 7:1}
        self.rx_to_bram_channel_map = {0:[0, 1], 1:[2, 3], 2:[4, 5], 3:[6, 7], 4:[0, 1], 5:[2, 3], 6:[4, 5], 7:[6, 7]}

    def compare_data(self, exp, got):
        for i, s in enumerate(exp):
            if s != got[i]:
                print(f'Sample missmatch i={i}')
                print[got[i-32:i+32]]
                print[exp[i-32:i+32]]
                assert False

    def getBramData(self, rxn, wDwellWindow):
        bram_id = self.rx_to_bram_map[rxn]
        dac_channel = self.rx_to_bram_channel_map[rxn]

        bramI = self.player.decompose_buf(bram_id, dac_channel[0])[0]
        bramQ = self.player.decompose_buf(bram_id, dac_channel[1])[0]

        bramI = np.tile(bramI, wDwellWindow)
        bramQ = np.tile(bramQ, wDwellWindow)
        return (bramI, bramQ)

    def proc_cap_data_raw(self, area, dtype=np.int16):
        for rxn in self.rx:
            a = area[rxn]

            aI, sI = a["I"]
            aQ, sQ = a["Q"]

            wDwellWindow = self.getDwellWindowPeriods()
            wDwellOffsetMax = self.integrator_depth - wDwellWindow
            wDwellOffsetMin = 0
            wDwellOffset = random.randint(wDwellOffsetMin, wDwellOffsetMax)
            print(f'[RAW] Iteration: rxn={rxn}, window offset={wDwellOffset}, window size={wDwellWindow}')

            wOffset = self.samples_in_unit * wDwellOffset
            wSize = self.samples_in_unit * wDwellWindow

            I = self.xddr_read(aI, sI, dtype)
            Q = self.xddr_read(aQ, sQ, dtype)

            Iw = I[wOffset:wOffset+wSize]
            Qw = Q[wOffset:wOffset+wSize]

            bramI, bramQ = self.getBramData(rxn, wDwellWindow)

            #print(Iw[:128])
            #print(bramI[:128])
            assert np.array_equal(Iw, bramI)
            assert np.array_equal(Qw, bramQ)

    def proc_cap_data_integrated(self, area, dtype=np.int16):
        for rxn in self.rx:
            a = area[rxn]

            aI, sI = a["I"]
            aQ, sQ = a["Q"]

            wDwellWindow = self.getDwellWindowPeriods()
            print(f'[INTEGRATED] Iteration: rxn={rxn}')

            I = self.xddr_read(aI, sI, dtype)
            Q = self.xddr_read(aQ, sQ, dtype)

            bramI, bramQ = self.getBramData(rxn, wDwellWindow)

            I = self.integrator.do_integration(I)
            Q = self.integrator.do_integration(Q)

            #print(I[:128])
            #print(bramI[:128])
            assert np.array_equal(I, bramI)
            assert np.array_equal(Q, bramQ)

    @TestSuite.Test
    def run_test(self):
        rx_dma_map = self.map_rx_to_dma_id(self.rx)

        self.adc_dac_sync(False)
        self.start_dma(rx_dma_map)

        self.apply_hw_delay_per_tx(self.tx[0])
        area = self.start_dma(rx_dma_map)
        self.adc_dac_sync(True)

        self.wait_capture_done()

        if test.isIntegrationEnabled():
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