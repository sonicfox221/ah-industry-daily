#!/usr/bin/env bash
# 接入自检：确认依赖/配置就绪。
DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$DIR"
echo "== 接入自检 =="
command -v python3 >/dev/null && echo "✅ python3: $(python3 --version 2>&1)" || echo "❌ 缺 python3"
if [ -f config.json ]; then echo "✅ config.json"; else echo "⚠️ 缺 config.json → cp config.example.json config.json"; fi
if [ -s requirements.txt ] && grep -qv '^#' requirements.txt 2>/dev/null; then
  echo "ℹ️ 记得装依赖：pip install -r requirements.txt"
fi
echo "👉 跑一次：bash demo.sh"
