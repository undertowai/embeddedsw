import sys, argparse
import numpy as np
import os

sys.path.append("../misc")
sys.path.append("../bram")
sys.path.append("../test")
sys.path.append("../axi")
sys.path.append("../rfdc")
sys.path.append("../hw")

from bram import BramFactory
from gpio import AxiGpio
from hw import Hw
from swave import Wave
from widebuf import WideBuf
from rfdc import Rfdc
import json

class DacPlayer(AxiGpio):

    class Parameters:
        pass

    def __init__(self):
        AxiGpio.__init__(self, "axi_gpio")
        bram_f = BramFactory()
        self.bram0 = bram_f.makeBram("ram_player_8wide_0_axi_bram_ctrl_0")
        self.bram1 = bram_f.makeBram("ram_player_8wide_1_axi_bram_ctrl_0")

        self.gpio_bram_count = self.getGpio("axi_gpio_0")
        self.hw = Hw()
        self.rfdc = Rfdc("rfdc2")

        self.samplingFreq = self.rfdc.getSamplingFrequency()

    def load_json(self, path):
        with open(path, 'r') as f:
            j = json.load(f)
            f.close()
        return j

    def getBramSize(self):
        assert self.bram0.getSize() == self.bram1.getSize()
        return self.bram0.getSize()

    def getParameters(self):
        par = self.Parameters()

        par.sampleSize = self.hw.BYTES_PER_SAMPLE
        par.buffersCount = self.hw.BUFFERS_IN_BRAM
        par.numBytes = int(self.getBramSize() / par.buffersCount)
        par.numSamples = int(par.numBytes / par.sampleSize)
        par.samplesPerFLit = self.hw.SAMPLES_PER_FLIT

        assert self.hw.BYTES_PER_SAMPLE == 2
        par.dtype = np.int16

        return par


    def make_zero_bram(self):
        p = self.getParameters()

        buffer = np.zeros(p.buffersCount * p.numSamples, dtype=p.dtype)
        return buffer

    def make_sweep_tone_bram(self, samplingFreq, freq, dBFS, freqStep, phase_degrees, phase_step, numSamples):
        p = self.getParameters()
        fullCycles = True
        phaseDegrees = phase_degrees
        numSamples = numSamples if p.numSamples > numSamples and numSamples != 0 else p.numSamples

        buffer = np.empty(p.buffersCount * numSamples, dtype=p.dtype)

        if freqStep == 0 and phase_step == 0:

            tone = Wave().getSine(
                p.numBytes,
                freq,
                dBFS,
                samplingFreq,
                p.sampleSize,
                phaseDegrees,
                fullCycles,
            )

            for i in range(p.buffersCount):
                WideBuf().make(buffer, tone, i, p.buffersCount, p.samplesPerFLit)

        else :
            for i in range(p.buffersCount):

                tone = Wave().getSine(
                    p.numBytes,
                    freq,
                    dBFS,
                    samplingFreq,
                    p.sampleSize,
                    phaseDegrees,
                    fullCycles,
                )

                freq = freq + freqStep
                phaseDegrees += phase_step

                WideBuf().make(buffer, tone, i, p.buffersCount, p.samplesPerFLit)

        return buffer, freq, phaseDegrees

    def make_saw_bram(self):
        p = self.getParameters()

        buffer = np.empty(p.buffersCount * p.numSamples, dtype=p.dtype)

        tone = Wave().setSaw( p.numBytes, p.sampleSize )

        for i in range(p.buffersCount):

            WideBuf().make(buffer, tone, i, p.buffersCount, p.samplesPerFLit)

        return buffer

    def make_noise_bram(self, numSamples, scale):
        p = self.getParameters()
        numSamples = numSamples if p.numSamples > numSamples else p.numSamples

        data = np.random.randint(low = -scale, high = scale, size = p.buffersCount * numSamples, dtype=p.dtype)
        return data

    def load_dac_player(self, bram0_data, bram1_data):
        bram0_size = self.bram0.load(data=bram0_data)
        bram1_size = self.bram1.load(data=bram1_data)

        assert bram0_size == bram1_size

        div = (
            self.hw.BUFFERS_IN_BRAM
            * self.hw.SAMPLES_PER_FLIT
            / self.hw.BYTES_PER_SAMPLE
        )

        assert int(bram0_size) % int(div) == 0, f'Bram size must be multiply of {div}'
        playerTicksPerBuffer = int(bram0_size / div) - 1

        self.gpio_bram_count.set(val=playerTicksPerBuffer)


    def load_single(self, bram1_data):
        self.bram1.load(data=bram1_data)

    def load_dac_player_from_file(self, bram0_path, bram1_path):

        _, bram0_ext = os.path.splitext(bram0_path)
        _, bram1_ext = os.path.splitext(bram1_path)

        assert bram0_ext == bram1_ext
        assert bram0_ext == '.npy', "Must be .npy format !"

        data0 = np.load(bram0_path)
        data1 = np.load(bram1_path)

        self.load_dac_player(data0, data1)

    def make_bram_content_from_file(self, Ipath, Qpath):
        p = self.getParameters()

        assert self.hw.BYTES_PER_SAMPLE == 2
        dtype = np.int16

        buffer = np.empty(p.buffersCount * p.numSamples, dtype=dtype)

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

        for i in range(0, p.buffersCount, 2):
            WideBuf().make(buffer, I, i, p.buffersCount, p.samplesPerFLit)
            WideBuf().make(buffer, Q, i + 1, p.buffersCount, p.samplesPerFLit)

        return buffer

    def __make_bram_content_from_files(self, IQarray):
        sampleSize = self.hw.BYTES_PER_SAMPLE
        buffersCount = self.hw.BUFFERS_IN_BRAM
        numBytes = int(self.getBramSize() / buffersCount)
        numSamples = int(numBytes / sampleSize)
        samplesPerFLit = self.hw.SAMPLES_PER_FLIT

        assert self.hw.BYTES_PER_SAMPLE == 2
        dtype = np.int16

        buffer = np.empty(buffersCount * numSamples, dtype=dtype)

        assert int(len(IQarray)/2) == int(buffersCount)

        for i, Ipath, Qpath in enumerate(IQarray):

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

            WideBuf().make(buffer, I, i, buffersCount, samplesPerFLit)
            WideBuf().make(buffer, Q, i + 1, buffersCount, samplesPerFLit)

        return buffer

    def make_bram_content_from_files(self, IQjsonPath):
        tx_2_bram_map = self.load_json('../hw/tx_to_bram_map.json')
        IQjson = self.load_json(IQjsonPath)


        buffers = {}
        for bram in tx_2_bram_map:
            IQarray = []
            for tx in tx_2_bram_map[bram]:
                IQarray.append( ( IQjson[tx]['I'], IQjson[tx]['Q'] ) )
            buffers[bram] = self.__make_bram_content_from_files(IQarray)

        return buffers

    def decompose_buf(self, bram_idx, dac_idx=None):
        p = self.getParameters()

        bram = self.bram0 if bram_idx == 0 else self.bram1
        bram_data = bram.read(dtype=p.dtype)

        buffers = []
        if dac_idx is not None:
            buffer = WideBuf().decompose(bram_data, p.numSamples, dac_idx, p.buffersCount, p.samplesPerFLit)
            buffers.append(buffer)
        else:
            for i in range(0, p.buffersCount, 1):
                buffer = WideBuf().decompose(bram_data, p.numSamples, i, p.buffersCount, p.samplesPerFLit)
                buffers.append(buffer)

        return buffers

    def export(self, bram0_path, bram1_path):
        p = self.getParameters()

        bram0_data = self.bram0.read(dtype=p.dtype)
        bram1_data = self.bram1.read(dtype=p.dtype)

        np.save(bram0_path, bram0_data)
        np.save(bram1_path, bram1_data)

    def decompose(self, bram_idx):
        buffers = self.decompose_buf(bram_idx)

        for i, buffer in enumerate(buffers):
            with open('samples_{}.bin'.format(i), '+wb') as f:
                np.save(f, buffer)

if __name__ == "__main__":

    argparser=argparse.ArgumentParser()

    argparser.add_argument('--dec', help='Decompose specified bram into linear samples', type=int)

    argparser.add_argument('--size', help='Specify size of BRAM content', type=int)

    argparser.add_argument('--zero', help='Zero BRAM content', action='store_true')
    argparser.add_argument('--export', help='Export BRAM content', type=str)

    argparser.add_argument('--bram0', help='specify file with bram0 content', type=str)
    argparser.add_argument('--bram1', help='specify file with bram1 content', type=str)

    argparser.add_argument('--ifile', help='specify I data to be loaded in BRAM', type=str)
    argparser.add_argument('--qfile', help='specify Q data to be loaded in BRAM', type=str)

    argparser.add_argument('--iqjson', help='specify I/Q json file to load from', type=str)

    argparser.add_argument('--tone', help='Specify tone frequency to be loaded in BRAM', type=int)
    argparser.add_argument('--step', help='Specify tone step frequency', type=int)
    argparser.add_argument('--db', help='Specify tone amplitude', type=int)
    argparser.add_argument('--pstep', help='Specify phase_step', type=int)

    argparser.add_argument('--saw', help='Generate Incrementing sequence between min and max values (int16)', action='store_true')
    argparser.add_argument('--noise', help='generate noise', action='store_true')
    argparser.add_argument('--scale', help='Set scale for noise', type=int)

    args  = argparser.parse_args()

    player = DacPlayer()

    size = int(0)
    if args.size is not None:
        size = args.size

    if args.export is not None:
        print(f'Exporting BRAM to path {args.export}')
        bram0_path = f'{args.export}{os.sep}bram0'
        bram1_path = f'{args.export}{os.sep}bram1'
        player.export(bram0_path, bram1_path)

    elif args.dec is not None:
        print('Decomposing: {}'.format('bram0' if args.dec == 0 else 'bram1'))
        player.decompose(args.dec)
    elif args.bram0 is not None and args.bram1 is not None:

        print('Loading raw content : bram0={} bram1={}'.format(args.bram0, args.bram1))
        player.load_dac_player_from_file(args.bram0, args.bram1)

    elif args.ifile is not None or args.qfile is not None:
        if args.ifile is None or args.qfile is None:
            raise Exception('Both I & Q data has to be specified')

        print('Flattening BRAM from files : {} {}'.format(args.ifile, args.qfile))
        bram_data = player.make_bram_content_from_file(args.ifile, args.qfile)
        player.load_dac_player(bram_data, bram_data)
    elif args.iqjson is not None:
        print('Flattening BRAM from json : {}'.format(args.iqjson))

        buffers = player.make_bram_content_from_files(args.iqjson)
        player.load_dac_player(buffers['bram0'], buffers['bram1'])
    elif args.tone is not None:
        freq = int(args.tone)
        step = int(0)
        dBFS = int(-9)
        phase_step = 0
        if args.step is not None:
            step = int(args.step)
        if args.db is not None:
            dBFS = int(args.db)
        if args.pstep is not None:
            phase_step = float(args.pstep)

        print('Flattening BRAM using tone freq={} step={} dBFS={}, phase_step={}'.format(freq, step, dBFS, phase_step))
        bram0, freq, phaseDegrees = player.make_sweep_tone_bram(player.samplingFreq, freq, dBFS, step, 0, phase_step, size)
        if step != 0 or phase_step != 0:
            bram1, _, _ = player.make_sweep_tone_bram(player.samplingFreq, freq, dBFS, step, phaseDegrees, phase_step, size)
        else: bram1 = bram0

        player.load_dac_player(bram0, bram1)
    elif args.saw is True:

        print('Flattening BRAM using SAW ')
        bram0 = player.make_saw_bram()

        player.load_dac_player(bram0, bram0)
    elif args.zero is True:
        print('Zero BRAM')
        bram_data = player.make_zero_bram()
        player.load_dac_player(bram_data, bram_data)
    elif args.noise is True:
        scale = 0.1 if args.scale is None else args.scale
        print(f'Loading noise: swing={-scale}:{scale}, size={size}')
        bram_data = player.make_noise_bram(size, scale)
        player.load_dac_player(bram_data, bram_data)

    print("Pass")
