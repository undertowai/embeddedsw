import sys
from test import TestSuite
import numpy as np
from time import sleep, time

sys.path.append("../misc")


class Test_1x8_Sweep(TestSuite):
    def __init__(self):
        super().__init__()

    def iteration(self, outputDir, txi, offset):
        outputDir = self.mkdir(outputDir, str(txi))

        ids = [i for i in range(8)]
        paths = list(map(self.cap_name, ids))

        self.capture(self.ddr0, outputDir, paths, ids, offset, self.captureSize)

        ids = [i for i in range(8, 16, 1)]
        paths = list(map(self.cap_name, ids))

        self.capture(self.ddr1, outputDir, paths, ids, offset, self.captureSize)

    @TestSuite.Test
    def run_test(self, **kw):

        self.get_args(**kw)

        samplingFreq = self.rfdc.getSamplingFrequency()

        print("\n\n\n=== Running test ===")
        print("RFDC Sampling Rate = {}".format(samplingFreq))

        dtype = np.uint16

        print("=== Generating tones ===")
        if load_bram:
            bram0_data, _ = self.make_sweep_tone_bram(
                samplingFreq, self.freq, self.dBFS, self.freqStep, dtype
            )
            bram1_data, _ = self.make_sweep_tone_bram(
                samplingFreq, self.freq, self.dBFS, self.freqStep, dtype
            )

            self.load_dac_player(bram0_data, bram1_data)

        self.setup_RF_Clk(self.ticsFilePath, self.restart_rfdc)
        # Turn on all the dac player outputs
        self.dac_gate(0xFFFF)

        self.setup_RF([], self.rx)

        offset = 0x0

        ifvga_p = self.parameters["ifvga_vga_adj"]
        RFVGA_p = self.parameters["RFVGAgain"]
        bbamp_iq_p = self.parameters["bbamp_atten_iq"]
        bbamp_atten2_p = self.parameters["bbamp_atten2"]
        if_gain_p = self.parameters["if_gain"]
        lna_gain_p = self.parameters["lna_gain"]

        for ifvga in ifvga_p:
            for rfvga in RFVGA_p:
                for bbamp_iq in bbamp_iq_p:
                    for bbamp_atten2 in bbamp_atten2_p:
                        for if_gain in if_gain_p:
                            for lna_gain in lna_gain_p:

                                print("Running Iteration:")
                                print(
                                    "ifvga={} rfvga={} bbamp_iq={} bbamp_att2={} if_gain={} lna_gain={}".format(
                                        ifvga,
                                        rfvga,
                                        bbamp_iq,
                                        bbamp_atten2,
                                        if_gain,
                                        lna_gain,
                                    )
                                )

                                outputDir = (
                                    self.outputDir
                                    + "/"
                                    + "ifvga-{}/rfvga-{}/bbamp_iq-{}/bbamp_att2-{}/if_gain-{}/lna_gain-{}".format(
                                        ifvga,
                                        rfvga,
                                        bbamp_iq,
                                        bbamp_atten2,
                                        if_gain,
                                        lna_gain,
                                    )
                                )

                                for txi in self.tx:

                                    start_t = time()
                                    self.setup_RF([txi], self.rx)

                                    for rxi in rx:
                                        self.hmc.SetAtt_6301(
                                            ic=rxi,
                                            i=bbamp_iq,
                                            q=bbamp_iq,
                                            att=bbamp_atten2,
                                        )
                                        self.hmc.IfGain_6301(ic=rxi, val=if_gain)
                                        self.hmc.LNAGain_6301(ic=rxi, gain=lna_gain)

                                    self.hmc.IfGain_6300(ic=txi, val=ifvga)
                                    self.hmc.RVGAGain_6300(ic=txi, val=rfvga)

                                    end_t = time()

                                    print(
                                        "TX{}: Configuring radios done in {:.2f}s".format(
                                            txi, end_t - start_t
                                        )
                                    )
                                    start_t = end_t

                                    # Let the RF to settle the configuration
                                    sleep(1)
                                    self.iteration(outputDir, txi, offset)

                                    end_t = time()
                                    print(
                                        "TX{}: Capturing data done in {:.2f}s".format(
                                            txi, end_t - start_t
                                        )
                                    )

                                    self.shutdown_RF()

        self.shutdown_RF()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("{}: Usage".format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]

    freq = 75_000_000
    freqStep = 0
    dBFS = int(-3)
    captureSize = 128 * 4096 * 2
    restart_rfdc = False
    load_bram = False
    capture_data = True
    # Which radios to use:
    tx = [i for i in range(1)]
    rx = [i for i in range(8)]
    outputDir = "/home/captures"

    test = Test_1x8_Sweep()

    parameters = {
        "ifvga_vga_adj": [0x6, 0xA, 0xD],
        "RFVGAgain": [0x9, 0xB, 0xF],
        "bbamp_atten_iq": [0x0, 0x3, 0x5],
        "bbamp_atten2": [0x0],
        "if_gain": [0x6, 0xC, 0xF],
        "lna_gain": [0x0, 0x2, 0x3],
    }

    # parameters = {
    #    'ifvga_vga_adj' : [0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xa, 0xb, 0xc, 0xd],
    #    'RFVGAgain' : [0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf],
    #    'bbamp_atten_iq' : [0x0, 0x1, 0x2, 0x3, 0x4, 0x5],
    #    'bbamp_atten2' : [0x0],
    #    'if_gain': [0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf],
    #    'lna_gain' : [0x0, 0x1, 0x2, 0x3]
    # }

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
        outputDir=outputDir,
        parameters=parameters,
    )
