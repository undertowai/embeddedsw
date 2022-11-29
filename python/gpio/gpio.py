import sys
import ctypes as ct

sys.path.append('../misc')

from dts import Dts
from make import Make

class Gpio:
    def __init__(self, lib, ipName):
        self.lib = lib
        self.devName = Dts().ipToDtsName(ipName)

    def set(self, val):
        fun = self.lib.AXI_Gpio_Set

        status = fun(ct.c_char_p(self.devName.encode('UTF-8')), int(val))
        assert status == 0

    def get(self):
        raise Exception('Not yet implemented')

class AxiGpio:
    def __init__(self, libName):
        libPath = Make().makeLibs(libName)
        self.lib = ct.CDLL(libPath)

    def getGpio(self, ipName):
        return Gpio(self.lib, ipName)

if __name__ == "__main__":

    axiGpio = AxiGpio('axi_gpio')

    gpio = axiGpio.getGpio('dma_sync_gpio_0')
    gpio.set(0)
    print('Pass')