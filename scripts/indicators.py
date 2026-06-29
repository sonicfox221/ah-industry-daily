"""指标框架（可插拔）：每个指标输出 0-100「景气分」（统一：越高越景气）。
加新指标 = 写个函数 + @indicator 注册；若需新数据，在 sources.py 实现对应取数方法。
权重在 config.json 的 indicator_weights 里可微调（缺省用注册时的默认权重）。
合成：行业景气总分 = 各可用指标景气分的加权平均。
"""
import pandas as pd

REGISTRY = {}


def indicator(name, label, weight=1.0):
    def deco(fn):
        REGISTRY[name] = {"fn": fn, "label": label, "weight": weight}
        return fn
    return deco


# ---------- 工具 ----------
def _win(dates, vals, days):
    cut = dates[-1] - pd.Timedelta(days=days)
    return [vals[i] for i, d in enumerate(dates) if d >= cut]


def _ret_pctile(vals, n=21):
    """近 n 交易日收益率 在 历史所有 n 日收益率 中的百分位(0-100)。"""
    if len(vals) <= n:
        return 50.0
    rets = [(vals[i] - vals[i - n]) / vals[i - n] for i in range(n, len(vals)) if vals[i - n]]
    if not rets:
        return 50.0
    cur = rets[-1]
    return round(sum(1 for r in rets if r <= cur) / len(rets) * 100, 1)


def _diff_pctile(vals, n=21):
    """近 n 日差分(适合价差/利润，可正可负) 在 历史 n 日差分 中的百分位。"""
    if len(vals) <= n:
        return 50.0
    diffs = [vals[i] - vals[i - n] for i in range(n, len(vals))]
    if not diffs:
        return 50.0
    cur = diffs[-1]
    return round(sum(1 for x in diffs if x <= cur) / len(diffs) * 100, 1)


def _level_pctile(vals):
    """当前绝对水平 在 历史水平 中的百分位。"""
    cur = vals[-1]
    return round(sum(1 for x in vals if x <= cur) / len(vals) * 100, 1)


# ---------- 第一批：数据可得，现在做实 ----------
@indicator("price_mom", "价格动量", weight=1.0)
def _price_mom(ctx):
    _, v = ctx.price()
    s = _ret_pctile(v)
    return {"score": s, "raw": f"涨幅近3年{s}分位"}


@indicator("spread_widen", "盘面利润走阔", weight=1.5)
def _spread_widen(ctx):
    d, v = ctx.spread()
    s = _diff_pctile(v)
    chg = _win(d, v, 30)
    return {"score": s, "raw": f"价差变化{chg[-1] - chg[0]:+.0f}(走阔分位{s})"}


@indicator("profit_level", "盘面利润绝对水平", weight=1.0)
def _profit_level(ctx):
    _, v = ctx.spread()
    s = _level_pctile(v)
    return {"score": s, "raw": f"利润处近3年{s}分位"}


@indicator("margin_yoy", "财报毛利同比", weight=0.5)
def _margin_yoy(ctx):
    m = ctx.financial_margin()
    if m is None:
        return None
    score = max(0.0, min(100.0, 50 + m * 5))  # 同比每 +1pp ≈ +5 分
    return {"score": round(score, 1), "raw": f"毛利同比{m:+.1f}pp"}


# ---------- 留接口：实现 sources 对应方法后自动参与 ----------
@indicator("inventory", "库存去化", weight=1.0)
def _inventory(ctx):
    inv = ctx.inventory()            # 未接数据 -> None -> 跳过
    if inv is None:
        return None
    s = 100 - _level_pctile(inv)     # 库存越低越景气(反向)
    return {"score": s, "raw": f"库存处近3年{100 - s}分位(去库)"}


@indicator("basis", "基差/期限结构", weight=1.0)
def _basis(ctx):
    b = ctx.basis()
    if b is None:
        return None
    s = _level_pctile(b)             # 升水越深越景气
    return {"score": s, "raw": f"基差分位{s}"}


@indicator("open_interest", "持仓增减", weight=0.5)
def _oi(ctx):
    oi = ctx.open_interest()
    if oi is None:
        return None
    s = _diff_pctile(oi)
    return {"score": s, "raw": f"持仓变化分位{s}"}


@indicator("valuation", "板块估值(反向)", weight=0.5)
def _valuation(ctx):
    p = ctx.valuation_pct()
    if p is None:
        return None
    s = 100 - p                      # 估值越低越有空间(反向)
    return {"score": s, "raw": f"估值分位{p}(越低越有空间)"}


# ---------- 数据访问上下文 ----------
class Ctx:
    def __init__(self, source, item):
        self.s = source
        self.item = item

    def price(self):
        return self.s.price(self.item["futures"])

    def spread(self):
        legs = self.item.get("spread") or [[self.item["futures"], 1]]
        cols = []
        for sym, c in legs:
            d, v = self.s.price(sym)
            cols.append(pd.Series(v, index=pd.DatetimeIndex(d)) * c)
        df = pd.concat(cols, axis=1, sort=True).dropna()
        sp = df.sum(axis=1)
        return list(df.index), [float(x) for x in sp]

    def financial_margin(self):
        return self.s.financial_margin_yoy(self.item["stocks"][0]["code"])

    def _try(self, fn, *a):
        try:
            return fn(*a)
        except NotImplementedError:
            return None
        except Exception:
            return None

    def inventory(self):
        return self._try(self.s.inventory, self.item["futures"])

    def basis(self):
        return self._try(self.s.basis, self.item["futures"])

    def open_interest(self):
        return self._try(self.s.open_interest, self.item["futures"])

    def valuation_pct(self):
        return self._try(self.s.valuation_pct, self.item.get("sw2", ""))


def composite(ctx, weights=None):
    """跑所有已注册指标，输出 {prosperity, parts}。weights 可覆盖默认权重。"""
    weights = weights or {}
    parts = {}
    tot_s = tot_w = 0.0
    for name, spec in REGISTRY.items():
        try:
            r = spec["fn"](ctx)
        except Exception:
            r = None
        if not r:
            continue
        w = weights.get(name, spec["weight"])
        parts[name] = {"label": spec["label"], "score": r["score"], "raw": r.get("raw", ""), "weight": w}
        tot_s += r["score"] * w
        tot_w += w
    return {"prosperity": round(tot_s / tot_w, 1) if tot_w else 0.0, "parts": parts}
