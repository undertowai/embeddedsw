#!/bin/bash
py=python

config="configs/sanity_1.json"

$py ../dac/player.py --tone 50000 --pstep 90

$py test_sanity_1.py $config

echo "$0: Done"
