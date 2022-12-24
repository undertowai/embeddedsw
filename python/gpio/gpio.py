import sys
import ctypes as ct

from misc.dts import Dts
from misc.make import Make
from misc.mlock import MLock

class Gpio(MLock):
    def __init__(self, lib, ipName):
        self.lib = lib
        self.devName = Dts().ipToDtsName(ipName)

        reg = Dts().readPropertyU32(ipName, "reg")
        self.addr = (reg[0] << 32) | reg[1]
        self.size = (reg[2] << 32) | reg[3]

    @MLock.Lock
    def set(self):
        fun = self.lib.AXI_Gpio_Set

        status = fun(ct.c_char_p(self.devName.encode("UTF-8")), int(self.val))
        assert status == 0

    @MLock.Lock
    def get(self):
        raise Exception("Not yet implemented")


class AxiGpio:
    def __init__(self, libName):
        libPath = Make().makeLibs(libName)
        self.lib = ct.CDLL(libPath)

    def getGpio(self, ipName):
        return Gpio(self.lib, ipName)


if __name__ == "__main__":

    axiGpio = AxiGpio("axi_gpio")

    gpio = axiGpio.getGpio("dma_sync_gpio_0")
    gpio.set(val=0)
    print("Pass")
