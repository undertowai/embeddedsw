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

    def __init__(self):
        TestSuite.__init__(self)
        self.data_proc = DataProc('misc')
        self.player = DacPlayer()
        self.rx_to_bram_map = {0:0, 1:0, 2:0, 3:0, 4:1, 5:1, 6:1, 7:1}
        self.rx_to_bram_channel_map = {0:[0, 1], 1:[2, 3], 2:[4, 5], 3:[6, 7], 4:[0, 1], 5:[2, 3], 6:[4, 5], 7:[6, 7]}

    def proc_cap_data(self, area, do_average=False, dtype=np.int16):
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

            wOffset = self.dwell_samples * wDwellOffset
            wSize = self.dwell_samples * wDwellSize

            I = self.xddr_read(aI, sI, dtype, hwOffsetSamples)
            Q = self.xddr_read(aQ, sQ, dtype, hwOffsetSamples)

            Iw = I[wOffset:wOffset+wSize]
            Qw = Q[wOffset:wOffset+wSize]

            bram_id = self.rx_to_bram_map[rxn]
            dac_channel = self.rx_to_bram_channel_map[rxn]
            bramI = self.player.decompose_buf(bram_id, dac_channel[0])[0]
            bramQ = self.player.decompose_buf(bram_id, dac_channel[1])[0]

            bramTileI = np.tile(bramI, wDwellSize)
            bramTileQ = np.tile(bramQ, wDwellSize)

            assert np.array_equal(Iw, bramTileI)
            assert np.array_equal(Qw, bramTileQ)
            
            if do_average:
                
                assert (self.dwell_num % 2) == 0, "self.dwell_num should be multiply of 2"

                I = np.asarray(I, dtype=np.int32)
                Q = np.asarray(Q, dtype=np.int32)
                
                wAvg = 2
                shape = (int(self.dwell_num / wAvg), int(self.dwell_samples * wAvg))
                I = np.reshape(I, shape)
                Q = np.reshape(Q, shape)

                I = np.mean(I, axis=0, dtype=np.int32)
                Q = np.mean(Q, axis=0, dtype=np.int32)
                
                bramTileI = np.tile(bramI, wAvg)
                bramTileQ = np.tile(bramQ, wAvg)
                
                assert np.array_equal(I, bramTileI)
                assert np.array_equal(Q, bramTileQ)


    @TestSuite.Test
    def run_test(self):
        print('Running Sanity #1: Check Data coherence using SW loopback')

        rx_dma_map = self.map_rx_to_dma_id(self.rx)

        self.adc_dac_sync(False)
        area = self.start_dma(rx_dma_map, self.cap_ddr_offset, self.capture_size)
        #self.xddr_clear_area(area)
        self.adc_dac_sync(True)

        sleep(self.calc_capture_time(self.capture_size))

        self.proc_cap_data(area, do_average=self.do_average)

    @TestSuite.Test
    def warm_up(self):
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
        test.run_test(do_average=False)

    print('Checking Average :')
    test.run_test(do_average=True)