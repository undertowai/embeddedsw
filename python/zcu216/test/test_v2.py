import os

from zcu216.rfdc.rfdc_clk import RfdcClk
from zcu216.axi.gpio import AxiGpio

    

class TestV2():

    def __init__(self):
        self.AxiGpio = AxiGpio("axi_gpio");
        self.RfdcClk = RfdcClk()

        self.RfdcClk.setup_rfdc()

        print("Test init done\n")
        return None

    
if __name__ == "__main__":

    test = TestV2();



    exit(0)


