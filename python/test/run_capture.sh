#!/bin/bash

if [ $# -lt 2 ]; then
    echo "Usage $0 <ticsFilePath> <Max iterations>"
    exit 1
fi

output_dir="./captures"
ticsfilePath=$1
max_iterations=$2

num_iterations=1
sn=0

[ -d $output_dir ] && rm -rf $output_dir

python ../rfdc/rfdc_clk.py $ticsfilePath

while [ $sn -lt $max_iterations ]; do
    python test_capture.py $output_dir $num_iterations $sn
    if [[ $? != 0 ]];
    then
        exit 1
    fi
    sn=$(($sn + 1))
done

echo "$0: Done"