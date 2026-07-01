"""功能3 生成核心驱动（数字锚）：对"重点关注"品种，基于景气分项写一句驱动，
并标"利润扩张型/成本推动型"。
- QClaw/agent 里：可由自带模型直接读 analysis 填 driver（无需 key）。
- 纯脚本：调 llm_client（配置在 scripts/llm_config.json，key 读环境变量）；无 key/无重点品种跳过。
用法: python3 gen_driver.py <analysis.json>
"""
import sys
import os
from common import read_json, write_json
from llm_client import chat, CFG

SYS_PROMPT = (
    "你是大宗商品行业研究员。根据给定品种的景气总分与各分项指标（价格动量/盘面利润走阔/利润水平/财报毛利等）、"
    "起涨日，用一句话(40字内)解释核心驱动因素，并**必须指出**这是"
    "'利润扩张型'(盘面利润走阔分高，行业自己赚到钱)还是"
    "'成本推动型'(价格涨但利润走阔分低，利好被上游吃掉)。只输出这一句话。")


def main():
    path = sys.argv[1]
    ana = read_json(path)
    inds = [r for r in ana.get("ranking", []) if r.get("focus")]
    if not inds:
        print("[gen_driver] 无重点关注品种，跳过")
        return
    if not os.environ.get(CFG["api_key_env"]):
        print(f"[gen_driver] 未设 {CFG['api_key_env']}，driver 留空（降级；QClaw 里可由自带模型填）")
        return

    for r in inds:
        parts = "；".join(f"{p['label']}{p['score']}" for p in r.get("parts", {}).values())
        up = (f"品种：{r['industry']}/{r['product']}；景气总分 {r['prosperity']}；"
              f"分项：{parts}；起涨日 {r['first_signal_date']}。")
        try:
            r["driver"] = chat(up, system=SYS_PROMPT)
            print(f"  · {r['product']}: {r['driver']}")
        except Exception as e:
            print(f"  ! {r['product']} 生成失败(留空): {e}")

    write_json(path, ana)
    print(f"[gen_driver] 完成 -> {path}")


if __name__ == "__main__":
    main()
