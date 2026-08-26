# 给安装 AI 的任务合同

把本仓库安装到当前用户的 Codex 配置目录，使 Root Base、九个角色和九个体系 Skill 在新任务中可用。

## 目标与边界

- 先解析当前环境真实使用的 `CODEX_HOME`，不要根据仓库作者的路径猜测；
- 修改范围仅限当前用户的 Codex 配置以及为验收新建的测试任务；
- 保留接收者已有且与本体系无关的配置、Agents、Skills、MCP、插件和项目资料；
- 写入前备份将被创建或替换的文件，以及合并前的 `config.toml`；
- 不复制仓库之外的备份、会话、缓存、账户数据或凭据；
- 模型不可用、目标路径无法确定、同名文件无法安全合并，或需要扩大权限时，停止写入并说明具体冲突。

## 安装步骤

1. 读取 `examples/config.toml`、`prompt-lab/`、`agents/` 和 `skills/`，确认仓库结构完整。
2. 在 `CODEX_HOME` 下创建 `prompt-lab`、`agents`、`skills` 和独立备份目录。
3. 复制以下内容：
   - `prompt-lab/codex_base_instruction_5.6.md`；
   - `prompt-lab/functional-block-baseline.md` 和 `prompt-lab/module-map.md`；
   - `agents/` 下九个角色 TOML；
   - `skills/` 下九个 Skill 的完整目录。
4. 把示例和角色文件中出现的 `{{CODEX_HOME}}` 替换为真实绝对路径。只替换这个占位符，不改写其他指令内容。
5. 合并 `config.toml`：
   - 保留无关顶层配置；
   - 更新 Root 的 `model`、`model_reasoning_effort` 和 `model_instructions_file`；
   - 如果 `[agents]` 缺少限制，设置 `max_depth = 2` 和 `max_concurrent_threads_per_session = 10`；若已有不同值，先说明这会影响全部 Agent 的嵌套或并发上限，由用户决定是否覆盖；
   - 创建或替换本仓库点名的九个 `[agents.<role>]` 注册段；
   - 保留其他 Agent、MCP、插件和功能配置。
6. 如果示例模型不可用，列出 Root、Luna 执行、Terra 阶段与评审、Spark Worker 四个能力层级，请用户确认映射；不要自行选择实质不同的模型。
7. 预检目标宿主和父配置：`browser-operator` 需要浏览器能力，`visual-usability-tester` 需要 Computer Use。若它们未启用或目标版本不支持，说明这两个角色不可用；启用这类真实交互能力前先取得用户确认，不要因为安装而自动扩大权限。
8. 解析合并后的 TOML，检查所有目标文件存在，并确认配置引用的路径都能解析。
9. 新建一个 Root 测试任务和至少一个 subagent 测试任务，验证真实运行时已加载新 Base 和角色指令。可用时分别验证浏览器角色和视觉测试角色的实际工具；无法进行真实加载测试时，明确写“未验证”，不要用文件存在代替。

## 模型层级参考

| 层级 | 默认模型 | 用途 |
| --- | --- | --- |
| Root | `gpt-5.6-sol` | 全局理解、判断、整合和调度 |
| Luna 执行 | `gpt-5.6-luna` | Explorer、Web Researcher、Worker Luna、Browser Operator、Visual Usability Tester |
| Terra 阶段与评审 | `gpt-5.6-terra` | Research Lead、Code Executor、Code Reviewer |
| 高速 Worker | `gpt-5.3-codex-spark` | 合同明确且速度收益明显的执行单元 |

## 完成报告

说明：

- 实际使用的 `CODEX_HOME`；
- 创建、替换和保留了哪些文件或配置段；
- 最终模型映射；
- TOML 解析、路径检查和真实加载各验证到哪一层；
- 仍未验证或需要用户处理的事项。
