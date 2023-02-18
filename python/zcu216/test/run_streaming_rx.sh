#!/bin/bash

if [ $# -lt 2 ]; then
    echo "Usage $0 <config.json> <ticsFilePath>"
    exit 1
fi

config=$1
ticsfilePath=$2
lmk_config="../rfdc/configs/LMK_300MHz_RefClk_Out.txt"
num_iterations=300
sn=0

python ../rfdc/rfdc_clk.py --cfg $config --lmk $lmk_config --lmx2820 $ticsfilePath
[[ $? != 0 ]] && exit 1

while true; do
    python test_streaming_rx.py $num_iterations $sn $config

    [[ $? != 0 ]] && exit 1

    sn=$(($sn + $num_iterations))
done