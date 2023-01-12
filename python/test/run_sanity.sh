#!/bin/bash
py=python

$py ../dac/player.py --tone 50000 --pstep 90

$py test_sanity_1.py
