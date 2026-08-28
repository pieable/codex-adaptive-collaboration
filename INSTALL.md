# 给安装 AI 的任务合同

把本仓库合并安装到当前用户真实使用的 `CODEX_HOME`，使 Root Base、共同执行层、Worker Base、两个自包含阶段角色、十个命名角色和十个体系 Skill 在新任务中可用。

## 目标与边界

- 先解析当前环境真实使用的 `CODEX_HOME`，不要根据仓库作者的路径猜测；
- 保留接收者已有且与本体系无关的配置、Agents、Skills、MCP、插件和项目资料；
- 写入前备份所有将被创建、替换或合并的文件，以及原始 `config.toml`；
- 不复制仓库之外的备份、会话、缓存、账户数据或凭据；
- 模型不可用、同名文件无法安全合并、真实加载机制与本文不符或需要扩大权限时，停止相应写入并报告具体矛盾；
- 不增加 Python 同步程序、常驻进程或 Hook 来拼接提示词。

## 安装步骤

1. 读取 [`examples/config.toml`](examples/config.toml)、`prompt-lab/`、`global/AGENTS.md`、`agents/` 和 `skills/`，确认仓库结构完整。
2. 在 `CODEX_HOME` 下创建 `prompt-lab`、`agents`、`skills` 和独立备份目录。
3. 复制 `prompt-lab/` 中的 Root Base 与公开维护材料。
4. 复制 `agents/` 中的共享中性 Base、Worker Base、十份角色 TOML 和维护说明。
5. 复制 `skills/` 下十个体系 Skill 的完整目录。
6. 把 `global/AGENTS.md` 的共同执行层合并到 `CODEX_HOME/AGENTS.md`。保留已有无关内容，已经存在的相同规则不重复写入。
7. 把示例中出现的 `{{CODEX_HOME}}` 替换为真实绝对路径。
8. 合并 `config.toml`：
   - 保留无关顶层配置；
   - 按用户确认的模型映射设置 Root 模型与推理强度；
   - 令 `model_instructions_file` 指向 `agents/shared-runtime-base-instructions.md`；
   - 把 `prompt-lab/codex_base_instruction_5.6.md` 的正文逐字写入顶层 `developer_instructions`，替换示例中的 `{{ROOT_BASE_CONTENT}}`；
   - 设置或确认 `[agents]` 的深度与并发限制；
   - 创建或替换本仓库点名的十个 `[agents.<role>]` 注册段；
   - 保留其他 Agent、MCP、插件、Hook 状态和功能配置。
9. 不要把 Root Base 配置为 `model_instructions_file`。该层会被 subagent 继承，只能放所有责任层都安全的中性 Base。
10. 解析合并后的 TOML，并检查：
    - `developer_instructions` 与 Root Base 的长度和 SHA-256 一致；
    - 其余八个角色逐字符以 Worker Base 开头；
    - `code-executor` 与 `research-lead` 不以 Worker Base 开头，并分别包含完整的代码阶段与研究阶段专属边界、路线和交回规则；
    - 所有配置引用路径存在；
    - 角色 TOML 不包含当前运行时不支持的伪权限或伪环境字段。
11. 新建一个 Root 测试任务，确认 Root 加载完整 Root Base、共同执行层与当前项目规则。
12. 使用命名角色和 `fork_turns: "none"` 新建至少一个阶段负责人及一个执行型 subagent 测试，确认它们加载中性 Base、相应角色提示词和共同执行层，而不依赖 Root developer 镜像或父对话历史。
13. 每次委派都显式指定 `fork_turns`。有限轮数只在最近用户原话或既有判断无法安全概括时使用；绝不使用 `all`，也不省略参数形成 Full History。
14. 浏览器角色和视觉测试角色还需要宿主实际提供对应能力。复制角色文件不会自动开启能力或扩大外部操作授权。

## 模型层级参考

| 层级 | 默认模型 | 用途 |
| --- | --- | --- |
| Root | `gpt-5.6-sol` | 用户理解、整体路线、跨阶段判断、整合与最终交付 |
| Terra 阶段与评审 | `gpt-5.6-terra` | Research Lead、Code Executor、Code Reviewer |
| Luna 执行 | `gpt-5.6-luna` | Explorer、Web Researcher、Worker Luna、Browser Operator、Visual Usability Tester |
| 高速 Worker | `gpt-5.3-codex-spark` | 合同明确且速度收益明显的执行单元 |

## 完成报告

说明实际使用的 `CODEX_HOME`、备份位置、创建和替换的文件、保留的配置、最终模型映射、Root 镜像一致性、Worker 前缀与阶段专属提示词检查、TOML 解析、真实 Root/阶段角色/Worker 加载证据，以及仍未验证的部分。
