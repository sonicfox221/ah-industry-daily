"""第3步 输出：渲染结果为 Markdown，并（可选）推送。
用法: python3 step3_output.py <result.json>
"""
import sys
import os
from common import SKILL_DIR, read_json, load_config, today


def main():
    data = read_json(sys.argv[1])
    lines = [f"# 结果（{data['as_of']}）", ""]
    for i, r in enumerate(data["rows"], 1):
        lines.append(f"{i}. {r.get('item')} — {r.get('value')}")
    text = "\n".join(lines)

    out = os.path.join(SKILL_DIR, "reports", f"report_{today()}.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)

    # TODO: 需要推送就读 config.notify，POST 到 webhook（或交给 QClaw 推当前渠道）。
    print(f"\n[step3] 报告 -> {out}")


if __name__ == "__main__":
    main()
