---
name: ah-industry-daily
description: 生成行业景气日报：覆盖约50个有期货的周期品种(申万二级)，用可扩展的多指标框架算景气度并排行，解释核心驱动(利润扩张/成本推动)、给出起涨日与最受益的A股或港股标的，推送当前会话渠道或飞书。每日盯行业景气拐点。
version: "1.0"
trigger_keywords:
  - 行业日报
  - 行业景气
  - 涨价
  - 毛利改善
  - AH公司
  - 景气日报
metadata: {"openclaw": {"emoji": "📈"}}
---

# AH 行业景气日报

每天回答这个固定问题并推送：

> 列出最近 1 个月，价格有明显上涨产品和毛利率明显改善的行业，尝试解释核心驱动因素，
> 并给出最早出现相关信号的日期，并给出最受益的 AH 上市公司。

分工：**脚本产客观数字，"核心驱动因素"由 gen_driver.py 调 LLM（默认 DeepSeek，用各自的 api key）生成。**
全流程纯脚本，与前端用什么模型/CLI 无关。

## 流水线（纯脚本五步；`<date>` 用今天日期，脚本在 `scripts/` 下）

1. **`python3 fetch_data.py reports/raw_<date>.json`** — 拉数 + 算景气。对每个品种用
   **指标框架**(`indicators.py` 多指标 → 0-100 景气分 → 加权合成景气总分) + 起涨拐点。
   数据源在 `sources.py`(可换/留接口)。`data_source=mock` 回落 `data/sample_data.json`。

2. **`python3 analyze.py reports/raw_<date>.json reports/analysis_<date>.json`** —
   按景气总分**排行全部品种**，≥ `prosperity_focus` 标"重点关注"。`driver` 先留空。

> 可扩展：加指标=在 `indicators.py` 写函数 `@indicator` 注册；加/换数据源=在 `sources.py` 实现方法。主流程不动。

3. **生成核心驱动因素**（按运行环境二选一）：
   - **在 QClaw / agent 里运行（推荐）**：由你（当前 AI / QClaw 自带模型）读
     `reports/analysis_<date>.json`，为每个达标行业结合涨幅/毛利/信号日写**一句**驱动解释，
     用 `Edit` 填进 `driver` 字段。这步只是把脚本已算好的数字总结成一句话，对模型要求很低，
     普通模型即可；0 达标则跳过。
   - **纯脚本 / 无人值守定时**：`python3 gen_driver.py reports/analysis_<date>.json`，
     调 `config.ai`（默认 DeepSeek，需环境变量 key）；无 key 自动跳过、driver 留空、不阻断。

4. **`python3 render_report.py reports/analysis_<date>.json reports/report_<date>.md`** —
   渲染 Markdown 日报。

5. **推送（双通道）**：
   - **默认**：把 `reports/report_<date>.md` 的内容**发到当前会话渠道**（QClaw 负责投递；
     定时用 `qclaw-cron-skill` 默认也推当前渠道）——同事零配置，在哪个群跑就推哪个群。
   - **可选**：`python3 notify.py reports/report_<date>.md` 固定推某飞书群
     （需在 config.json 把 channel 改回 `feishu` 并填 `webhook_url` + `keyword`）。

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
