---
# ====== skill 元数据：QClaw / Claude Code / openclaw 读这块来"发现并路由"你的 skill ======
name: your-skill-name            # 小写连字符，建议与文件夹名一致
description: 一句话说清这个 skill 干什么、什么时候该被调用。agent 全靠这句判断要不要用它——越具体越容易被正确触发，别写空话。
version: "0.1"
trigger_keywords:                # 用户说到这些词时更易触发（QClaw 用）
  - 关键词1
  - 关键词2
metadata: {"openclaw": {"emoji": "🧩"}}
---

# <你的 Skill 名称>

一句话定位：这个 skill 帮用户做什么。

## 流水线（脚本在 `scripts/` 下，按顺序执行）

> 核心思想：**每一步是一个独立小脚本，吃上一步的输出、吐下一步的输入**（文件传递）。
> 这样每步可单独测、可替换、AI 也能在中间步骤插手。

1. **`python3 scripts/step1_fetch.py <out.json>`** — 取数：从数据源拿原始数据。
2. **`python3 scripts/step2_process.py <in.json> <out.json>`** — 处理：清洗 / 计算 / 筛选 / 排序。
3. **`python3 scripts/step3_output.py <in.json>`** — 输出：渲染结果，并（可选）推送。

> 需要 AI 在中间做判断的步骤（如生成解释），可单列一步：让 agent 读中间 JSON、用 `Edit` 填字段。

一键全流程：`bash demo.sh`

## 配置
`cp config.example.json config.json`，按需填写（数据源、推送、阈值、密钥用环境变量）。详见 `README.md`。

## 每日定时（可选）
`daily_run.sh` 挂系统 crontab，或用平台原生定时（QClaw 直接说"每天X点跑"）。

## 可扩展点（可选，复杂 skill 才需要）
- 数据源抽象：`scripts/sources.py`（换源/加源只改这里）
- 指标/规则插件：`scripts/indicators.py`（加新逻辑不动主流程）
