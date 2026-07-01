"""极简 LLM 客户端：只用 urllib。参数全在 llm_config.json，key 从环境变量读。
用法: export DEEPSEEK_API_KEY=sk-...; python3 llm_client.py "你的问题"
import: from llm_client import chat; chat("问题", system="你是研究员")
"""
import sys, os, json, urllib.request

CFG = json.load(open(os.path.join(os.path.dirname(__file__), "llm_config.json"), encoding="utf-8"))


def chat(user, system=""):
    key = os.environ.get(CFG["api_key_env"], "")
    if not key:
        raise SystemExit(f"请先 export {CFG['api_key_env']}=sk-...")
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    body = json.dumps({"model": CFG["model"], "messages": msgs, "temperature": CFG.get("temperature", 0)}).encode()
    req = urllib.request.Request(CFG["base_url"], data=body,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["choices"][0]["message"]["content"].strip()


if __name__ == "__main__":
    print(chat(" ".join(sys.argv[1:])))
