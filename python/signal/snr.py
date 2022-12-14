
from genericpath import exists
import sys
import math
import numpy as np
from scipy import signal

import matplotlib.pyplot as plt


class Sig:
    def __init__(self) -> None:
        pass

    def cap_name(id):
        return 'cap{}_{}.bin'.format('I' if id%2==0 else 'Q', int(id/2))

    def tx_name(id):
        return 'TX_{}'.format(id)

    def get_fn(farr, freq):
        for fn, f in enumerate(farr):
            if f > freq:
                return fn
        return None
            
    def get_SNR(x, freq, fs):
        f, Pxx_den = signal.welch(x, fs, nperseg=1024)


        l = list(f)
        fn = Sig.get_fn(l, freq)

        N = np.mean(Pxx_den)
        P = (Pxx_den[fn-1] + Pxx_den[fn]) / 2
        return 10*math.log10(P/N)


if __name__ == "__main__":

    capturesPath = sys.argv[1]

    fs = 600_000_000
    freq = 15_000_000
    
    ids = [i for i in range(16)]
    caps = list(map(Sig.cap_name, ids))
    ids = [i for i in range(8)]
    txs = list(map(Sig.tx_name, ids))
    
    for tx in txs:
        for cap in caps:
            path = capturesPath + '/' + tx + '/' + cap
            x = np.fromfile(path, dtype=np.uint16)
            snr = Sig.get_SNR(x, freq, fs)
            print('{} -> {} : {:.2f} {}'.format(tx, cap.replace('cap', '').replace('.bin', ''), snr, '#' * int(snr)))
        print('============')


