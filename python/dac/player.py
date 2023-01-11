import sys, argparse
import numpy as np
import os

sys.path.append("../misc")
sys.path.append("../bram")
sys.path.append("../test")
sys.path.append("../axi")
sys.path.append("../rfdc")

from bram import BramFactory
from gpio import AxiGpio
from hw import Hw
from swave import Wave
from widebuf import WideBuf
from rfdc import Rfdc

class DacPlayer(AxiGpio):
    def __init__(self):
        AxiGpio.__init__(self, "axi_gpio")
        bram_f = BramFactory()
        self.bram0 = bram_f.makeBram("ram_player_8wide_0_axi_bram_ctrl_0")
        self.bram1 = bram_f.makeBram("ram_player_8wide_1_axi_bram_ctrl_0")

        self.gpio_bram_count = self.getGpio("axi_gpio_0")
        self.hw = Hw()
        self.rfdc = Rfdc("rfdc2")

        self.samplingFreq = self.rfdc.getSamplingFrequency()

    def getBramSize(self):
        assert self.bram0.getSize() == self.bram1.getSize()
        return self.bram0.getSize()

    def make_zero_bram(self):
        sampleSize = self.hw.BYTES_PER_SAMPLE
        buffersCount = self.hw.BUFFERS_IN_BRAM
        numBytes = int(self.getBramSize() / buffersCount)
        numSamples = int(numBytes / sampleSize)

        assert self.hw.BYTES_PER_SAMPLE == 2
        dtype = np.int16

        buffer = np.empty(buffersCount * numSamples, dtype=dtype)
        return buffer

    def make_sweep_tone_bram(self, samplingFreq, freq, dBFS, freqStep):
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

    def make_saw_bram(self):
        sampleSize = self.hw.BYTES_PER_SAMPLE
        buffersCount = self.hw.BUFFERS_IN_BRAM
        numBytes = int(self.getBramSize() / buffersCount)
        numSamples = int(numBytes / sampleSize)
        samplesPerFLit = self.hw.SAMPLES_PER_FLIT

        assert self.hw.BYTES_PER_SAMPLE == 2
        dtype = np.int16

        buffer = np.empty(buffersCount * numSamples, dtype=dtype)

        tone = Wave().setSaw( numBytes, sampleSize )

        for i in range(buffersCount):

            WideBuf().make(buffer, tone, i, buffersCount, samplesPerFLit)

        return buffer

    def load_dac_player(self, bram0_data, bram1_data):
        bram0_size = self.bram0.load(data=bram0_data)
        bram1_size = self.bram1.load(data=bram1_data)

        assert bram0_size == bram1_size

        div = (
            self.hw.BUFFERS_IN_BRAM
            * self.hw.SAMPLES_PER_FLIT
            / self.hw.BYTES_PER_SAMPLE
        )
        playerTicksPerBuffer = int(bram0_size / div) - 1

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

        _, Iext = os.path.splitext(Ipath)
        _, Qext = os.path.splitext(Qpath)

        assert Iext == Qext

        if Iext == '.npy':
            I = np.load(Ipath)
            Q = np.load(Qpath)
            assert I.dtype == np.int16
        else:
            I = np.fromfile(Ipath, dtype=np.int16)
            Q = np.fromfile(Qpath, dtype=np.int16)

        for i in range(0, buffersCount, 2):
            WideBuf().make(buffer, I, i, buffersCount, samplesPerFLit)
            WideBuf().make(buffer, Q, i + 1, buffersCount, samplesPerFLit)

        return buffer

    def decompose_buf(self, bram_idx, dac_idx=None):
        sampleSize = self.hw.BYTES_PER_SAMPLE
        buffersCount = self.hw.BUFFERS_IN_BRAM
        numBytes = int(self.getBramSize() / buffersCount)
        numSamples = int(numBytes / sampleSize)
        samplesPerFLit = self.hw.SAMPLES_PER_FLIT

        assert self.hw.BYTES_PER_SAMPLE == 2
        dtype = np.int16

        bram = self.bram0 if bram_idx == 0 else self.bram1
        bram_data = bram.read(dtype=dtype)
        
        buffers = []
        if dac_idx is not None:
            buffer = WideBuf().decompose(bram_data, numSamples, dac_idx, buffersCount, samplesPerFLit)
            buffers.append(buffer)
        else:
            for i in range(0, buffersCount, 1):
                buffer = WideBuf().decompose(bram_data, numSamples, i, buffersCount, samplesPerFLit)
                buffers.append(buffer)

        return buffers

    def decompose(self, bram_idx):
        buffers = self.decompose_buf(bram_idx)

        for i, buffer in enumerate(buffers):
            with open('samples_{}.bin'.format(i), '+wb') as f:
                np.save(f, buffer)

if __name__ == "__main__":

    argparser=argparse.ArgumentParser()

    argparser.add_argument('--dec', help='Decompose specified bram into linear samples', type=int)

    argparser.add_argument('--zero', help='Zero BRAM content', action='store_true')

    argparser.add_argument('--bram0', help='specify file with bram0 content', type=str)
    argparser.add_argument('--bram1', help='specify file with bram1 content', type=str)

    argparser.add_argument('--ifile', help='specify I data to be loaded in BRAM', type=str)
    argparser.add_argument('--qfile', help='specify Q data to be loaded in BRAM', type=str)

    argparser.add_argument('--tone', help='Specify tone frequency to be loaded in BRAM', type=int)
    argparser.add_argument('--step', help='Specify tone step frequency', type=int)
    argparser.add_argument('--db', help='Specify tone amplitude', type=int)

    argparser.add_argument('--saw', help='Generate Incrementing sequence between min and max values', action='store_true')

    args  = argparser.parse_args()

    player = DacPlayer()

    if args.dec is not None:
        print('Decomposing: {}'.format('bram0' if args.dec == 0 else 'bram1'))
        player.decompose(args.dec)
    elif args.bram0 is not None or args.bram1 is not None:
        if args.bram0 is None or args.bram1 is None:

            print('Loading raw content : bram0={} bram1={}'.format(args.bram0, args.bram1))
            player.load_dac_player_from_file(args.bram0, args.bram1)

    elif args.ifile is not None or args.qfile is not None:
        if args.ifile is None or args.qfile is None:
            raise Exception('Both I & Q data has to be specified')
        
        print('Flattening BRAM from files : {} {}'.format(args.ifile, args.qfile))
        bram_data = player.make_bram_content_from_file(args.ifile, args.qfile)
        player.load_dac_player(bram_data, bram_data)
    elif args.tone is not None:
        freq = int(args.tone)
        step = int(0)
        dBFS = int(-9)
        if args.step is not None:
            step = int(args.step)  
        if args.db is not None:
            dBFS = int(args.db)

        print('Flattening BRAM using tone freq={} step={} dBFS={}'.format(freq, step, dBFS))
        bram0, freq = player.make_sweep_tone_bram(player.samplingFreq, freq, dBFS, step)
        if step != 0:
            bram1, freq = player.make_sweep_tone_bram(player.samplingFreq, freq, dBFS, step)
        else: bram1 = bram0

        player.load_dac_player(bram0, bram1)
    elif args.saw is not None:

        print('Flattening BRAM using SAW ')
        bram0 = player.make_saw_bram()

        player.load_dac_player(bram0, bram0)
    elif args.zero is not None:
        print('Zeroing BRAM')
        bram_data = player.make_zero_bram()
        player.load_dac_player(bram_data, bram_data)

    print("Pass")
