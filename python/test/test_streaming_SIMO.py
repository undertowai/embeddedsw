import sys
from test import TestSuite
from time import sleep
import numpy as np

from inet import Inet

class Test_Streaming(TestSuite):
    def __init__(self, config_path):
        TestSuite.__init__(self, config_path)

    @TestSuite.Test
    def run_test(self):
        samplingFreq = self.rfdc.getSamplingFrequency()

        assert len(self.tx) == 1
        txn = self.tx[0]

        self.setup_integrator(txn)

        self.ext_main_executor.loop(fs=samplingFreq, wait_time=self.calc_wait_time_ms(),
                         txn=txn, rx=self.rx, sn=self.sn, num_iterations=self.num_iterations)

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <start sn> <config.json>")
        assert False

    sn=int(sys.argv[1])
    config_path = sys.argv[2]

    test = Test_Streaming(config_path)

    try:
        test.run_test(sn=sn)

    except KeyboardInterrupt:
        test.shutdown_hmc()
        sys.exit(-1)