import sys

import json

sys.path.append("../hw")

from hw import Hw

class TestConfig(Hw):
    num_iterations: int = 1
    hw_offset_map: dict = {}

    adc_dac_hw_loppback: bool = False
    adc_dac_sw_loppback: bool = False

    samples_in_unit: int = 0
    integrator_depth: int = 0
    dwell_in_stream: int = 2

    integrator_mode: str = "bypass" #'hw', 'sw', 'bypass'
    integrator_type: str = "ofdm" # 'ofdm', 'dwell'

    units_in_dwell: int  = 1
    offset_map: dict = {}

    rx: list = []
    tx: list = []
    rf_power: dict = {}

    hw_offset_map_path: str = '../hw/hw_offset.json'
    rf_power_cfg_path: str = '../hmc/configs/rf_power.json'
    rx_to_dma_map_path: str = '../hw/rx_to_dma_map.json'

    ext_main_exec_lib: str = None
    debug: bool = False

    def init_attrs(self, obj, config_json_path):
        j = self.load_json(config_json_path)
        for parameter in j:
            if hasattr(obj, parameter):
                setattr(obj, parameter, j[parameter])

    def __init__(self, config_json_path):
        self.init_attrs(self, config_json_path)

        self.rf_power = self.load_json(self.rf_power_cfg_path)
        self.hw_offset_map = self.load_json(self.hw_offset_map_path)

    def load_json(self, path):
        with open(path, 'r') as f:
            j = json.load(f)
            f.close()
        return j

    def map_rx_to_dma_id(self, rx):

        j = self.load_json(self.rx_to_dma_map_path)
        rx_dma_map = {}
        for rxn in rx:
            m = j[f'rx{rxn}']
            if m['ddr'] not in rx_dma_map: rx_dma_map[m['ddr']] = []
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
        return self.dwell_in_stream

    def getStreamSizeSamples(self):
        return int(self.samples_in_unit * self.integrator_depth * self.units_in_dwell)

    def __getStreamSizeBytes(self):
        capture_num_samples = self.getStreamSizeSamples()
        return int(capture_num_samples * self.BYTES_PER_SAMPLE)

    def getStreamSizeBytesPerDma(self):
        capture_size_bytes = self.__getStreamSizeBytes()
        return self.__alignToCpuPage(capture_size_bytes)

    def getDwellCaptureWindowSizeSamples(self):
        return int(self.samples_in_unit * self.dwell_in_stream)

    def getOfdmCaptureWindowSizeSamples(self):
        return int(self.samples_in_unit * self.units_in_dwell * self.dwell_in_stream)

    def getDwellCaptureWindowSizebytes(self):
        capture_size_bytes = int(self.getDwellCaptureWindowSizeSamples() * self.BYTES_PER_SAMPLE)
        return self.__alignToCpuPage(capture_size_bytes)

    def getOfdmCaptureWindowSizebytes(self):
        capture_size_bytes = int(self.getOfdmCaptureWindowSizeSamples() * self.BYTES_PER_SAMPLE)
        return self.__alignToCpuPage(capture_size_bytes)

    def getCaptureSizePerDma(self):
        if self.integrator_mode == 'hw':
            if self.integrator_type == 'ofdm':
                return self.getOfdmCaptureWindowSizebytes()
            else:
                return self.getDwellCaptureWindowSizebytes()
        else:
            return self.getStreamSizeBytesPerDma()

    def getDdrCaptureSizeSamples(self):
        if self.integrator_mode == 'hw':
            if self.integrator_type == 'ofdm':
                return self.getOfdmCaptureWindowSizeSamples()
            else:
                return self.getDwellCaptureWindowSizeSamples()
        else:
            return self.getStreamSizeSamples()

    def getCaptureTimeForBytes(self, captureSize):
        numCaptures = 0x1
        batchSize = captureSize * numCaptures
        numSamples = batchSize / (self.BYTES_PER_SAMPLE)
        t = numSamples / self.samplingFreq
        return t
