import sys
import ctypes as ct
import numpy as np

from misc.dts import Dts
from misc.make import Make
from misc.mlock import MLock

class Bram(MLock):
    PAGE_SIZE = 128

    def __init__(self, lib, devName, size):
        self.size = size
        self.lib = lib
        self.devName = devName

    def __writeData(self, data, address=0):
        fun = self.lib.AXI_Bram_Write

        status = fun(
            ct.c_char_p(self.devName.encode("UTF-8")),
            int(address),
            ct.c_void_p(data.ctypes.data),
            int(data.size),
        )
        assert status == 0

    def __readData(self, data, address=0):
        fun = self.lib.AXI_Bram_Read

        status = fun(
            ct.c_char_p(self.devName.encode("UTF-8")),
            int(address),
            ct.c_void_p(data.ctypes.data),
            int(data.size),
        )
        assert status == 0

    def __compare(self, expData, gotData):
        for i, d in enumerate(expData):
            if gotData[i] != d:
                raise Exception(
                    "Data doesn't match i={}; got: {} != exp: {}".format(
                        i, gotData[i], d
                    )
                )

    @MLock.Lock
    def load(self):

        data = self.data
        data = data.view(dtype=np.uint32)

        assert int(data.size * 4) <= self.size

        self.__writeData(data)
        gotData = np.empty(data.size, dtype=data.dtype)
        self.__readData(gotData)
        self.__compare(data, gotData)
        return data.size

    def loadFromFile(self, path, dtype):
        data = np.fromfile(path, dtype=dtype)
        return self.load(data=data)

    def getSize(self):
        return self.size


class BramFactory:
    def __init__(self):
        libPath = Make().makeLibs("bram2")
        self.lib = ct.CDLL(libPath)

    def makeBram(self, ipName):
        devName = Dts().ipToDtsName(ipName)
        reg = Dts().readPropertyU32(ipName, "reg")
        size = (reg[2] << 32) | reg[3]

        return Bram(self.lib, devName, size)


if __name__ == "__main__":
    if len(sys.argv) != 1:
        print("{}: Usage".format(sys.argv[0]))
        exit()

    ipName = "ram_player_8wide_0_axi_bram_ctrl_0"

    bram = BramFactory()
    bram = bram.makeBram(ipName)

    expData = np.random.randint(0, 255, (bram.PAGE_SIZE, 1), dtype=np.uint8)

    bram.load(data=expData)

    print("Pass")
