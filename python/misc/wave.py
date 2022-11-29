from genericpath import exists
import sys
import math
import numpy as np

class Wave:
    def calcAmp(self, dBFS):
        ratio = pow(10.0, dBFS/20)
        amplitude = 0x7ffe * ratio
        if amplitude > 0x7ffe:
            raise Exception("Bad amplitude")
        return int(amplitude)

    def getSine(self, NumBytes, freq, dBFS, samplingFreq, sampleSize, phaseDegrees, fullCycles=True):
        amplitude = self.calcAmp(dBFS)
        numSamples = int(NumBytes / sampleSize)
        if fullCycles:
            numCycles = int(numSamples / (samplingFreq / freq))
            newFreq = 1/(( (1/samplingFreq) * numSamples ) / numCycles)
        else:
            numCycles = numSamples / (samplingFreq / freq)
            newFreq = 1/(( (1/samplingFreq) * numSamples ) / numCycles)

        stepSize = 360.0 / (numSamples / numCycles)
        phaseRads = (math.pi / 360.0) * phaseDegrees

        print("Full sycles: {}".format(fullCycles))
        print("Adjusted Sampling Frequency: {} Hz".format(samplingFreq))
        print("Requested Frequency:         {} Hz".format(freq))
        print("Adjusted Frequency:          {} Hz".format(newFreq))
        print("num samples in buffer:  {}".format(numSamples))
        print("num cycles in buffer:  {}".format(numCycles))
        print("calculated step size:  {}".format(stepSize))
        print("Calculated Amplitude: {}".format(amplitude))
        print("Phase rads: {}".format(phaseRads))

        buffer = np.empty(numSamples, dtype=np.uint16)
        for i in range(numSamples):
            rads = math.pi/180
            val = amplitude * math.cos(stepSize * i * rads + phaseRads)
            buffer[i] = int(val)

        return buffer

    def strNegative(self, s):
        s = 'minus_' + str(-s) if (s < 0) else str(s)
        return s

    def sinewave(self, freq, dBFS, phaseDegrees, outputDirectory, numBytes, samplingFreq, fullCycles=True, sampleSize = 2):

        fileName = str(int(freq/1000)) + 'KHz_' + self.strNegative(dBFS) + 'dB_' + self.strNegative(phaseDegrees) +  '.dac'
        buffer = self.getSine(numBytes, freq, dBFS, samplingFreq, sampleSize, phaseDegrees, fullCycles)
        buffer.tofile(outputDirectory + fileName)
        return fileName

if __name__ == "__main__":

    freq = int(sys.argv[1])
    dBFS = int(sys.argv[2])
    outputDirectory = sys.argv[3]
    numBytes = int(sys.argv[4])
    samplingFreq = int(sys.argv[5])
    fullCycles = True if sys.argv[6] == 'TRUE' else False

    Wave().sinewave(freq, dBFS, 0, outputDirectory, numBytes, samplingFreq, fullCycles, sampleSize = 2)
