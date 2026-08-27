# Agents role configuration

这个目录是独立 Agents 源仓库的可移植发布副本，保存 Codex 命名角色的运行时配置和提示词来源。

## 真实加载结构

1. 接收环境的全局 `config.toml` 将 [`shared-runtime-base-instructions.md`](shared-runtime-base-instructions.md) 配置为 `model_instructions_file`。它只包含所有责任层都安全的中性文字。
2. Root 的完整 Base 由顶层 `developer_instructions` 加载，其权威正文位于 `prompt-lab/codex_base_instruction_5.6.md`。
3. 运行时按角色名读取对应 `*.toml`，其中 `developer_instructions` 是角色层。
4. `code-executor.toml` 与 `research-lead.toml` 必须逐字符以 [`stage-lead-base-instructions.md`](stage-lead-base-instructions.md) 开头。
5. 其余八个角色必须逐字符以 [`worker-subagent-base-instructions.md`](worker-subagent-base-instructions.md) 开头。
6. TOML 内的共同 Base 是运行镜像；三份 Markdown Base 是维护权威源。共享中性 Base 不重复内联进角色 TOML。

命名角色使用 `fork_turns: "none"` 时，角色 TOML 的 `developer_instructions` 覆盖父配置中的 Root developer 镜像。该 subagent 加载共享中性 Base与角色 Base，但不复制父对话历史。有限轮数仍携带对应父对话内容，不能泛化为完全隔离。

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

1. 先更新对应 Markdown Base 或角色专属段落。
2. 将 Stage/Worker Base 全文同步到相应 TOML 的 `developer_instructions` 前缀。
3. 解析全部 TOML。
4. 逐字符核对两个 Stage 前缀和八个 Worker 前缀。
5. 使用全新命名角色及 `fork_turns: "none"` 验证真实加载；静态文件、Git 提交和 TOML 解析不能代替运行时证据。
