import os


class Make:
    DRIVERS_PATH="../../XilinxProcessorIPLib/drivers"
    METALAPI_LIB_PATH="lmetal/src"

    def __init__(self):
        pass

    def __MakeMetal(self):
        ret = os.system('make -C {}/{} -s all'.format(self.DRIVERS_PATH, self.METALAPI_LIB_PATH))
        assert ret == 0

    def __MakeLib(self, lib, keys=''):
        ret = os.system('make -C {}/{} -s all'.format(self.DRIVERS_PATH, lib))
        assert ret == 0

    def makeLibs(self, libName):
        print('Building lib \'{}\' ...'.format(libName))
        self.__MakeMetal()
        self.__MakeLib(libName + '/src')
        return self.DRIVERS_PATH + '/' + libName + '/src/lib' + libName + '.so'
