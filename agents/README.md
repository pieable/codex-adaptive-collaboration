# Agents role configuration

这个目录的权威源是独立 Agents Git 仓库；在公开仓库中，它作为可移植发行副本，保存 Codex 子角色的运行时配置和提示词来源。它不管理全局 `config.toml`、Prompt Lab 或全局 `AGENTS.md`。

## 真实加载结构

1. 全局 `config.toml` 将 [`shared-runtime-base-instructions.md`](shared-runtime-base-instructions.md) 配置为 `model_instructions_file`；该文件是共享中性 Base 的维护来源，不是顶层 Root developer mirror。
2. 运行时按角色名读取对应 `*.toml`。其中 `developer_instructions` 是角色层；它不应依赖 TOML 的其他字段来注入环境、权限或工具。
3. `code-executor.toml` 与 `research-lead.toml` 分别保存完整、自包含的阶段专属提示词，不共享阶段负责人 Base。
4. 其余八个角色 TOML 必须以 [`worker-subagent-base-instructions.md`](worker-subagent-base-instructions.md) 的全文开头；TOML 内的前缀是运行时真正使用的内联镜像，该 Markdown 文件是其权威维护来源。共享中性 Base 不重复内联到角色 TOML。

命名角色使用 `fork_turns = "none"` 时，角色 TOML 的 `developer_instructions` 覆盖父配置的顶层 developer mirror：该 subagent 会加载共享中性 Base 与角色 Base，不加载顶层 Root developer mirror，也不复制父对话历史。LastN 和 FullHistory 仍是运行时机制，但不进入当前自动委派路线；本体系统一显式使用 `none`，以自包含合同和稳定项目来源交接。

## 提示词排序

同一提示词层内，从大到小按以下顺序组织：

1. 目的与原则
2. 责任与权限边界
3. 工作路线
4. 具体行动
5. 验证与交回

下位内容只落实上位内容，不能改变上位已经确定的结果、权限或边界。角色专属段落在不改变内联 Base 的前提下遵循同一顺序。

## 运行时支持的角色配置

当前 Codex `rust-v0.150.0-alpha.8` 会读取角色文件的这些元数据：

- `name`
- `description`
- `nickname_candidates`

进入 subagent 配置的角色覆盖字段为：

- `model`
- `model_reasoning_effort`
- `model_reasoning_summary`
- `model_verbosity`
- `personality`
- `service_tier`
- `developer_instructions`

另外，运行时只会传递下列能力或 Skill 的显式关闭项，不会用角色文件开启父配置没有的能力：

- `[features]` 内 `apps = false`、`plugins = false`、`memories = false`、`shell_tool = false`、`request_permissions_tool = false`、`personality = false`
- `[skills] include_instructions = false`
- `[skills.bundled] enabled = false`
- `[[skills.config]] enabled = false`

其他表或字段不会为角色注入权限、环境、工具、MCP 服务或协作能力，也不会按角色改变沙箱或 Web 搜索设置。不要在角色 TOML 中加入 `sandbox_mode`、`web_search`、`project_doc_max_bytes`、`include_apps_instructions`、`include_collaboration_mode_instructions`、`include_environment_context`、`include_permissions_instructions`、`[agents]`、`[tools]`、`[memories]`、`[mcp_servers]` 等无效字段。

## 当前最小配置

- `browser-operator` 只保留核心字段。
- `code-executor`、`code-reviewer` 禁用 apps、plugins、memories 和 bundled skills。
- `explorer`、`web-researcher`、`worker`、`worker-luna` 在上述基础上关闭 Skill 指令注入。
- `research-lead` 只禁用 apps、plugins、memories。
- `visual-usability-tester` 仅禁用 memories、shell tool；它通过继承父配置中已启用的 Browser 与 Computer Use 能力，以截图和坐标完成受合同边界约束的黑盒验证。
- `default` 是兼容叶子角色，只保留其实际需要的核心字段和内联 Worker Base。

## 更新与验证

1. 修改共同工人规则时先更新 Worker Base，再把全文同步到八个执行角色的 `developer_instructions` 前缀；修改阶段角色时直接更新对应的自包含 TOML。
2. 保持本 README 的排序与运行时支持面说明同步；不要把未被运行时读取的字段当作权限或能力控制。`visual-usability-tester` 需要 Browser 或 Computer Use 时，只能通过不关闭 `apps` 来继承父配置已经启用的能力；角色 TOML 不能自行开启不存在的能力。
3. 在本目录执行下列静态验证，不运行模型，也不要 `git add` 或提交：

```powershell
$python = 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python -c "import pathlib, tomllib; [tomllib.load(p.open('rb')) for p in pathlib.Path('.').glob('*.toml')]; print('TOML OK')"
rg -n '^(sandbox_mode|web_search|project_doc_max_bytes|include_(apps|collaboration_mode|environment_context|permissions)_instructions|\[agents\]|\[tools\.|\[memories\]|\[mcp_servers\])' . --glob '*.toml'
```

4. 另外逐字符比较 `worker-subagent-base-instructions.md` 与八份 Worker 角色前缀，并分别检查 `code-executor` 与 `research-lead` 的专属责任、路线、投入边界和交回规则；不为了消除少量相似文字重新建立共同 Stage Base。
