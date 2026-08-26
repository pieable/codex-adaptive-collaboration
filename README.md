# Codex Adaptive Collaboration

一套面向长期协作的 Codex 配置体系。它让 Root 持续理解用户逐步表达出来的需求，维护从当前状态到完成条件的路径，并在已授权范围内调查、调度、整合和验收。

> 这是社区配置，不是 OpenAI 官方项目。

## 它解决什么问题

- 用户的要求常在纠正、选择、试用和反例中逐步明确；
- Root 需要掌握整体路径，而不是把普通实现判断反复交还用户；
- 大量搜索、实现和工具输出应当隔离在合适的执行者中，同时避免重复工作；
- 自主推进必须有权限边界，替代路线也要与任务规模相称；
- 提示词、角色和 Skill 要能随系统演进同步，而不靠堆叠临时补丁维持。

## 组成

### Root Base

[`prompt-lab/codex_base_instruction_5.6.md`](prompt-lab/codex_base_instruction_5.6.md) 是当前运行时的 Root 指令。它覆盖用户协作、授权边界、任务推进、调度、验证、交付以及 Skill 的使用方式。

[`functional-block-baseline.md`](prompt-lab/functional-block-baseline.md) 保留 Base 的功能块测试基线；[`module-map.md`](prompt-lab/module-map.md) 说明各功能块的性质和修改方式。它们用于校准和维护，不替代运行时 Base。

### 九个按职责选择的角色

| 角色 | 责任 |
| --- | --- |
| `explorer` | 有界的本地只读取证 |
| `web-researcher` | 有界的网络取证 |
| `research-lead` | 多轮研究、来源覆盖、冲突处理和阶段综合 |
| `code-executor` | 一个代码模块或功能阶段的调查、实现、整合、验证和收尾 |
| `code-reviewer` | 独立、只读地评审代码变更 |
| `worker` | 在 Spark 额度可用且速度收益明显时执行边界清楚的工作 |
| `worker-luna` | 边界清楚的主要执行工作，包括修改、批处理、构建和测试 |
| `browser-operator` | 需要连续页面状态的浏览器阶段 |
| `visual-usability-tester` | 仅通过截图和坐标完成黑盒视觉可用性测试 |

这不是要求每个任务都开启全部角色。Root 根据任务的依赖、共享状态、风险和上下文隔离价值选择最简单的组织结构；一个有界步骤可以直接完成，完整而复杂的阶段才交给对应负责人。

角色 TOML 都是自包含的 `developer_instructions`，不依赖额外的 `*-base-instructions.txt`。角色的历史和关系说明见 [`agents/PROMPT_HISTORY.md`](agents/PROMPT_HISTORY.md)。

`browser-operator` 需要宿主实际提供浏览器能力，`visual-usability-tester` 需要 Computer Use。安装时应先检查目标 Codex 版本及父配置是否启用这些能力；它们涉及真实页面或桌面操作，不能因为复制角色文件而自动扩大权限。

### 九个体系 Skill

- `batch-execution`：控制重复批量操作的扩散风险和验收；
- `code-development`：代码调查、实现、评审和分层验证；
- `code-review`：面向可合入性与交付风险的独立评审；
- `deep-research`：多来源、反例和综合的系统研究；
- `product-development`：从客户现实形成产品定义并迭代验证；
- `workflow-route-mapper`：保存任务分叉、失败路线和下一步；
- `workflow-state-distiller`：从多轮协作恢复可执行的当前状态；
- `write-instructions-zh`：创建和维护 Base、Agent、Skill 与长期规则；
- `xy-axis-thinking`：追溯形成原因、明确目标并建立可比参照。

每个 Skill 目录包含运行所需的当前 `SKILL.md`，以及适用的 metadata、references、agents 或变更记录；不包含本机备份或 Git 元数据。

## 安装

请让安装用的 Codex 按 [`INSTALL.md`](INSTALL.md) 合并安装。流程会保留已有的 Agents、Skills、MCP、插件和项目配置，不要求清空用户环境。

原始模型层级是 Root 使用 `gpt-5.6-sol`，阶段负责人和评审使用 `gpt-5.6-terra`，常规执行和取证使用 `gpt-5.6-luna`，高速 Worker 使用 `gpt-5.3-codex-spark`。若目标环境没有这些模型，先由用户确认能力层级映射，不要静默替换。

## 仓库结构

```text
.
├── prompt-lab/                 # Root Base 与公开维护材料
├── agents/                     # 9 个自包含角色 TOML
├── skills/                     # 9 个体系 Skill 的完整目录
├── examples/config.toml        # 可移植的注册示例
└── INSTALL.md
```

## 设计取舍

- 正确、完整和用户可用的结果优先，成本与速度在此基础上优化；
- Root 负责跨阶段判断和最终验收，职责明确的工作交给成本合适的角色；
- 委派用于减少上下文噪声和执行成本，不为形式增加层级；
- 隐含目标可以帮助选择路线，但不能覆盖明确结果、权限和硬边界；
- 当证据表明当前路线不再接近用户结果时，允许停止扩张、补证据或换路。

## License

[MIT](LICENSE)
