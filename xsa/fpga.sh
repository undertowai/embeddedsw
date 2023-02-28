#!/bin/bash

bits=design_1_wrapper.bin

cp ./$bits /lib/firmware/

echo 0 > /sys/class/fpga_manager/fpga0/flags
echo $bits > /sys/class/fpga_manager/fpga0/firmware

echo $0 done
