
import sys
from test import TestSuite
import numpy as np
import os

sys.path.append('../misc')

from swave import Wave
from widebuf import WideBuf

class Test_1x1_ST(TestSuite):
    def __init__(self):
        super().__init__()

    def make_single_tone_bram(self, samplingFreq, freq, dBFS, freqStep, dtype):
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

    def run_test(self, ticsFilePath, freq, dBFS, freqStep, captureSize, restart_rfdc, load_bram):

        samplingFreq = self.rfdc.getSamplingFrequency()

        print('\n\n\n=== Running test ===')
        print('RFDC Sampling Rate = {}'.format(samplingFreq))

        if load_bram:
            bram0_data, freq = self.make_single_tone_bram(samplingFreq, freq, dBFS, freqStep, np.uint16)
            bram1_data, freq = self.make_single_tone_bram(samplingFreq, freq, dBFS, freqStep, np.uint16)

            self.load_dac_player(bram0_data, bram1_data)

        self.setup_RF_Clk(ticsFilePath, restart_rfdc)
        tx = [i for i in range(0, 4, 1)]
        rx = [i for i in range(8)]

        capturesDir = '/tmp/captures'
        if not os.path.exists(capturesDir):
            os.mkdir(capturesDir)

        for i in tx:

            print('Setting UP RF ...')
            self.setup_RF([i], rx)

            self.hmc.IfGain_6300(i, 12)

            outputDir = '{}/TX_{}'.format(capturesDir, i)
            if not os.path.exists(outputDir):
                os.mkdir(outputDir)

            offset = 0x0
            ids = [i for i in range(8)]
            paths = list(map(lambda id: 'cap{}.bin'.format(id), ids))

            print('Capturing DDR0: {}'.format(outputDir))

            self.capture(self.ddr0, outputDir, paths, ids, offset, captureSize)

            ids = [i for i in range(8, 16, 1)]
            paths = list(map(lambda id: 'cap{}.bin'.format(id), ids))

            print('Capturing DDR1: {}'.format(outputDir))

            self.capture(self.ddr1, outputDir, paths, ids, offset, captureSize)

            self.shutdown_RF()

        print('Pass')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('{}: Usage'.format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]

    freq = 75_000_000
    freqStep = 5_000_000
    dBFS = int(-3)
    captureSize = 128 * 4096 * 2
    restart_rfdc = False
    load_bram = True

    test = Test_1x1_ST()
    
    test.run_test(ticsFilePath, freq, dBFS, freqStep, captureSize, restart_rfdc, load_bram)
