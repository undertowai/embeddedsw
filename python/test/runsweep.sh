#!/bin/bash

output_dir="/home/captures"
lmx_regs_path="../lmx/lmx2820_HexRegisterValues.txt"

rm -rf $output_dir

python test_1x8_RF_sweep.py  $lmx_regs_path $output_dir
