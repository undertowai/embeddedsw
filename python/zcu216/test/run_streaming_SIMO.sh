#!/bin/bash


test="test_streaming_SIMO.py"
export py=python

. config.sh

if [ $# -lt 1 ]; then
    echo "Usage $0 <config.json> [clk_config.json]"
    echo "Example: sudo ./run_streaming_SIMO.sh configs/streaming_large.json ../rfdc/configs/300MHz_RefClk_58G.json"
    exit 1
fi

test_config=$1
clk_config=$2

. test_config.sh

test_setup $test_config $clk_config

num_iterations=$(get_config $test_config num_iterations 10)
sn=0

while true; do
    $py $test $sn $test_config
    [[ $? != 0 ]] && exit 1

    sn=$(($sn + $num_iterations))
done
