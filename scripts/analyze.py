"""功能2 分析：按阈值筛出"价格明显上涨 + 毛利明显改善"的行业，
按改善强度排序，标出最早信号日期与最受益 AH 公司。
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
    rows = read_json(raw_path)

    hits = [
        r for r in rows
        if r["price_change_pct"] >= th["price_up_pct"]
        and r["margin_change_pp"] >= th["margin_improve_pp"]
    ]
    # 综合强度 = 涨价幅度 + 毛利改善(放大权重)，从高到低
    hits.sort(key=lambda r: r["price_change_pct"] + r["margin_change_pp"] * 2,
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
    print(f"[analyze] {len(hits)}/{len(rows)} 个行业入选 -> {out}")


if __name__ == "__main__":
    main()
