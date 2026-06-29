"""功能4 推送：
- channel=feishu：POST 到飞书群机器人(纯文本)。
- channel=wecom：POST 到企业微信群机器人(markdown)。
- 否则 / URL 未填：回落到本地落地 + 打印预览(离线也能跑)。
用法: python3 notify.py <report.md>
"""
import sys
import os
from common import SKILL_DIR, load_config, today


def _post(url, payload):
    import json
    import urllib.request
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        print(f"[notify] 已推送, HTTP {r.status}: {r.read().decode()[:120]}")


def main():
    md_path = sys.argv[1]
    with open(md_path, encoding="utf-8") as f:
        content = f.read()

    nf = load_config()["notify"]
    channel = nf.get("channel", "file")
    url = nf.get("webhook_url", "")

    # 飞书"自定义关键词"校验兜底：保证每条消息都含 keyword
    kw = nf.get("keyword", "")
    if kw and kw not in content:
        content = f"{kw}\n{content}"

    if url.startswith("http"):
        if channel == "feishu":
            _post(url, {"msg_type": "text", "content": {"text": content}})
            return
        if channel == "wecom":
            _post(url, {"msgtype": "markdown",
                        "markdown": {"content": content}})
            return

    # 回落：写"已发送"标记 + 打印预览
    marker = os.path.join(SKILL_DIR, "reports", f"SENT_{today()}.txt")
    with open(marker, "w", encoding="utf-8") as f:
        f.write(f"would push {md_path} via channel={channel}\n")
    print(f"[notify] (未配置 webhook) 已落地标记 -> {marker}")
    print("---- 推送内容预览 ----")
    print(content)


if __name__ == "__main__":
    main()
