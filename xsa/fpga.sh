#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Usage $0 design_1_wrappe.bin"
    exit 1
fi

bits=$1
fpga_mng=/sys/class/fpga_manager

echo "$0 Updating fpga bits: $bits"

cp ./$bits /lib/firmware/

echo 0 > $fpga_mng/fpga0/flags
echo $bits > $fpga_mng/fpga0/firmware

echo $0 done
