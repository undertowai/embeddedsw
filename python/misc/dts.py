import subprocess
import numpy as np


class Dts:
    IP_SYMBOLS_PATH = "/proc/device-tree/__symbols__"
    DTS_PATH = "/sys/devices/platform"

    def __init__(self):
        pass

    def __readIp(self, ip):
        with open(self.IP_SYMBOLS_PATH + "/" + ip) as f:
            out = f.read().replace("\x00", "").split("/")
        return out

    def ipToDtsName(self, ip):
        dts = self.__readIp(ip)
        dts = dts[2].split("@")
        dts = dts[1] + "." + dts[0]
        return dts

    def ipToDtsPath(self, ip):
        dts = self.__readIp(ip)
        platform = dts[1]
        dts = dts[2].split("@")
        path = platform + "/" + dts[1] + "." + dts[0]
        return path

    def readPropertyU32(self, ipName, propName):
        path = self.DTS_PATH + "/" + self.ipToDtsPath(ipName) + "/of_node/" + propName
        data = np.fromfile(path, dtype=np.uint32)
        data.byteswap(inplace=True)
        return data
