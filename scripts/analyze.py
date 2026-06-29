"""功能2 分析（指导性）：按景气总分排行全部品种，标记"重点关注"(≥阈值)。
用法: python3 analyze.py <raw.json> [输出路径]
"""
import sys
import os
from common import SKILL_DIR, load_config, read_json, write_json, today


def main():
    raw_path = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        SKILL_DIR, "reports", f"analysis_{today()}.json")

    cfg = load_config()
    th = cfg["thresholds"]
    focus_min = th.get("prosperity_focus", 70)
    rows = read_json(raw_path)

    rows.sort(key=lambda r: r.get("prosperity", 0), reverse=True)
    for r in rows:
        r["focus"] = r.get("prosperity", 0) >= focus_min

    result = {
        "as_of": today(),
        "data_source": cfg.get("data_source", "akshare"),
        "thresholds": th,
        "count_total": len(rows),
        "count_focus": sum(1 for r in rows if r["focus"]),
        "ranking": rows,
    }
    write_json(out, result)
    print(f"[analyze] {result['count_focus']}/{len(rows)} 个重点关注 -> {out}")


if __name__ == "__main__":
    main()
