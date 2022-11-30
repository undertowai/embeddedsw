
import sys
from time import sleep
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

    def setup_RF(self, ticsFilePath, init_rfdc=True):
        if init_rfdc:
            self.rfdc.init()
        self.lmx.config(ticsFilePath)
        self.hmc.DefaultConfig_6300(0x0)
        self.hmc.DefaultConfig_6301(0x0)
        
    def shutdown_RF(self):
        self.hmc.Reset()
    
    def getBramSize(self):
        assert self.bram0.getSize() == self.bram1.getSize()
        return self.bram0.getSize()

    def load_dac_player(self, bram0_data, bram1_data):
        bram0_size = self.bram0.load(bram0_data)
        bram1_size = self.bram1.load(bram1_data)

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

    def capture(self, ddr, paths, ids, offset, size):

        assert len(paths) == len(ids)

        base_address = ddr.base_address() + offset
        addr = base_address

        self.adc_dac_sync(False)
        for id in ids:
            devName = self.dma.devIdToIpName(id)
            self.dma.reset(devName)
            self.dma.startTransfer(devName, addr, size)
            addr = addr + size

        self.adc_dac_sync(True)

        #FIXME Interrupt or poll ?
        sleep(1)
        addr = base_address
        for path in paths:
            ddr.capture(path, addr, size)
            addr = addr + size


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('{}: Usage'.format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]

    test = TestSuite(ticsFilePath)

    test.run_test()
