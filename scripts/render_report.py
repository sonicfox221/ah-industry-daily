"""功能4 渲染（指导性排行）：重点关注详列（分项景气+起涨+驱动+多标的）+ 完整排行榜。
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
    focus_min = ana["thresholds"].get("prosperity_focus", 70)
    rk = ana["ranking"]

    lines = [
        f"# 行业景气日报（{ana['as_of']}）",
        "",
        f"> 数据源：**{src}**",
        "",
        f"> {ana['count_total']} 个周期品种景气度排行（0–100，多指标加权）；"
        f"**≥{focus_min} 为重点关注**，本期 **{ana['count_focus']}** 个。",
        "",
        "## 🔥 重点关注",
    ]
    focus = [r for r in rk if r.get("focus")]
    if not focus:
        lines.append("_本期无 ≥ 阈值的重点品种，见下方完整排行(关注靠前的)。_")
    for i, r in enumerate(focus, 1):
        parts = r.get("parts", {})
        lines += [
            f"### {i}. {r['industry']}（{r['product']}）— 景气 **{r['prosperity']}**",
            f"- 最早信号(起涨)：**{r['first_signal_date']}**",
            f"- 核心驱动：{r.get('driver') or '（待 AI 补充）'}",
            "- 景气分项：" + "；".join(
                f"{p['label']} {p['score']}" for p in parts.values()),
            "- 受益标的（按弹性）：",
        ]
        for s in r.get("stocks", []):
            lines.append(
                f"    - {s.get('role','')}：**{s['name']}**（{s['code']}·{s['market']}）— {s.get('why','')}")
        lines.append("")

    # 完整排行榜（Top 20）
    lines += [
        "## 📊 完整景气排行（Top 20）",
        "",
        "| # | 行业 | 品种 | 景气 | 价格动量 | 利润走阔 | 利润水平 |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(rk[:20], 1):
        p = r.get("parts", {})
        def g(k):
            return p.get(k, {}).get("score", "-")
        lines.append(
            f"| {i} | {r['industry']} | {r['product']} | **{r['prosperity']}** | "
            f"{g('price_mom')} | {g('spread_widen')} | {g('profit_level')} |")

    text = "\n".join(lines)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[render] 报告 -> {out}")
    print(out)


if __name__ == "__main__":
    main()
