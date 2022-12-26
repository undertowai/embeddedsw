import sys
from test import TestSuite
import numpy as np
import os
from time import sleep

sys.path.append("../misc")

from widebuf import WideBuf


class Test_1x8_Sweep(TestSuite):
    def __init__(self):
        super().__init__()

    @TestSuite.Test
    def run_test(self):
        print("\n\n\n=== Running test ===")

        self.setup_RF_Clk(self.ticsFilePath, self.restart_rfdc)
        # Turn on all the dac player outputs
        self.dac_gate(0xFFFF)

        offset = 0x0

        for txi in self.tx:

            print("*** Running Iteration : rx={}, tx={}".format(self.rx, txi))
            self.setup_RF([txi], self.rx)

            outputDir = self.mkdir(self.outputDir, str(txi))

            ids = [i for i in range(8)]
            paths = list(map(self.cap_name, ids))

            # input("Press Enter to continue...")

            # Let the RF to settle the configuration
            sleep(1)
            self.capture(self.ddr0, outputDir, paths, ids, offset, self.captureSize)

            ids = [i for i in range(8, 16, 1)]
            paths = list(map(self.cap_name, ids))

            self.capture(self.ddr1, outputDir, paths, ids, offset, self.captureSize)

            self.shutdown_RF()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("{}: Usage".format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]

    captureSize = 128 * 4096 * 2
    #ext_bram_path = None
    ext_bram_path = "/home/petalinux/Work/embeddedsw/python/test/"
    # Which radios to use:
    tx = [i for i in range(8)]
    rx = [i for i in range(8)]
    outputDir = "/home/captures"

    restart_rfdc = False
    capture_data = True

    test = Test_1x8_Sweep()

    test.run_test(
        ticsFilePath=ticsFilePath,
        captureSize=captureSize,
        restart_rfdc=restart_rfdc,
        capture_data=capture_data,
        tx=tx,
        rx=rx,
        outputDir=outputDir,
        ext_bram_path=ext_bram_path,
    )
