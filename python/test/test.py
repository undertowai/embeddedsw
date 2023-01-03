import os
import sys
from time import sleep
import traceback
import logging
import pickle
import time

sys.path.append("../lmx")
sys.path.append("../hmc")
sys.path.append("../axi")
sys.path.append("../rfdc")
sys.path.append("../xddr")
sys.path.append("../dac")
sys.path.append("../misc")

from lmx import Lmx2820
from hmc import HMC63xx
from axidma import AxiDma
from xddr import Xddr
from rfdc import Rfdc
from gpio import AxiGpio
from axis_switch import AxisSwitch

from hw import Hw
from inet import Inet


class TestSuite(AxiGpio):
    def getargs(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    def Test(func):
        def inner(self, **kw):
            try:
                self.getargs(**kw)
                func(self)
            except Exception as e:
                logging.error(traceback.format_exc())
                print("=== FAILED ===")
                self.shutdown_RF()
            else:
                print("=== PASS ===")

        return inner

    def __init__(self):
        AxiGpio.__init__(self, 'axi_gpio')
        self.hw = Hw()

        self.lmx = Lmx2820("axi_quad_spi_0")
        self.hmc = HMC63xx("spi_gpio")
        self.dma = AxiDma("axidma")
        self.ddr0 = Xddr("ddr4_0")
        self.ddr1 = Xddr("ddr4_1")
        self.rfdc = Rfdc("rfdc2")
        self.axis_switch0 = AxisSwitch("axis_switch_0")
        self.axis_switch1 = AxisSwitch("axis_switch_1")

        self.gpio_sync = self.getGpio("adc_dac_sync_gpio_0")
        self.gpio_flush = self.getGpio("adc_dac_flush_gpio_0")

        self.set_loobback(False)

        self.samplingFreq = self.rfdc.getSamplingFrequency()

    def set_loobback(self, loopback):
        self.axis_switch0.route(s=[0 if loopback else 1], m=[0])
        self.axis_switch1.route(s=[0 if loopback else 1], m=[0])

    def mkdir(self, outputDir, suffix):
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)

        outputDir = "{}/TX_{}".format(outputDir, suffix)
        if not os.path.exists(outputDir):
            os.mkdir(outputDir)

        return outputDir

    def map_id_to_cap_name(self, id):
        return "cap{}_{}.bin".format("I" if id % 2 == 0 else "Q", int(id / 2))

    def map_rx_to_dma_id(self, rx_in):
        ids0 = []
        ids1 = []
        for rx in rx_in:
            if rx > 3:
                ids1.extend([rx * 2, rx * 2 + 1])
            else:
                ids0.extend([rx * 2, rx * 2 + 1])

        return ids0, ids1

    def setup_RF_Clk(self, ticsFilePath, restart_rfdc=True):

        if restart_rfdc:
            self.rfdc.restart()

        print("Configuring RF clocks ...")
        self.rfdc.init_clk104()

        self.lmx.power_reset(False, 0x0)
        self.lmx.power_reset(True, 0x0)
        self.lmx.power_reset(True, 0x1)
        sleep(1)

        self.lmx.config(ticsFilePath=ticsFilePath)

        assert self.lmx.readLockedReg() == True

    def setup_RF(self, hmc_6300_ics, hmc_6301_ics):
        self.hmc.GpioInit()
        for ic in hmc_6300_ics:
            self.hmc.DefaultConfig_6300(ic=ic)

        for ic in hmc_6301_ics:
            self.hmc.DefaultConfig_6301(ic=ic)

    def shutdown_RF(self):
        self.hmc.Reset()

    def adc_dac_sync(self, sync):
        if sync:
            self.gpio_flush.set(val=0x00)
            self.gpio_sync.set(val=0xff)
        else:
            self.gpio_flush.set(val=0xff)
            #Use approximate time to flush the FIFO
            sleep(self.calc_capture_time(512))
            self.gpio_sync.set(val=0x00)

    def __start_dma(self, ddr, ids, offset, size):

        base_address = ddr.base_address() + offset
        addr = base_address

        data = []
        for id in ids:
            data.append((addr, size))
            devName = self.dma.devIdToIpName(id)

            self.dma.startTransfer(devName=devName, addr=addr, len=size)
            addr = addr + size
        return data

    def __write_cap_data(self, path, data):
        with open(path, "wb") as f:
            f.write(data)
            f.close()

    def collect_captures_from_ddr(self, ddr, outputdir, paths, offset, size):
        base_address = ddr.base_address() + offset

        addr = base_address
        for path in paths:
            outputPath = outputdir + "/" + path
            data = ddr.capture(addr, size)
            if outputPath is not None:
                self.__write_cap_data(outputPath, data)
            addr = addr + size

    def publish(self, area, sn, freq, fs):
        for a in area:
            for j in range(0, len(a), 2):
                addrI, sizeI = a[j]
                addrQ, sizeQ = a[j + 1]
                bytesI = Xddr.read(addrI, sizeI)
                bytesQ = Xddr.read(addrQ, sizeQ)

                print("publishing : I=%x:%x Q=%x:%x" % (addrI, sizeI, addrQ, sizeQ))
                self.publisher.send_multipart(
                    [
                        bytes(str(Inet.TOPIC_FILTER), "utf-8"),
                        bytes(str(sn), "utf-8"),
                        bytes(str(fs), "utf-8"),
                        bytes(str(freq), "utf-8"),
                        bytes(str(time.time_ns() / 1_000_000_000), "utf-8"),
                        pickle.dumps(bytesI),
                        pickle.dumps(bytesQ),
                    ]
                )

    def start_dma(self, ddr, ids, offset, size):
        return self.__start_dma(ddr, ids, offset, size)

    def reset_dma(self, ids):
        return self.__reset_dma(ids)

    def calc_capture_time(self, captureSize):
        numCaptures = 0x1
        batchSize = captureSize * numCaptures
        numSamples = batchSize / (self.hw.BYTES_PER_SAMPLE)
        t = numSamples / self.samplingFreq
        return t


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("{}: Usage".format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]

    test = TestSuite(ticsFilePath)

    test.run_test()
