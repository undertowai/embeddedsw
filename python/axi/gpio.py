import sys, argparse
import ctypes as ct
import os

sys.path.append("../misc")

from dts import Dts
from make import Make
from mlock import MLock


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
        self.lib_gpio = ct.CDLL(libPath)

    def getGpio(self, ipName):
        return Gpio(self.lib_gpio, ipName)

    def getGpioId(self, ipName):
        path = Dts().ipToDtsPathAbsolute(ipName) + os.sep + 'gpio' + os.sep

        listdir = os.listdir(path)
        gpio = listdir[0].replace('gpio', '').replace('chip', '')
        gpio_id = int(gpio)
        return gpio_id

if __name__ == "__main__":

    argparser=argparse.ArgumentParser()
    argparser.add_argument('--adc_dac_sync', help='Toggle adc/dac sync', type=int)
    argparser.add_argument('--get_gpio_id', help='Get gpio id for the given ip name', type=str)

    args  = argparser.parse_args()

    axiGpio = AxiGpio("axi_gpio")

    if args.get_gpio_id is not None:
        axiGpio.getGpioId(args.get_gpio_id)

    elif args.adc_dac_sync is not None:
        gpio = axiGpio.getGpio("adc_dac_sync_gpio_0")
        gpio.set(val=args.adc_dac_sync)

    print("Pass")
