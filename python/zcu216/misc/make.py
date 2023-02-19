import os


class Make:
    METALAPI_LIB_PATH = "lmetal/src"

    def __init__(self):
        # Needs XILINX_IP_PATH to be a directory path to XilinxProcessorIPLib
        self.XilinxIPRoot = os.environ["XILINX_IP_PATH"]
        self.DRIVERS_PATH = self.XilinxIPRoot + "/drivers"
        assert(self.XilinxIPRoot != None)
        pass

    def __MakeMetal(self):
        ret = os.system(
            "make -C {}/{} -s all".format(self.DRIVERS_PATH, self.METALAPI_LIB_PATH)
        )
        assert ret == 0

    def __MakeLib(self, lib, keys=""):
        ret = os.system("make -C {}/{} -s all {}".format(self.DRIVERS_PATH, lib, keys))
        assert ret == 0

    def makeLibs(self, libName, keys=""):
        self.__MakeMetal()
        self.__MakeLib(libName + "/src", keys=keys)
        return self.DRIVERS_PATH + "/" + libName + "/src/lib" + libName + ".so"
