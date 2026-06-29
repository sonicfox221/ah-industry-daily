"""功能3 生成报告：把分析结果渲染成 Markdown，结构对齐每日推送的提问。
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
    lines = [
        f"# 行业涨价 & 毛利改善日报（{ana['as_of']}）",
        "",
        f"> 数据源：**{src}**",
        "",
        f"> 近1个月，{ana['count_total']} 个行业中 **{ana['count_hit']}** 个同时满足"
        f"涨价≥{ana['thresholds']['price_up_pct']}% 且毛利改善≥"
        f"{ana['thresholds']['margin_improve_pp']}pp。",
        "",
    ]
    for i, r in enumerate(ana["industries"], 1):
        c = r["ah_company"]
        lines += [
            f"## {i}. {r['industry']}（{r['product']}）",
            f"- 价格：**+{r['price_change_pct']:.0f}%**　|　毛利率：**+{r['margin_change_pp']:.1f}pp**",
            f"- 最早信号日期：**{r['first_signal_date']}**",
            f"- 核心驱动：{r['driver'] or '（待 AI 补充）'}",
            f"- 最受益 AH 公司：**{c['name']}**（A {c['a_code']} / H {c['h_code']}）",
            "",
        ]
    if not ana["industries"]:
        lines.append("_本期无行业达标。_")

    text = "\n".join(lines)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[render] 报告 -> {out}")
    print(out)


if __name__ == "__main__":
    main()
