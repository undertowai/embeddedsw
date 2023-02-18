#!/bin/bash

test="test_capture.py"
export py=python

. config.sh

if [ $# -lt 2 ]; then
    echo "Usage $0 <config.json> <clk_config.json>"
    echo "Example: sudo ./run_capture_SIMO.sh configs/streaming_large.json ../rfdc/configs/300MHz_RefClk_58G.json"
    exit 1
fi

test_config=$1
clk_config=$2

test_setup $test_config $clk_config

num_iterations=$(get_config $test_config num_iterations 10)
max_iterations=$(get_config $test_config max_iterations 100)

sn=0

while [ $sn -lt $max_iterations ]; do
    python $test $output_dir $num_iterations $sn $test_config
    [[ $? != 0 ]] && exit 1

    sn=$(($sn + $num_iterations))
done

echo "$0: Done"