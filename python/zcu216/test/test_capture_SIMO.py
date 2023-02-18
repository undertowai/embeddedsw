import sys
from test import TestSuite
from time import sleep
import time
import numpy as np
import os

from inet import Inet

sys.path.append("../misc")
sys.path.append("../xddr")
from xddr import Xddr

class Test_Streaming(TestSuite):
    def __init__(self, port):
        TestSuite.__init__(self)

    def proc_cap_data(self, area, sn, txn, freq, fs, dtype=np.int16):
        for rxn in area.keys():
            a = area[rxn]
            addrI, sizeI = a["I"]
            addrQ, sizeQ = a["Q"]

            I = self.xddr_read(addrI, sizeI, dtype)
            Q = self.xddr_read(addrQ, sizeQ, dtype)

            dir_path = self.output_dir + os.sep + f'TX_{txn}' + os.sep + f'RX_{rxn}'
            
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                
            ipath = dir_path + os.sep + f'I_{sn}'
            qpath = dir_path + os.sep + f'Q_{sn}'

            np.save(ipath, I)
            np.save(qpath, Q)


    @TestSuite.Test
    def run_test(self):
        samplingFreq = self.rfdc.getSamplingFrequency()

        assert len(self.tx) == 1
        txn = self.tx[0]

        sn = self.sn
        iter_count = 0

        rx_dma_map = self.map_rx_to_dma_id(self.rx)

        while iter_count < self.num_iterations:

            print("*** Running Iteration : sn={}, rx={}, tx={}".format(sn, self.rx, [txn]))

            self.adc_dac_sync(False)

            area = self.start_dma(rx_dma_map, self.cap_ddr_offset, self.capture_size)

            self.adc_dac_sync(True)

            sleep(self.calc_capture_time(self.capture_size))

            self.proc_cap_data(area, sn, txn, 0, samplingFreq)

            sn += 1
            iter_count += 1


if __name__ == "__main__":

    if len(sys.argv) != 5:
        print(f"Usage: {sys.argv[0]} <output dir> <num_iterations> <current sn> <config.json>")

    output_dir = sys.argv[1]
    num_iterations = int(sys.argv[2])
    sn=int(sys.argv[3])
    config_path = sys.argv[4]

    test = Test_Streaming(Inet.PORT)

    try:
        test.load_config(config_path)

        test.run_test(
            num_iterations=num_iterations,
            sn=sn,
            output_dir=output_dir
        )
    except KeyboardInterrupt:
        test.shutdown_hmc()
        sys.exit(-1)