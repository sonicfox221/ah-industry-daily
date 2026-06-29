# 📈 AH 行业景气日报 · ah-industry-daily

> 每天自动扫描 **近 1 个月价格明显上涨 + 毛利率明显改善** 的行业，用 LLM 解释核心驱动因素，
> 给出最早信号日期与最受益的 **AH 上市公司**，一键推送到飞书群。

纯 Python，可作为 [Claude Code](https://claude.com/claude-code) / QClaw 的 **skill** 调用，也可直接跑脚本或挂 crontab 定时。数据来自 [akshare](https://github.com/akfamily/akshare)，驱动解释由你**自己的 LLM API**（默认 DeepSeek，可换）生成。

> 📖 **制作方法 / 方法论**（数据源、盘面价差公式与系数出处、达标逻辑、局限）见 **[METHODOLOGY.md](METHODOLOGY.md)**。

---

## ✨ 特性

- **真实数据**：期货主力连续合约近 30 日涨幅 + A 股财报毛利率同比，全部来自 akshare 实时接口。
- **AI 解释驱动**：`gen_driver.py` 调 LLM（OpenAI 兼容接口）为每个达标行业生成一句核心驱动，**接你自己的 key**，模型可换（DeepSeek / 通义 / Kimi …）。
- **飞书推送**：内置飞书群机器人推送，自带关键词兜底；也支持企业微信 / 本地落地。
- **一键定时**：纯脚本五步链，系统 crontab 即可每日自动跑，无需常驻进程。
- **零重依赖**：只需 `akshare + pandas`，LLM 调用走标准库，不装 SDK。
- **优雅降级**：没设 LLM key 也能跑，只是驱动留空，其它照常。
- **可扩展框架**：多指标景气评分(指标 `indicators.py`、数据源 `sources.py` 均可插拔，未接的数据留接口自动跳过)，输出**景气度排行榜**——加新指标/数据源不动主流程。

---

## 📋 效果示例

> 数据源：**akshare 实时行情**
>
> 近 1 个月，6 个行业中 **2** 个同时满足涨价≥5% 且毛利改善≥1pp。

```
## 1. 航运-集运（欧线集运期货 EC）
- 价格：+22%  |  毛利率：+5.0pp
- 最早信号日期：2026-06-08
- 核心驱动：红海绕行拉长航距、旺季抢运，6/8 SCFI 单周跳涨确认信号
- 最受益 AH 公司：中远海控（A 601919.SH / H 01919.HK）
```

> 实际跑出的行业/数字以当天行情为准；没有达标行业时会如实显示「本期无行业达标」。

---

## 🚀 快速开始（QClaw 一键）

```bash
git clone https://github.com/sonicfox221/ah-industry-daily.git
cd ah-industry-daily
bash install.sh
```

`install.sh` 自动：探测 **QClaw 自带 python** → 装 akshare/pandas → 部署到 `~/.qclaw/skills/` → 建 config。
（检测不到 QClaw 会报错——本 skill 面向 QClaw。）

然后**重启 QClaw**，说一句：

> 生成今天的行业景气日报

报告就推到你**当前会话渠道**。要每天自动 —— 在 QClaw 说：

> 每个交易日早上 8:30 生成行业景气日报

> 驱动因素用 **QClaw 自带模型**生成，**无需任何 key**；想把日报固定推到某个飞书群，见下方「推送」。

## 通用命令行（非 QClaw 用户）

```bash
pip install -r requirements.txt
bash demo.sh    # 报告生成到 reports/；driver 需 export DEEPSEEK_API_KEY 才生成
```

---

## ⚙️ 配置说明（config.json）

| 字段 | 说明 |
|---|---|
| `data_source` | `akshare`=真实拉数 / `mock`=用 `data/sample_data.json` 离线样例 |
| `notify.channel` | `feishu` / `wecom`（企业微信）/ `file`（仅本地落地不推送） |
| `notify.webhook_url` | 你的群机器人地址 |
| `notify.keyword` | 飞书自定义关键词兜底，需与飞书机器人设置一致 |
| `thresholds.price_up_pct` | 涨价入选门槛（%） |
| `thresholds.margin_improve_pp` | 毛利改善入选门槛（百分点） |
| `ai.base_url` / `ai.model` | LLM 接口与模型（OpenAI 兼容，换模型改这里） |
| `ai.api_key_env` | 读哪个环境变量当 api key（默认 `DEEPSEEK_API_KEY`） |
| `data/universe.json` | 行业 ↔ 期货品种 ↔ 龙头股（算毛利）↔ AH 公司 映射，按需增删 |

---

## 🧩 工作原理（纯脚本五步）

```
fetch_data.py   →  拉数：期货主力日线算近30日涨幅+最早信号日，财报毛利率算同比
analyze.py      →  按 thresholds 筛出达标行业、排序
gen_driver.py   →  调 LLM 为每个达标行业生成一句“核心驱动因素”
render_report.py→  渲染 Markdown 日报
notify.py       →  推送飞书（或企业微信 / 本地落地）
```

`demo.sh` 把这五步串起来；`daily_run.sh` 是给 crontab 的定时入口（同样五步 + 日志 + 自动读 key）。

---

## 📊 数据来源与口径（请务必了解）

数据是**真实**的，但属于**扫描级、非投研级**精度：

- **涨幅** 用期货「主力连续合约」近 30 日，换月时可能有价差失真；
- **毛利改善** 用财报毛利率**同比**（季报口径，季度才更新一次），与「近 1 个月价格」非同一时间窗，是近似；
- **最早信号日期** 是价格累计涨幅破阈值的那天，属技术信号，非基本面事件溯源。

👉 适合做**每日初筛提示**，落地投资动作前请人工复核。

---

## ⏰ 每日定时（本地 crontab）

`daily_run.sh` 是纯脚本五步链，无需常驻进程。

```bash
echo 'export DEEPSEEK_API_KEY=sk-...' >> ~/.ah_env
crontab -e
# 加一行（每个交易日 8:30，本机时区）：
30 8 * * 1-5 ~/.claude/skills/ah-industry-daily/daily_run.sh
```

日志写到 `reports/cron_<日期>.log`。停掉就 `crontab -e` 删那行。
（`1-5` 是周一至周五，不排除 A 股节假日，节假日照跑但当天无新数据、基本无达标。）

---

## 🛠 自定义

- **加/减行业**：编辑 `data/universe.json`（行业、期货品种代码、算毛利的龙头股、AH 公司）。
- **调门槛**：改 `config.json` 的 `thresholds`。
- **换模型**：改 `config.json` 的 `ai.base_url` / `ai.model` / `ai.api_key_env`（任意 OpenAI 兼容接口）。
- **换推送**：`notify.channel` 改 `wecom`（企业微信）或 `file`（只生成本地报告不推送）。
- **改驱动文风**：编辑 `scripts/gen_driver.py` 里的 `SYS_PROMPT`。

---

## 📁 目录结构

```
ah-industry-daily/
├── SKILL.md             # skill 定义 / 流水线说明
├── README.md            # 本文档
├── config.example.json  # 配置模板（拷成 config.json 再填）
├── requirements.txt     # 依赖：akshare + pandas
├── setup_check.sh       # 接入自检
├── demo.sh              # 一键跑全链路
├── daily_run.sh         # 定时入口（纯脚本五步链）
├── data/
│   ├── universe.json    # 行业映射表
│   └── sample_data.json # mock 离线样例
└── scripts/
    ├── common.py        # 共享工具
    ├── fetch_data.py    # ① 拉数
    ├── analyze.py       # ② 筛选
    ├── gen_driver.py    # ③ LLM 生成驱动
    ├── render_report.py # ④ 渲染
    └── notify.py        # ⑤ 推送
```

---

## ❓ FAQ

**Q：没有 LLM key 能用吗？**
A：能。`gen_driver` 会优雅跳过，驱动因素留空，其它步骤照常。

**Q：经常显示「本期无行业达标」？**
A：这是真实结论——市场上确实没有同时"涨价 + 毛利改善"的行业时就会这样，不是 bug。想看到内容可适当调低 `thresholds`（但那是放水）。

**Q：飞书报错 `Key Words Not Found`？**
A：飞书机器人的自定义关键词没和 `config.json` 的 `keyword` 对齐。两边都设成 `日报` 即可（报告标题恒含"日报"）。

**Q：能换企业微信 / 钉钉吗？**
A：企业微信改 `notify.channel=wecom` 即用；钉钉等改 `notify.py` 里的请求体格式（都是往一个 webhook POST JSON）。

**Q：数据准吗？**
A：真实但属扫描级，见上方「数据来源与口径」。

---

## ⚠️ 免责声明

本项目仅用于行业景气的**初筛与信息提示**，不构成任何投资建议。数据可能存在口径误差，请自行核实，据此操作风险自负。

## License

可自行添加（如 MIT）。
