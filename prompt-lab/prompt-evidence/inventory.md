# 提示词版本与承载清单

本文件记录 2026-08-30 这一轮审计开始时直接观察到的版本关系。静态一致只证明文件内容相同，不证明宿主已经加载或模型会按预期行动。

## 仓库快照

| 范围 | 权威候选 | 审计开始时状态 |
| --- | --- | --- |
| Root Base 私人编写与演变 | 私人 Prompt Lab | Git `b8e33fa`，工作区干净 |
| Agent 私人编写与演变 | 本机 `agents` 仓库 | Git `0100c62`；`README.md` 和 `visual-usability-tester.toml` 有未提交修改 |
| 公开发行与共同维护材料 | 本仓库 | Git `f4b807c`，工作区在本轮新建证据文件以前干净 |
| Root 运行镜像 | `config.toml` 顶层 `developer_instructions` | 与私人 Root Base 逐字一致 |

## Root 与全局层

| 提示词 | 私人/公开/运行关系 | 快照证据 | 当前结论 |
| --- | --- | --- | --- |
| Root Base | 私人 Prompt Lab、公开 `prompt-lab/codex_base_instruction_5.6.md` 和 `config.toml` 镜像三者一致 | SHA-256 `7129a1a42c39dd1d0086e3148fd83804e104a5224a95f2a04d3839c3407a93a7` | 静态一致；fresh-task 加载和真实行为不能据此宣称完成 |
| 全局 `AGENTS.md` | 公开文件与本机运行副本一致 | SHA-256 `69ab13cde895daf1b6a9be9b74f6bffd564d70af547d5116db9166b0ad260c55` | 静态一致；规则正确性仍需历史核对 |

## Agent 层

公开仓库与本机运行副本比较覆盖 Shared Runtime Base、Worker Base 和十个 Agent TOML。

- `shared-runtime-base-instructions.md`、`worker-subagent-base-instructions.md`、`browser-operator.toml`、`code-executor.toml`、`code-reviewer.toml`、`default.toml`、`explorer.toml`、`research-lead.toml`、`web-researcher.toml`、`worker-luna.toml`、`worker.toml` 逐字一致。
- 审计开始时 `visual-usability-tester.toml` 不一致。本机 `agents` 工作区和运行副本包含尚未提交、尚未公开的 Browser/Computer Use 能力继承、范围收紧和注意力竞争观察规则。用户于 2026-08-30 确认本机文字是已认可的最新版，而非实验稿。
- 本轮已从本机最新版向公开仓库同步 `visual-usability-tester.toml` 及配套 `agents/README.md`，两份公开文件与本机候选字节一致；没有反向覆盖本机。这个结果只证明发行副本一致，真实 Luna low 黑盒行为仍为 `unverified`。

## 本仓库维护的 Skill

| 状态 | Skill |
| --- | --- |
| 公开与安装 `SKILL.md` 字节及正文一致 | `code-development`、`code-review`、`deep-research`、`eli5`、`write-instructions-zh` |
| 正文逐字符一致，仅 CRLF/LF 换行不同 | `batch-execution`、`product-development`、`workflow-route-mapper`、`workflow-state-distiller`、`xy-axis-thinking` |
| 本轮从已审计的安装副本纳入公开仓库 | `search-source-registry`；当前正文、UI 元数据、references 与 scripts 已复制，历史备份未进入发行目录 |

上述五项不是语义或版本漂移。原始 SHA-256 不同只反映换行编码不同；统一换行为 LF 后正文逐字符一致。以后版本审计同时记录字节哈希和规范化正文比较，不能只凭哈希不同宣布规则发生变化。

## 尚未进入公开仓库的本机 Skill

| Skill | 直接观察到的来源状态 | 本轮处理边界 |
| --- | --- | --- |
| `company-research-brief` | 用户为风投同事制作；有 2026-06 至 2026-08 的多份命名备份和 Prompt Lab 路由记录；用户确认已经很久未维护，可能需要重新制作 | 旧版保留并暂停普通维护；未来作为独立产品任务重新定义和验证，不直接进入当前公开体系 |
| `search-source-registry` | 用户为网络搜索 Agent 维护的通用搜索基础 Skill；有命名备份、脚本、来源注册表和实验记录 | 已完成正文、资源、脚本和历史核对并纳入本仓库；真实联网覆盖仍为 `unverified` |
| `humanizer-zh` | 第三方中文翻译/衍生包，声明来源 `blader/humanizer`、`hardikpandya/stop-slop` 和 MIT 许可 | 只记录来源和本地漂移，不重写上游规则 |
| `resume-jd-optimizer-cn` | 外部 GitHub 项目的安装副本；本地版本标记存在 `1.0.0` 与 `0.1.0` 冲突 | 保留原文，先解决来源和版本证据 |
| `playwright` | Microsoft `playwright-cli` 材料的 Codex 适配；与本机 vendor import 哈希一致 | 视为外部/官方来源，不在本轮改正文 |
| `frontend-design` | 来源未知，元数据引用的 `LICENSE.txt` 在安装目录缺失 | 保留并标为 `unknown`，不擅改 |
| `markitdown-files` | 来源未知，无本地 Git、备份或来源声明 | 保留并标为 `unknown`，不擅改 |

`xy-axis-thinking` 虽属于本仓库维护范围，但用户于 2026-08-30 明确决定保持当前正文、不再修改。除非用户以后主动恢复维护，它不进入优化、精简或重写候选，也不继续要求用户补齐历史原因。

Bundled、system、插件缓存和 OpenAI 官方 Skill 不属于本机自维护提示词审计范围。它们只有在本机副本发生明确改写或版本漂移时记录来源，不建立虚构的用户规则理由。
