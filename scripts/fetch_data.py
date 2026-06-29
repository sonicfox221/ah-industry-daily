"""功能1 拉数据：
- data_source="akshare"：真实拉数。期货主力日线算近30日涨幅+最早信号日；
  财报毛利率算同比改善(同口径)；AH公司取自 universe.json 的人工映射。
- data_source="mock"：回落 data/sample_data.json，离线也能跑。
用法: python3 fetch_data.py [输出路径]
"""
import sys
import os
from common import SKILL_DIR, load_config, read_json, write_json, today


def _price_block(symbol, price_up_pct):
    """返回 (近30日涨幅%, 最早信号日期)。"""
    import pandas as pd
    import akshare as ak
    df = ak.futures_main_sina(symbol=symbol)
    df["日期"] = pd.to_datetime(df["日期"])
    df = df.sort_values("日期")
    last = df["日期"].max()
    win = df[df["日期"] >= last - pd.Timedelta(days=30)].reset_index(drop=True)
    start = float(win["收盘价"].iloc[0])
    end = float(win["收盘价"].iloc[-1])
    chg = (end - start) / start * 100
    # 最早信号：累计涨幅首次达到阈值的那天
    sig = win["日期"].iloc[-1]
    for _, r in win.iterrows():
        if (float(r["收盘价"]) - start) / start * 100 >= price_up_pct:
            sig = r["日期"]
            break
    return round(chg, 1), sig.date().isoformat()


def _margin_block(stock):
    """返回毛利率同比改善(pp)：最新报告期 vs 去年同期(同口径)。"""
    import akshare as ak
    fa = ak.stock_financial_abstract(symbol=stock)
    row = fa[fa["指标"] == "毛利率"].iloc[0]
    cols = sorted([c for c in fa.columns if c.isdigit() and len(c) == 8],
                  reverse=True)
    latest = cols[0]
    yoy = str(int(latest[:4]) - 1) + latest[4:]
    cur = float(row[latest])
    base = float(row[yoy]) if yoy in fa.columns else float(row[cols[1]])
    return round(cur - base, 1)


def fetch_akshare():
    cfg = load_config()
    up = cfg["thresholds"]["price_up_pct"]
    universe = read_json(os.path.join(SKILL_DIR, "data", "universe.json"))
    out = []
    for u in universe:
        try:
            chg, sig = _price_block(u["futures"], up)
            margin = _margin_block(u["margin_stock"])
        except Exception as e:
            print(f"  ! 跳过 {u['industry']}: {e}")
            continue
        out.append({
            "industry": u["industry"],
            "product": u["product"],
            "price_change_pct": chg,
            "margin_change_pp": margin,
            "first_signal_date": sig,
            "driver": "",
            "ah_company": u["ah_company"],
        })
        print(f"  · {u['industry']}: 涨{chg}% 毛利{margin:+}pp 信号{sig}")
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
    print(f"[fetch] source={source}, {len(data)} 个行业 -> {out_path}")


if __name__ == "__main__":
    main()
