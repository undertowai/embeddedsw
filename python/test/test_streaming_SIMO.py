import sys
from test import TestSuite
from time import sleep
import numpy as np

from inet import Inet

class Test_Streaming(TestSuite):
    def __init__(self, config_path):
        TestSuite.__init__(self, config_path)

    def proc_cap_data(self, area, sn, txn, freq, fs, dtype=np.int16):
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

        self.publish(sn, txn, fs, freq, self.rx, iq_data)

    @TestSuite.Test
    def run_test(self):
        samplingFreq = self.rfdc.getSamplingFrequency()

        assert len(self.tx) == 1

        sn = self.sn
        iter_count = 0
        txn = self.tx[0]

        rx_dma_map = self.map_rx_to_dma_id(self.rx)

        while iter_count < self.num_iterations:

            print("*** Running Iteration : sn={}, rx={}, tx={}".format(sn, self.rx, [txn]))

            self.adc_dac_sync(False)
            self.start_dma(rx_dma_map)

            self.apply_hw_delay_per_tx(txn)
            area = self.start_dma(rx_dma_map)
            self.adc_dac_sync(True)

            self.wait_capture_done()
            self.proc_cap_data(area, sn, txn, 0, samplingFreq)

            sn += 1
            iter_count += 1

    @TestSuite.Test
    def run_test_c(self):
        samplingFreq = self.rfdc.getSamplingFrequency()

        assert len(self.tx) == 1
        txn = self.tx[0]

        rx_dma_map = self.map_rx_to_dma_id(self.rx)
        dmaBacth, area = self.prep_dma_batched(rx_dma_map)

        self.apply_hw_delay_per_tx(txn)

        self.c_loop.init(port=self.PORT, topic=self.TOPIC_FILTER,
                         sync_gpio_name=self.gpio_sync.getDtsName(),
                         fs=samplingFreq,
                         debug=self.debug)

        self.c_loop.loop(dmaBatch=dmaBacth, wait_time=self.calc_wait_time_ms(),
                         txn=txn, rx=self.rx)

        self.c_loop.destroy()

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <start sn> <config.json>")
        assert False

    sn=int(sys.argv[1])
    config_path = sys.argv[2]

    test = Test_Streaming(config_path)

    try:
        if not test.main_loop_in_c:
            test.run_test(sn=sn)
        else:
            test.run_test_c()

    except KeyboardInterrupt:
        test.shutdown_hmc()
        sys.exit(-1)