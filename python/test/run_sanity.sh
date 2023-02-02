#!/bin/bash
py=python

config="configs/sanity_1.json"

#$py ../dac/player.py --tone 50000 --pstep 90
#$py test_sanity_1.py $config

player_path="../dac"

echo "************** Loading ofdm data **************"
$py $player_path/player.py --ifile $player_path/ofdm/ofdm_256x2_480M/Ichannel_ofdm_18jan.npy --qfile $player_path/ofdm/ofdm_256x2_480M/Qchannel_ofdm_18jan.npy
echo "************** Running test **************"
$py test_sanity_1.py $config

echo "$0: Done"
