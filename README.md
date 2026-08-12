# Codex Adaptive Collaboration

一套面向长期协作的 Codex 配置体系。它不只负责把任务分给多个 Agent，还让 Root 持续理解用户逐步表达出来的真实需求、掌握任务从当前状态到完成条件的整体路径，并在权限范围内自主调查、换路、整合和验收。

> 这是社区配置，不是 OpenAI 官方项目。

## 它解决什么问题

普通的多 Agent 配置往往只回答“谁来做哪一块”。这套体系还处理：

- 用户一开始无法完整写出规格，真实要求会在纠正、选择、试用和反例中逐渐形成；
- Root 需要保留全局路径，根据依赖关系安排并行阶段，而不是每遇到一道坎就把决定交还用户；
- subagent 应隔离大规模搜索、实现和工具噪声，同时避免 Root 重复它们已经完成的工作；
- 自主推进不能变成越权或小题大做，替代路线需要和原任务规模相称；
- 提示词经过多轮校准后，要保留当前规则、形成原因和可复用方法，不能不断堆叠局部补丁。

## 四个组成部分

### 1. 自适应协作 Base

[`prompt-lab/codex_base_instruction_5.6.md`](prompt-lab/codex_base_instruction_5.6.md) 是 Root 的独立母本，包含：

- 与用户的协作、进度和交付方式；
- 从当前状态到完成条件的持续推进；
- 授权、自主性、最小方案和受阻换路；
- 文件、PowerShell、测试、破坏性操作和 Skill 使用规则；
- Root 的调度循环、委派所有权和成本结构。

### 2. 分层 Agent 体系

| 角色 | 责任 |
| --- | --- |
| `explorer` | 低成本本地文件搜索和只读定位 |
| `web-researcher` | 边界明确的联网取证 |
| `research-lead` | 多轮研究、来源覆盖、冲突处理和综合 |
| `code-executor` | 完整代码阶段的调查、实现、验证和收尾 |
| `worker` | 合同明确的高速执行、批处理、构建和测试 |
| `browser-operator` | 需要连续页面状态的浏览器操作 |

Root 负责整体路径、关键判断、重新调度、结果整合和最终验收。每项责任只有一个所有者；已经交给 subagent 的工作，Root 不会为了保持忙碌而重复执行。

### 3. 可同步的共享规则

[`prompt-lab/shared-subagent-instruction-blocks.md`](prompt-lab/shared-subagent-instruction-blocks.md) 是六个角色中 XML 共享区块的唯一来源。Root Base 独立维护，不参与机械同步。

修改共享规则后运行：

```powershell
pwsh -NoProfile -File prompt-lab/sync-subagent-instruction-blocks.ps1
pwsh -NoProfile -File prompt-lab/sync-subagent-instruction-blocks.ps1 -Check
```

### 4. 理解、研究与执行 Skills

仓库附带六个通用 Skill：

- `workflow-state-distiller`：从纠正、选择和试用中提炼正在形成的真实要求；
- `workflow-route-mapper`：保存任务分叉、失败路线、当前位置和下一步；
- `write-instructions-zh`：创建和维护 Base、Agent、Skill 与长期规则；
- `code-development`：跨文件代码调查、实现和验证；
- `deep-research`：多来源系统研究；
- `batch-execution`：控制批量处理的扩散风险和验收。

## 安装

最省事的方法是把本仓库交给另一个 Codex 或 AI，让它遵循 [`INSTALL.md`](INSTALL.md) 安装。安装流程会合并现有配置，不会要求清空用户已有的 Agents、Skills、MCP 或插件。

模型名称来自原作者的注册配置。如果你的环境没有这些模型，让安装 AI 先请你确认能力层级映射，不要静默替换。

## 仓库结构

```text
.
├── prompt-lab/
│   ├── codex_base_instruction_5.6.md
│   ├── shared-subagent-instruction-blocks.md
│   └── sync-subagent-instruction-blocks.ps1
├── agents/
│   ├── *-base-instructions.txt
│   └── *.toml
├── skills/
├── examples/config.toml
└── INSTALL.md
```

## 设计取舍

- 正确、完整和用户可用的结果优先，成本与速度在此基础上优化；
- Root 使用高能力模型掌握全局，便宜模型承担适合可靠交接的大块工作；
- 委派用于降低上下文噪声和执行成本，不为形式而增加 Agent 层级；
- 隐含目标帮助选择路线，但不能覆盖明确结果、权限和硬边界；
- 正常路线受阻时允许自主换路，但不会为了局部障碍训练新模型或搭建与任务不相称的大型系统。

## License

[MIT](LICENSE)
