import sys
from test import TestSuite

class Test_Streaming(TestSuite):
    def __init__(self, config_path):
        TestSuite.__init__(self, config_path)

    def run_test(self, sn):
        samplingFreq = self.rfdc.getSamplingFrequency()

        self.ext_main_executor.loop(fs=samplingFreq, wait_time=self.calc_wait_time_ms(),
                         tx=self.tx, rx=self.rx, sn=sn, num_iterations=self.num_iterations)

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <start sn> <config.json>")
        assert False

    sn=int(sys.argv[1])
    config_path = sys.argv[2]

    test = Test_Streaming(config_path)
    test.run_test(sn=sn)

