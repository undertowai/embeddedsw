import sys
import os

from reg import AxiReg

class AxisSwitch(AxiReg):
    def __init__(self, ipName):
        AxiReg.__init__(self, ipName)

    def __route(self, s, m):
        offset = 0x40 + int(m * 0x4)
        self.write_reg_u32(offset, s)

    def __commit(self):
        self.write_reg_u32(0x0, 0x2)

    def route(self, s, m):
        assert len(s) == len(m)

        for i, mi in enumerate(m):
            self.__route(s[i], mi)
        self.__commit()


if __name__ == "__main__":
    axis_sw = AxisSwitch("axis_switch_0")

    axis_sw.route([0], [0])