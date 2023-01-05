import sys
from test import TestSuite
from time import sleep

from scipy.io import savemat


from iq_correction import computeIQcorrection
from iq_correction import computeIQcorrection2

sys.path.append("../misc")
sys.path.append("../dac")

from player import DacPlayer

class Test_Streaming(TestSuite):
    def __init__(self):
        TestSuite.__init__(self)

        self.coeff = {}

    def IQ_correction_wrapper(self, I, Q, sn, freq, fs):
        _, _, coeff = computeIQcorrection2(I, Q)
        self.coeff['sc_{}_{}'.format(self.sc, sn)] = coeff

    def setup_rf_clocks(self, ticsFilePath, restart_rfdc):
        self.setup_RF_Clk(ticsFilePath, restart_rfdc)

    @TestSuite.Test
    def run_test(self):
        samplingFreq = self.rfdc.getSamplingFrequency()

        offset = 0x0

        ids0, ids1 = self.map_rx_to_dma_id(self.rx)

        count = 0
        while count < self.count:

            self.adc_dac_sync(False)

            area = []
            for ids, ddr in [(ids0, self.ddr0), (ids1, self.ddr1)]:
                a = self.start_dma(ddr, ids, offset, self.captureSize)
                area.append(a)

            self.adc_dac_sync(True)

            sleep(self.calc_capture_time(self.captureSize))

            self.proc_cap_data(self.IQ_correction_wrapper, area, count, 0, samplingFreq)
            count += 1

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: {} <lmx2820_regs_file_path.txt> <num SC>".format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]
    num_SC = int(sys.argv[2])

    # Which radios to use:
    #tx = [i for i in range(8)]
    # rx = [i for i in range(8)]
    tx = [0]
    rx = [0]

    test = Test_Streaming()
    captureSize = 64 * 1024 * 2 * test.hw.BYTES_PER_SAMPLE

    adc_dac_loopback = True

    #test.set_loobback(True)
    test.set_loobback(False)

    player = DacPlayer()

    test.setup_rfdc()

    if adc_dac_loopback == False:
        test.setup_lmx(ticsFilePath)
        test.setup_hmc(tx, rx)

    for sc in range(num_SC):

        ifile = '../dac/IQexpt/Ichannel_{}.npy'.format(sc)
        qfile = '../dac/IQexpt/Qchannel_{}.npy'.format(sc)

        bram_data = player.make_bram_content_from_file(ifile, qfile)
        player.load_dac_player(bram_data, bram_data)

        test.run_test(
            captureSize=captureSize,
            count = 3,
            sc=sc
        )

    test.shutdown_hmc()
    print(test.coeff)
    savemat('IQcoeff.mat', test.coeff)
