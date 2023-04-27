import sys
import os
import subprocess

sys.path.append("../misc")

from dts import Dts

class AxiReg:
    def __init__(self, ipName):
        reg = Dts().readPropertyU32(ipName, "reg")

        self.address = (reg[0] << 32) | reg[1]
        self.length = (reg[2] << 32) | reg[3]

    def write_reg_u32(self, offset, value):
        offset += self.address
        os.system(f'devmem {hex(offset)} 32 {hex(value)}')

    def read_reg_u32(self, offset) -> int:
        offset += self.address
        out = subprocess.check_output(f'devmem {hex(offset)}', shell=True)
        return int(out, 16)
