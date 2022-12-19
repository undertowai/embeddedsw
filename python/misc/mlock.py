from filelock import Timeout, FileLock

class MLock:
    LOCK_PATH = '../metal.lock'
    LOCK_TIMEOUT = 1

    def getargs(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    def delargs(self, **kw):
        for k, v in kw.items():
            delattr(self, k)

    def Lock(func):
        def inner(self, **kw):
            self.mlock = FileLock(self.LOCK_PATH, self.LOCK_TIMEOUT)
            self.getargs(**kw)
            try:
                with self.mlock.acquire(timeout=MLock.LOCK_TIMEOUT):
                    ret = func(self)
            except Timeout:
                raise Exception('Can\'t acquire metal lock' )
            finally:
                self.mlock.release()
                self.delargs(**kw)
                
            return ret

        return inner