
import numpy as np
import math

class IntegratorHwIf:
    def __init__ (self, offset_hw_ctrl, period_hw_ctrl):
        self.offset_hw_ctrl = offset_hw_ctrl
        self.period_hw_ctrl = period_hw_ctrl
    
    def set_offset_samples(self, samples):
        self.offset_hw_ctrl.set(val=samples)

    def set_period_log2_samples(self, log2_samples):
        self.period_hw_ctrl.set(val=log2_samples)

class Integrator:

    def __init__(self, hw_if: IntegratorHwIf, mode, num_samples, num_periods, window):
        self.mode = mode
        self.num_samples = num_samples
        self.num_periods = num_periods
        self.window = window
        self.hw_if = hw_if
        
        print(f'Integrator settings : mode={mode}, num_samples={num_samples}, num_periods={num_periods} \
            window={window}')

    def setup(self):
        if self.mode == 'hw':
            periods_log2 = math.log2(self.num_periods)
            num_periods = 2 ** periods_log2

            assert num_periods == self.num_periods, "num_periods parameter must be equal to 2^N if integrator mode is HW"

            self.hw_if.set_period_log2_samples(periods_log2)
        else:
            self.hw_if.set_period_log2_samples(0)

    def __do_sw_integration(self, data):

        assert (self.num_periods % 2) == 0, "self.dwell_num should be multiply of 2"

        data = np.asarray(data, dtype=np.int32)

        shape = (int(self.num_periods / self.window), int(self.num_samples * self.window))
        data = np.reshape(data, shape)

        data = np.mean(data, axis=0, dtype=np.int32)
        return data

    def do_integration(self, data):
        if self.mode == 'hw':
            return data
        else:
            return self.__do_sw_integration(data)