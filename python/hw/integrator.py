
import sys, argparse
import numpy as np
import math

sys.path.append("../axi")
sys.path.append("../test")

from test_config import TestConfig
from reg import AxiReg

class IntegratorHwIf(AxiReg):
    def __init__ (self, debug=False):
        AxiReg.__init__(self, 'axis_dwell_proc_0_axi_bram_ctrl_int_regs_0')
        self.debug = debug

    def readParameters(self, id):
        base_addr = int(id) << 8
        val = self.read_reg_u32(base_addr + 0x8)
        beats_in_unit_max = val & 0xffff
        depth_log2_max = (val >> 16) & 0xffff
        return (beats_in_unit_max, depth_log2_max)

    def checkHwType(self):
        hwType = self.read_reg_u32(0xc) & 0x3
        assert hwType == 0x1

    def checkConfig(self, id, offset, beats_in_unit, ofdm_pulses, depth_log2):
        beats_in_unit_max, depth_log2_max = self.readParameters(id)

        assert beats_in_unit <= beats_in_unit_max, f'beats_in_unit {hex(beats_in_unit)} > beats_in_unit_max {hex(beats_in_unit_max)}'
        assert depth_log2 <= depth_log2_max
        assert ofdm_pulses <= 1024 * 64
        assert offset <= 1024 * 64

    def writeConfig(self, id, offset, beats_in_unit, ofdm_pulses, depth_log2):
        offset = int(offset)
        beats_in_unit = int(beats_in_unit)
        ofdm_pulses = int(ofdm_pulses)
        depth_log2 = int(depth_log2)

        if (self.debug):
            print(f'integrator.writeConfig: id={id}, beats_in_unit={beats_in_unit}, ofdm_pulses={ofdm_pulses}, depth_log2={depth_log2}')

        base_addr = int(id) << 8
        self.write_reg_u32( base_addr + 0x0, offset | (beats_in_unit << 16) )
        self.write_reg_u32( base_addr + 0x4, ofdm_pulses | (depth_log2 << 16) )

    def writeConfigAll(self, hw_offset_map, beats_in_unit, ofdm_pulses, depth_log2):
        assert len(hw_offset_map) == 8
        self.checkConfig(0, hw_offset_map[0], beats_in_unit, ofdm_pulses, depth_log2)

        for i, hw_offset in enumerate(hw_offset_map):
            self.writeConfig(i*2, hw_offset, beats_in_unit, ofdm_pulses, depth_log2)
            self.writeConfig(i*2 + 1, hw_offset, beats_in_unit, ofdm_pulses, depth_log2)

    def readConfig(self):
        pass

class Integrator:
    def __init__(self, config):
        self.integrator_mode = config.integrator_mode
        self.integrator_type = config.integrator_type

        self.samples_in_unit = config.samples_in_unit
        self.integrator_depth = config.integrator_depth
        self.dwell_in_stream = config.dwell_in_stream
        self.units_in_dwell = config.units_in_dwell
        self.samples_in_beat = config.SAMPLES_PER_FLIT

        assert self.integrator_mode in ['sw', 'hw', 'bypass']
        assert self.integrator_type in ['dwell', 'ofdm']

        if self.integrator_mode == 'hw' and self.integrator_type == 'dwell':
            assert False, 'Current HW version doesn\'t support dwell integrator type'
            assert self.dwell_in_stream == config.HW_INTEGRATOR_WINDOW_SIZE, \
                    f'For integrator HW mode dwell_in_stream size must be {config.HW_INTEGRATOR_WINDOW_SIZE}'

        if config.debug:
            print(f'Integrator settings : integrator_mode={self.integrator_mode}, \
                    samples_in_unit={self.samples_in_unit}, \
                    integrator_depth={self.integrator_depth}, \
                    dwell_in_stream={self.dwell_in_stream}')


class IntegratorHW(Integrator, IntegratorHwIf):

    def __init__(self, config):
        Integrator.__init__(self, config)
        IntegratorHwIf.__init__(self, config.debug)

    def setup(self, hw_offset_map):
        if self.integrator_mode not in ['hw']:
            self.writeConfigAll([0, 0, 0, 0, 0, 0, 0, 0], 0, 0, 0)
        else:
            periods_log2 = math.log2(self.integrator_depth)
            integrator_depth = 2 ** periods_log2
            beats_in_unit = self.samples_in_unit // self.samples_in_beat

            assert (int(self.samples_in_unit) % self.samples_in_beat) == 0, f'samples_in_unit must be multiply of {self.samples_in_beat}'
            assert integrator_depth == self.integrator_depth, "IntegratorHW: integrator_depth parameter must be equal to 2^N if integrator_mode is HW"

            self.checkHwType()
            self.writeConfigAll(hw_offset_map, beats_in_unit, self.units_in_dwell * self.dwell_in_stream, periods_log2)

    def do_integration(self, data):
        return data

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

    def do_integration(self, data):
        assert self.integrator_mode in ['sw', 'bypass'],  "IntegratorHW: Incorrect mode, must be SW/Bypass"

        if self.integrator_mode == 'bypass':
            return data

        if self.integrator_type == 'dwell':
            return self.__do_sw_integration(data)
        elif self.integrator_type == 'ofdm':
            return self.__do_sw_integration_ofdm_wrapper(data)

    def test_sw_integrator_ofdm(self):
        data = np.array([0, 1, 2, 3, 0, -1, -2, -3, 0, 1, 2, 3, 4, 5, 6, 7, 4, 5, 6, 7, -4, -5, -6, -7])

        data = self.__do_sw_integration_ofdm(data, 6, 2, 1, 2)
        print(data)

if __name__ == '__main__':
    argparser=argparse.ArgumentParser()

    argparser.add_argument('--cfg', help='specify test configuration file', type=str)
    argparser.add_argument('--test_ofdm', help='Do SW integrator test (OFDM)', action='store_true')
    args  = argparser.parse_args()

    assert args.cfg is not None

    print('Setting up integrator')

    test_config = TestConfig(args.cfg)

    if args.test_ofdm is True:
        integrator = IntegratorSW(test_config)
        integrator.test_sw_integrator_ofdm()
    else:
        integrator = IntegratorHW(test_config)

        hw_del = test_config.getStreamHwOffset(test_config.tx[0])
        integrator.setup(hw_del)
    print('Done')

