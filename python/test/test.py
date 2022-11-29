
import sys

import numpy as np

sys.path.append('../lmx')
sys.path.append('../hmc')
sys.path.append('../gpio')
sys.path.append('../axidma')
sys.path.append('../rfdc')
sys.path.append('../xddr')
sys.path.append('../bram')

from lmx import Lmx2820
from hmc import HMC63xx
from gpio import AxiGpio
from axidma import AxiDma
from xddr import Xddr
from rfdc import Rfdc
from bram import BramFactory

class TestSuite:
    def __init__(self):

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

    def setup_RF(self, ticsFilePath):
        self.rfdc.init()
        self.lmx.config(ticsFilePath)
        self.hmc.DefaultConfig_6300(0x0)
        self.hmc.DefaultConfig_6301(0x0)
        
    def shutdown_RF(self):
        self.hmc.reset()
    
    def load_dac_player(self, bram0_file, bram1_file):
        bram0_size = self.bram0.loadFromFile(bram0_file, np.uint16)
        bram1_size = self.bram1.loadFromFile(bram1_file, np.uint16)

        assert(bram0_size == bram1_size)

        #TODO add an explanation
        samplesPerSymbol = int(bram0_size / 128)

        self.gpio_gate_0.set(0xff)
        self.gpio_gate_1.set(0xff)
        self.gpio_bram_count.set(samplesPerSymbol)

    def adc_dac_sync(self, sync):
        if sync:
            self.gpio_sync.set(0xff)
        else:
            self.gpio_sync.set(0x0)

    def run_test(self, ticsFilePath, bram0_file, bram1_file):

        self.setup_RF(ticsFilePath)

        self.adc_dac_sync(False)

        self.load_dac_player(bram0_file, bram1_file)

        base_address = self.ddr0.base_address()
        chunk_length = 0x1000
        self.dma.startTransfer(self.dma.devIdToIpName(id), base_address, chunk_length)

        self.ddr0.capture('cap0.bin', base_address, chunk_length)

        self.shutdown_RF()

        print('Pass')

        

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('{}: Usage'.format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]

    test = TestSuite(ticsFilePath)

    test.run_test()
