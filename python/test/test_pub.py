import sys
from test import TestSuite
import numpy as np
from time import sleep, time
import zmq
import json
import os

from inet import Inet

sys.path.append("../misc")

from widebuf import WideBuf


class Test_1x8_Sweep(TestSuite):
    def __init__(self, port):
        TestSuite.__init__(self)

        context = zmq.Context()
        self.publisher = context.socket(zmq.PUB)
        self.publisher.bind("tcp://0.0.0.0:%s" % port)

    @TestSuite.Test
    def run_test(self):
        samplingFreq = self.rfdc.getSamplingFrequency()

        print("\n\n\n=== Running test ===")
        print("RFDC Sampling Rate = {}".format(samplingFreq))
        print("Using Max Gain = {}".format(self.max_gain))

        if load_bram:
            if self.ext_bram_path is not None:
                Ipath = self.ext_bram_path + os.sep + "Ichannel.npy"
                Qpath = self.ext_bram_path + os.sep + "Qchannel.npy"
                bram0_data = self.make_bram_content_from_file(Ipath, Qpath)
                bram1_data = np.copy(bram0_data)
            else:
                print("=== Generating tones ===")
                bram0_data, _ = self.make_sweep_tone_bram(
                    samplingFreq, self.freq, self.dBFS, self.freqStep
                )
                if self.freqStep != 0:
                    bram1_data, _ = self.make_sweep_tone_bram(
                        samplingFreq, self.freq, self.dBFS, self.freqStep
                    )
                else:
                    bram1_data = np.copy(bram0_data)

            self.load_dac_player(bram0_data, bram1_data)

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
        for tx in self.tx:
            self.hmc.Power_6300(ic=tx, pwup=False)

        while True:
            for txi in self.tx:

                self.hmc.Power_6300(ic=txi, pwup=True)
                sleep(0.2)
                print(
                    "*** Running Iteration : sn={}, rx={}, tx={}".format(
                        sn, self.rx, txi
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

                self.publish(area, sn, self.freq, samplingFreq)
                sn += 1
                self.hmc.Power_6300(ic=txi, pwup=False)

        self.shutdown_RF()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("{}: Usage".format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]

    freq = 75_000_000
    freqStep = 0
    dBFS = int(-9)
    captureSize = 128 * 1024 * 2
    # Which radios to use:
    # tx = [i for i in range(8)]
    # rx = [i for i in range(8)]
    tx = [0]
    rx = [0]
    restart_rfdc    = False
    load_bram       = True
    ext_bram_path   = None
    capture_data    = True
    max_gain        = False

    test = Test_1x8_Sweep(Inet.PORT)

    test.run_test(
        ticsFilePath=ticsFilePath,
        freq=freq,
        dBFS=dBFS,
        freqStep=freqStep,
        captureSize=captureSize,
        restart_rfdc=restart_rfdc,
        load_bram=load_bram,
        capture_data=capture_data,
        tx=tx,
        rx=rx,
        max_gain=max_gain,
        ext_bram_path=ext_bram_path,
    )
