# Agents role configuration

这个目录是独立 Agents 源仓库的可移植发布副本，保存 Codex 命名角色的运行时配置和提示词来源。

## 真实加载结构

1. 接收环境的全局 `config.toml` 将 [`shared-runtime-base-instructions.md`](shared-runtime-base-instructions.md) 配置为 `model_instructions_file`。它只包含所有责任层都安全的中性文字。
2. Root 的完整 Base 由顶层 `developer_instructions` 加载，其权威正文位于 `prompt-lab/codex_base_instruction_5.6.md`。
3. 运行时按角色名读取对应 `*.toml`，其中 `developer_instructions` 是角色层。
4. `code-executor.toml` 与 `research-lead.toml` 分别保存完整、自包含的阶段专属提示词，不共享阶段负责人 Base。
5. 其余八个角色必须逐字符以 [`worker-subagent-base-instructions.md`](worker-subagent-base-instructions.md) 开头。
6. TOML 内的 Worker Base 是运行镜像；共享中性 Base 与 Worker Base 的 Markdown 文件是各自的维护权威源。共享中性 Base 不重复内联进角色 TOML。

命名角色使用 `fork_turns: "none"` 时，角色 TOML 的 `developer_instructions` 覆盖父配置中的 Root developer 镜像。该 subagent 加载共享中性 Base 与角色 Base，但不复制父对话历史。运行时虽然支持有限轮数携带最近父对话，本体系统一显式使用 `none`，用自包含合同和稳定项目来源交接；`all` 与省略参数形成的 Full History 永久禁用。

## 两类责任

### 阶段负责人

- `research-lead`
- `code-executor`

阶段负责人连续掌握一个完整阶段，完成核心判断、核心工作、下属组织、整合与阶段验收。跨阶段路线、用户决定、未授权的明显投入或大范围结构变化交回 Root。

### 执行型角色

- `explorer`
- `web-researcher`
- `browser-operator`
- `code-reviewer`
- `visual-usability-tester`
- `worker-luna`
- `worker`
- `default`

执行型角色只完成结果、边界、权限和验收已经确定的一项责任，不创建下属。`default` 是兼容入口，不用于自动路由兜底。

## 提示词排序

同一提示词层按以下关系从大到小组织：

1. 目的与原则
2. 责任与权限边界
3. 工作路线
4. 具体行动
5. 验证与交回

下位内容只落实上位内容，不能改变上位已经确定的结果、权限或边界。

## 当前运行时支持面

角色文件的主要元数据为 `name`、`description` 和 `nickname_candidates`。角色覆盖字段包括模型、推理强度、摘要、verbosity、personality、service tier 和 `developer_instructions`。

显式能力关闭项只能关闭父配置已有的能力，不能为角色开启父配置没有的权限、工具或服务。不要用角色 TOML 中的 `sandbox_mode`、`web_search`、`project_doc_max_bytes`、`include_apps_instructions`、`include_collaboration_mode_instructions`、`include_environment_context`、`include_permissions_instructions`、`[agents]`、`[tools]`、`[memories]` 或 `[mcp_servers]` 伪造角色隔离。

## 更新与验证

1. 修改共同工人规则时先更新 Worker Base，再同步八个角色前缀；修改阶段角色时直接更新对应的自包含 TOML。
2. 不为了消除 `code-executor` 与 `research-lead` 之间的少量相似文字重新建立共同 Stage Base。
3. 解析全部 TOML。
4. 逐字符核对八个 Worker 前缀，并分别检查两个阶段角色的专属边界和方法仍然完整。
5. 使用全新命名角色及 `fork_turns: "none"` 验证真实加载；静态文件、Git 提交和 TOML 解析不能代替运行时证据。
