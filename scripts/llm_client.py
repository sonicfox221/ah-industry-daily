import sys, os, json, urllib.request

CFG = json.load(open(os.path.join(os.path.dirname(__file__), "llm_config.json"), encoding="utf-8"))

PARAM_KEYS = ["temperature", "top_p", "max_tokens",
              "frequency_penalty", "presence_penalty", "stop", "seed", "stream"]


def chat(user, system=None):
    key = os.environ.get(CFG["api_key_env"], "")
    if not key:
        raise SystemExit(f"请先 export {CFG['api_key_env']}=sk-...")

    system = CFG.get("system_prompt", "") if system is None else system
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]

    payload = {"model": CFG["model"], "messages": msgs}
    for k in PARAM_KEYS:
        if CFG.get(k) is not None:
            payload[k] = CFG[k]

    req = urllib.request.Request(
        CFG["base_url"],
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=CFG.get("timeout", 60)) as r:
        return json.load(r)["choices"][0]["message"]["content"].strip()


if __name__ == "__main__":
    print(chat(" ".join(sys.argv[1:]) or "做自我介绍"))
