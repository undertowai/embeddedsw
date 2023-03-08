
import sys, argparse
import numpy as np
import math

sys.path.append("../axi")
sys.path.append("../test")

from test_config import TestConfig
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

    def set_num_pulses_log2_samples(self, log2_samples, units_in_dwell):
        val = (int(log2_samples) & 0xffff) | ((int(units_in_dwell) & 0xffff) << 16)
        self.period_hw_ctrl.set(val=val)

class Integrator:
    def __init__(self, config):
        self.integrator_mode = config.integrator_mode
        self.integrator_type = config.integrator_type

        self.samples_in_unit = config.samples_in_unit
        self.integrator_depth = config.integrator_depth
        self.dwell_in_stream = config.dwell_in_stream
        self.units_in_dwell = config.units_in_dwell

        assert self.integrator_mode in ['sw', 'hw', 'bypass']
        assert self.integrator_type in ['dwell', 'ofdm']


        if self.integrator_mode == 'hw' and self.integrator_type == 'dwell':
            assert False, 'Current HW version doesn\'t support dwell integrator type'
            assert self.dwell_in_stream == config.HW_INTEGRATOR_WINDOW_SIZE, \
                    f'For integrator HW mode dwell_in_stream size must be {config.HW_INTEGRATOR_WINDOW_SIZE}'

        if self.integrator_type == 'ofdm':
            assert self.samples_in_unit == 512, "OFDM+CP pulse samples is hard coded to be 512 in HW integrator_mode"
            assert self.integrator_depth > 4, "integrator_depth must be higher than 4"
            assert self.units_in_dwell <= 1024*64


        if config.debug:
            print(f'Integrator settings : integrator_mode={self.integrator_mode}, \
                    samples_in_unit={self.samples_in_unit}, \
                    integrator_depth={self.integrator_depth}, \
                    dwell_in_stream={self.dwell_in_stream}')


class IntegratorHW(Integrator, IntegratorHwIf):

    def __init__(self, config):
        Integrator.__init__(self, config)
        IntegratorHwIf.__init__(self, config.debug)

    def setup(self, hw_offset_map = []):
        if self.integrator_mode == 'hw':
            periods_log2 = math.log2(self.integrator_depth)
            integrator_depth = 2 ** periods_log2

            assert integrator_depth == self.integrator_depth, "integrator_depth parameter must be equal to 2^N if integrator_mode is HW"

            self.set_num_pulses_log2_samples(periods_log2, self.units_in_dwell * self.dwell_in_stream)
        else:
            self.set_num_pulses_log2_samples(0, 0)

        self.set_offset_samples(hw_offset_map)

class IntegratorSW(Integrator):

    def __init__(self, config):
        Integrator.__init__(self, config)

    def __do_sw_integration(self, data):

        assert (self.integrator_depth % 2) == 0, "self.integrator_depth should be multiply of 2"

        data = np.asarray(data, dtype=np.int32)

        shape = (int(self.units_in_dwell / self.dwell_in_stream), int(self.samples_in_unit * self.dwell_in_stream))
        data = np.reshape(data, shape)

        data = np.mean(data, axis=0, dtype=np.int32)
        return data

    def __do_sw_integration_ofdm(self, data, samples, units, dwels, depth):
        shape = (units * dwels, depth, samples)
        data = np.reshape(data, shape)
        data = np.mean(data, axis=1, dtype=np.int32)

        return data.flatten()

    def __do_sw_integration_ofdm_wrapper(self, data):

        samples_in_stream = self.dwell_in_stream * self.samples_in_unit * self.units_in_dwell * self.integrator_depth

        data = np.asarray(data[:samples_in_stream], dtype=np.int32)

        return self.__do_sw_integration_ofdm(data, self.samples_in_unit, self.units_in_dwell, self.dwell_in_stream, self.integrator_depth)


    def test_sw_integrator_ofdm(self):
        data = np.array([0, 1, 2, 3, 0, -1, -2, -3, 0, 1, 2, 3, 4, 5, 6, 7, 4, 5, 6, 7, -4, -5, -6, -7])

        data = self.__do_sw_integration_ofdm(data, 6, 2, 1, 2)
        print(data)

    def do_integration(self, data):
        if self.integrator_mode != 'sw':
            return data
        else:
            if self.integrator_type == 'dwell':
                return self.__do_sw_integration(data)
            elif self.integrator_type == 'ofdm':
                return self.__do_sw_integration_ofdm_wrapper(data)

if __name__ == '__main__':
    argparser=argparse.ArgumentParser()

    argparser.add_argument('--cfg', help='specify test configuration file', type=str)
    argparser.add_argument('--test_ofdm', help='Do SW integrator test (OFDM)', action='store_true')
    args  = argparser.parse_args()

    assert args.cfg is not None

    print('Setting up integrator')

    test_config = TestConfig(args.cfg)

    if args.test_ofdm is not None:
        integrator = IntegratorSW(test_config)
        integrator.test_sw_integrator_ofdm()
    else:
        integrator = IntegratorHW(test_config)

        assert len(test_config.tx) == 1
        hw_del = test_config.getStreamHwOffset(test_config.tx[0])
        integrator.setup(hw_del)
    print('Done')

