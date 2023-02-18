import sys, argparse
import ctypes as ct
import json
from time import sleep

sys.path.append("../misc")

from dts import Dts
from make import Make
from mlock import MLock

#TODO: make this common
def load_json(path):
    with open(path, 'r') as f:
        j = json.load(f)
        f.close()
    return j

class HMC63xx(MLock):
    def __init__(self, ipName, debug=False):

        libPath = Make().makeLibs("hmc63xx")
        devName = Dts().ipToDtsName(ipName)

        reg = Dts().readPropertyU32(ipName, "reg")
        self.addr = (reg[0] << 32) | reg[1]
        self.size = (reg[2] << 32) | reg[3]

        self.libPath = libPath
        self.devName = devName
        self.lib = ct.CDLL(self.libPath)

        self.devNamePtr = ct.c_char_p(self.devName.encode("UTF-8"))
        self.debug = debug

    def log(self, *argv):
        if self.debug:
            s = f'{self.__class__.__name__} : '
            for v in argv:
                s += f'{v}; '
            print(s)

    def read_conf(path):
        lines=[]
        with open(path) as f:
            lines = f.readlines()
            f.close()

        regs=[]
        for line in lines:
            sline = line.replace('\n','').split(':')
            regs.append( (sline[1] ) )

        return regs

    @MLock.Lock
    def GpioInit(self):
        self.log('GpioInit')
        fun = self.lib.HMC63xx_GpioInit
        status = fun(self.devNamePtr)

        assert status == 0

    @MLock.Lock
    def IfGain_6300(self):
        self.log(f'IfGain_6300: ic={self.ic} gain={hex(self.gain)}')
        fun = self.lib.HMC6300_SetIfGain

        status = fun(self.devNamePtr, int(self.ic), self.gain)
        assert status == 0

    @MLock.Lock
    def RVGAGain_6300(self):
        self.log(f'RVGAGain_6300: ic={self.ic} gain={hex(self.gain)}')
        fun = self.lib.HMC6300_SetRVGAGain

        status = fun(self.devNamePtr, int(self.ic), self.gain)
        assert status == 0

    @MLock.Lock
    def Power_6300(self):
        fun = self.lib.HMC6300_Power

        status = fun(self.devNamePtr, int(self.ic), 0x1 if self.pwup == True else False)
        assert status == 0

    def __RMW_6300(self, ic, i, val, mask):
        fun = self.lib.HMC6300_RMW

        status = fun(self.devNamePtr, int(ic), i, val, mask)
        assert status >= 0
        return status

    def __RMW_6301(self, ic, i, val, mask):
        fun = self.lib.HMC6301_RMW

        status = fun(self.devNamePtr, int(ic), i, val, mask)
        assert status >= 0
        return status

    @MLock.Lock
    def __RMW(self):
        mask = (1 << (self.bp[1] + 1)) - 1
        mask = mask >> self.bp[0]

        assert self.val <= mask

        val = self.val << self.bp[0]

        mask = 0xFF & (0xFF ^ (mask << self.bp[0]))
        return self.func(self.ic, self.i, val, mask)

    def __CheckDefConfig_6300(self, ic):
        fun = self.lib.HMC6300_CheckConfig

        status = fun(self.devNamePtr, int(ic))
        if status != 0:
            raise Exception("Failed to config 6300 ic={}, status={}".format(ic, status))

    @MLock.Lock
    def DefaultConfig_6300(self):
        fun = self.lib.HMC6300_SendDefaultConfig

        status = fun(self.devNamePtr, int(self.ic))
        assert status == 0

        self.__CheckDefConfig_6300(self.ic)

    @MLock.Lock
    def ExtConfig_6300(self):
        fun = self.lib.HMC6300_SendExtConfig

        status = fun(self.devNamePtr, int(self.ic), int(self.id))
        assert status == 0

    @MLock.Lock
    def PrintConfig_6300(self):
        fun = self.lib.HMC6300_PrintConfig

        status = fun(self.devNamePtr, int(self.ic))
        assert status == 0

    def __CheckDefConfig_6301(self, ic):
        fun = self.lib.HMC6301_CheckConfig

        status = fun(self.devNamePtr, int(ic))
        if status != 0:
            raise Exception("Failed to config 6301 ic={}, status={}".format(ic, status))

    @MLock.Lock
    def DefaultConfig_6301(self):
        fun = self.lib.HMC6301_SendDefaultConfig

        status = fun(self.devNamePtr, int(self.ic))
        assert status == 0

        self.__CheckDefConfig_6301(self.ic)

    @MLock.Lock
    def ExtConfig_6301(self):
        fun = self.lib.HMC6301_SendExtConfig

        status = fun(self.devNamePtr, int(self.ic), int(self.id))
        assert status == 0

    @MLock.Lock
    def PrintConfig_6301(self):
        fun = self.lib.HMC6301_PrintConfig

        status = fun(self.devNamePtr, int(self.ic))
        assert status == 0

    @MLock.Lock
    def SetAtt_6301(self):
        self.log(f'SetAtt_6301: ic={self.ic} i={hex(self.i)}, q={hex(self.q)}, att={hex(self.att)}')

        fun = self.lib.HMC6301_SetAtt

        status = fun(self.devNamePtr, int(self.ic), self.i, self.q, self.att)
        assert status == 0

    @MLock.Lock
    def IfGain_6301(self):
        self.log(f'IfGain_6301: ic={self.ic} gain={hex(self.gain)}')

        fun = self.lib.HMC6301_SetIfGain

        status = fun(self.devNamePtr, int(self.ic), self.gain)
        assert status == 0

    def LNAGain_6301(self, ic, gain):
        self.log(f'LNAGain_6301: ic={ic} gain={hex(gain)}')

        i = int(8)
        maxGain = 0x3
        assert gain <= maxGain

        gain = maxGain - gain

        self.__RMW(func=self.__RMW_6301, ic=ic, i=i, val=gain, bp=[3, 4])

    def ReadReg_6300(self, ic, i):
        return self.__RMW(func=self.__RMW_6300, ic=ic, i=i, val=0x0, bp=[8, 8])

    def ReadReg_6301(self, ic, i):
        return self.__RMW(func=self.__RMW_6301, ic=ic, i=i, val=0x0, bp=[8, 8])

    def WriteReg_6300(self, ic, i, val):
        self.log(f'WriteReg_6300: ic={ic}, i={i}, val={hex(val)}')

        return self.__RMW(func=self.__RMW_6300, ic=ic, i=i, val=val, bp=[0, 7])

    def WriteReg_6301(self, ic, i, val):
        self.log(f'WriteReg_6301: ic={ic}, i={i}, val={hex(val)}')

        return self.__RMW(func=self.__RMW_6301, ic=ic, i=i, val=val, bp=[0, 7])

    def ReadTemp_6300(self, ic):
        # enable temperature sensor
        self.__RMW(func=self.__RMW_6300, ic=ic, i=3, val=0x1, bp=[0, 0])
        self.__RMW(func=self.__RMW_6300, ic=ic, i=10, val=0x0, bp=[0, 0])
        temp = self.ReadReg_6300(ic, 27)
        tempC = ((85 - (-40)) * temp) / 0x1F
        return int(tempC)

    @MLock.Lock
    def Reset_6300(self):
        fun = self.lib.HMC6300_Reset

        status = fun(self.devNamePtr)
        assert status == 0

    @MLock.Lock
    def Reset_6301(self):
        fun = self.lib.HMC6301_Reset

        status = fun(self.devNamePtr)
        assert status == 0

    def Reset(self):
        self.Reset_6300()
        self.Reset_6301()

    def __write_row_comm(self, func, ic, row, val):
        row = int(row.replace('ROW', ''))
        func(ic, row, int(val, 16))

    def __write_rows_comm(self, func, ic, config):
        if 'regs' in config:
            regs  =config['regs']
            for row in regs:
                self.__write_row_comm(func, ic, row, regs[row])

    def __get_param(self, conf, param, default):
        return conf[param] if param in conf else default

    def setup_tx(self, tx, rf_config):
        print('Configuring TX (HMC6300)')
        for ic in tx:
            self.ExtConfig_6300(ic=ic, id=0)
            tx_conf = rf_config['TX'][ic]
            tx_conf_w = rf_config['TX*']

            ifgain = self.__get_param(tx_conf_w, 'ifgain_1.3db_step', None)
            ifgain = self.__get_param(tx_conf, 'ifgain_1.3db_step', ifgain)

            if  ifgain is not None:
                self.IfGain_6300(ic=ic, gain=ifgain)

            rvgain = self.__get_param(tx_conf_w, 'rvga_gain_1.3db_step', None)
            rvgain = self.__get_param(tx_conf, 'rvga_gain_1.3db_step', rvgain)

            if rvgain is not None:
                self.RVGAGain_6300(ic=ic, gain=rvgain)

            self.__write_rows_comm(self.WriteReg_6300, ic, tx_conf_w)
            self.__write_rows_comm(self.WriteReg_6300, ic, tx_conf)

    def setup_rx(self, rx, rf_config):

        print('Configuring RX (HMC6301)')
        for ic in rx:
            self.ExtConfig_6301(ic=ic, id=0)
            rx_conf = rf_config['RX'][ic]
            rx_conf_w = rf_config['RX*']

            att_i = self.__get_param(rx_conf_w, 'RX_att_I_1db_step', None)
            att_i = self.__get_param(rx_conf, 'RX_att_I_1db_step', att_i)

            att_q = self.__get_param(rx_conf_w, 'RX_att_Q_1db_step', None)
            att_q = self.__get_param(rx_conf, 'RX_att_Q_1db_step', att_q)

            att_comm = self.__get_param(rx_conf_w, 'RX_att_comm_6db_step', None)
            att_comm = self.__get_param(rx_conf, 'RX_att_comm_6db_step', att_comm)

            if att_i is not None and att_q is not None and att_comm is not None:
                self.SetAtt_6301(ic=ic, i=att_i, q=att_q, att=att_comm)

            self.__write_rows_comm(self.WriteReg_6301, ic, rx_conf_w)
            self.__write_rows_comm(self.WriteReg_6301, ic, rx_conf)

if __name__ == "__main__":

    argparser=argparse.ArgumentParser()
    argparser.add_argument('--cfg', help='specify TEST config', type=str)
    argparser.add_argument('--rf_cfg', help='specify RF config', type=str)

    args  = argparser.parse_args()

    assert args.cfg is not None
    assert args.rf_cfg is not None


    cfg_path = args.cfg
    rf_cfg_path = args.rf_cfg

    config = load_json(cfg_path)
    rf_config = load_json(rf_cfg_path)

    debug = config['debug'] if 'debug' in config else False

    hmc = HMC63xx("spi_gpio", debug)

    hmc.GpioInit()
    hmc.Reset()

    sleep_s = int(rf_config['LO']['sleep'])
    print(f'Waiting {sleep_s} seconds before starting RF ...')
    sleep(sleep_s)
    hmc.setup_tx(config['tx'], rf_config)
    hmc.setup_rx(config['rx'], rf_config)

    print("Pass")
