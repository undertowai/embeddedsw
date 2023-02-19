from pathlib import Path
import subprocess
import numpy as np
import glob

class Dts:
    IP_SYMBOLS_PATH = "/proc/device-tree/__symbols__"
    DTS_PATH = "/sys/devices/platform"

    def __init__(self):
        pass

    def __readIp(self, ip):
        # Use glob to find the IP with variation between the prefix and IP name
        # adding hierarchy inside the block design will change the prefix before the ip 
        ip_path = glob.glob(self.IP_SYMBOLS_PATH+ "/" + "*" + ip)
        assert(len(ip_path) == 1)
        print("__readIP: Found %s as %s" % (ip, ip_path))
        with open(ip_path[0]) as f:
            out = f.read().replace("\x00", "").split("/")
            f.close()
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

    def ipToDtsPathAbsolute(self, ipName):
        return self.DTS_PATH + "/" + self.ipToDtsPath(ipName)

    def readPropertyU32(self, ipName, propName):
        path = self.DTS_PATH + "/" + self.ipToDtsPath(ipName) + "/of_node/" + propName
        data = np.fromfile(path, dtype=np.uint32)
        data.byteswap(inplace=True)
        return data
