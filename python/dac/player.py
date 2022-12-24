import sys
import numpy as np

sys.path.append("../misc")
sys.path.append("../bram")
sys.path.append("../test")

from bram import BramFactory
from gpio import AxiGpio
from hw import Hw
from swave import Wave
from widebuf import WideBuf

class DacPlayer(AxiGpio):
    def __init__(self):
        AxiGpio.__init__(self, "axi_gpio")
        bram_f = BramFactory()
        self.bram0 = bram_f.makeBram("ram_player_8wide_0_axi_bram_ctrl_0")
        self.bram1 = bram_f.makeBram("ram_player_8wide_1_axi_bram_ctrl_0")
        
        self.gpio_bram_count = self.getGpio("axi_gpio_0")
        self.hw = Hw()

    def getBramSize(self):
        assert self.bram0.getSize() == self.bram1.getSize()
        return self.bram0.getSize()

    def make_sweep_tone_bram(self, samplingFreq, freq, dBFS, freqStep, dtype):
        sampleSize = self.hw.BYTES_PER_SAMPLE
        fullCycles = True
        phaseDegrees = 0x0
        buffersCount = self.hw.BUFFERS_IN_BRAM
        numBytes = int(self.getBramSize() / buffersCount)
        numSamples = int(numBytes / sampleSize)
        samplesPerFLit = self.hw.SAMPLES_PER_FLIT

        assert self.hw.BYTES_PER_SAMPLE == 2
        dtype = np.int16

        buffer = np.empty(buffersCount * numSamples, dtype=dtype)

        for i in range(buffersCount):

            # Keep same frequency for I & Q channels
            if i % 2 == 0:
                tone = Wave().getSine(
                    numBytes,
                    freq,
                    dBFS,
                    samplingFreq,
                    sampleSize,
                    phaseDegrees,
                    fullCycles,
                )
                freq = freq + freqStep

            WideBuf().make(buffer, tone, i, buffersCount, samplesPerFLit)

        return buffer, freq

    def load_dac_player(self, bram0_data, bram1_data):
        bram0_size = self.bram0.load(data=bram0_data)
        bram1_size = self.bram1.load(data=bram1_data)

        assert bram0_size == bram1_size

        div = (
            self.hw.BUFFERS_IN_BRAM
            * self.hw.SAMPLES_PER_FLIT
            * self.hw.BYTES_PER_SAMPLE
        )
        playerTicksPerBuffer = int(bram0_size / div)

        self.gpio_bram_count.set(val=playerTicksPerBuffer)
        
    def load_dac_player_from_file(self, bram0_path, bram1_path):
        data0 = np.fromfile(bram0_path, dtype=np.uint8)
        data1 = np.fromfile(bram1_path, dtype=np.uint8)
        
        self.load_dac_player(data0, data1)

    def make_bram_content_from_file(self, Ipath, Qpath):
        sampleSize = self.hw.BYTES_PER_SAMPLE
        buffersCount = self.hw.BUFFERS_IN_BRAM
        numBytes = int(self.getBramSize() / buffersCount)
        numSamples = int(numBytes / sampleSize)
        samplesPerFLit = self.hw.SAMPLES_PER_FLIT

        assert self.hw.BYTES_PER_SAMPLE == 2
        dtype = np.int16

        buffer = np.empty(buffersCount * numSamples, dtype=dtype)

        I = np.fromfile(Ipath, dtype=np.int16)
        Q = np.fromfile(Qpath, dtype=np.int16)
        for i in range(0, buffersCount, 2):
            WideBuf().make(buffer, I, i, buffersCount, samplesPerFLit)
            WideBuf().make(buffer, Q, i + 1, buffersCount, samplesPerFLit)

        return buffer
        

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: {} <I file path> <Q file path>".format(sys.argv[0]))
        exit()
        
    I_path = sys.argv[1]
    Q_path = sys.argv[2]
    
    player = DacPlayer()
    
    bram_data = player.make_bram_content_from_file(I_path, Q_path)
    player.load_dac_player(bram_data, bram_data)
    
    print("Pass")
