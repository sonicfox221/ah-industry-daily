"""功能4 渲染：盘面利润 + 历史分位 + 起涨日 + 利润扩张/成本推动 + 多标的弹性。
用法: python3 render_report.py <analysis.json> [输出路径]
"""
import sys
import os
from common import SKILL_DIR, read_json, today


def main():
    ana = read_json(sys.argv[1])
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        SKILL_DIR, "reports", f"report_{today()}.md")

    src = "akshare 实时行情" if ana.get("data_source") == "akshare" \
        else "⚠️ 样例数据(mock，非真实行情)"
    pmin = ana["thresholds"].get("price_percentile_min", 90)

    lines = [
        f"# 行业景气日报（{ana['as_of']}）",
        "",
        f"> 数据源：**{src}**",
        "",
        f"> 近 1 个月，{ana['count_total']} 个品种中 **{ana['count_hit']}** 个达标"
        f"（涨幅 ≥ 近 3 年 {pmin} 分位 **且** 盘面利润走阔）。",
        "",
    ]
    for i, r in enumerate(ana["industries"], 1):
        if r.get("has_spread"):
            typ = "利润扩张型" if r.get("spread_change", 0) > 0 else "成本推动型"
            sp = f"盘面利润价差 **{r['spread_change']:+.0f}**（**{typ}**）"
        else:
            sp = "价格代理利润（无盘面价差，**利润扩张型**）"
        lines += [
            f"## {i}. {r['industry']}（{r['product']}）",
            f"- 价格：**{r['price_change_pct']:+.0f}%**（近 3 年 **{r['price_percentile']}** 分位）",
            f"- {sp}",
            f"- 最早信号(起涨)日期：**{r['first_signal_date']}**",
            f"- 核心驱动：{r['driver'] or '（待 AI 补充）'}",
            "- 受益标的（按弹性）：",
        ]
        for s in r.get("stocks", []):
            lines.append(
                f"    - {s.get('role','')}：**{s['name']}**（{s['code']} · {s['market']}）— {s.get('why','')}")
        m = r.get("margin_change_pp")
        lines.append(f"- 财报毛利(辅助·滞后)：{('%+.1fpp' % m) if m is not None else 'NA'}")
        lines.append("")

    if not ana["industries"]:
        lines.append("_本期无品种达标（无『涨幅高分位且利润走阔』的品种）。_")

    text = "\n".join(lines)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[render] 报告 -> {out}")
    print(out)


if __name__ == "__main__":
    main()
