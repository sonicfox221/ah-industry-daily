# 如何构建一个完整的 skill（构建指南）

这份文档讲清"**一个规范的 skill 由哪些部分组成、怎么从 0 搭起来**"。
- **空脚手架**：`_TEMPLATE/`（copy 一份改名就能开工）
- **参考实现**：本仓库根目录的 `ah-industry-daily`（一个填满的真实例子）

> 适用于 QClaw / Claude Code / openclaw 这类"读 SKILL.md 的 agent 客户端"。

---

## 一、一个完整 skill 的组成

```
your-skill/
├── SKILL.md            # 【必须】skill 定义：frontmatter(元数据) + 流水线说明。客户端靠它发现/路由
├── skill.yaml          # 【可选】通用 manifest 兼容层，给认 yaml 的平台
├── config.example.json # 【建议】配置模板，拷成 config.json 再填（私密信息不入库）
├── requirements.txt    # 【按需】Python 依赖
├── scripts/            # 【核心】功能脚本，一步一个
│   ├── common.py       #   共享工具（定位目录、读写 JSON）
│   ├── step1_fetch.py  #   取数
│   ├── step2_process.py#   处理
│   └── step3_output.py #   输出/推送
├── data/               # 【按需】静态数据/映射表/样例
├── reports/            # 运行产物（.gitignore 掉）
├── install.sh          # 【建议】一键装（探测 QClaw python→装依赖→部署）
├── demo.sh             # 【建议】一键跑全流程
├── daily_run.sh        # 【可选】定时入口
├── setup_check.sh      # 【可选】接入自检
├── .gitignore          # 【建议】挡掉 config.json / reports / 密钥
└── README.md           # 【建议】怎么用
```

**最小可用 skill**：只需 `SKILL.md` + `scripts/`。其余按需加。

---

## 二、从 0 构建（5 步）

```bash
# 1. 拷脚手架、改名
cp -R _TEMPLATE my-skill && cd my-skill

# 2. 改 SKILL.md 的 frontmatter（name/description/trigger_keywords）—— 见下方"关键规范"

# 3. 填 scripts/ 三步：step1 取你的数据、step2 你的处理、step3 你的输出

# 4. 配置
cp config.example.json config.json   # 填数据源/推送；密钥用环境变量

# 5. 跑通
bash setup_check.sh && bash demo.sh
```

装到 QClaw：`bash install.sh` → 重启 QClaw → 说触发词调用。

---

## 三、关键规范（踩过坑的）

### 1. SKILL.md frontmatter —— 决定"能不能被正确调用"
```yaml
---
name: my-skill                  # 小写连字符，和文件夹同名
description: 一句话说清干啥、何时调用。   # ★最重要：agent 全靠它判断要不要用你
trigger_keywords: [词1, 词2]     # 用户说到就触发
metadata: {"openclaw": {"emoji": "🧩"}}
---
```
**description 要具体**（"生成A股周期行业景气日报"而不是"分析股票"），否则要么不触发、要么乱触发。

### 2. 流水线 = 一步一个脚本，文件传递
每步吃上一步的输出 JSON、吐下一步的输入 JSON。好处：**每步可单独测、可替换、AI 能在中间步骤插手**（比如让 agent 读中间 JSON、写一个解释字段再继续）。

### 3. 配置与密钥
- 可调的东西放 `config.json`（阈值、渠道、开关）——**不改代码就能调**。
- **密钥绝不写进文件**：放环境变量，`config` 里只写"读哪个环境变量名"。
- `config.json` 进 `.gitignore`，只提交 `config.example.json`。

### 4. 推送
- 最省事：`channel=file` 出本地报告（零配置可跑）。
- 群机器人：POST webhook（飞书/企微/钉钉）。
- 在 QClaw 里：可让 agent 直接把结果推到当前会话渠道，免配置。

### 5. 安装（QClaw 专属坑）
QClaw 自带一个 **独立 python**（`~/Library/Application Support/QClaw/python/bin/python3`），**默认没有你的依赖**。`install.sh` 会探测它并 `pip install`——**这是新人最容易踩的坑**，务必用 install.sh 而不是手动。

### 6. 定时
- 通用：系统 crontab 调 `daily_run.sh`。
- QClaw：直接说"每天 X 点跑"，它的 cron-skill 接管。

---

## 四、进阶：可扩展（复杂 skill 才需要，别过度）

当 skill 会长期演进、要不断加新逻辑/数据源时，引入两层抽象（见参考实现的 `scripts/indicators.py` + `sources.py`）：

- **数据源抽象 `sources.py`**：所有取数走一个 provider 接口；换源/加源只改这里；没接的数据 `raise NotImplementedError`，**留接口**。
- **逻辑插件 `indicators.py`**：每个指标/规则 `@indicator` 注册，输出统一格式；**加新逻辑只加一个函数，主流程不动**。

> ⚠️ 简单 skill 不要上这套——三步脚本足够。过度抽象违背"保持简单"。

---

## 五、测试与交付

1. `bash setup_check.sh` —— 依赖/配置就绪？
2. `bash demo.sh` —— 整条链跑通、产出对不对？
3. `bash install.sh` —— 装到 QClaw，重启后能否被发现并调用？
4. 推 GitHub（`.gitignore` 确保 config.json/密钥不外泄）。
5. 写 `README.md`（怎么用）；复杂逻辑再写 `METHODOLOGY.md`（怎么做的）。

---

## 六、设计原则（来自这个项目的真实迭代）

1. **保持简单**：能三步脚本搞定就别上框架。
2. **诚实**：数据有口径限制就在报告里写明；做不到的留接口、别假装。
3. **配置驱动**：会变的进 config，别写死。
4. **密钥外置**：环境变量，永不入库。
5. **可扩展但不过度**：留接口 ≠ 现在就实现；框架是为"会长期加东西"准备的。
6. **客户端解耦**：脚本是纯 Python，跟用哪个 agent 客户端/哪个模型无关。

---

照着 `_TEMPLATE/` 起步、对着 `ah-industry-daily` 参考，就能搭出一个结构规范、可装可跑可定时、能扩展的 skill。
