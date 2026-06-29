"""第1步 取数：从数据源拿原始数据，写出 JSON。把 TODO 换成你的真实取数。
用法: python3 step1_fetch.py [out.json]
"""
import sys
import os
from common import SKILL_DIR, load_config, write_json, today


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        SKILL_DIR, "reports", f"raw_{today()}.json")
    cfg = load_config()

    # TODO: 在这里取你的数据（调 API / 读库 / 爬虫 / 本地文件）。
    #       data_source=mock 时可回退到本地样例，方便离线开发。
    data = [{"item": "示例A", "value": 42}, {"item": "示例B", "value": 17}]

    write_json(out, data)
    print(f"[step1] 取到 {len(data)} 条 -> {out}")


if __name__ == "__main__":
    main()
