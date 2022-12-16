
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

    def get_args(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    @TestSuite.Test
    def run_test(self, **kw):

        self.get_args(**kw)

        samplingFreq = self.rfdc.getSamplingFrequency()

        print('\n\n\n=== Running test ===')
        print('RFDC Sampling Rate = {}'.format(samplingFreq))

        dtype = np.uint16

        if load_bram:
            bram0_data, freq = self.make_sweep_tone_bram(samplingFreq, self.freq, self.dBFS, self.freqStep, dtype)
            bram1_data, freq = self.make_sweep_tone_bram(samplingFreq, self.freq, self.dBFS, self.freqStep, dtype)

            self.load_dac_player(bram0_data, bram1_data)

        self.setup_RF_Clk(self.ticsFilePath, self.restart_rfdc)
        #Turn on all the dac player outputs
        self.dac_gate(0xffff)

        offset = 0x0

        for txi in self.tx:

            print('*** Running Iteration : rx={}, tx={}'.format(self.rx, txi))
            self.setup_RF([txi], self.rx)

            self.hmc.IfGain_6300(txi, 12)

            outputDir = self.mkdir(self.outputDir, str(txi))

            ids = [i for i in range(8)]
            paths = list(map(self.cap_name, ids))

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

    freq = 50_000_000
    freqStep = 0
    dBFS = int(-3)
    captureSize = 128 * 4096 * 2
    restart_rfdc = False
    load_bram = True
    capture_data = True
    #Which radios to use:
    tx = [i for i in range(8)]
    rx = [i for i in range(8)]
    outputDir = '/home/captures'

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
                outputDir       =outputDir)