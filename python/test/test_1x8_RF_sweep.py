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

        self.setup_rfdc()

        if self.adc_dac_loopback == False:
            self.setup_lmx(self.ticsFilePath)

        dma_ids0, dma_ids1 = self.map_rx_to_dma_id(self.rx)

        cap_names0 = list(map(self.map_id_to_cap_name, dma_ids0))
        cap_names1 = list(map(self.map_id_to_cap_name, dma_ids1))

        cap_ddr_offset = 0x0

        for txi in self.tx:

            print("*** Running Iteration : rx={}, tx={}".format(self.rx, txi))
            if self.adc_dac_loopback == False:
                self.setup_hmc([txi], self.rx)

            outputDir = self.mkdir(self.outputDir, str(txi))

            self.adc_dac_sync(False)

            for ids, ddr in [(dma_ids0, self.ddr0), (dma_ids1, self.ddr1)]:
                self.start_dma(ddr, ids, cap_ddr_offset, self.captureSize)

            self.adc_dac_sync(True)

            sleep(self.calc_capture_time(self.captureSize))

            for paths, ddr in [(cap_names0, self.ddr0), (cap_names1, self.ddr1)]:
                self.collect_captures_from_ddr(ddr, outputDir, paths, cap_ddr_offset, self.captureSize)

            if self.adc_dac_loopback == False:
                self.shutdown_hmc()


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

    test = Test_1x8_Sweep()
    captureSize = 64 * 1024 * 2 * test.hw.BYTES_PER_SAMPLE
    adc_dac_loopback = False

    test.set_loobback(False)

    test.run_test(
        ticsFilePath=ticsFilePath,
        captureSize=captureSize,
        tx=tx,
        rx=rx,
        outputDir=outputDir,
        adc_dac_loopback=adc_dac_loopback
    )
