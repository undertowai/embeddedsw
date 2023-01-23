#!/bin/bash

py=python

$py ./rfdc_clk.py --dump_ip
$py ./rfdc_clk.py --dump_adc 0
$py ./rfdc_clk.py --dump_adc 1
$py ./rfdc_clk.py --dump_adc 2
$py ./rfdc_clk.py --dump_adc 3

$py ./rfdc_clk.py --dump_dac 0
$py ./rfdc_clk.py --dump_dac 1
$py ./rfdc_clk.py --dump_dac 2
$py ./rfdc_clk.py --dump_dac 3
