import sys
from test import TestSuite
from time import sleep
import numpy as np
from scipy.io import savemat


from iq_correction import computeIQcorrection
from iq_correction import computeIQcorrection2

sys.path.append("../misc")
sys.path.append("../dac")
sys.path.append("../xddr")

from xddr import Xddr
from player import DacPlayer

class Test_Streaming(TestSuite):
    def __init__(self):
        TestSuite.__init__(self)

        self.coeff = {}

    def IQ_correction_wrapper(self, I, Q, sc, sn, txn, rxn):
        _, _, coeff = computeIQcorrection2(I, Q)
        self.coeff['sc_{}_{}_tx_{}_rx_{}'.format(sc, sn, int(txn), int(rxn))] = coeff

    def proc_cap_data(self, area, sc, sn, txn, dtype=np.int16):
        rxn = 0
        for a in area:
            for j in range(0, len(a), 2):
                addrI, sizeI = a[j]
                addrQ, sizeQ = a[j + 1]
                I = Xddr.read(addrI, sizeI, dtype)
                Q = Xddr.read(addrQ, sizeQ, dtype)
                self.IQ_correction_wrapper(I, Q, sc, sn, txn, rxn/2)
                rxn +=1


    def setup_rf_clocks(self, ticsFilePath, restart_rfdc):
        self.setup_RF_Clk(ticsFilePath, restart_rfdc)

    @TestSuite.Test
    def run_test(self):
        offset = 0x0

        ids0, ids1 = self.map_rx_to_dma_id(self.rx)

        for txn in self.tx:
            count = 0

            self.setup_hmc([txn], self.rx)
            
            print("Setting 6300 gains")
            self.hmc.IfGain_6300(ic=txn, gain=6)
            self.hmc.RVGAGain_6300(ic=txn, gain=7)

            for rxn in self.rx:
                print("Settings 6301 gains")
                self.hmc.SetAtt_6301(ic=rxn, i=3, q=1, att=0)

            while count < self.count:

                self.adc_dac_sync(False)

                area = []
                for ids, ddr in [(ids0, self.ddr0), (ids1, self.ddr1)]:
                    a = self.start_dma(ddr, ids, offset, self.captureSize)
                    area.append(a)

                self.adc_dac_sync(True)

                sleep(self.calc_capture_time(self.captureSize))

                self.proc_cap_data(area, self.sc, count, txn)
                count += 1

            self.shutdown_hmc()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: {} <lmx2820_regs_file_path.txt> <num SC>".format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]
    num_SC = int(sys.argv[2])

    # Which radios to use:
    #tx = [i for i in range(8)]
    # rx = [i for i in range(8)]
    tx = [7]
    rx = [0, 1, 2, 3]
    num_trials = 5

    test = Test_Streaming()
    captureSize = 64 * 1024 * 2 * test.hw.BYTES_PER_SAMPLE

    adc_dac_loopback = False

    #test.set_loobback(True)
    test.set_loobback(False)

    player = DacPlayer()

    test.setup_rfdc()

    if adc_dac_loopback == False:
        test.setup_lmx(ticsFilePath)

    for sc in range(num_SC):

        ifile = '../dac/IQexpt/Ichannel_{}.npy'.format(sc)
        qfile = '../dac/IQexpt/Qchannel_{}.npy'.format(sc)

        bram_data = player.make_bram_content_from_file(ifile, qfile)
        player.load_dac_player(bram_data, bram_data)

        test.run_test(
            captureSize=captureSize,
            count = num_trials,
            sc=sc,
            tx=tx,
            rx=rx
        )

    test.shutdown_hmc()
    print(test.coeff)
    save_filename = 'IQcoeff_{}_{}.npy'.format(tx, rx)
    savemat('IQcoeff.mat', test.coeff)
