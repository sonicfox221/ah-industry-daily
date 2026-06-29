"""第2步 处理：清洗 / 计算 / 筛选 / 排序。
用法: python3 step2_process.py <raw.json> [out.json]
"""
import sys
import os
from common import SKILL_DIR, read_json, write_json, today


def main():
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        SKILL_DIR, "reports", f"result_{today()}.json")
    rows = read_json(src)

    # TODO: 你的处理逻辑。占位：按 value 降序排个名。
    rows.sort(key=lambda r: r.get("value", 0), reverse=True)

    write_json(out, {"as_of": today(), "rows": rows})
    print(f"[step2] 处理 {len(rows)} 条 -> {out}")


if __name__ == "__main__":
    main()
