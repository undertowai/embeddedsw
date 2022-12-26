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
        # Turn on all the dac player outputs
        self.dac_gate(0xFFFF)
        sn = 0x0
        offset = 0x0

        ids0 = []
        ids1 = []
        for rx in self.rx:
            if rx > 3:
                ids1.extend([rx * 2, rx * 2 + 1])
            else:
                ids0.extend([rx * 2, rx * 2 + 1])

        self.setup_RF(self.tx, self.rx)
        #for tx in self.tx:
        #    self.hmc.Power_6300(ic=tx, pwup=False)

        while True:
            #for tx in self.tx:
            #    self.hmc.Power_6300(ic=tx, pwup=True)

            sleep(0.2)
            print(
                "*** Running Iteration : sn={}, rx={}, tx={}".format(
                    sn, self.rx, tx
                )
            )

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
        print("{}: Usage".format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]

    captureSize = 128 * 1024 * 2
    # Which radios to use:
    #tx = [i for i in range(8)]
    # rx = [i for i in range(8)]
    tx = [0]
    rx = [0]
    restart_rfdc    = False
    capture_data    = True
    max_gain        = False

    test = Test_Streaming(Inet.PORT)

    test.run_test(
        ticsFilePath=ticsFilePath,
        captureSize=captureSize,
        restart_rfdc=restart_rfdc,
        capture_data=capture_data,
        tx=tx,
        rx=rx
    )
