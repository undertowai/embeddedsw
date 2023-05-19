#!/bin/bash
py=python

$py ../dac/player.py --tone 6000000 --pstep 90

. test_config.sh

run_test () {
    test_setup $1
    [[ $? != 0 ]] && exit 1
    $py test_sanity_1.py $1
    [[ $? != 0 ]] && exit 1
}

conig_hw () {
    test_config=$1
    samples_in_unit=$(get_config $test_config samples_in_unit)

    $py ../dac/player.py --tri --size $samples_in_unit
}

echo "****************** checking RAW data ******************"
test_config="configs/sanity_raw.json"
run_test $test_config

echo "****************** checking HW integrated data (OFDM) ******************"
conig_hw "configs/sanity_integrated_hw.json"
run_test $test_config

echo "****************** checking HW integrated data #2 (OFDM) ******************"
conig_hw "configs/sanity_integrated_hw_2.json"
run_test $test_config

echo "$0: Done"
