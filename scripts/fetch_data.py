"""功能1 拉数（框架版）：对每个品种用 indicators 框架算多指标景气分 + 合成景气度，
并给出起涨拐点。指标/数据源可插拔（见 indicators.py / sources.py）。
data_source=akshare 真实拉；=mock 用 data/sample_data.json。
用法: python3 fetch_data.py [输出路径]
"""
import sys
import os
import pandas as pd
from common import SKILL_DIR, load_config, read_json, write_json, today
from sources import get_source
from indicators import Ctx, composite


def _onset(dates, vals):
    """起涨拐点：近30日窗口最低点日；首日则回看60日找真底。"""
    def win(days):
        cut = dates[-1] - pd.Timedelta(days=days)
        idx = [i for i, d in enumerate(dates) if d >= cut]
        return [dates[i] for i in idx], [vals[i] for i in idx]
    d30, v30 = win(30)
    i = v30.index(min(v30))
    if i == 0:
        d60, v60 = win(60)
        j = v60.index(min(v60))
        return d60[j].date().isoformat()
    return d30[i].date().isoformat()


def fetch_akshare():
    cfg = load_config()
    weights = cfg.get("indicator_weights", {})
    source = get_source(cfg.get("source", "akshare"))
    universe = read_json(os.path.join(SKILL_DIR, "data", "universe.json"))
    out = []
    for u in universe:
        try:
            ctx = Ctx(source, u)
            comp = composite(ctx, weights)
            d, v = ctx.price()
            onset = _onset(d, v)
        except Exception as e:
            print(f"  ! 跳过 {u['sw2']}/{u['name']}: {e}")
            continue
        out.append({
            "industry": u["sw2"],
            "product": u["name"],
            "prosperity": comp["prosperity"],
            "parts": comp["parts"],
            "first_signal_date": onset,
            "driver": "",
            "stocks": u["stocks"],
        })
        print(f"  · {u['sw2']}/{u['name']}: 景气 {comp['prosperity']}（{len(comp['parts'])} 个指标）")
    return out


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        SKILL_DIR, "reports", f"raw_{today()}.json")
    source = load_config().get("data_source", "akshare")
    if source == "akshare":
        data = fetch_akshare()
    else:
        data = read_json(os.path.join(SKILL_DIR, "data", "sample_data.json"))
    write_json(out_path, data)
    print(f"[fetch] source={source}, {len(data)} 个品种 -> {out_path}")


if __name__ == "__main__":
    main()
