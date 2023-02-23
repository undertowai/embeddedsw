
import sys
import numpy as np
import math

sys.path.append("../axi")

from gpio import AxiGpio

class IntegratorHwIf(AxiGpio):
    def __init__ (self, debug=False):
        AxiGpio.__init__(self, 'axi_gpio')
        self.period_hw_ctrl = self.getGpio("axi_gpio_axis_dwell_ctrl")
        self.debug = debug

        self.offset_hw_ctrl_0 = self.getGpio("axis_dwell_proc_0_axi_gpio_offset_ctrl")
        self.offset_hw_ctrl_1 = self.getGpio("axis_dwell_proc_0_axi_gpio_offset_ctrl1")

    def set_offset_samples(self, hw_offset_map):
        assert len(hw_offset_map) == 8

        val0  = (int(hw_offset_map[0]) << 0) | (int(hw_offset_map[1]) << 16)
        val1  = (int(hw_offset_map[2]) << 0) | (int(hw_offset_map[3]) << 16)
        val2  = (int(hw_offset_map[4]) << 0) | (int(hw_offset_map[5]) << 16)
        val3  = (int(hw_offset_map[6]) << 0) | (int(hw_offset_map[7]) << 16)

        if self.debug:
            print(f'HW offset map ={hw_offset_map}')
            print(f'HW offset config : {hex(val0)}, {hex(val1)}, {hex(val2)}, {hex(val3)}')

        self.offset_hw_ctrl_0.set(val=val0, val2=val1)
        self.offset_hw_ctrl_1.set(val=val2, val2=val3)

    def set_period_log2_samples(self, log2_samples):
        self.period_hw_ctrl.set(val=log2_samples)

class Integrator(IntegratorHwIf):

    def __init__(self, mode, num_samples, num_periods, window, debug=False):
        IntegratorHwIf.__init__(self, debug)
        self.mode = mode
        self.num_samples = num_samples
        self.num_periods = num_periods
        self.window = window
        self.integrator_type = 'ofdm'

        if self.debug:
            print(f'Integrator settings : mode={mode}, num_samples={num_samples}, num_periods={num_periods} window={window}')

    def setup(self, hw_offset_map = []):
        if self.mode == 'hw':
            periods_log2 = math.log2(self.num_periods)
            num_periods = 2 ** periods_log2

            assert num_periods == self.num_periods, "num_periods parameter must be equal to 2^N if integrator mode is HW"

            self.set_period_log2_samples(periods_log2)
        else:
            self.set_period_log2_samples(0)

        self.set_offset_samples(hw_offset_map)

    def __do_sw_integration(self, data):

        assert (self.num_periods % 2) == 0, "self.dwell_num should be multiply of 2"

        data = np.asarray(data, dtype=np.int32)

        shape = (int(self.num_periods / self.window), int(self.num_samples * self.window))
        data = np.reshape(data, shape)

        data = np.mean(data, axis=0, dtype=np.int32)
        return data

    def __do_sw_integration_ofdm(self, data):

        num_samples_in_ofdm = 512
        num_ofdm_periods = 64
        num_periods = data.size // (num_samples_in_ofdm * num_ofdm_periods)

        data = np.asarray(data, dtype=np.int32)

        shape = (num_periods, num_ofdm_periods, num_samples_in_ofdm)
        data = np.reshape(data, shape)
        data = np.mean(data, axis=1, dtype=np.int32)

        return data.flatten()

    def do_integration(self, data):
        if self.mode != 'sw':
            return data
        else:
            if self.integrator_type == 'dwell':
                return self.__do_sw_integration(data)
            elif self.Integrator_type == 'ofdm':
                return self.__do_sw_integration_ofdm(data)