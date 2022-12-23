from genericpath import exists
import sys
import math
import numpy as np


class Wave:
    def calcAmp(self, dBFS):
        ratio = pow(10.0, dBFS / 20)
        amplitude = 0x7FFE * ratio
        if amplitude > 0x7FFE:
            raise Exception("Bad amplitude")
        return int(amplitude)

    def getSine(
        self,
        NumBytes,
        freq,
        dBFS,
        samplingFreq,
        sampleSize,
        phaseDegrees,
        fullCycles=True,
    ):
        amplitude = self.calcAmp(dBFS)
        numSamples = int(NumBytes / sampleSize)
        if fullCycles:
            numCycles = int(numSamples / (samplingFreq / freq))
            newFreq = 1 / (((1 / samplingFreq) * numSamples) / numCycles)
        else:
            numCycles = numSamples / (samplingFreq / freq)
            newFreq = 1 / (((1 / samplingFreq) * numSamples) / numCycles)

        stepSize = 360.0 / (numSamples / numCycles)
        phaseRads = (math.pi / 360.0) * phaseDegrees

        print("Adjusted Frequency:          {} Hz".format(newFreq))
        print("Calculated Amplitude: {}".format(amplitude))

        buffer = np.empty(numSamples, dtype=np.uint16)
        for i in range(numSamples):
            rads = math.pi / 180
            val = amplitude * math.cos(stepSize * i * rads + phaseRads)
            buffer[i] = int(val)

        return buffer

    def strNegative(self, s):
        s = "minus_" + str(-s) if (s < 0) else str(s)
        return s


if __name__ == "__main__":

    freq = int(sys.argv[1])
    dBFS = int(sys.argv[2])
    numBytes = int(sys.argv[3])
    samplingFreq = int(sys.argv[4])

    Wave().getSine(numBytes, freq, dBFS, samplingFreq, 2, 0.0)
