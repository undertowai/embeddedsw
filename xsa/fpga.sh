#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Usage $0 design_1_wrappe.bin"
    exit 1
fi

bits=$1
fpga_mng=/sys/class/fpga_manager

read_conf() {
    echo 0 > /sys/module/zynqmp_fpga/parameters/readback_type
    cat /sys/kernel/debug/fpga/fpga0/image
}

read_bits() {
    bits=$1
    echo 1 > /sys/module/zynqmp_fpga/parameters/readback_type
    rm /tmp/$bits
    cat /sys/kernel/debug/fpga/fpga0/image > /tmp/$bits
}

prog_bits() {
    bits=$1
    cp ./$bits /lib/firmware/

    echo 0 > $fpga_mng/fpga0/flags
    echo $bits > $fpga_mng/fpga0/firmware
}

cmp_bits() {
    bits=$1
    cmp=$(diff $bits /tmp/$bits)
    if [ ! -z "$cmp" ]; then
        echo "Can not program bits, content missmatch"
        exit 1
    fi
}

echo "$0 Programming fpga bits: $bits"

#read_conf
#read_bits $bits
#cmp_bits $bits
prog_bits $bits

echo $0 done
