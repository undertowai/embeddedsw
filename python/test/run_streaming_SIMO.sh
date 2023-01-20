#!/bin/bash


test="test_streaming_SIMO.py"
export py=python

. config.sh

if [ $# -lt 2 ]; then
    echo "Usage $0 <config.json> <clk_config.json>"
    echo "Example: sudo ./run_streaming_SIMO.sh configs/streaming_large.json ../rfdc/configs/300MHz_RefClk_58G.json"
    exit 1
fi

test_config=$1
clk_config=$2

lmk_config="../rfdc/configs/$(get_config $clk_config lmk None)"
lmx2820_config="../lmx/$(get_config $clk_config lmx2820 None)"
rf_pwr_config="../hmc/configs/rf_power.json"

num_iterations=$(get_config $test_config num_iterations 1)

$py ../rfdc/rfdc_clk.py --cfg $test_config --lmk $lmk_config  --lmx2820 $lmx2820_config
[[ $? != 0 ]] && exit 1

$py ../hmc/hmc.py $test_config $rf_pwr_config
[[ $? != 0 ]] && exit 1

sn=0

while true; do
    $py $test $sn $test_config
    [[ $? != 0 ]] && exit 1

    sn=$(($sn + $num_iterations))
done
