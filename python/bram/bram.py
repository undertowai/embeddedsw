import sys
import ctypes as ct
import numpy as np

sys.path.append('../misc')

from dts import Dts
from make import Make

class Bram:
    PAGE_SIZE = 128

    def __init__(self, lib, devName, size):
        self.size = size
        self.lib = lib
        self.devName = devName

    def writeData(self, data, address=0):
        fun = self.lib.AXI_Bram_Write

        status = fun(ct.c_char_p(self.devName.encode('UTF-8')), int(address), ct.c_void_p(data.ctypes.data), int(data.size))
        assert status == 0

    def readData(self, data, address=0):
        fun = self.lib.AXI_Bram_Read

        status = fun(ct.c_char_p(self.devName.encode('UTF-8')), int(address), ct.c_void_p(data.ctypes.data), int(data.size))
        assert status == 0

    def load(self, data):

        assert data.size <= self.size

        self.writeData(data)
        gotData = np.empty(data.size, dtype=data.dtype)
        self.readData(gotData)
        self.compare(data, gotData)
        return data.size

    def loadFromFile(self, path, dtype):
        data = np.fromfile(path, dtype=dtype)
        return self.load(data)

    def compare(self, expData, gotData):
        for i, d in enumerate(expData):
            if gotData[i] != d:
                raise Exception("Data doesn't match got: {} != exp: {}".format(gotData[i], d))

class BramFactory:
    def __init__(self):
        libPath = Make().makeLibs('bram2')
        self.lib = ct.CDLL(libPath)

    def makeBram(self, ipName):
        devName = Dts().ipToDtsName(ipName)
        reg = Dts().readPropertyU32(ipName, 'reg')
        size = (reg[2] << 32) | reg[3]

        return Bram(self.lib, devName, size)


if __name__ == "__main__":
    if len(sys.argv) != 1:
        print('{}: Usage'.format(sys.argv[0]))
        exit()

    ipName ='ram_player_8wide_0_axi_bram_ctrl_0'

    bram = BramFactory('bram2')
    bram = bram.makeBram(ipName)

    expData = np.random.randint(0, 255, (bram.PAGE_SIZE, 1), dtype=np.uint8)
    gotData = np.empty(bram.PAGE_SIZE, dtype=np.uint8)

    bram.writeData(expData)
    bram.readData(gotData)

    bram.compare(expData, gotData)

    print("Pass")