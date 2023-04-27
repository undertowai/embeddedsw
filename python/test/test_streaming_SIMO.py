import sys
from test import TestSuite
from time import sleep
import numpy as np

from inet import Inet

class Test_Streaming(TestSuite):
    def __init__(self, config_path):
        TestSuite.__init__(self, config_path)

    def proc_cap_data(self, area, sn, freq, fs, dtype=np.int16):
        iq_data = []
        for rxn in self.rx:
            a = area[rxn]
            addrI, sizeI = a["I"]
            addrQ, sizeQ = a["Q"]

            I = self.xddr_read(addrI, sizeI, dtype)
            Q = self.xddr_read(addrQ, sizeQ, dtype)

            I = self.integrator.do_integration(I)
            Q = self.integrator.do_integration(Q)

            iq_data.append((I, Q))

        self.publish(sn, self.tx, fs, freq, self.rx, iq_data)

    @TestSuite.Test
    def run_test(self):
        samplingFreq = self.rfdc.getSamplingFrequency()

        sn = self.sn
        iter_count = 0
        txn = self.tx[0]

        rx_dma_map = self.map_rx_to_dma_id(self.rx)

        while iter_count < self.num_iterations:

            print("*** Running Iteration : sn={}, rx={}, tx={}".format(sn, self.rx, self.tx))

            self.adc_dac_sync(False)
            self.start_dma(rx_dma_map)

            self.apply_hw_delay_per_tx(txn)
            area = self.start_dma(rx_dma_map)
            self.adc_dac_sync(True)

            self.wait_capture_done()
            self.proc_cap_data(area, sn, 0, samplingFreq)

            sn += 1
            iter_count += 1

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <start sn> <config.json>")
        assert False

    sn=int(sys.argv[1])
    config_path = sys.argv[2]

    test = Test_Streaming(config_path)

    try:
        test.run_test(
            sn=sn
        )
    except KeyboardInterrupt:
        test.shutdown_hmc()
        sys.exit(-1)
