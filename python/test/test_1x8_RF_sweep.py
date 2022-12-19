
import sys
from test import TestSuite
import numpy as np
import os
from time import sleep

sys.path.append('../misc')

from swave import Wave
from widebuf import WideBuf

class Test_1x8_Sweep(TestSuite):
    def __init__(self):
        super().__init__()

    def make_sweep_tone_bram(self, samplingFreq, freq, dBFS, freqStep, dtype):
        sampleSize = np.dtype(dtype).itemsize
        fullCycles = True
        phaseDegrees = 0x0
        buffersCount = self.hw.BUFFERS_IN_BRAM
        numBytes = int(self.getBramSize() / buffersCount)
        numSamples = int(numBytes / sampleSize)
        samplesPerFLit = self.hw.SAMPLES_PER_FLIT

        buffer = np.empty(buffersCount * numSamples, dtype=dtype)

        for i in range(buffersCount):

            #Keep same frequency for I & Q channels
            if i%2 == 0:
                tone = Wave().getSine(numBytes, freq, dBFS, samplingFreq, sampleSize, phaseDegrees, fullCycles)
                freq = freq + freqStep

            WideBuf().make(buffer, tone, i, buffersCount, samplesPerFLit)

        return buffer, freq

    def mkdir(self, outputDir, suffix):
        if not os.path.exists(outputDir):
            os.mkdir(outputDir)

        if self.capture_data:
            outputDir = '{}/TX_{}'.format(outputDir, suffix)
            if not os.path.exists(outputDir):
                os.mkdir(outputDir)
        else:
            outputDir = None
        return outputDir

    def cap_name(self, id):
        return 'cap{}_{}.bin'.format('I' if id%2==0 else 'Q', int(id/2))

    @TestSuite.Test
    def run_test(self):
        samplingFreq = self.rfdc.getSamplingFrequency()

        print('\n\n\n=== Running test ===')
        print('RFDC Sampling Rate = {}'.format(samplingFreq))
        print('Using Max Gain = {}'.format(self.max_gain))

        dtype = np.uint16

        print('=== Generating tones ===')
        if load_bram:
            bram0_data, _ = self.make_sweep_tone_bram(samplingFreq, self.freq, self.dBFS, self.freqStep, dtype)
            bram1_data, _ = self.make_sweep_tone_bram(samplingFreq, self.freq, self.dBFS, self.freqStep, dtype)

            self.load_dac_player(bram0_data, bram1_data)

        self.setup_RF_Clk(self.ticsFilePath, self.restart_rfdc)
        #Turn on all the dac player outputs
        self.dac_gate(0xffff)

        offset = 0x0

        for txi in self.tx:

            print('*** Running Iteration : rx={}, tx={}'.format(self.rx, txi))
            self.setup_RF([txi], self.rx)

            if self.max_gain:
                for rxi in rx:
                    self.hmc.SetAtt_6301(ic=rxi, i=0x0, q=0x0, att=0x0)
                    self.hmc.IfGain_6301(ic=rxi, val=0xf)
                    self.hmc.LNAGain_6301(ic=rxi, val=0x3)

                self.hmc.IfGain_6300(ic=txi, val=0xd)
                self.hmc.RVGAGain_6300(ic=txi, val=0xf)
            else:
                self.hmc.IfGain_6300(ic=txi, val=0x3)
                self.hmc.RVGAGain_6300(ic=txi, val=0x3)

            outputDir = self.mkdir(self.outputDir, str(txi))

            ids = [i for i in range(8)]
            paths = list(map(self.cap_name, ids))

            #input("Press Enter to continue...")

            #Let the RF to settle the configuration
            sleep(1)
            self.capture(self.ddr0, outputDir, paths, ids, offset, self.captureSize)

            ids = [i for i in range(8, 16, 1)]
            paths = list(map(self.cap_name, ids))

            self.capture(self.ddr1, outputDir, paths, ids, offset, self.captureSize)

            self.shutdown_RF()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('{}: Usage'.format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]

    freq = 75_000_000
    freqStep = 0
    dBFS = int(-9)
    captureSize = 128 * 4096 * 2
    restart_rfdc = False
    load_bram = True
    capture_data = True
    #Which radios to use:
    tx = [i for i in range(8)]
    rx = [i for i in range(8)]
    outputDir = '/home/captures'
    max_gain = False

    test = Test_1x8_Sweep()
    
    test.run_test(ticsFilePath  =ticsFilePath,
                freq            =freq,
                dBFS            =dBFS,
                freqStep        =freqStep,
                captureSize     =captureSize,
                restart_rfdc    =restart_rfdc,
                load_bram       =load_bram,
                capture_data    =capture_data,
                tx              =tx,
                rx              =rx,
                outputDir       =outputDir,
                max_gain        =max_gain)