"""功能3 生成核心驱动（数字锚）：调 LLM（默认 DeepSeek，OpenAI 兼容）为每个达标品种
基于真实数字写一句驱动，并强制标注"利润扩张型/成本推动型"。
- 在 QClaw/agent 里跑：可由 agent 自己读 analysis 填 driver（用自带模型，无需 key）。
- 纯脚本：本脚本调 config.ai，api key 读环境变量；无 key/0 达标优雅跳过。
用法: python3 gen_driver.py <analysis.json>
"""
import sys
import os
import json
import urllib.request
from common import load_config, read_json, write_json

SYS_PROMPT = (
    "你是大宗商品行业研究员。根据给定的价格涨幅、历史分位、盘面利润价差变化、起涨日，"
    "用一句话(40字内)解释核心驱动因素，并**必须明确指出**这是"
    "'利润扩张型'(价格涨且盘面价差走阔，行业自己赚到钱)还是"
    "'成本推动型'(价格涨但价差收窄，利好被上游吃掉)。只输出这一句话。")


def call_llm(ai, key, user_prompt):
    body = json.dumps({
        "model": ai["model"],
        "messages": [
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.4,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        ai["base_url"], data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    return d["choices"][0]["message"]["content"].strip()


def main():
    path = sys.argv[1]
    ai = load_config().get("ai", {})
    key_env = ai.get("api_key_env", "DEEPSEEK_API_KEY")
    key = os.environ.get(key_env, "")

    ana = read_json(path)
    inds = ana.get("industries", [])
    if not inds:
        print("[gen_driver] 无达标品种，跳过")
        return
    if not key:
        print(f"[gen_driver] 未设 {key_env}，driver 留空（降级；在 QClaw 里可由自带模型填）")
        return

    for r in inds:
        kind = "有盘面价差" if r.get("has_spread") else "价格代理(上游)"
        up = (f"品种：{r['industry']}/{r['product']}；近30日涨幅 {r['price_change_pct']}%"
              f"（近3年 {r['price_percentile']} 分位）；盘面利润价差变化 {r.get('spread_change')}"
              f"（{kind}）；起涨日 {r['first_signal_date']}。")
        try:
            r["driver"] = call_llm(ai, key, up)
            print(f"  · {r['product']}: {r['driver']}")
        except Exception as e:
            print(f"  ! {r['product']} 生成失败(留空): {e}")

    write_json(path, ana)
    print(f"[gen_driver] 完成 -> {path}")


if __name__ == "__main__":
    main()
