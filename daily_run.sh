#!/usr/bin/env bash
# 每日定时入口：纯脚本五步链(含 gen_driver 调 LLM)。无需 headless AI 会话。
# 在 crontab 里调用本脚本即可：
#   30 8 * * 1-5 /Users/dengdeng/.claude/skills/ah-industry-daily/daily_run.sh
set -e
# cron 的 PATH/环境很精简：补 PATH，并从 ~/.ah_env 读 DEEPSEEK_API_KEY 等
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
[ -f "$HOME/.ah_env" ] && . "$HOME/.ah_env"   # 内含: export DEEPSEEK_API_KEY=sk-...

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SKILL_DIR/scripts"
D="$(python3 -c 'import datetime;print(datetime.date.today())')"
RAW="$SKILL_DIR/reports/raw_$D.json"
ANA="$SKILL_DIR/reports/analysis_$D.json"
REP="$SKILL_DIR/reports/report_$D.md"
LOG="$SKILL_DIR/reports/cron_$D.log"

{
  echo "===== $(date) ====="
  python3 fetch_data.py    "$RAW"
  python3 analyze.py       "$RAW" "$ANA"
  python3 gen_driver.py    "$ANA"
  python3 render_report.py "$ANA" "$REP"
  python3 notify.py        "$REP"
} >> "$LOG" 2>&1
