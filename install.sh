#!/usr/bin/env bash
# 一键安装到 QClaw：探测 QClaw 自带 python → 装依赖 → 部署 skill → 建配置。
# 用法：git clone 后，cd 进目录，bash install.sh
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"

echo "== 1/4 探测 QClaw 自带 python =="
QPY=""
for c in \
  "$HOME/Library/Application Support/QClaw/python/bin/python3" \
  "$HOME/Library/Application Support/QClaw/openclaw/config/bin/python/python3"; do
  [ -x "$c" ] && QPY="$c" && break
done
[ -z "$QPY" ] && QPY="$(find "$HOME/Library/Application Support/QClaw" -path '*python*/bin/python3' -type f 2>/dev/null | head -1)"
if [ -z "$QPY" ]; then
  echo "❌ 未发现 QClaw（找不到它的 python）。"
  echo "   本 skill 面向 QClaw（腾讯）。请先安装 QClaw 后再运行本脚本。"
  echo "   想用命令行方式：见 README「通用命令行」一节。"
  exit 1
fi
echo "✅ QClaw python: $QPY"

echo "== 2/4 装依赖 akshare + pandas（一两分钟）=="
"$QPY" -m pip install --quiet akshare pandas

echo "== 3/4 部署 skill 到 ~/.qclaw/skills =="
DST="$HOME/.qclaw/skills/ah-industry-daily"
if [ "$SRC" != "$DST" ]; then
  mkdir -p "$HOME/.qclaw/skills"
  rm -rf "$DST"; cp -R "$SRC" "$DST"; rm -rf "$DST/.git"
fi
echo "✅ 已部署到 $DST"

echo "== 4/4 初始化配置 =="
[ -f "$DST/config.json" ] || cp "$DST/config.example.json" "$DST/config.json"
echo "✅ config.json 就绪（默认本地出报告 + 由 QClaw 推当前会话渠道；要固定推某飞书群，填 config.json 的 webhook_url 并把 channel 改回 feishu）"

echo
echo "🎉 装好了！重启 QClaw，然后说一句："
echo "     生成今天的行业景气日报"
echo "   要每天自动：在 QClaw 说「每个交易日早上 8:30 生成行业景气日报」"
