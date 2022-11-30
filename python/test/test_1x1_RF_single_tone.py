
import sys
from test import TestSuite
import numpy as np

sys.path.append('../misc')

from swave import Wave
from widebuf import WideBuf

class Test_1x1_ST(TestSuite):
    def __init__(self):
        super().__init__()

    def generate_bram_content(self, samplingFreq, numBytes, freq, dBFS, dtype):
        sampleSize = np.dtype(dtype).itemsize
        fullCycles = True
        phaseDegrees = 0x0
        buffersCount = 0x8
        numSamples = int(numBytes / sampleSize)
        samplesPerFLit = 0x8

        tone = Wave().getSine(numBytes, freq, dBFS, samplingFreq, sampleSize, phaseDegrees, fullCycles)

        buffer = np.empty(buffersCount * numSamples, dtype=dtype)

        for i in range(buffersCount):
            WideBuf().make(buffer, tone, i, buffersCount, samplesPerFLit)

        return buffer

    def run_test(self, ticsFilePath, freq, dBFS, captureSize):

        self.setup_RF(ticsFilePath, False)

        self.hmc.IfGain_6300(0, 3)

        samplingFreq = self.rfdc.getSamplingFrequency()
        numBytes = int(self.getBramSize() / 0x8)

        print('\n\n\n=== Running test ===')
        print('Sample Rate = {}\nBuffer size = {}'.format(samplingFreq, numBytes))

        bram_data = self.generate_bram_content(samplingFreq, numBytes, freq, dBFS, np.uint16)

        self.load_dac_player(bram_data, bram_data)

        offset = 0x0
        self.capture(self.ddr0, ['cap0.bin', 'cap1.bin'], [0, 1], offset, captureSize)

        self.shutdown_RF()

        print('Pass')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('{}: Usage'.format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]

    freq = 75_000_000
    dBFS = int(-20)
    captureSize = 2000 * 4096 * 2

    test = Test_1x1_ST()

    test.run_test(ticsFilePath, freq, dBFS, captureSize)
