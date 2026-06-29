---
name: ah-industry-daily
description: 生成"近1个月价格明显上涨 + 毛利率明显改善的行业"日报——LLM 解释核心驱动、给出最早信号日期与最受益的 AH 上市公司，并推送到飞书。用于每日定时盯行业景气拐点。
---

# AH 行业景气日报

每天回答这个固定问题并推送：

> 列出最近 1 个月，价格有明显上涨产品和毛利率明显改善的行业，尝试解释核心驱动因素，
> 并给出最早出现相关信号的日期，并给出最受益的 AH 上市公司。

分工：**脚本产客观数字，"核心驱动因素"由 gen_driver.py 调 LLM（默认 DeepSeek，用各自的 api key）生成。**
全流程纯脚本，与前端用什么模型/CLI 无关。

## 流水线（纯脚本五步；`<date>` 用今天日期，脚本在 `scripts/` 下）

1. **`python3 fetch_data.py reports/raw_<date>.json`** — 拉数。`config.json` 的
   `data_source=akshare` 走真实接口（期货主力日线算近30日涨幅+最早信号日，财报毛利率算同比），
   `=mock` 回落 `data/sample_data.json`。

2. **`python3 analyze.py reports/raw_<date>.json reports/analysis_<date>.json`** —
   按 `thresholds` 筛出达标行业、排序。`driver` 字段先留空。

3. **`python3 gen_driver.py reports/analysis_<date>.json`** — 调 LLM（`config.ai`，默认 DeepSeek）
   为每个达标行业生成一句核心驱动因素，写回 `driver`。api key 读环境变量 `DEEPSEEK_API_KEY`；
   未设 key 或 0 达标则优雅跳过（driver 留空，不阻断）。

4. **`python3 render_report.py reports/analysis_<date>.json reports/report_<date>.md`** —
   渲染 Markdown 日报。

5. **`python3 notify.py reports/report_<date>.md`** — 推送。`notify.channel=feishu`
   时发到飞书群（正文自动带上 `keyword` 兜底关键词），否则本地落地预览。

> 一键全链路：`bash demo.sh`（设了 `DEEPSEEK_API_KEY` 才会真生成驱动，否则 driver 留空）。

## 接生产 / 分发给同事

见 `README.md`。每人只改 `config.json`：`data_source`、飞书 `webhook_url`、`keyword`、`thresholds`；
行业池在 `data/universe.json`。

## 每日定时

纯脚本链，直接系统 crontab 跑 `daily_run.sh` 即可（无需 headless AI 会话）：
```
30 8 * * 1-5 /绝对路径/ah-industry-daily/daily_run.sh
```
key 放 `~/.ah_env`（`export DEEPSEEK_API_KEY=sk-...`），`daily_run.sh` 会自动 source。详见 README.md。
