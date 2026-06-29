"""功能2 分析：达标 = 涨幅历史高分位 且 盘面价差走阔（同期、量纲统一）。
按利润扩张强度排序。
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
    pmin = th.get("price_percentile_min", 90)
    need_widen = th.get("require_spread_widen", True)
    rows = read_json(raw_path)

    hits = []
    for r in rows:
        if r.get("price_percentile", 0) < pmin:
            continue
        if need_widen and r.get("spread_change", 0) <= 0:
            continue
        hits.append(r)

    # 利润扩张强度优先（价差走阔% 加权）+ 涨幅分位
    hits.sort(key=lambda r: r.get("spread_change_pct", 0) * 2 + r.get("price_percentile", 0),
              reverse=True)

    result = {
        "as_of": today(),
        "data_source": cfg.get("data_source", "akshare"),
        "thresholds": th,
        "count_total": len(rows),
        "count_hit": len(hits),
        "industries": hits,
    }
    write_json(out, result)
    print(f"[analyze] {len(hits)}/{len(rows)} 个品种达标 -> {out}")


if __name__ == "__main__":
    main()
