
from hmc import HMC63xx

if __name__ == "__main__":

    hmc = HMC63xx("spi_gpio")

    hmc.GpioInit()
    hmc.Reset()

    print("Pass")