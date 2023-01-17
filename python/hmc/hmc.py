import sys
import ctypes as ct
import json

sys.path.append("../misc")

from dts import Dts
from make import Make
from mlock import MLock


class HMC63xx(MLock):
    def __init__(self, ipName):

        libPath = Make().makeLibs("hmc63xx")
        devName = Dts().ipToDtsName(ipName)

        reg = Dts().readPropertyU32(ipName, "reg")
        self.addr = (reg[0] << 32) | reg[1]
        self.size = (reg[2] << 32) | reg[3]

        self.libPath = libPath
        self.devName = devName
        self.lib = ct.CDLL(self.libPath)

        self.devNamePtr = ct.c_char_p(self.devName.encode("UTF-8"))

    def load_json(self, path):
        with open(path, 'r') as f:
            j = json.load(f)
            f.close()
        return j

    def read_conf(path):
        lines=[]
        with open(path) as f:
            lines = f.readlines()

        regs=[]
        for line in lines:
            sline = line.replace('\n','').split(':')
            regs.append( (sline[1] ) )

        return regs

    @MLock.Lock
    def GpioInit(self):
        fun = self.lib.HMC63xx_GpioInit
        status = fun(self.devNamePtr)

        assert status == 0

    @MLock.Lock
    def IfGain_6300(self):
        #print("XXX 6300 IFGain XXX")
        fun = self.lib.HMC6300_SetIfGain

        status = fun(self.devNamePtr, int(self.ic), self.gain)
        assert status == 0

    @MLock.Lock
    def RVGAGain_6300(self):
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
        fun = self.lib.HMC6301_SetAtt

        status = fun(self.devNamePtr, int(self.ic), self.i, self.q, self.att)
        assert status == 0

    @MLock.Lock
    def IfGain_6301(self):
        fun = self.lib.HMC6301_SetIfGain

        status = fun(self.devNamePtr, int(self.ic), self.gain)
        assert status == 0

    def LNAGain_6301(self, ic, gain):
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
        return self.__RMW(func=self.__RMW_6300, ic=ic, i=i, val=val, bp=[0, 7])

    def WriteReg_6301(self, ic, i, val):
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

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <config.json> <rf_config.json>")
        assert False

    hmc = HMC63xx("spi_gpio")

    hmc.GpioInit()
    hmc.Reset()

    cfg_path = sys.argv[1]
    rf_cfg_path = sys.argv[2]
    config = hmc.load_json(cfg_path)
    rf_config = hmc.load_json(rf_cfg_path)
    
    print('Configuring TX (HMC6300)')
    for ic in config['tx']:
        hmc.ExtConfig_6300(ic=ic, id=0)
        tx_conf = rf_config['TX'][ic]

        ifgain = tx_conf['ifgain_1.3db_step']
        rvgain = tx_conf['rvga_gain_1.3db_step']
        hmc.IfGain_6300(ic=ic, gain=ifgain)
        hmc.RVGAGain_6300(ic=ic, gain=rvgain)

    print('Configuring RX (HMC6301)')
    for ic in config['rx']:
        hmc.ExtConfig_6301(ic=ic, id=0)
        rx_conf = rf_config['RX'][ic]
        att_i = rx_conf['RX_att_I_6db_step']
        att_q = rx_conf['RX_att_Q_6db_step']
        att_comm = rx_conf['RX_att_comm_6db_step']

        hmc.SetAtt_6301(ic=ic, i=att_i, q=att_q, att=att_comm)

    print("Pass")
