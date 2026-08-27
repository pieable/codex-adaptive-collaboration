# 运行时加载与发布

这份文档记录当前提示词加载关系、Root Base 的版本边界和可移植发布步骤。它描述机制，不保存第二份 Root 正文。

## 当前加载关系

| 层 | 安装后来源 | Root | 命名 subagent（`fork_turns: "none"`） | 维护位置 |
| --- | --- | --- | --- | --- |
| 中性运行层 | `config.toml` 的 `model_instructions_file`，指向 `agents/shared-runtime-base-instructions.md` | 加载 | 继承 | `agents/` |
| Root Base 运行镜像 | `config.toml` 顶层 `developer_instructions` | 加载 | 被命名角色正文覆盖 | `prompt-lab/` |
| 共同执行层 | `CODEX_HOME/AGENTS.md` | 加载 | 加载 | `global/AGENTS.md` 的安装副本 |
| 项目规则 | 当前任务路径适用的项目 `AGENTS.md` | 加载 | 加载 | 对应项目 |
| 角色层 | `agents/*.toml` 的 `developer_instructions` | 不适用 | 加载 | `agents/` |
| 领域方法 | 当前会话或角色配置提供的 Skill | 按触发加载 | 按触发或角色配置加载 | `skills/` |

命名角色使用 `fork_turns: "none"` 时，其 TOML `developer_instructions` 覆盖父配置中的 Root developer 镜像；父配置的 base instructions 仍会复制，因此 `model_instructions_file` 只能放所有责任层都安全的中性 Base。有限历史和 Full History 具有不同的父上下文语义，不能用 `none` 的结论描述所有 fork。

## Root Base 的权威源与运行镜像

仓库权威源：

`prompt-lab/codex_base_instruction_5.6.md`

安装后维护副本：

`{{CODEX_HOME}}/prompt-lab/codex_base_instruction_5.6.md`

运行时镜像：

`{{CODEX_HOME}}/config.toml` 顶层 `developer_instructions`

权威源用于编辑、审查、比较和回退；运行镜像只负责当前宿主加载。两份正文必须逐字一致，不能在镜像中独立维护另一套规则。

## 发布步骤

1. 只编辑 Prompt Lab 中的权威 Root Base，先检查提示词 diff 和权威层归属。
2. 保存 Root Base 及同一变更需要的架构说明。
3. 把 Root Base 全文原样写入目标 `config.toml` 的 `developer_instructions`，不改动无关配置。
4. 令 `model_instructions_file` 指向共享中性 Base，而不是 Root Base。
5. 解析最终 TOML。
6. 比较解析后的 `developer_instructions` 与权威源，要求字符长度和 SHA-256 一致。
7. 逐字符核对角色 TOML 的 Stage/Worker Base 前缀。
8. 需要证明宿主或模型实际加载时，使用全新 Root 和命名 subagent 任务验证；当前任务不会热替换已经加载的指令。

这套发布方式故意不增加 Python 同步文件、常驻进程或 Hook。复制是明确的部署动作，Git 只记录仓库中的权威源和可移植材料，避免接收者 `config.toml` 的日常变化污染提示词版本。

## 其他提示词的版本边界

共享中性 Base、Stage Base、Worker Base 和命名角色 TOML 位于 `agents/`。全局共同规则位于 `global/AGENTS.md`，按任务加载的方法位于 `skills/`。修改任何一层时先改该层自己的权威文件，再更新它实际需要的运行镜像。

静态文件一致、TOML 可解析、全新任务加载和真实行为是四种不同证据。发布报告必须明确各自验证到哪一层。
