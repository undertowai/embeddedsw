#!/bin/bash
py=python

$py ../dac/player.py --tone 50000 --pstep 90

echo "****************** checking RAW data ******************"
$py test_sanity_1.py "configs/sanity_raw.json"

echo "****************** checking SW integrated data ******************"
$py test_sanity_1.py "configs/sanity_integrated_sw.json"

echo "****************** checking HW integrated data ******************"
$py test_sanity_1.py "configs/sanity_integrated_hw.json"

echo "****************** checking HW integrated data (Large) ******************"
$py test_sanity_1.py "configs/sanity_integrated_hw_large.json"

echo "$0: Done"
