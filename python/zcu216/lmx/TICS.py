import sys
import numpy as np
import string


def read(path):
    lines = []
    with open(path) as f:
        lines = f.readlines()

    regs = []
    for line in lines:
        regs.append((line.split()[1], line.split()[0]))

    buffer = np.empty(len(regs), dtype=np.uint32)

    for i, reg in enumerate(regs):
        buffer[i] = int(reg[0], 16)

    return buffer

def LMK_get_reg_id(reg):
    return (int(reg, 16) >> 8) & 0x1fff

def write(csv_like_file_path, output_file_path):

    with open(csv_like_file_path) as f:
        csv_data = f.read()
        f.close()
    
    csv_data = csv_data.translate({ord(c): None for c in string.whitespace})

    regs = csv_data.split(',')
    
    with open(output_file_path, '+w') as f:
        f.write('R0\t(INIT)\t{}\r\n'.format(regs[0]))
        for i, reg in enumerate(regs[1:]):
            f.write('R{}\t{}\r\n'.format(LMK_get_reg_id(reg), reg))
        f.close()

def generateDummy(length, value):
    buffer = np.full(length, value, dtype=np.uint32)

    return buffer


if __name__ == '__main__':
    csv_like_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    
    write(csv_like_file_path, output_file_path)
    print('Done')