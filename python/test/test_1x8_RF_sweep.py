import sys
from test import TestSuite
import numpy as np
import os
from time import sleep

sys.path.append("../misc")

class Test_1x8_Sweep(TestSuite):
    def __init__(self):
        super().__init__()

    @TestSuite.Test
    def run_test(self):
        print("\n\n\n=== Running test ===")

        self.setup_RF_Clk(self.ticsFilePath, self.restart_rfdc)

        ids0, ids1 = self.map_rx_to_dma_id(self.rx)

        paths0 = list(map(self.map_id_to_cap_name, ids0))
        paths1 = list(map(self.map_id_to_cap_name, ids1))

        offset = 0x0

        for txi in self.tx:

            print("*** Running Iteration : rx={}, tx={}".format(self.rx, txi))
            self.setup_RF([txi], self.rx)

            outputDir = self.mkdir(self.outputDir, str(txi))

            self.adc_dac_sync(False)

            for ids, ddr in [(ids0, self.ddr0), (ids1, self.ddr1)]:
                self.start_dma(ddr, ids, offset, self.captureSize)

            self.adc_dac_sync(True)

            sleep(self.calc_capture_time(self.captureSize))

            for paths, ddr in [(paths0, self.ddr0), (paths1, self.ddr1)]:
                self.collect_captures_from_ddr(ddr, outputDir, paths, offset, self.captureSize)

            self.shutdown_RF()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: {} <lmx2820_reg_file_path.txt> <output dir>".format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]
    outputDir = sys.argv[2]

    # Which radios to use:
    #tx = [i for i in range(8)]
    #rx = [i for i in range(8)]
    tx = [0]
    rx = [0]

    restart_rfdc = False

    test = Test_1x8_Sweep()
    captureSize = 64 * 1024 * 2 * test.hw.BYTES_PER_SAMPLE

    test.set_loobback(True)

    test.run_test(
        ticsFilePath=ticsFilePath,
        captureSize=captureSize,
        restart_rfdc=restart_rfdc,
        tx=tx,
        rx=rx,
        outputDir=outputDir,
    )
