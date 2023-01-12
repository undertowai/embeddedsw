#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Usage $0 <ticsFilePath>"
    exit 1
fi

ticsfilePath=$1
num_iterations=10
sn=0

python ../rfdc/rfdc_clk.py $ticsfilePath

while true; do
    python test_streaming.py $num_iterations $sn
    if [[ $? != 0 ]];
    then
        exit 1
    fi
    sn=$(($sn + $num_iterations))
done