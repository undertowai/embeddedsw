from genericpath import exists
import sys
import math
import os
import numpy as np


class WideBuf:
    def __init__(self):
        pass

    def compose(self, dst, src, bufferNum, buffersCount, samplesPerFLit):
        offset = bufferNum * samplesPerFLit
        for i in range(0, src.size, samplesPerFLit):

            for j in range(samplesPerFLit):
                dst[offset + j] = src[i + j]

            offset += buffersCount * samplesPerFLit
            if offset >= dst.size:
                break

    def decompose(self, src, numSamples, bufferNum, buffersCount, samplesPerFLit, dtype=np.int16):
        buffer = np.empty(numSamples, dtype=dtype)
        offset = bufferNum * samplesPerFLit
        for i in range(0, buffer.size, samplesPerFLit):

            for j in range(samplesPerFLit):
                buffer[i + j] = src[offset + j]

            offset += buffersCount * samplesPerFLit
            if offset >= src.size:
                break
        return buffer

    def make(self, buffer, tone, bufferNum, buffersCount, samplesPerFLit):

        self.compose(buffer, tone, bufferNum, buffersCount, samplesPerFLit)

        # dec_buffer = np.empty(numSamples, dtype=np.uint16)
        # decompose(dec_buffer, buffer, bufferNum, buffersCount, samplesPerFLit)
        # dec_buffer.tofile(wideFilePath + '.decomposed')


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: {} <wide file> <buffer to insert> <dac num>".format(sys.argv[0]))
        exit()

    wideFilePath = sys.argv[1]
    bufferToInsert = sys.argv[2]
    bufferNum = int(sys.argv[3])

    WideBuf().makewide(wideFilePath, bufferToInsert, bufferNum)
