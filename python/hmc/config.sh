#!/bin/bash

PY=python3
DRIVERS_PATH="../../XilinxProcessorIPLib/drivers"
HMC63xx_LIB_PATH="$DRIVERS_PATH/hmc63xx/src"
METALAPI_LIB_PATH="$DRIVERS_PATH/lmetal/src"

make -C $METALAPI_LIB_PATH
make -C $HMC63xx_LIB_PATH

IC=$1

DEVICE_SYMBOL="spi_gpio"
HMC_GPIO_DTS_NAME=$(cat /proc/device-tree/__symbols__/$DEVICE_SYMBOL)

$PY hmc.py $HMC63xx_LIB_PATH/libhmc.so $HMC_GPIO_DTS_NAME $IC
