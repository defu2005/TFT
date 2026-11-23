#!/bin/bash
# Pipeline day du tren noi dung tong hop da sua cong thuc. Ket qua vao results/fixed/.
set -e
S=$1; R=/home/user/TFT/tft-sim/results/fixed; mkdir -p $R
export PYTHONPATH=/home/user/mielpopsssssss/tft_goat/src:/home/user/TFT/tft-sim/src
PY=$S/tftgoat-venv/bin/python
cd /home/user/TFT/tft-sim
$PY scripts/diag_equip.py > $R/equip_diag.txt 2>&1
$PY scripts/known_answer_scripted.py $R/known_answer_scripted_200.json > /dev/null 2>&1
$PY scripts/collect_train.py val 800 850 $S/fixed_val.npz
$PY scripts/collect_train.py train 200 350 $S/fixed_train.npz
echo collected
