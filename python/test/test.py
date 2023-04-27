import sys
from time import sleep
import traceback
import logging

sys.path.append("../hmc")
sys.path.append("../axi")
sys.path.append("../rfdc")
sys.path.append("../xddr")
sys.path.append("../dac")
sys.path.append("../misc")
sys.path.append("../main")

from hmc import HMC63xx
from axidma import AxiDma
from xddr import Xddr
from rfdc_clk import RfdcClk
from gpio import AxiGpio
from axis_switch import AxisSwitch
from main import MainLoopExt, MainLoopPython

from inet import Inet
from test_config import TestConfig
from integrator import IntegratorSW, IntegratorHW

class TestSuite(TestConfig, AxiGpio, RfdcClk, Inet):

    def __init__(self, config):
        TestConfig.__init__(self, config)
        AxiGpio.__init__(self, 'axi_gpio')
        RfdcClk.__init__(self)
        Inet.__init__(self)

        self.hmc = HMC63xx("spi_gpio")
        self.dma = AxiDma("axidma")
        self.ddr0 = Xddr("ddr4_0")
        self.ddr1 = Xddr("ddr4_1")

        self.axis_switch0 = AxisSwitch("axis_switch_0")
        self.axis_switch1 = AxisSwitch("axis_switch_1")

        self.gpio_sync = self.getGpio("adc_dac_sync_gpio_0")

        self.ext_main_executor = MainLoopPython(self) \
                                if self.ext_main_exec_lib == "" else MainLoopExt(self, self.ext_main_exec_lib)

        self.integrator = IntegratorHW(self) if self.integrator_mode == 'hw' else IntegratorSW(self)

        self.__set_loopback(self.adc_dac_sw_loppback)

        self.samplingFreq = self.rfdc.getSamplingFrequency()

        self.checkBwCapacity(self.samplingFreq)

    def __set_loopback(self, loopback):
        s = [0, 2, 4, 6, 8, 10, 12, 14] if loopback else [1, 3, 5, 7, 9, 11, 13, 15]
        m = [0, 1, 2, 3, 4, 5, 6, 7]

        self.axis_switch0.route(s, m)
        self.axis_switch1.route(s, m)

    def adc_dac_sync(self, sync):
        self.gpio_sync.set(val=0xff if sync else 0x0)

    def prep_dma_batched(self, ddr_rx_dma_map):
        dmaBatch = []
        area = {}
        size = self.getCaptureSizePerDma()
        for ddr_id in ddr_rx_dma_map:
            ddr = getattr(self, f'ddr{ddr_id}')
            rx_dma_id = ddr_rx_dma_map[ddr_id]

            base_address = ddr.base_address()
            addr = base_address

            for rxn, dma_id in rx_dma_id:
                #2 DMA channels for I and Q
                assert len(dma_id) == 2

                addrI = addr
                addrQ = addr + size
                if self.debug:
                    print(f'dmaBatch: {int(ddr_id), self.dma.devIdToIpName(dma_id[0])}, addr={hex(addrI)}, size={hex(size)}')
                    print(f'dmaBatch: {int(ddr_id), self.dma.devIdToIpName(dma_id[1])}, addr={hex(addrI)}, size={hex(size)}')

                dmaBatch.append( ( int(ddr_id), self.dma.devIdToIpName(dma_id[0]), addrI, size ) )
                dmaBatch.append( ( int(ddr_id), self.dma.devIdToIpName(dma_id[1]), addrQ, size ) )

                addr = addrQ + size
                area[rxn] = {"I": (addrI, size), "Q": (addrQ, size)}
        return dmaBatch, area

    def start_dma(self, rx_dma_map):
        dmaBatch, area = self.prep_dma_batched(rx_dma_map)
        self.dma.startTransferBatched(dmaBatch=dmaBatch)

        return area

    def calc_wait_time_ms(self):
        capture_size_bytes = self.getStreamSizeBytesPerDma()
        sleep_time = self.getCaptureTimeForBytes(capture_size_bytes)
        return int(sleep_time*1000)

    def xddr_read(self, addr, size, dtype):
        capture_samples = self.getDdrCaptureSizeSamples()

        if self.debug:
            print(f'xddr_read: addr={hex(addr)}, size={hex(size)}, capture_samples={hex(capture_samples)}')

        return Xddr.read(addr, size, dtype)[:capture_samples]
