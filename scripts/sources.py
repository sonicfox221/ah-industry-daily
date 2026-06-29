"""数据源层（provider）：统一对上提供各类数据。换源/加源只改这里。
- 已实现：期货价格、财报毛利率同比。
- 留接口（raise NotImplementedError）：库存、基差、持仓、板块估值、开工率…
  以后在这里实现对应方法即自动生效（对应指标会从"跳过"变成"参与景气评分"）。
加新数据源：再写一个 class 实现同名方法，注册到 SOURCES 即可。
"""
import pandas as pd


class AkshareSource:
    name = "akshare"

    def __init__(self):
        self._cache = {}

    # ---- 已实现 ----
    def price(self, symbol):
        """期货主力连续日线 -> (dates, closes)，带缓存。"""
        if symbol in self._cache:
            return self._cache[symbol]
        import akshare as ak
        df = ak.futures_main_sina(symbol=symbol)
        df["日期"] = pd.to_datetime(df["日期"])
        df = df.sort_values("日期").reset_index(drop=True)
        res = (list(df["日期"]), [float(x) for x in df["收盘价"]])
        self._cache[symbol] = res
        return res

    def financial_margin_yoy(self, stock):
        """财报毛利率同比(pp)，取不到返回 None。"""
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

    # ---- 留接口：实现后对应指标自动参与评分 ----
    def inventory(self, symbol):
        raise NotImplementedError("库存/仓单数据源待接")

    def basis(self, symbol):
        raise NotImplementedError("基差/期限结构数据源待接")

    def open_interest(self, symbol):
        raise NotImplementedError("持仓量数据源待接")

    def valuation_pct(self, sw_code):
        raise NotImplementedError("板块估值分位数据源待接")

    def utilization(self, symbol):
        raise NotImplementedError("开工率/产能利用率数据源待接")


SOURCES = {"akshare": AkshareSource}


def get_source(name="akshare"):
    return SOURCES[name]()
