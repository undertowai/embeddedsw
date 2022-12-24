import os
import sys
from time import sleep
import traceback
import logging
import numpy as np
import pickle
import time

from misc.swave import Wave
from misc.widebuf import WideBuf

from lmx.lmx import Lmx2820
from hmc.hmc import HMC63xx
from gpio.gpio import AxiGpio
from axidma.axidma import AxiDma
from xddr.xddr import Xddr
from rfdc.rfdc import Rfdc
from bram.bram import BramFactory

from hw import Hw
from inet import Inet


class TestSuite:
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

        self.hw = Hw()

        self.lmx = Lmx2820("axi_quad_spi_0")
        self.hmc = HMC63xx("spi_gpio")
        self.axiGpio = AxiGpio("axi_gpio")
        self.dma = AxiDma("axidma")
        self.ddr0 = Xddr("ddr4_0")
        self.ddr1 = Xddr("ddr4_1")
        self.rfdc = Rfdc("rfdc2")

        self.gpio_sync = self.axiGpio.getGpio("dma_sync_gpio_0")
        self.gpio_gate_0 = self.axiGpio.getGpio("axis_gate_0_axi_gpio_0")
        self.gpio_gate_1 = self.axiGpio.getGpio("axis_gate_1_axi_gpio_0")
        self.gpio_bram_count = self.axiGpio.getGpio("axi_gpio_0")

        bram_f = BramFactory()
        self.bram0 = bram_f.makeBram("ram_player_8wide_0_axi_bram_ctrl_0")
        self.bram1 = bram_f.makeBram("ram_player_8wide_1_axi_bram_ctrl_0")

    def load_ext_bram(self, Ipath, Qpath, dtype):
        sampleSize = np.dtype(dtype).itemsize
        buffersCount = self.hw.BUFFERS_IN_BRAM
        numBytes = int(self.getBramSize() / buffersCount)
        numSamples = int(numBytes / sampleSize)
        samplesPerFLit = self.hw.SAMPLES_PER_FLIT

        buffer = np.empty(buffersCount * numSamples, dtype=dtype)

        I = np.fromfile(Ipath, dtype=np.int16)
        Q = np.fromfile(Qpath, dtype=np.int16)
        for i in range(0, buffersCount, 2):
            WideBuf().make(buffer, I, i, buffersCount, samplesPerFLit)
            WideBuf().make(buffer, Q, i + 1, buffersCount, samplesPerFLit)

        return buffer

    def make_sweep_tone_bram(self, samplingFreq, freq, dBFS, freqStep, dtype):
        sampleSize = np.dtype(dtype).itemsize
        fullCycles = True
        phaseDegrees = 0x0
        buffersCount = self.hw.BUFFERS_IN_BRAM
        numBytes = int(self.getBramSize() / buffersCount)
        numSamples = int(numBytes / sampleSize)
        samplesPerFLit = self.hw.SAMPLES_PER_FLIT

        buffer = np.empty(buffersCount * numSamples, dtype=dtype)

        for i in range(buffersCount):

            # Keep same frequency for I & Q channels
            if i % 2 == 0:
                tone = Wave().getSine(
                    numBytes,
                    freq,
                    dBFS,
                    samplingFreq,
                    sampleSize,
                    phaseDegrees,
                    fullCycles,
                )
                freq = freq + freqStep

            WideBuf().make(buffer, tone, i, buffersCount, samplesPerFLit)

        return buffer, freq

    def mkdir(self, outputDir, suffix):
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)

        if self.capture_data:
            outputDir = "{}/TX_{}".format(outputDir, suffix)
            if not os.path.exists(outputDir):
                os.mkdir(outputDir)
        else:
            outputDir = None
        return outputDir

    def cap_name(self, id):
        return "cap{}_{}.bin".format("I" if id % 2 == 0 else "Q", int(id / 2))

    def setup_RF_Clk(self, ticsFilePath, restart_rfdc=True):

        if restart_rfdc:
            self.rfdc.restart()

        if False == self.lmx.readLockedReg():
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

    def getBramSize(self):
        assert self.bram0.getSize() == self.bram1.getSize()
        return self.bram0.getSize()

    def load_dac_player(self, bram0_data, bram1_data):
        bram0_size = self.bram0.load(data=bram0_data)
        bram1_size = self.bram1.load(data=bram1_data)

        assert bram0_size == bram1_size

        div = (
            self.hw.BUFFERS_IN_BRAM
            * self.hw.SAMPLES_PER_FLIT
            * self.hw.BYTES_PER_SAMPLE
        )
        playerTicksPerBuffer = int(bram0_size / div)

        self.gpio_bram_count.set(val=playerTicksPerBuffer)

    def adc_dac_sync(self, sync):
        self.gpio_sync.set(val=(0xFF if sync else 0x0))

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

    def __reset_dma(self, ids):

        for id in ids:
            devName = self.dma.devIdToIpName(id)
            self.dma.reset(devName=devName)

    def __write_cap_data(self, path, data):
        with open(path, "wb") as f:
            f.write(data)
            f.close()

    def __capture_memory(self, ddr, outputdir, paths, offset, size):
        base_address = ddr.base_address() + offset

        addr = base_address
        for path in paths:
            outputPath = None if outputdir is None else outputdir + "/" + path
            data = ddr.capture(addr, size)
            if outputPath is not None:
                self.__write_cap_data(outputPath, data)
            addr = addr + size

    def dac_gate(self, val):
        self.gpio_gate_0.set(val=(val >> 0) & 0xFF)
        self.gpio_gate_1.set(val=(val >> 8) & 0xFF)

    def capture(self, ddr, outputDir, paths, ids, offset, size):

        assert len(paths) == len(ids)

        self.adc_dac_sync(False)

        self.__start_dma(ddr, ids, offset, size)

        self.adc_dac_sync(True)

        sleep(self.calc_capture_time(size))

        self.__reset_dma(ids)

        return self.__capture_memory(ddr, outputDir, paths, offset, size)

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

    def calc_capture_time(self, captureSize):
        numCaptures = 0x1
        batchSize = captureSize * numCaptures
        numFlits = batchSize / (self.hw.SAMPLES_PER_FLIT * self.hw.BYTES_PER_SAMPLE)
        t = numFlits / self.hw.FABRIC_CLOCK
        return t


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("{}: Usage".format(sys.argv[0]))
        exit()

    ticsFilePath = sys.argv[1]

    test = TestSuite(ticsFilePath)

    test.run_test()
