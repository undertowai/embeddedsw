import sys
import ctypes as ct
import numpy as np
from numpy.ctypeslib import ndpointer

from TICS import read as TICSread 
from TICS import generateDummy as TICSdummy

class SharedObject:
    def __init__(self, libPath, devName):
        self.libPath = libPath
        self.devName = devName

        self.__loadSo()

    def __loadSo(self):
        self.lib = ct.CDLL(self.libPath)


class Lmx(SharedObject):
    def __init__(self, libPath, devName):
        super().__init__(libPath, devName)
        self.RF_DATA_READ_BIT = 0x80

    def setMuxOut(self, lmxData):
        for i, d in enumerate(lmxData):
            if ((d >> 16) & 0x7f) == 0:
                lmxData[i] = lmxData[i] & (~(1 << 2))

    def writeData(self, data):
        fun  = self.lib.SpiSendData

        status = fun(ct.c_char_p(self.devName.encode('UTF-8')), int(0), int(3), ct.c_void_p(data.ctypes.data), int(data.size))
        assert status == 0

    def readData(self, data):
        fun  = self.lib.SpiRecvData

        status = fun(ct.c_char_p(self.devName.encode('UTF-8')), int(0), int(3), ct.c_void_p(data.ctypes.data), int(data.size), self.RF_DATA_READ_BIT)
        assert status == 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('{}: Usage'.format(sys.argv[0]))
        exit()

    libPath = sys.argv[1]
    devName = sys.argv[2]
    ticsFilePath = sys.argv[3]

    #TODO:
    devName = devName.split('/')[2].split('@')
    devName = devName[1] + '.' + devName[0]

    lmx = Lmx(libPath, devName)

    expData = TICSread(ticsFilePath)

    gotData = np.empty(expData.size, dtype=np.uint32)
    lmx.setMuxOut(expData)
    lmx.writeData(expData)
    lmx.readData(gotData)

    for i, d in enumerate(expData):
        if expData[i] != gotData[i]:
            print("Data doesn't match: i={} : exp={}, got={}".format(i, hex(expData[i]), hex(gotData[i])))
            raise Exception
            


