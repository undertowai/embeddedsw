import sys
import ctypes as ct
import numpy as np

from lmx import Lmx2820

sys.path.append('../misc')

from dts import Dts

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('{}: Usage'.format(sys.argv[0]))
        exit()

    libPath = sys.argv[1]
    ipName = sys.argv[2]
    ticsFilePath = sys.argv[3]

    devName = Dts().ipToDtsName(ipName)

    lmx = Lmx2820(libPath, devName)
    expData = lmx.loadTICS(ticsFilePath)

    gotData = np.empty(expData.size, dtype=np.uint32)
    lmx.setMuxOut(expData)
    lmx.writeData(expData)
    lmx.readData(gotData)

    expData = np.flip(expData, 0)

    lmx.checkConfig(expData, gotData)

    LD = lmx.getPllStatus(gotData)
    if LD != 0x2:
        raise Exception('PLL is not locked')