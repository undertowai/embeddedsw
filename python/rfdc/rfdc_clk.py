
import sys, argparse
from time import sleep
import json

sys.path.append("../lmx")

from lmx import Lmx2820
from rfdc import Rfdc
from TICS import read as TICSread

def load_json(path):
    with open(path, 'r') as f:
        j = json.load(f)
        f.close()
    return j

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

    def setup_rfdc_external(self, lmk_path, lmx_rf1_path, lmx_rf2_path):
        lmk_data = TICSread(lmk_path) if lmk_path is not None else None
        lmx_rf1_data = TICSread(lmx_rf1_path) if lmx_rf1_path is not None else None
        lmx_rf2_data = TICSread(lmx_rf2_path) if lmx_rf2_path is not None else None

        self.rfdc.init_clk104_External(lmk_data, lmx_rf1_data, lmx_rf2_data)

    def setup_clk104(self, lmk_path=None, lmx_rf1_path=None, lmx_rf2_path=None):

        print('Configuring CLK104 ...')

        if lmk_path is None and lmx_rf1_path is None and lmx_rf2_path is None:
            self.rfdc.init_clk104()
        else:
            self.setup_rfdc_external(lmk_path, lmx_rf1_path, lmx_rf2_path)

    def setup_rfdc(self, mts_adc = 0xf, mts_dac = 0xf, adc_ref=0, dac_ref=0):
        print('Configuring RFDC ...')
        self.rfdc.restart()
        self.rfdc.setRFdcMTS(adc=mts_adc, dac=mts_dac, adc_ref=adc_ref, dac_ref=dac_ref)



if __name__ == "__main__":

    argparser=argparse.ArgumentParser()

    argparser.add_argument('--cfg', help='specify config.json used for setup', type=str)
    argparser.add_argument('--lmx2820', help='specify LMX2820 configuration file', type=str)


    argparser.add_argument('--lmk', help='specify LMK configuration file', type=str)
    argparser.add_argument('--lmx_rf1', help='specify LMX RF1 configuration file', type=str)
    argparser.add_argument('--lmx_rf2', help='specify LMX RF2 configuration file', type=str)

    args  = argparser.parse_args()

    adc_dac_hw_loppback = False

    if args.cfg is not None:
        config = load_json(args.cfg)
        adc_dac_hw_loppback = config['adc_dac_hw_loppback']

    rfdc_clk = RfdcClk()

    rfdc_clk.setup_clk104(args.lmk, args.lmx_rf1, args.lmx_rf2)
    rfdc_clk.setup_rfdc()

    if args.lmx2820 is not None and adc_dac_hw_loppback == False:
        rfdc_clk.setup_lmx(args.lmx2820)
    else:
        print(f'Skip LMX2820 configuration: adc_dac_hw_loppback={adc_dac_hw_loppback}')

    print("Pass")