#!/bin/bash
py=python

$py ../dac/player.py --tone 6000000 --pstep 90

. config.sh
. test_config.sh

run_test () {
    test_setup $1
    $py test_sanity_1.py $1
    [[ $? != 0 ]] && exit 1
}

echo "****************** checking RAW data ******************"
run_test "configs/sanity_raw.json"

echo "****************** checking SW integrated data ******************"
run_test "configs/sanity_integrated_sw.json"

echo "****************** checking HW integrated data ******************"
run_test "configs/sanity_integrated_hw.json"

echo "****************** checking HW integrated data (Large) ******************"
run_test "configs/sanity_integrated_hw_large.json"

echo "$0: Done"
