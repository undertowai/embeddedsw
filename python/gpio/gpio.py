import sys
import ctypes as ct

sys.path.append('../misc')

from dts import Dts
from make import Make

class AxiGpio:
    def __init__(self, libName):
        libPath = Make().makeLibs(libName)
        self.lib = ct.CDLL(libPath)

    def set(self, DevName, val):
        fun = self.lib.AXI_Gpio_Set

        status = fun(ct.c_char_p(DevName.encode('UTF-8')), int(val))
        assert status == 0

    def get(self, DevName):
        #Not yet
        pass

if __name__ == "__main__":

    gpio = AxiGpio('axi_gpio')
    ipName = 'dma_sync_gpio_0'
    devName = Dts().ipToDtsName(ipName)

    gpio.set(devName, 0)
    print('Pass')