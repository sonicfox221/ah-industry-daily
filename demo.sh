#!/usr/bin/env bash
# demo：把 skill 的 5 个功能串成一条流水线全部跑一遍。
# gen_driver 需设环境变量 DEEPSEEK_API_KEY 才会真生成驱动；没设则 driver 留空(降级)。
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR/scripts"
D="$(python3 -c 'import datetime;print(datetime.date.today())')"
RAW="$DIR/reports/raw_$D.json"
ANA="$DIR/reports/analysis_$D.json"
REP="$DIR/reports/report_$D.md"

echo "== 1/5 fetch =="      && python3 fetch_data.py    "$RAW"
echo "== 2/5 analyze =="    && python3 analyze.py       "$RAW" "$ANA"
echo "== 3/5 gen_driver ==" && python3 gen_driver.py    "$ANA"
echo "== 4/5 render =="     && python3 render_report.py "$ANA" "$REP"
echo "== 5/5 notify =="     && python3 notify.py        "$REP"
echo "== done: $REP =="
