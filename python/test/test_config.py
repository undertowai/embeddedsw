import sys

import json

sys.path.append("../hw")

from hw import Hw

class TestConfig(Hw):
    num_iterations: int = 1
    hw_offset_map: dict = {}

    adc_dac_hw_loppback: bool = False
    adc_dac_sw_loppback: bool = False

    dwell_samples: int = 0
    dwell_num: int = 0
    dwell_window: int = 2

    integrator_mode: str = "bypass" #'hw', 'sw', 'bypass'

    offset_map: dict = {}

    rx: list = []
    tx: list = []
    rf_power: dict = {}

    hw_offset_map_path: str = '../hw/hw_offset.json'
    rf_power_cfg_path: str = '../hmc/configs/rf_power.json'

    debug: bool = False

    def init_attrs(self, obj, config_json_path):
        j = self.load_json(config_json_path)
        for parameter in j:
            if hasattr(obj, parameter):
                setattr(obj, parameter, j[parameter])

    def __init__(self, config_json_path):
        self.init_attrs(self, config_json_path)

        #TODO: Find another way to get path
        self.rf_power = self.load_json(self.rf_power_cfg_path)
        self.hw_offset_map = self.load_json(self.hw_offset_map_path)

        assert self.integrator_mode in ['sw', 'hw', 'bypass']

        if self.integrator_mode == 'hw':
            assert self.dwell_window == self.HW_INTEGRATOR_WINDOW_SIZE, f'For integrator HW mode dwell_window size must be {self.HW_INTEGRATOR_WINDOW_SIZE}'

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

    def getStreamHwOffset(self, txn):
        tx = f'TX{txn}'
        return self.hw_offset_map[tx]

    def __alignToCpuPage(self, size):
        cpu_page = int(self.CPU_PAGE_SIZE)
        size = int(((size - 1) / cpu_page) + 1) * cpu_page

        return size

    def isIntegratorSwMode(self):
        return self.integrator_mode != 'hw'

    def isIntegrationEnabled(self):
        return self.integrator_mode != 'bypass'

    def getDwellWindowPeriods(self):
        return self.dwell_window

    def getStreamSizeSamples(self):
        return int(self.dwell_samples * self.dwell_num)

    def __getStreamSizeBytes(self):
        capture_num_samples = self.getStreamSizeSamples()
        return int(capture_num_samples * self.BYTES_PER_SAMPLE)

    def getStreamSizeBytesPerDma(self):
        capture_size_bytes = self.__getStreamSizeBytes()
        return self.__alignToCpuPage(capture_size_bytes)

    def getDwellCaptureWindowSizeSamples(self):
        return int(self.dwell_samples * self.dwell_window)

    def getDwellCaptureWindowSizebytes(self):
        capture_size_bytes = int(self.getDwellCaptureWindowSizeSamples() * self.BYTES_PER_SAMPLE)
        return self.__alignToCpuPage(capture_size_bytes)

    def getCaptureSizePerDma(self):
        if self.integrator_mode == 'hw':
            return self.getDwellCaptureWindowSizebytes()
        else:
            return self.getStreamSizeBytesPerDma()

    def getCaptureTimeForBytes(self, captureSize):
        numCaptures = 0x1
        batchSize = captureSize * numCaptures
        numSamples = batchSize / (self.BYTES_PER_SAMPLE)
        t = numSamples / self.samplingFreq
        return t

    def getDdrCaptureSizeSamples(self):
        if self.integrator_mode == 'hw':
            return self.getDwellCaptureWindowSizeSamples()
        else:
            return self.getStreamSizeSamples()