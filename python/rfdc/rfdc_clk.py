
import sys, argparse
import json

sys.path.append("../lmx")

from rfdc import Rfdc
from TICS import read as TICSread

def load_json(path):
    with open(path, 'r') as f:
        j = json.load(f)
        f.close()
    return j

class RfdcClk:
    def __init__(self):
        self.rfdc = Rfdc("rfdc2")

    def init_clk104_External(self, lmk_path, lmx_rf1_path, lmx_rf2_path):
        lmk_data = TICSread(lmk_path) if lmk_path is not None else None
        lmx_rf1_data = TICSread(lmx_rf1_path) if lmx_rf1_path is not None else None
        lmx_rf2_data = TICSread(lmx_rf2_path) if lmx_rf2_path is not None else None

        self.rfdc.init_clk104_External(lmk_data, lmx_rf1_data, lmx_rf2_data)

    def init_clk104(self, lmk_path=None, lmx_rf1_path=None, lmx_rf2_path=None):

        print('Configuring CLK104 ...')

        self.rfdc.reset_clk104()
        if lmk_path is None and lmx_rf1_path is None and lmx_rf2_path is None:
            self.rfdc.init_clk104()
        else:
            self.init_clk104_External(lmk_path, lmx_rf1_path, lmx_rf2_path)

    def setup_rfdc(self, dac_ref=0):
        print('Configuring RFDC :')
        print('Restarting RFDC..')
        self.rfdc.restart()
        self.setup_mts()
        print('Configuring RFDC DIther..')
        tiles = [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]]
        self.rfdc.setRFdcDither(tiles=tiles, mode=1)

    def setup_mts(self, mts_adc = 0xf, mts_dac = 0xf, adc_ref=0, dac_ref=0):
        print('Configuring RFDC MTS..')
        self.rfdc.setRFdcMTS(adc=mts_adc, dac=mts_dac, adc_ref=adc_ref, dac_ref=dac_ref)


if __name__ == "__main__":

    argparser=argparse.ArgumentParser()

    argparser.add_argument('--lmk', help='specify LMK configuration file', type=str)
    argparser.add_argument('--lmx_rf1', help='specify LMX RF1 configuration file', type=str)
    argparser.add_argument('--lmx_rf2', help='specify LMX RF2 configuration file', type=str)

    argparser.add_argument('--rfdc', help='Init RFDC', action='store_true')
    argparser.add_argument('--rfdc_mts', help='Init RFDC MTS', action='store_true')
    argparser.add_argument('--clk_104', help='Init CLK 104', action='store_true')

    argparser.add_argument('--dump_adc', help='Dump reg file from <N> TIle according to the rfdc_tile_reg_map.json', type=int)
    argparser.add_argument('--dump_dac', help='Dump reg file from <N> TIle according to the rfdc_tile_reg_map.json', type=int)
    argparser.add_argument('--dump_ip', help='Dump rfdc reg file according to rfdc_reg_map.json', action='store_true')

    args  = argparser.parse_args()

    rfdc_clk = RfdcClk()

    if args.dump_ip is not False:
        print('Dumping rfdc IP:')
        regs = rfdc_clk.rfdc.readRegAll()
        for name, addr, val in regs:
            print(f'{hex(addr)} = {hex(val)}: {name}')

    elif args.dump_adc is not None:
        print(f'Dumping RFDC ADC tile{args.dump_adc}: ')
        regs = rfdc_clk.rfdc.readADCTileRegAll(args.dump_adc)
        for name, addr, val, bits in regs:
            print(f'{hex(addr)} = {hex(val)}: {name}')
            for b, val in bits:
                print(f'\t{hex(val)}: {b}')

    elif args.dump_dac is not None:
        print(f'Dumping RFDC DAC tile{args.dump_dac}: ')
        regs = rfdc_clk.rfdc.readDACTileRegAll(args.dump_dac)
        for name, addr, val, bits in regs:
            print(f'{hex(addr)} = {hex(val)}: {name}')
            for b, val in bits:
                print(f'\t{hex(val)}: {b}')

    else:

        if args.clk_104 == True:
            rfdc_clk.init_clk104(args.lmk, args.lmx_rf1, args.lmx_rf2)

        if args.rfdc == True:
            rfdc_clk.setup_rfdc()

        if args.rfdc_mts == True:
            rfdc_clk.setup_mts()

    print("Pass")