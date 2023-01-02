import sys
from test import TestSuite
from time import sleep
import zmq

from inet import Inet

sys.path.append("../misc")

class Test_Streaming(TestSuite):
    def __init__(self, port):
        TestSuite.__init__(self)

        context = zmq.Context()
        self.publisher = context.socket(zmq.PUB)
        self.publisher.bind("tcp://0.0.0.0:%s" % port)

    @TestSuite.Test
    def run_test(self):
        samplingFreq = self.rfdc.getSamplingFrequency()

        print("\n\n\n=== Running test ===")

        self.setup_RF_Clk(self.ticsFilePath, self.restart_rfdc)

        sn = 0x0
        offset = 0x0

        ids0, ids1 = self.map_rx_to_dma_id(self.rx)

        self.setup_RF(self.tx, self.rx)
        #for tx in self.tx:
        #    self.hmc.Power_6300(ic=tx, pwup=False)

        while True:
            #for tx in self.tx:
            #    self.hmc.Power_6300(ic=tx, pwup=True)

            print("*** Running Iteration : sn={}, rx={}, tx={}".format(sn, self.rx, tx))

            self.adc_dac_sync(False)

            area = []
            for ids, ddr in [(ids0, self.ddr0), (ids1, self.ddr1)]:
                a = self.start_dma(ddr, ids, offset, self.captureSize)
                area.append(a)

            self.adc_dac_sync(True)

            t = self.calc_capture_time(self.captureSize)
            print("Waiting %fs for capture to complete " % t)
            sleep(t)

            self.publish(area, sn, 0, samplingFreq)
            sn += 1
            #for tx in self.tx:
            #    self.hmc.Power_6300(ic=tx, pwup=False)

        self.shutdown_RF()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: {} <lmx2820_regs_file_path.txt>".format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]

    # Which radios to use:
    #tx = [i for i in range(8)]
    # rx = [i for i in range(8)]
    tx = [0]
    rx = [0]
    restart_rfdc    = False

    test = Test_Streaming(Inet.PORT)
    captureSize = 64 * 1024 * 2 * test.hw.BYTES_PER_SAMPLE

    test.set_loobback(True)

    test.run_test(
        ticsFilePath=ticsFilePath,
        captureSize=captureSize,
        restart_rfdc=restart_rfdc,
        tx=tx,
        rx=rx
    )
