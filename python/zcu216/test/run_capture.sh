#!/bin/bash

if [ $# -lt 3 ]; then
    echo "Usage $0 <config.json> <ticsFilePath> <Max iterations>"
    exit 1
fi

output_dir="./captures"

config=$1
ticsfilePath=$2
max_iterations=$3
lmk_config="../rfdc/configs/LMK_300MHz_RefClk_Out.txt"
num_iterations=1
sn=0

[ -d $output_dir ] && rm -rf $output_dir

python ../rfdc/rfdc_clk.py --cfg $config --lmk $lmk_config --lmx2820 $ticsfilePath
[[ $? != 0 ]] && exit 1

while [ $sn -lt $max_iterations ]; do
    python test_capture.py $output_dir $num_iterations $sn $config
    [[ $? != 0 ]] && exit 1

    sn=$(($sn + 1))
done

echo "$0: Done"