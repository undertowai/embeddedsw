import sys
import ctypes as ct
import numpy as np
import json

sys.path.append("../misc")

from make import Make
from mlock import MLock

def load_json(path):
    with open(path, 'r') as f:
        j = json.load(f)
        f.close()
    return j

class Rfdc(MLock):
    def __init__(self, libName):
        libPath = Make().makeLibs(libName)
        self.lib = ct.CDLL(libPath)

    def init_clk104_External(self, lmk_data, lmx_rf1_data, lmx_rf2_data):
        fun = self.lib.RFDC_Init_Clk104_External

        status = fun(
            ct.c_void_p(lmk_data.ctypes.data) if lmk_data is not None else None,
            int(lmk_data.size) if lmk_data is not None else 0,

            ct.c_void_p(lmx_rf1_data.ctypes.data) if lmx_rf1_data is not None else None,
            int(lmx_rf1_data.size) if lmx_rf1_data is not None else 0,

            ct.c_void_p(lmx_rf2_data.ctypes.data) if lmx_rf2_data is not None else None,
            int(lmx_rf2_data.size) if lmx_rf2_data is not None else 0
        )
        assert status == 0

    def reset_clk104(self):
        fun = self.lib.resetAllClk104

        status = fun()
        assert status == 0

    def init_clk104(self):
        fun = self.lib.RFDC_Init_Clk104

        status = fun()
        assert status == 0

    @MLock.Lock
    def restart(self):
        fun = self.lib.RFDC_Restart

        status = fun()
        assert status == 0

    @MLock.Lock
    def getSamplingFrequency(self):
        fun = self.lib.RFDC_GetSamplingFreq

        freq = fun()
        assert freq > 0

        return int(freq * 1_000_000)
    
    @MLock.Lock
    def setRFdcMTS(self):
        fun = self.lib.RFdcMTS
        
        status = fun(int(self.adc), int(self.dac), int(self.adc_ref), int(self.dac_ref))
        assert status == 0

    @MLock.Lock
    def __readReg(self):
        fun = self.lib.RFDC_ReadReg
        val = ct.c_int()

        status = fun(int(self.base_addr), int(self.reg_addr), ct.byref(val))
        assert status == 0
        
        return val

    @MLock.Lock
    def __readRegAll(self):
        fun = self.lib.RFDC_ReadRegRange

        reg_map = load_json('./rfdc_reg_map.json')

        rlist = [ int(reg, 16) for reg in reg_map['ip'] ]
        rlist.append(0xffffffff)

        regs = np.asarray( rlist, dtype=np.uint32 )
        data = np.empty(regs.size, dtype=np.uint32)

        status = fun(int(0x0), ct.c_void_p(regs.ctypes.data), ct.c_void_p(data.ctypes.data))
        assert status == 0

        return [ (reg_map['ip'][reg], int(reg, 16), data[i]) for i, reg in enumerate(reg_map['ip'])]

    @MLock.Lock
    def __readTileReg(self):
        fun = self.lib.RFDC_ReadReg
        val = ct.c_int()

        tile_id = self.tile_id
        assert tile_id <= 0x3, "Incorrect Tile ID"

        reg_map = load_json('./rfdc_reg_map.json')

        tile_name = f'{"RF-DAC" if self.is_dac else "RF-ADC"} Tile {tile_id}'
        base_addr = int(reg_map['tiles'][tile_name], 16)

        status = fun(int(base_addr), int(self.reg_addr), ct.byref(val))
        assert status == 0

        return val

    def __bp_to_mask(self, bp):
        return (1<<(bp+1)) - 1

    def __getMask(self, string):
        mask = 0x0
        for b in string.split(','):
            bits = b.split(':')
            hi = int(bits[0])
            lo = int(bits[1])

            mask |= self.__bp_to_mask(hi) ^ self.__bp_to_mask(lo) | (1<<lo)
        return mask

    def __procRegs(self, tile_reg_map, data):
        regs = []
        for i, reg in enumerate(tile_reg_map):
            name = tile_reg_map[reg]['name']
            reg_data = data[i]
            reg_addr = int(reg, 16)
            bits = []
            if 'bits' in tile_reg_map[reg]:
                for b in tile_reg_map[reg]['bits']:
                    mask = self.__getMask(tile_reg_map[reg]['bits'][b])
                    val = reg_data & mask
                    bits.append( (b, val) )
            regs.append( (name, reg_addr, reg_data, bits) )
        return regs

    @MLock.Lock
    def __readTileRegAll(self):
        fun = self.lib.RFDC_ReadRegRange

        tile_id = self.tile_id
        assert tile_id <= 0x3, "Incorrect Tile ID"

        reg_map = load_json('./rfdc_reg_map.json')
        tile_reg_map = load_json('./rfdc_tile_reg_map.json')

        rlist = [ int(reg, 16) for reg in tile_reg_map ]
        rlist.append(0xffffffff)

        regs = np.asarray( rlist, dtype=np.uint32 )
        data = np.empty(regs.size, dtype=np.uint32)

        tile_name = f'{"RF-DAC" if self.is_dac else "RF-ADC"} Tile {tile_id}'
        base_addr = int(reg_map['tiles'][tile_name], 16)

        status = fun(int(base_addr), ct.c_void_p(regs.ctypes.data), ct.c_void_p(data.ctypes.data))
        assert status == 0

        return self.__procRegs(tile_reg_map, data)

    def readReg(self, base_addr, reg_addr):
        return self.__readReg(base_addr=base_addr, reg_addr=reg_addr)

    def readADCTileReg(self, tile_id, reg_addr):
        return self.__readTileReg(tile_id=tile_id, reg_addr=reg_addr, is_dac=False)

    def readDACTileReg(self, tile_id, reg_addr):
        return self.__readTileReg(tile_id=tile_id, reg_addr=reg_addr, is_dac=True)

    def readADCTileRegAll(self, tile_id):
        return self.__readTileRegAll(tile_id=tile_id, is_dac=False)

    def readDACTileRegAll(self, tile_id):
        return self.__readTileRegAll(tile_id=tile_id, is_dac=True)

    def readRegAll(self):
        return self.__readRegAll()

    def read_Common_Interrupt_Status_Register(self):
        return self.readReg(0x100, 0x0)

    def print_Common_Interrupt_Status_Register(self):
        val = self.read_Common_Interrupt_Status_Register()

        print(f'AXI timeout interrupt: {val & (0x1 << 31)}')
        print(f'ADC Tile 0..3 interrupts : {val & 0xf0}')
        print(f'DAC Tile 0..3 interrupts : {val & 0xf}')

if __name__ == "__main__":
    rfdc = Rfdc("rfdc2")
    # rfdc.init_clk104()
    # rfdc.restart()
    freq = rfdc.getSamplingFrequency()
    print(freq)

    print("Pass")
