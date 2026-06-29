"""共享小工具：定位 skill 根目录、读配置。各脚本都引用它，保持简单。"""
import json
import os

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config():
    with open(os.path.join(SKILL_DIR, "config.json"), encoding="utf-8") as f:
        return json.load(f)


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def today():
    import datetime
    return datetime.date.today().isoformat()
