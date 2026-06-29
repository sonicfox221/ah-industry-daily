#!/usr/bin/env bash
# 新环境(同事)接入自检：确认依赖/配置就绪。在 skill 目录下 bash setup_check.sh
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
ok=1
echo "== ah-industry-daily 接入自检 =="

if command -v python3 >/dev/null; then echo "✅ python3: $(python3 --version 2>&1)"; else echo "❌ 缺 python3"; ok=0; fi

if python3 -c "import akshare, pandas" 2>/dev/null; then
  echo "✅ akshare + pandas 已装"
else
  echo "❌ 依赖未装 → pip install -r requirements.txt"; ok=0
fi

if [ -f config.json ]; then
  echo "✅ config.json 存在"
  if grep -q "PUT_YOUR_FEISHU" config.json; then echo "⚠️ 飞书 webhook 还没填(config.json)"; else echo "✅ 飞书 webhook 已填"; fi
else
  echo "❌ 缺 config.json → cp config.example.json config.json 再填飞书"; ok=0
fi

if [ -n "$DEEPSEEK_API_KEY" ]; then echo "✅ DEEPSEEK_API_KEY 已设"; else echo "⚠️ DEEPSEEK_API_KEY 未设(driver 会留空) → export DEEPSEEK_API_KEY=sk-..."; fi

echo
if [ "$ok" = 1 ]; then echo "👉 核心就绪，跑一次：bash demo.sh"; else echo "👉 先解决上面的 ❌ 项再跑。"; fi
