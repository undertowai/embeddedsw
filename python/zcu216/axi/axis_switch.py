import sys
import os

from zcu216.misc.dts import Dts

class AxisSwitch:
    def __init__(self, ipName):
        reg = Dts().readPropertyU32(ipName, "reg")

        self.address = (reg[0] << 32) | reg[1]
        self.length = (reg[2] << 32) | reg[3]

    def __write_reg(self, offset, value):
        os.system('devmem {} 32 {}'.format(hex(offset), hex(value)))

    def __route(self, s, m):
        offset = 0x40 + int(m * 0x4)
        self.__write_reg(self.address + offset, s)

    def __commit(self):
        self.__write_reg(self.address, 0x2)

    def route(self, s, m):
        assert len(s) == len(m)
        
        for i, mi in enumerate(m):
            self.__route(s[i], mi)
        self.__commit()


if __name__ == "__main__":
    axis_sw = AxisSwitch("axis_switch_0")
    
    axis_sw.route([0], [0])