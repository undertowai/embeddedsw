
import sys
from time import sleep

sys.path.append("../lmx")

from lmx import Lmx2820
from rfdc import Rfdc

class RfdcClk:
    def __init__(self):
        self.lmx = Lmx2820("axi_quad_spi_0")
        self.rfdc = Rfdc("rfdc2")

    def setup_lmx(self, ticsFilePath):

        print('Configuring LMX2820 ...')
        self.lmx.power_reset(False, 0x0)
        self.lmx.power_reset(True, 0x0)
        self.lmx.power_reset(True, 0x1)
        sleep(1)

        self.lmx.config(ticsFilePath=ticsFilePath)

        assert self.lmx.readLockedReg() == True

    def setup_rfdc(self, mts_adc = 0xf, mts_dac = 0xf):
        print('Configuring RFDC + Clk104 ...')
        self.rfdc.init_clk104()
        self.rfdc.restart()
        self.rfdc.setRFdcMTS(adc=mts_adc, dac=mts_dac)



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage : {} <lmx2820 tics file path>'.format(sys.argv[0]))

    ticsFilePath = sys.argv[1]

    rfdc_clk = RfdcClk()

    rfdc_clk.setup_lmx(ticsFilePath)
    rfdc_clk.setup_rfdc()

    print("Pass")