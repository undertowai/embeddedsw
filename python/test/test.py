
import sys
from time import sleep
import traceback
import logging
import numpy as np

sys.path.append('../lmx')
sys.path.append('../hmc')
sys.path.append('../gpio')
sys.path.append('../axidma')
sys.path.append('../rfdc')
sys.path.append('../xddr')
sys.path.append('../bram')
sys.path.append('../misc')

from swave import Wave
from widebuf import WideBuf

from lmx import Lmx2820
from hmc import HMC63xx
from gpio import AxiGpio
from axidma import AxiDma
from xddr import Xddr
from rfdc import Rfdc
from bram import BramFactory

from hw import Hw

class TestSuite:
    def getargs(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    def Test(func):
        def inner(self, **kw):
            try:
                self.getargs(**kw)
                func(self)
            except Exception as e:
                logging.error(traceback.format_exc())
                print('=== FAILED ===')
                self.shutdown_RF()
            else:
                print('=== PASS ===')
        
        return inner


    def __init__(self):

        self.hw = Hw()

        self.lmx = Lmx2820('axi_quad_spi_0')
        self.hmc = HMC63xx('spi_gpio')
        self.axiGpio = AxiGpio('axi_gpio')
        self.dma = AxiDma('axidma')
        self.ddr0 = Xddr('ddr4_0')
        self.ddr1 = Xddr('ddr4_1')
        self.rfdc = Rfdc('rfdc2')

        self.gpio_sync = self.axiGpio.getGpio('dma_sync_gpio_0')
        self.gpio_gate_0 = self.axiGpio.getGpio('axis_gate_0_axi_gpio_0')
        self.gpio_gate_1 = self.axiGpio.getGpio('axis_gate_1_axi_gpio_0')
        self.gpio_bram_count = self.axiGpio.getGpio('axi_gpio_0')

        bram_f = BramFactory()
        self.bram0 = bram_f.makeBram('ram_player_8wide_0_axi_bram_ctrl_0')
        self.bram1 = bram_f.makeBram('ram_player_8wide_1_axi_bram_ctrl_0')

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

    def setup_RF_Clk(self, ticsFilePath, restart_rfdc=True):
        self.rfdc.init_clk104()

        if restart_rfdc:
            self.rfdc.restart()

        self.lmx.config(ticsFilePath=ticsFilePath)


    def setup_RF(self, hmc_6300_ics, hmc_6301_ics):
        self.hmc.GpioInit()
        for ic in hmc_6300_ics:
            self.hmc.DefaultConfig_6300(ic=ic)
        
        for ic in hmc_6301_ics:
            self.hmc.DefaultConfig_6301(ic=ic)
        
    def shutdown_RF(self):
        self.hmc.Reset()
    
    def getBramSize(self):
        assert self.bram0.getSize() == self.bram1.getSize()
        return self.bram0.getSize()

    def load_dac_player(self, bram0_data, bram1_data):
        bram0_size = self.bram0.load(data=bram0_data)
        bram1_size = self.bram1.load(data=bram1_data)

        assert(bram0_size == bram1_size)

        div = self.hw.BUFFERS_IN_BRAM * self.hw.SAMPLES_PER_FLIT * self.hw.BYTES_PER_SAMPLE
        playerTicksPerBuffer = int(bram0_size / div)

        self.gpio_bram_count.set(val=playerTicksPerBuffer)

    def adc_dac_sync(self, sync):
        self.gpio_sync.set(val= (0xff if sync else 0x0))

    def __start_dma(self, ddr, ids, offset, size):

        base_address = ddr.base_address() + offset
        addr = base_address

        for id in ids:
            devName = self.dma.devIdToIpName(id)
            self.dma.startTransfer(devName=devName, addr=addr, len=size)
            addr = addr + size

    def __reset_dma(self, ids):

        for id in ids:
            devName = self.dma.devIdToIpName(id)
            self.dma.reset(devName=devName)

    def __write_cap_data(self, path, data):
        with open(path, 'wb') as f:
            f.write(data)
            f.close()

    def __capture_memory(self, ddr, outputdir, paths, offset, size):
        base_address = ddr.base_address() + offset

        addr = base_address
        for path in paths:
            outputPath = None if outputdir is None else outputdir + '/' + path
            data = ddr.capture(addr, size)
            if outputPath is not None:
                self.__write_cap_data(outputPath, data)
            addr = addr + size

    def dac_gate(self, val):
        self.gpio_gate_0.set(val=(val >> 0) & 0xff)
        self.gpio_gate_1.set(val=(val >> 8) & 0xff)

    def capture(self, ddr, outputDir, paths, ids, offset, size):

        assert len(paths) == len(ids)

        self.adc_dac_sync(False)

        self.__start_dma(ddr, ids, offset, size)

        self.adc_dac_sync(True)

        #FIXME Interrupt or poll ?
        sleep(0.1)

        self.__reset_dma(ids)

        return self.__capture_memory(ddr, outputDir, paths, offset, size)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('{}: Usage'.format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]

    test = TestSuite(ticsFilePath)

    test.run_test()
