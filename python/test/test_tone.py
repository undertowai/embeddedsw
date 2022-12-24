import sys
from test import TestSuite
import numpy as np

from misc.swave import Wave
from misc.widebuf import WideBuf

class TestTone(TestSuite):
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

        tone = Wave().getSine(
            numBytes, freq, dBFS, samplingFreq, sampleSize, phaseDegrees, fullCycles
        )

        buffer = np.empty(buffersCount * numSamples, dtype=dtype)

        for i in range(buffersCount):
            WideBuf().make(buffer, tone, i, buffersCount, samplesPerFLit)

        return buffer

    def run_test(self, freq, dBFS):

        samplingFreq = self.rfdc.getSamplingFrequency()

        print("\n\n\n=== Running test ===")
        print("RFDC Sampling Rate = {}".format(samplingFreq))

        bram_data = self.make_single_tone_bram(samplingFreq, freq, dBFS, np.uint16)
        self.load_dac_player(bram_data, bram_data)

        self.gpio_gate_0.set(0xFF)
        self.gpio_gate_1.set(0xFF)
        self.adc_dac_sync(True)

        print("Pass")


if __name__ == "__main__":

    freq = 5_000_000
    dBFS = int(-0)

    test = TestTone()

    test.run_test(freq, dBFS)
