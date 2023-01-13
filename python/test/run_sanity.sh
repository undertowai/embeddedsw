#!/bin/bash
py=python

if [ $# -lt 1 ]; then
    echo "Usage $0 <config.json>"
    exit 1
fi

config=$1

#$py ../dac/player.py --tone 50000 --pstep 90

$py test_sanity_1.py $config

echo "$0: Done"
