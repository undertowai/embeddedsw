import sys
from test import TestSuite
from time import sleep
import zmq
import pickle
import time
import numpy as np

from inet import Inet

sys.path.append("../misc")
sys.path.append("../xddr")
from xddr import Xddr

class Test_Streaming(TestSuite):
    def __init__(self, port):
        TestSuite.__init__(self)

        context = zmq.Context()
        self.publisher = context.socket(zmq.PUB)
        self.publisher.bind("tcp://0.0.0.0:%s" % port)

    def proc_cap_data(self, area, sn, txn, freq, fs, dtype=np.int16):
        iq_data = []
        for a in area:
            for j in range(0, len(a), 2):
                addrI, sizeI = a[j]
                addrQ, sizeQ = a[j + 1]
                I = Xddr.read(addrI, sizeI, dtype)
                Q = Xddr.read(addrQ, sizeQ, dtype)
                iq_data.append((I, Q))
        
        mpart_data = [
            bytes(str(Inet.TOPIC_FILTER), "utf-8"),
            bytes(str(sn), "utf-8"),
            bytes(str(txn), "utf-8"),
            bytes(str(fs), "utf-8"),
            bytes(str(freq), "utf-8"),
            bytes(str(time.time_ns() / 1_000_000_000), "utf-8"),
            pickle.dumps(iq_data)
        ]
        self.publisher.send_multipart(mpart_data)
        print(txn)

    @TestSuite.Test
    def run_test(self):
        samplingFreq = self.rfdc.getSamplingFrequency()

        self.setup_rfdc()

        if self.adc_dac_loopback == False:
            self.setup_lmx(self.ticsFilePath)
            self.setup_hmc([], self.rx)

        sn = 0
        cap_ddr_offset = 0x0

        dma_ids0, dma_ids1 = self.map_rx_to_dma_id(self.rx)

        while sn < self.num_iterations:


            #self.hmc.Power_6300(ic=txn, pwup=True)
            print("*** Running Iteration : sn={}, rx={}".format(sn, self.rx))

            for rxn in self.rx:
                print("Settings 6301 gains")
                self.hmc.SetAtt_6301(ic=rxn, i=3, q=1, att=0)

            self.adc_dac_sync(False)

            area = []
            for ids, ddr in [(dma_ids0, self.ddr0), (dma_ids1, self.ddr1)]:
                a = self.start_dma(ddr, ids, cap_ddr_offset, self.captureSize)
                area.append(a)

            self.adc_dac_sync(True)

            sleep(self.calc_capture_time(self.captureSize))

            self.proc_cap_data(area, sn, 0, 0, samplingFreq)

            sn += 1
        self.shutdown_hmc()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: {} <lmx2820_regs_file_path.txt>".format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]

    # Which radios to use:
    rx = [0, 1, 2, 3]
    adc_dac_loopback = False

    test = Test_Streaming(Inet.PORT)
    captureSize = 64 * 1024 * 2 * test.hw.BYTES_PER_SAMPLE

    test.set_loobback(False)
    #test.set_loobback(True)

    test.run_test(
        ticsFilePath=ticsFilePath,
        captureSize=captureSize,
        rx=rx,
        adc_dac_loopback=adc_dac_loopback,
        num_iterations=2000
    )
