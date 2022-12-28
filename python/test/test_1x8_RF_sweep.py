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
        # Turn on all the dac player outputs
        self.dac_gate(0xFFFF)

        ids0 = []
        ids1 = []
        for rx in self.rx:
            if rx > 3:
                ids1.extend([rx * 2, rx * 2 + 1])
            else:
                ids0.extend([rx * 2, rx * 2 + 1])
                #ids0.extend([rx * 2])

        paths0 = list(map(self.cap_name, ids0))
        paths1 = list(map(self.cap_name, ids1))

        offset = 0x0

        for txi in self.tx:

            print("*** Running Iteration : rx={}, tx={}".format(self.rx, txi))
            self.setup_RF([txi], self.rx)

            outputDir = self.mkdir(self.outputDir, str(txi))

            # input("Press Enter to continue...")

            for ids, paths, ddr in [(ids0, paths0, self.ddr0), (ids1, paths1, self.ddr1)]:
                self.capture(ddr, outputDir, paths, ids, offset, self.captureSize)

            self.shutdown_RF()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("{}: Usage".format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]

    captureSize = 128 * 4096 * 2
    # Which radios to use:
    #tx = [i for i in range(8)]
    #rx = [i for i in range(8)]
    tx = [0]
    rx = [0]
    outputDir = "/home/captures"

    restart_rfdc = False
    capture_data = True

    test = Test_1x8_Sweep()
    
    test.set_loobback(True)

    test.run_test(
        ticsFilePath=ticsFilePath,
        captureSize=captureSize,
        restart_rfdc=restart_rfdc,
        capture_data=capture_data,
        tx=tx,
        rx=rx,
        outputDir=outputDir,
    )
