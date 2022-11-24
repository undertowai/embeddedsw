#!/bin/bash

PY=python3
DRIVERS_PATH="../../XilinxProcessorIPLib/drivers"
QSPI_LIB_PATH="$DRIVERS_PATH/spi/examples"
METALAPI_LIB_PATH="$DRIVERS_PATH/lmetal/src"

lmxRegsFile=$1

if [[ -z $lmxRegsFile ]]; then
    echo "Example : $0 lmx2820_HexRegisterValues.txt"
    exit
fi

make -C $QSPI_LIB_PATH/../src
make -C $METALAPI_LIB_PATH
make -C $QSPI_LIB_PATH so

DEVICE_SYMBOL="axi_quad_spi_0"
QSPI_DTS_NAME=$(cat /proc/device-tree/__symbols__/$DEVICE_SYMBOL)

#while true
#do
$PY lmx.py $QSPI_LIB_PATH/libqspi.so $QSPI_DTS_NAME $lmxRegsFile
#done
