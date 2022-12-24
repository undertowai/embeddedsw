from genericpath import exists
import sys
import math
import numpy as np
from scipy import signal
import json
import os

from misc.traverse import Traverse

class Sig:
    fs = 600_000_000
    freq = 75_000_000

    def __init__(self) -> None:
        pass

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
        P = (Pxx_den[fn - 1] + Pxx_den[fn]) / 2
        return 10 * math.log10(P / N)

    # FIXME
    def set_dict(dict, keys):
        if len(keys) == 0:
            return {}

        d = Sig.set_dict(dict.copy(), keys[1:])

        if not keys[0] in dict:
            dict[keys[0]] = d

        return dict

    def process(dict, root, files):
        print("processing : {}".format(root))
        snr_dict = {}

        list.sort(files)
        for file in files:
            x = np.fromfile(root + os.sep + file, dtype=np.uint16)
            snr = Sig.get_SNR(x, Sig.freq, Sig.fs)
            snr_dict[file] = "{:.2f}".format(snr)

        keys = root.split(os.sep)[4:]

        if not keys[-1] in dict:
            dict[keys[-1]] = {}

        if not keys[-7] in dict[keys[-1]]:
            dict[keys[-1]][keys[-7]] = {}

        if not keys[-6] in dict[keys[-1]][keys[-7]]:
            dict[keys[-1]][keys[-7]][keys[-6]] = {}

        if not keys[-5] in dict[keys[-1]][keys[-7]][keys[-6]]:
            dict[keys[-1]][keys[-7]][keys[-6]][keys[-5]] = {}

        if not keys[-4] in dict[keys[-1]][keys[-7]][keys[-6]][keys[-5]]:
            dict[keys[-1]][keys[-7]][keys[-6]][keys[-5]][keys[-4]] = {}

        if not keys[-3] in dict[keys[-1]][keys[-7]][keys[-6]][keys[-5]][keys[-4]]:
            dict[keys[-1]][keys[-7]][keys[-6]][keys[-5]][keys[-4]][keys[-3]] = {}

        # if not keys[-2] in dict[keys[-1]][keys[-7]][keys[-6]][keys[-5]][keys[-4]][keys[-3]]:
        #    dict[keys[-1]][keys[-7]][keys[-6]][keys[-5]][keys[-4]][keys[-3]][keys[-2]] = {}

        dict[keys[-1]][keys[-7]][keys[-6]][keys[-5]][keys[-4]][keys[-3]][
            keys[-2]
        ] = snr_dict


if __name__ == "__main__":

    capturesPath = sys.argv[1]

    dict = {}
    Traverse.walk(dict, capturesPath, Sig.process)

    data = json.dumps(dict, indent=4)

    with open("." + os.sep + "snr.json", "w") as f:
        f.write(data)
