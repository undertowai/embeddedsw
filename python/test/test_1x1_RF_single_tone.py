
import sys
from test import TestSuite
import numpy as np

sys.path.append('../misc')

from swave import Wave
from widebuf import WideBuf

class Test_1x1_ST(TestSuite):
    def __init__(self):
        super().__init__()

    def make_single_tone_bram(self, samplingFreq, freq, dBFS, dtype):
        sampleSize = np.dtype(dtype).itemsize
        fullCycles = True
        phaseDegrees = 0x0
        buffersCount = self.hw.BUFFERS_IN_BRAM
        numBytes = int(self.getBramSize() / buffersCount)
        numSamples = int(numBytes / sampleSize)
        samplesPerFLit = self.hw.SAMPLES_PER_FLIT

        tone = Wave().getSine(numBytes, freq, dBFS, samplingFreq, sampleSize, phaseDegrees, fullCycles)

        buffer = np.empty(buffersCount * numSamples, dtype=dtype)

        for i in range(buffersCount):
            WideBuf().make(buffer, tone, i, buffersCount, samplesPerFLit)

        return buffer

    def run_test(self, ticsFilePath, freq, dBFS, captureSize, restart_rfdc, load_bram):

        rx = [i for i in range(8)]
        tx = [i for i in range(8)]
        self.setup_RF(ticsFilePath, rx, tx, restart_rfdc)

        self.hmc.IfGain_6300(0, 0)

        samplingFreq = self.rfdc.getSamplingFrequency()

        print('\n\n\n=== Running test ===')
        print('RFDC Sampling Rate = {}'.format(samplingFreq))

        if load_bram:
            bram_data = self.make_single_tone_bram(samplingFreq, freq, dBFS, np.uint16)
            self.load_dac_player(bram_data, bram_data)

        offset = 0x0
        ids = [i for i in range(8)]
        paths = list(map(lambda p: 'cap{}.bin'.format(p), ids))
 
        self.capture(self.ddr0, paths, ids, offset, captureSize)

        ids = [i for i in range(8, 16, 1)]
        paths = list(map(lambda p: 'cap{}.bin'.format(p), ids))

        self.capture(self.ddr1, paths, ids, offset, captureSize)

        self.shutdown_RF()

        print('Pass')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('{}: Usage'.format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]

    freq = 75_000_000
    dBFS = int(-9)
    captureSize = 128 * 4096 * 2
    restart_rfdc = False
    load_bram = True

    test = Test_1x1_ST()
    
    test.run_test(ticsFilePath, freq, dBFS, captureSize, restart_rfdc, load_bram)
