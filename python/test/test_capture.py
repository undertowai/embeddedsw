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

            I = Xddr.read(addrI, sizeI, dtype)
            Q = Xddr.read(addrQ, sizeQ, dtype)

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

        sn = self.sn
        iter_count = 0
        cap_ddr_offset = 0x0

        rx_dma_map = self.map_rx_to_dma_id(self.rx)

        while iter_count < self.num_iterations:

            for txn in self.tx:
                if self.adc_dac_loopback == False:
                    self.setup_hmc([txn], self.rx)
                
                    self.hmc.IfGain_6300(ic=txn, gain=6)
                    self.hmc.RVGAGain_6300(ic=txn, gain=7)
                
                    for rxn in self.rx:
                        self.hmc.SetAtt_6301(ic=rxn, i=3, q=1, att=0)

                print("*** Running Iteration : sn={}, rx={}, tx={}".format(sn, self.rx, [txn]))

                self.adc_dac_sync(False)

                area = self.start_dma(rx_dma_map, cap_ddr_offset, self.captureSize)

                self.adc_dac_sync(True)

                sleep(self.calc_capture_time(self.captureSize))

                self.proc_cap_data(area, sn, txn, 0, samplingFreq)

                if self.adc_dac_loopback == False:
                    self.shutdown_hmc()

            sn += 1
            iter_count += 1


if __name__ == "__main__":

    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <output dir> <num_iterations> <current sn>")

    # Which radios to use:
    #tx = [i for i in range(8)]
    # rx = [i for i in range(8)]
    tx = [7]
    rx = [0, 1, 2, 3]

    output_dir = sys.argv[1]
    num_iterations = int(sys.argv[2])
    sn=int(sys.argv[3])

    adc_dac_loopback = False


    test = Test_Streaming(Inet.PORT)
    dwell_samples = 32 * 1024
    dwell_num = 1023
    captureSize = dwell_num * dwell_samples * test.hw.BYTES_PER_SAMPLE

    test.set_loobback(False)
    #test.set_loobback(True)

    test.run_test(
        captureSize=captureSize,
        tx=tx,
        rx=rx,
        adc_dac_loopback=adc_dac_loopback,
        num_iterations=num_iterations,
        sn=sn,
        output_dir=output_dir
    )
