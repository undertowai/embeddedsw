#!/bin/bash

test="test_streaming_SIMO.py"
py=python

if [ $# -lt 2 ]; then
    echo "Usage $0 <config.json> <lmx2820 config>"
    exit 1
fi

config=$1
ticsfilePath=$2
lmk_config="../rfdc/configs/LMK_300MHz_RefClk_Out.txt"
rf_pwr_config="../hmc/configs/rf_power.json"
num_iterations=300
sn=0

$py ../rfdc/rfdc_clk.py --cfg $config --lmk $lmk_config  --lmx2820 $ticsfilePath
[[ $? != 0 ]] && exit 1

sleep 10
$py ../hmc/hmc.py $config $rf_pwr_config

while true; do
    $py $test $num_iterations $sn $config
    [[ $? != 0 ]] && exit 1
    
    sn=$(($sn + $num_iterations))
done
