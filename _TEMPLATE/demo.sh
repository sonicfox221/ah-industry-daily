#!/usr/bin/env bash
# 一键全流程：把各步骤串起来跑一遍。
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR/scripts"
D="$(python3 -c 'import datetime;print(datetime.date.today())')"
python3 step1_fetch.py   "$DIR/reports/raw_$D.json"
python3 step2_process.py "$DIR/reports/raw_$D.json" "$DIR/reports/result_$D.json"
python3 step3_output.py  "$DIR/reports/result_$D.json"
