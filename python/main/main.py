
import sys
import ctypes as ct
import numpy as np
from time import sleep

sys.path.append("../misc")

from make import Make
from mlock import MLock

class MainLoopExt(MLock):
    def __init__(self, test_suite, libName):
        self.test_suite = test_suite
        libPath = Make().makeLibs(libName)
        self.lib = ct.CDLL(libPath)

    def __to_c_array(self, dtype, data):
        arr = (dtype * len(data))()
        arr[:] = data
        return arr

    def __loop_init(self, fs):
        ts = self.test_suite
        fun = self.lib.MainLoopInit

        status = fun(
            ct.c_char_p(ts.PORT.encode("UTF-8")),
            ct.c_char_p(ts.TOPIC_FILTER.encode("UTF-8")),
            ct.c_char_p(ts.gpio_sync.getDtsName().encode("UTF-8")),
            int(fs),
            int(ts.debug)
        )
        assert status == 0

    def __loop_exec(self, rx, txn, wait_time):

        ts = self.test_suite
        rx_dma_map = ts.map_rx_to_dma_id(rx)
        dmaBatch, _ = ts.prep_dma_batched(rx_dma_map)

        fun = self.lib.MainLoop

        ddr_id_arr = []
        name_arr = []
        addr_arr = []
        size_arr = []
        rxn_arr = []

        for d, n, a, s in dmaBatch:
            ddr_id_arr.append(d), name_arr.append(n.encode("UTF-8")), addr_arr.append(a), size_arr.append(s)

        ddr_id_arr = self.__to_c_array(ct.c_uint32, ddr_id_arr)
        name_arr = self.__to_c_array(ct.c_char_p, name_arr)
        addr_arr = self.__to_c_array(ct.c_uint64, addr_arr)
        size_arr = self.__to_c_array(ct.c_uint64, size_arr)
        rxn_arr = self.__to_c_array(ct.c_uint32, rx)

        status = fun(
            ddr_id_arr,
            name_arr,
            addr_arr,
            size_arr,
            len(name_arr),
            int(wait_time),
            int(txn),
            rxn_arr,
            len(rxn_arr)
        )

        assert status == 0

    def __loop_destroy(self):
        fun = self.lib.MainLoopDestroy

        status = fun()
        assert status == 0

    @MLock.Lock
    def loop(self):

        self.__loop_init(self.fs)
        self.__loop_exec(self.rx, self.txn, self.wait_time)
        self.__loop_destroy()

        print(f'**** {__file__}: Exiting')
        exit(1)

class MainLoopPython:
    VERSION = 0x1

    def __init__(self, test_suite):
        self.test_suite = test_suite
        pass

    def __proc_cap_data(self, area, sn, rx, txn, freq, fs, dtype=np.int16):
        ts = self.test_suite
        iq_data = []

        ts.integrator.do_check_errors(rx)

        for rxn in rx:
            a = area[rxn]
            addrI, sizeI = a["I"]
            addrQ, sizeQ = a["Q"]

            I = ts.xddr_read(addrI, sizeI, dtype)
            Q = ts.xddr_read(addrQ, sizeQ, dtype)

            I = ts.integrator.do_integration(I)
            Q = ts.integrator.do_integration(Q)

            iq_data.append((I, Q))

        ts.publish(self.VERSION, sn, txn, fs, freq, rx, iq_data)

    def loop(self, fs, wait_time, txn, rx, sn, num_iterations):

        iter_count = 0
        ts = self.test_suite

        ts.init_publisher()
        rx_dma_map = ts.map_rx_to_dma_id(rx)

        while iter_count < num_iterations:

            print("*** Running Iteration : sn={}".format(sn))

            ts.adc_dac_sync(False)

            _ = ts.start_dma(rx_dma_map)
            area = ts.start_dma(rx_dma_map)
            ts.adc_dac_sync(True)

            sleep(wait_time/1000)
            self.__proc_cap_data(area, sn, rx, txn, 0, fs)

            sn += 1
            iter_count += 1

