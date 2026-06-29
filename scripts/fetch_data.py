"""功能1 拉数（升级版）：
- 主信号：盘面价差/利润（spread legs 线性组合，与涨价同频），只看变化；上游品种用价格自身。
- 显著性：近30日涨幅在该品种近3年滚动涨幅里的历史分位。
- 起涨拐点：近30日窗口最低点（首日则往前看60日找真底）。
- 财报毛利率同比：降为辅助验证（取不到返回 None，不阻断）。
data_source=akshare 真实拉；=mock 用 data/sample_data.json。
用法: python3 fetch_data.py [输出路径]
"""
import sys
import os
import pandas as pd
from common import SKILL_DIR, load_config, read_json, write_json, today

_cache = {}


def _series(symbol):
    if symbol in _cache:
        return _cache[symbol]
    import akshare as ak
    df = ak.futures_main_sina(symbol=symbol)
    df["日期"] = pd.to_datetime(df["日期"])
    df = df.sort_values("日期").reset_index(drop=True)
    res = (list(df["日期"]), [float(x) for x in df["收盘价"]])
    _cache[symbol] = res
    return res


def _win(dates, vals, days):
    cut = dates[-1] - pd.Timedelta(days=days)
    idx = [i for i, d in enumerate(dates) if d >= cut]
    return [dates[i] for i in idx], [vals[i] for i in idx]


def _pct30(dates, vals):
    _, v = _win(dates, vals, 30)
    return (v[-1] - v[0]) / v[0] * 100 if v[0] else 0.0


def _percentile(vals, n=21):
    """近30日(≈21交易日)涨幅在历史所有滚动涨幅中的百分位 0-100。"""
    if len(vals) <= n:
        return 50.0
    rets = [(vals[i] - vals[i - n]) / vals[i - n] for i in range(n, len(vals)) if vals[i - n]]
    if not rets:
        return 50.0
    cur = rets[-1]
    return round(sum(1 for r in rets if r <= cur) / len(rets) * 100, 1)


def _onset(dates, vals):
    """起涨拐点：近30日窗口最低点日；最低点在首日则往前看60日找真底。"""
    d30, v30 = _win(dates, vals, 30)
    i = v30.index(min(v30))
    if i == 0:
        d60, v60 = _win(dates, vals, 60)
        j = v60.index(min(v60))
        return d60[j].date().isoformat()
    return d30[i].date().isoformat()


def _spread(legs):
    """价差序列：对齐各腿日期后 Σ coef×price。返回 (dates, vals)。"""
    cols = []
    for sym, coef in legs:
        d, v = _series(sym)
        cols.append(pd.Series(v, index=pd.DatetimeIndex(d)) * coef)
    df = pd.concat(cols, axis=1, sort=True).dropna()
    sp = df.sum(axis=1)
    return list(df.index), [float(x) for x in sp]


def _margin_yoy(stock):
    """财报毛利率同比(pp)，辅助；取不到返回 None。"""
    try:
        import akshare as ak
        fa = ak.stock_financial_abstract(symbol=stock)
        if fa is None or fa.empty:
            return None
        sub = fa[fa["指标"] == "毛利率"]
        if sub.empty:
            return None
        row = sub.iloc[0]
        cols = sorted([c for c in fa.columns if c.isdigit() and len(c) == 8], reverse=True)
        latest = cols[0]
        yoy = str(int(latest[:4]) - 1) + latest[4:]
        cur = float(row[latest])
        base = float(row[yoy]) if yoy in fa.columns else float(row[cols[1]])
        return round(cur - base, 1)
    except Exception:
        return None


def fetch_akshare():
    universe = read_json(os.path.join(SKILL_DIR, "data", "universe.json"))
    out = []
    for u in universe:
        try:
            dates, vals = _series(u["futures"])
            chg = _pct30(dates, vals)
            pctile = _percentile(vals)
            onset = _onset(dates, vals)
            legs = u.get("spread") or [[u["futures"], 1]]
            sd, sv = _spread(legs)
            _, spw = _win(sd, sv, 30)
            sp_chg = spw[-1] - spw[0]
            sp_chg_pct = (sp_chg / abs(spw[0]) * 100) if spw[0] else 0.0
            margin = _margin_yoy(u["stocks"][0]["code"])
        except Exception as e:
            print(f"  ! 跳过 {u['sw2']}/{u['name']}: {e}")
            continue
        out.append({
            "industry": u["sw2"],
            "product": u["name"],
            "price_change_pct": round(chg, 1),
            "price_percentile": pctile,
            "spread_change": round(sp_chg, 1),
            "spread_change_pct": round(sp_chg_pct, 1),
            "has_spread": bool(u.get("spread")),
            "first_signal_date": onset,
            "margin_change_pp": margin,
            "driver": "",
            "stocks": u["stocks"],
        })
        tag = "" if u.get("spread") else "(价格代理)"
        print(f"  · {u['sw2']}/{u['name']}: 涨{chg:+.1f}% 分位{pctile} 价差{sp_chg:+.0f}{tag}")
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
