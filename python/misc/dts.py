import subprocess

class Dts:
    IP_SYMBOLS_PATH='/proc/device-tree/__symbols__'
    def __init__(self):
        pass

    def ipToDtsName(self, ip):
        out = subprocess.check_output(['cat', '{}/{}'.format(self.IP_SYMBOLS_PATH, ip)])
        out = out.decode('UTF-8').replace('\x00', '')
        dts = out.split('/')[2].split('@')
        dts = dts[1] + '.' + dts[0]

        return dts