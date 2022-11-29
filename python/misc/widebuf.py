from genericpath import exists
import sys
import math
import os
import numpy as np

class WideBuf:
    def __init__(self):
        pass

    def readWide(self, path, buffer):
        if exists(path):
            buffer = np.fromfile(path, dtype=np.uint16)
            os.remove(path)
        return buffer

    def compose(self, dst, src, bufferNum, buffersCount, samplesPerFLit):
        offset = bufferNum * samplesPerFLit
        for i in range(0, src.size, samplesPerFLit):

            for j in range(samplesPerFLit):
                dst[offset+j] = src[i+j]

            offset += buffersCount * samplesPerFLit
            if (offset >= dst.size):
                break

    def decompose(self, dst, src, bufferNum, buffersCount, samplesPerFLit):
        offset = bufferNum * samplesPerFLit
        for i in range(0, dst.size, samplesPerFLit):

            for j in range(samplesPerFLit):
                dst[i+j] = src[offset+j]

            offset += buffersCount * samplesPerFLit
            if (offset >= src.size):
                break

    def make(self, wideFilePath, bufferToInsert, bufferNum, buffersCount = int(8), bufferSize = int(128 * 1024), sampleSize = int(2), samplesPerFLit = int(8)):
        numSamples = int(bufferSize / sampleSize)
        buffer = np.empty(buffersCount * numSamples, dtype=np.uint16)

        buffer = self.readWide(wideFilePath, buffer)
        dacBuffer = np.fromfile(bufferToInsert, dtype=np.uint16)
        self.compose(buffer, dacBuffer, bufferNum, buffersCount, samplesPerFLit)

        #dec_buffer = np.empty(numSamples, dtype=np.uint16)
        #decompose(dec_buffer, buffer, bufferNum, buffersCount, samplesPerFLit)
        #dec_buffer.tofile(wideFilePath + '.decomposed')
        buffer.tofile(wideFilePath)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: {} <wide file> <buffer to insert> <dac num>".format(sys.argv[0]))
        exit()

    wideFilePath = sys.argv[1]
    bufferToInsert = sys.argv[2]
    bufferNum = int(sys.argv[3])

    WideBuf().makewide(wideFilePath, bufferToInsert, bufferNum)
