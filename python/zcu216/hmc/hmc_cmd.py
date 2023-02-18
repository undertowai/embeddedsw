import cmd
import json

from hmc import HMC63xx


class HMC_shell(cmd.Cmd):
    """
    HMC63xx command processor
    """

    def __init__(self):
        super(HMC_shell, self).__init__()
        self.hmc = HMC63xx("spi_gpio")
        self.hmc.GpioInit()


    def load_json(self, path):
        with open(path, 'r') as f:
            j = json.load(f)
            f.close()
        return j

    def do_6300_def(self, ic):
        "Write default configuration to 6300 [x] ic"
        try:
            self.hmc.DefaultConfig_6300(ic=ic)
        except AssertionError:
            pass


    def do_6300_ext(self, line):
        "Write External configuration to 6300: 6300_ext <ic> <config id>"
        ic, id = [int(s) for s in line.split()]
        try:
            self.hmc.ExtConfig_6300(ic=ic, id=id)
        except AssertionError:
            pass

    def do_6301_def(self, ic):
        "Write default configuration to 6301 [x] ic"
        try:
            self.hmc.DefaultConfig_6301(ic=ic)
        except AssertionError:
            pass

    def do_6301_ext(self, line):
        "Write External configuration to 6300: 6301_ext <ic> <config id>"
        ic, id = [int(s) for s in line.split()]
        try:
            self.hmc.ExtConfig_6301(ic=ic, id=id)
        except AssertionError:
            pass

    def do_6300_print(self, ic):
        "Dump registers"
        self.hmc.PrintConfig_6300(ic=ic)

    def do_6301_print(self, ic):
        "Dump registers"
        self.hmc.PrintConfig_6301(ic=ic)

    def do_6300_ifgain(self, line):
        "Set ifgain"
        ic, ifgain = [int(s) for s in line.split()]
        print("Setting if gain ic={}, gain={}".format(ic, ifgain))
        try:
            self.hmc.IfGain_6300(ic=ic, gain=ifgain)
        except AssertionError:
            pass

    def do_6301_ifgain(self, line):
        "Set ifgain"
        ic, ifgain = [int(s) for s in line.split()]
        print("Setting if gain ic={}, gain={}".format(ic, ifgain))
        try:
            self.hmc.IfGain_6301(ic=ic, gain=ifgain)
        except AssertionError:
            pass

    def do_6300_rvga_gain(self, line):
        "Set rvga gain"
        ic, gain = [int(s) for s in line.split()]
        print("Setting rvga gain ic={}, gain={}".format(ic, gain))
        try:
            self.hmc.RVGAGain_6300(ic=ic, gain=gain)
        except AssertionError:
            pass

    def do_6300_power(self, line):
        "Set power on/off"
        ic, pwup = [int(s) for s in line.split()]
        try:
            self.hmc.Power_6300(ic=ic, pwup=pwup)
        except AssertionError:
            pass

    def do_6301_att(self, line):
        "Set i/q/att2 attenuation: 6301_att <ic> <i> <q> <att2>"
        ic, i, q, att = [int(s) for s in line.split()]
        print("Setting atttenuation ic={}, i={}, q={}, att={}".format(ic, i, q, att))
        try:
            self.hmc.SetAtt_6301(ic=ic, i=i, q=q, att=att)
        except AssertionError:
            pass

    def do_6301_lna_gain(self, line):
        "Set lna gain: 6301_lna_gain <ic> <gain>"
        ic, gain = [int(s) for s in line.split()]
        print("Setting lna gain ic={}, gain={}".format(ic, gain))
        try:
            self.hmc.LNAGain_6301(ic=ic, gain=gain)
        except AssertionError:
            pass

    def do_6300_t(self, ic):
        "Read temperature"
        tempC = self.hmc.ReadTemp_6300(ic)
        print("6300_{} temperature = {}^C".format(ic, tempC))

    def do_6300_rd(self, line):
        "read register: 6300_rd <ic> <i>"
        ic, i = [int(s) for s in line.split()]
        reg = self.hmc.ReadReg_6300(ic=ic, i=i)
        print('reg={}'.format(hex(reg)))

    def do_6301_rd(self, line):
        "read register: 6301_rd <ic> <i>"
        ic, i = [int(s) for s in line.split()]
        reg = self.hmc.ReadReg_6301(ic=ic, i=i)
        print('reg={}'.format(hex(reg)))

    def do_6300_wr(self, line):
        "write register: 6300_rd <ic> <i>"
        ic, i, val = [int(s) for s in line.split()]
        self.hmc.WriteReg_6300(ic=ic, i=i, val=val)

    def do_6301_wr(self, line):
        "write register: 6301_rd <ic> <i>"
        ic, i, val = [int(s) for s in line.split()]
        self.hmc.WriteReg_6301(ic=ic, i=i, val=val)

    def do_reset_tx(self, line):
        self.hmc.Reset_6300()

    def do_reset_rx(self, line):
        self.hmc.Reset_6301()

    def do_config_pwr_tx(self, line):
        config_path = line
        tx_cfg = self.load_json(config_path)['TX']
        for ic, cfg in enumerate(tx_cfg):
            ifgain = cfg['ifgain_1.3db_step']
            rvgain = cfg['rvga_gain_1.3db_step']
            self.hmc.IfGain_6300(ic=ic, gain=ifgain)
            self.hmc.RVGAGain_6300(ic=ic, gain=rvgain)

    def do_config_pwr_rx(self, line):
        config_path = line
        rx_cfg = self.load_json(config_path)['RX']
        for ic, cfg in enumerate(rx_cfg):
            att_i = cfg['RX_att_I_6db_step']
            att_q = cfg['RX_att_Q_6db_step']
            att_comm = cfg['RX_att_comm_6db_step']

            self.hmc.SetAtt_6301(ic=ic, i=att_i, q=att_q, att=att_comm)

    def do_reset(self, line):
        self.hmc.Reset()

    def do_EOF(self, line):
        return True
    
    def do_exit(self, line):
        return True


if __name__ == "__main__":
    HMC_shell().cmdloop()
