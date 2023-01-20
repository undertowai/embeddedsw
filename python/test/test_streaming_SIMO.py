import sys
from test import TestSuite
from time import sleep
import numpy as np

from inet import Inet

class Test_Streaming(TestSuite):
    def __init__(self, port):
        TestSuite.__init__(self)

    def proc_cap_data(self, area, sn, txn, freq, fs, dtype=np.int16):
        iq_data = []
        for rxn in self.rx:
            a = area[rxn]
            addrI, sizeI = a["I"]
            addrQ, sizeQ = a["Q"]

            if self.DEBUG:
                print(f'I: {hex(addrI)}:{hex(sizeI)}, Q: {hex(addrQ)}:{hex(sizeQ)}')

            hwOffsetSamples = self.hw_offset_map[f'TX{txn}'][rxn]

            I = self.xddr_read(addrI, sizeI, dtype, hwOffsetSamples)
            Q = self.xddr_read(addrQ, sizeQ, dtype, hwOffsetSamples)
            
            if self.do_dwell_avg:
                print('Do Dwell Averaging ...')
                assert (self.dwell_num % 2) == 0, "self.dwell_num should be multiply of 2"

                I = np.asarray(I, dtype=np.int32)
                Q = np.asarray(Q, dtype=np.int32)
                
                wAvg = 2
                shape = (int(self.dwell_num / wAvg), int(self.dwell_samples * wAvg))
                I = np.reshape(I, shape)
                Q = np.reshape(Q, shape)

                I = np.mean(I, axis=0, dtype=np.int32)
                Q = np.mean(Q, axis=0, dtype=np.int32)

            iq_data.append((I, Q))

        self.publish(sn, txn, fs, freq, self.rx, iq_data)

    @TestSuite.Test
    def run_test(self):
        samplingFreq = self.rfdc.getSamplingFrequency()

        assert len(self.tx) == 1

        sn = self.sn
        iter_count = 0
        cap_ddr_offset = 0x0
        txn = self.tx[0]

        rx_dma_map = self.map_rx_to_dma_id(self.rx)

        while iter_count < self.num_iterations:

            print("*** Running Iteration : sn={}, rx={}, tx={}".format(sn, self.rx, [txn]))

            self.adc_dac_sync(False)
            area = self.start_dma(rx_dma_map, cap_ddr_offset, self.capture_size)
            self.adc_dac_sync(True)

            sleep(self.calc_capture_time(self.capture_size))
            self.proc_cap_data(area, sn, txn, 0, samplingFreq)

            sn += 1
            iter_count += 1

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <start sn> <config.json>")
        assert False

    sn=int(sys.argv[1])
    config_path = sys.argv[2]

    test = Test_Streaming(Inet.PORT)

    try:
        test.load_config(config_path)

        test.run_test(
            sn=sn
        )
    except KeyboardInterrupt:
        test.shutdown_hmc()
        sys.exit(-1)