import sys
import numpy as np

def read(path):
    lines=[]
    with open(path) as f:
        lines = f.readlines()

    regs = []
    for line in lines:
        regs.append( (line.split()[1], line.split()[0]) )

    buffer = np.empty(len(regs), dtype=np.uint32)

    for i, reg in enumerate(regs):
        buffer[i] = int(reg[0], 16)


def generateDummy(length, value):
    buffer = np.full(length, value, dtype=np.uint32)

    return buffer
