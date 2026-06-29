#!/usr/bin/env bash
# 一键装到 QClaw：探测 QClaw 自带 python -> 装依赖 -> 部署到 ~/.qclaw/skills -> 建 config。
# （通用脚本，新 skill 可直接用；检测不到 QClaw 会报错。）
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
NAME="$(basename "$SRC")"

QPY=""
for c in \
  "$HOME/Library/Application Support/QClaw/python/bin/python3" \
  "$HOME/Library/Application Support/QClaw/openclaw/config/bin/python/python3"; do
  [ -x "$c" ] && QPY="$c" && break
done
[ -z "$QPY" ] && QPY="$(find "$HOME/Library/Application Support/QClaw" -path '*python*/bin/python3' -type f 2>/dev/null | head -1)"
if [ -z "$QPY" ]; then
  echo "❌ 未发现 QClaw（找不到它的 python）。本 skill 面向 QClaw，请先安装。"
  exit 1
fi
echo "✅ QClaw python: $QPY"

if [ -s requirements.txt ] && grep -qv '^#' requirements.txt 2>/dev/null; then
  echo "装依赖..."; "$QPY" -m pip install --quiet -r requirements.txt
fi

DST="$HOME/.qclaw/skills/$NAME"
if [ "$SRC" != "$DST" ]; then
  mkdir -p "$HOME/.qclaw/skills"; rm -rf "$DST"; cp -R "$SRC" "$DST"; rm -rf "$DST/.git"
fi
[ -f "$DST/config.json" ] || cp "$DST/config.example.json" "$DST/config.json"
echo "🎉 装好了。重启 QClaw，调用 skill：$NAME"
