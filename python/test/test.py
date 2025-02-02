import os
import sys
from time import sleep
import traceback
import logging
import json

sys.path.append("../hmc")
sys.path.append("../axi")
sys.path.append("../rfdc")
sys.path.append("../xddr")
sys.path.append("../dac")
sys.path.append("../misc")
sys.path.append("../hw")

from hmc import HMC63xx
from axidma import AxiDma
from xddr import Xddr
from rfdc_clk import RfdcClk
from gpio import AxiGpio
from axis_switch import AxisSwitch

from hw import Hw
from inet import Inet

class TestSuiteMisc:
    def __init__(self) -> None:
        pass

    def load_json(self, path):
        with open(path, 'r') as f:
            j = json.load(f)
            f.close()
        return j

    def map_rx_to_dma_id(self, rx):
        rx_to_dma_map_path = '../hw/rx_to_dma_map.json'
        j = self.load_json(rx_to_dma_map_path)
        rx_dma_map = {"ddr0": [], "ddr1": []}
        for rxn in rx:
            m = j[f'rx{rxn}']
            rx_dma_map[m['ddr']].append( (rxn, m['dma']) )
        
        return rx_dma_map
    
    def load_config(self, path):
        j = self.load_json(path)

        self.rx = list(j['rx'])
        self.tx = list(j['tx'])

        self.dwell_samples = int(j['dwell_samples'])
        self.dwell_num = int(j['dwell_num'])
        capture_num_samples = int(self.dwell_samples * self.dwell_num)
        self.capture_size = int(capture_num_samples * self.hw.BYTES_PER_SAMPLE)
        self.cap_ddr_offset = int(j['cap_ddr_offset'])

        self.adc_dac_hw_loppback = bool(j['adc_dac_hw_loppback'])
        self.adc_dac_sw_loppback = bool(j['adc_dac_sw_loppback'])

        num_iterations = 1
        if 'num_iterations' in j:
            num_iterations = j['num_iterations']
        self.num_iterations = num_iterations

        do_dwell_avg = False
        if 'do_dwell_avg' in j:
            do_dwell_avg = j['do_dwell_avg']
        self.do_dwell_avg = do_dwell_avg

        #TODO: Find another way to get path
        self.rf_config = self.load_json('../hmc/configs/rf_power.json')
        
        self.hw_offset_map = self.load_json('../hw/hw_offset.json')

        self.set_loopback(self.adc_dac_sw_loppback)

class TestSuite(TestSuiteMisc, AxiGpio, RfdcClk, Inet):
    DEBUG=False

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

    def __init__(self):
        TestSuiteMisc.__init__(self)
        AxiGpio.__init__(self, 'axi_gpio')
        RfdcClk.__init__(self)
        Inet.__init__(self)
        self.hw = Hw()

        self.hmc = HMC63xx("spi_gpio")
        self.dma = AxiDma("axidma")
        self.ddr0 = Xddr("ddr4_0")
        self.ddr1 = Xddr("ddr4_1")

        self.axis_switch0 = AxisSwitch("axis_switch_0")
        self.axis_switch1 = AxisSwitch("axis_switch_1")

        self.gpio_flush = self.getGpio("adc_dac_flush_gpio_0")

        self.gpio_sync = self.getGpio("adc_dac_sync_gpio_0")

        self.set_loopback(False)

        self.samplingFreq = self.rfdc.getSamplingFrequency()
        
        if self.DEBUG:
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

    def __start_dma(self, id, addr, size):
        devName = self.dma.devIdToIpName(id)
        self.dma.startTransfer(devName=devName, addr=addr, len=size)

    #TODO: Do this properly (Assuning mmap need 4096 aligned addr and size)
    def __dma_fix_size(self, size):
        cpu_page = int(4096)
        hw_del = self.hw.HW_AXIS_DELAY_SAMPLES * self.hw.BYTES_PER_SAMPLE
        size += hw_del
        size = int(((size - 1) / cpu_page) + 1) * cpu_page

        return size

    def start_dma(self, rx_dma_map, _, size):
        area = {}
        size = self.__dma_fix_size(size)
        for _ddr in rx_dma_map.keys():
            ddr = getattr(self, _ddr)
            rx_dma_id = rx_dma_map[_ddr]

            base_address = ddr.base_address()
            addr = base_address

            if self.DEBUG:
                print(f'start_dma: DDR={ddr} base address={hex(base_address)}')

            for rxn, dma_id in rx_dma_id:
                #2 DMA channels for I and Q
                assert len(dma_id) == 2

                if self.DEBUG:
                    print(f'dma id={dma_id}')
                addrI = addr
                addrQ = addr + size
                self.__start_dma(dma_id[0], addrI, size)
                self.__start_dma(dma_id[1], addrQ, size)

                addr += size * 2
                area[rxn] = {"I": (addrI, size), "Q": (addrQ, size)}
        return area

    #HW delay, etc.. is to be applied here
    def xddr_read(self, addr, size, dtype, offset_samples = 0):
        #FIXME !!! Add proper offset per Rx n TX !!!
        capture_samples = self.dwell_num * self.dwell_samples
        offset_samples = offset_samples + self.hw.HW_AXIS_DELAY_SAMPLES
        return Xddr.read(addr, size, dtype)[offset_samples:capture_samples+offset_samples]

    def xddr_clear_area(self, area):
        for ai in area:
            for iq in area[ai]:
                addr, size = area[ai][iq]
                #Use ddr0 as source for C library
                self.ddr0.clear(addr, size)

    def calc_capture_time(self, captureSize):
        numCaptures = 0x1
        batchSize = captureSize * numCaptures
        numSamples = batchSize / (self.hw.BYTES_PER_SAMPLE)
        t = numSamples / self.samplingFreq
        return t

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("{}: Usage".format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]

    test = TestSuite(ticsFilePath)

    test.run_test()
