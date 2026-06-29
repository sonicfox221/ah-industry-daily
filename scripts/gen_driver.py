"""功能3 生成核心驱动因素：调 LLM(默认 DeepSeek，OpenAI 兼容接口)为每个达标行业
写一句驱动解释，写回 analysis 的 driver 字段。
- api key 从环境变量读(见 config.ai.api_key_env)，不写进 config，避免泄露。
- 无 key / 无达标行业 / 调用失败时优雅跳过(driver 留空)，不阻断流水线。
用法: python3 gen_driver.py <analysis.json>
"""
import sys
import os
import json
import urllib.request
from common import load_config, read_json, write_json

SYS_PROMPT = ("你是A股行业研究员。根据给定行业的近期涨价幅度、毛利率同比变化、最早信号日期，"
              "用一句话(40字内)精炼解释其价格上涨与毛利改善的核心驱动因素，可点出最早信号的事件线索。"
              "只输出这一句话，不要前后缀。")


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
        print("[gen_driver] 无达标行业，跳过")
        return
    if not key:
        print(f"[gen_driver] 未设环境变量 {key_env}，driver 留空(降级，不影响其它步骤)")
        return

    for r in inds:
        up = (f"行业：{r['industry']}（{r['product']}）；近30日涨幅 {r['price_change_pct']}%；"
              f"毛利率同比 {r['margin_change_pp']:+}pp；最早信号日 {r['first_signal_date']}；"
              f"代表 AH 公司 {r['ah_company']['name']}。")
        try:
            r["driver"] = call_llm(ai, key, up)
            print(f"  · {r['industry']}: {r['driver']}")
        except Exception as e:
            print(f"  ! {r['industry']} 生成失败(driver 留空): {e}")

    write_json(path, ana)
    print(f"[gen_driver] 完成 -> {path}")


if __name__ == "__main__":
    main()
