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

from hmc import HMC63xx
from axidma import AxiDma
from xddr import Xddr
from rfdc_clk import RfdcClk
from gpio import AxiGpio
from axis_switch import AxisSwitch

from inet import Inet
from test_config import TestConfig
from integrator import Integrator, IntegratorHwIf

class TestSuite(TestConfig, AxiGpio, RfdcClk, Inet):

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
                print("=== FAILED ===")
                self.shutdown_hmc()
                raise Exception()
            else:
                print("=== PASS ===")

        return inner

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

        self.integrator = Integrator(self.integrator_mode, self.dwell_samples, self.dwell_num, self.dwell_window, self.debug)

        self.apply_hw_delay_per_tx(0)
        self.set_loopback(self.adc_dac_sw_loppback)

        self.samplingFreq = self.rfdc.getSamplingFrequency()

        if self.debug:
            print(f'Test Init Done; Sampling frequency {self.samplingFreq}')

    def set_loopback(self, loopback):
        s = [0, 2, 4, 6, 8, 10, 12, 14] if loopback else [1, 3, 5, 7, 9, 11, 13, 15]
        m = [0, 1, 2, 3, 4, 5, 6, 7]

        self.axis_switch0.route(s, m)
        self.axis_switch1.route(s, m)

    def setup_hmc(self, tx, rx):
        self.hmc.GpioInit()
        self.hmc.setup(tx, rx, self.rf_config)

    def shutdown_hmc(self):
        self.hmc.Reset()

    def adc_dac_sync(self, sync):
        if sync:
            self.gpio_sync.set(val=0xff)
        else:
            self.gpio_sync.set(val=0x0)

    def apply_hw_delay_per_tx(self, txn):
        hw_del = self.getStreamHwOffset(txn)
        self.integrator.setup(hw_del)

    def __start_dma(self, id, addr, size):
        devName = self.dma.devIdToIpName(id)
        if self.debug:
            print(f'__start_dma: {devName}, addr={hex(addr)}, size={hex(size)}')
        self.dma.startTransfer(devName=devName, addr=addr, len=size)

    def start_dma(self, rx_dma_map):
        area = {}
        size = self.getCaptureSizePerDma()
        for _ddr in rx_dma_map.keys():
            ddr = getattr(self, _ddr)
            rx_dma_id = rx_dma_map[_ddr]

            base_address = ddr.base_address()
            addr = base_address

            for rxn, dma_id in rx_dma_id:
                #2 DMA channels for I and Q
                assert len(dma_id) == 2

                addrI = addr
                addrQ = addr + size
                self.__start_dma(dma_id[0], addrI, size)
                self.__start_dma(dma_id[1], addrQ, size)

                addr = addrQ + size
                area[rxn] = {"I": (addrI, size), "Q": (addrQ, size)}
        return area

    def wait_capture_done(self):
        capture_size_bytes = self.getStreamSizeBytesPerDma()
        sleep_time = self.getCaptureTimeForBytes(capture_size_bytes)
        sleep(sleep_time)

    def xddr_read(self, addr, size, dtype, offset_samples = 0):
        if self.debug:
            print(f'xddr_read: addr={hex(addr)}, size={hex(size)}, offset samples={offset_samples}')
        capture_samples = self.getDdrCaptureSizeSamples()
        offset_samples += self.getDdrOffsetSamples()

        if self.debug:
            print(f'xddr_read: capture_samples={hex(capture_samples)}, offset_samples={hex(offset_samples)}')

        return Xddr.read(addr, size, dtype)[offset_samples:capture_samples+offset_samples]
