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
        phaseRads = ((2*math.pi) / 360.0) * phaseDegrees

        print("Adjusted Frequency:          {} Hz".format(newFreq))
        print("Calculated Amplitude: {}".format(amplitude))
        print("Phase rads: {}".format(phaseRads))

        buffer = np.empty(numSamples, dtype=np.int16)
        for i in range(numSamples):
            rads = math.pi / 180
            val = amplitude * math.cos(stepSize * i * rads + phaseRads)
            buffer[i] = int(val)

        return buffer

    def setSaw(self, numSampels):
        buffer = np.empty(numSamples, dtype=np.int16)
        for i in range(numSamples):
            buffer[i] = int(i)

        return buffer

    def setTriangle(self, numSamples, period):

        buffer = np.empty(numSamples, dtype=np.int16)

        for i in range(1, numSamples//period, 2):
            for j in range(period):
                buffer[(i-1)*period + j] = j - period//2 + 40
            for j in range(period):
                buffer[i*period + j] = period//2 - j

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
