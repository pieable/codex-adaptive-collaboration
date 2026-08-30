<div align="center">
  <img src="assets/four-star-dragon-ball.png" alt="四星龙珠" width="180">
  <h1>龙珠 Agent</h1>
</div>

一套面向长期协作的 Codex 配置体系。Root 负责理解用户、维护整体路线和最终验收；阶段负责人掌握完整阶段；执行型 subagent 只完成边界与验收已经确定的责任。

> 这是社区配置，不是 OpenAI 官方项目。

## 它解决什么问题

- 先做能够验证核心价值的最小成品或 Demo，而不是在未经验证的路线中持续扩大投入；
- 继续、重试或扩张前检查动作能否推进可验收结果或产生新证据，避免无用功和反复钻牛角尖；
- 用户目标、整体路线和跨阶段决定留在 Root，执行细节与长日志隔离在对应责任层；
- 小而固定的工作可以直接委派，仍需持续判断和多轮组织的工作交给阶段负责人；
- 高成本运行、大范围修改和跨阶段影响沿责任链上报；
- 阶段结束、路线变化或准备扩大投入时，由 Root 用视觉优先的方式向用户说明全局位置。

## 当前提示词装配

| 层 | 来源 | Root | 命名 subagent（`fork_turns: "none"`） |
| --- | --- | --- | --- |
| 中性运行 Base | [`agents/shared-runtime-base-instructions.md`](agents/shared-runtime-base-instructions.md) | 加载 | 加载 |
| Root Base | [`prompt-lab/codex_base_instruction_5.6.md`](prompt-lab/codex_base_instruction_5.6.md) 的 `config.toml` 运行镜像 | 加载 | 被角色 `developer_instructions` 替换 |
| 共同执行层 | [`global/AGENTS.md`](global/AGENTS.md) | 加载 | 加载 |
| 角色层 | `agents/*.toml` | 不适用 | 阶段专属完整提示词，或 Worker Base 加角色专属文字 |
| 领域方法 | `skills/*` | 按触发加载 | 按角色配置或触发加载 |

命名角色配合 `fork_turns: "none"` 时，不复制父对话历史，也不加载 Root developer 镜像。所有自动委派都显式使用 `none`；必要的用户决定进入自包含合同或稳定项目文件，不使用有限轮数、`all`，也不省略参数。项目 `AGENTS.md` 可以同时保存项目专属规则和权威文件索引，示例见 [`examples/project-AGENTS.md`](examples/project-AGENTS.md)。

## 三层责任结构

```text
用户
  └─ Root：目标、整体路线、跨阶段决定、最终验收与用户报告
       ├─ 阶段负责人：完整阶段、核心判断、下属组织、整合与阶段验收
       │    └─ 执行型 subagent：一项边界和验收已经确定的责任
       └─ 少量执行型 subagent：仅用于预计一轮即可交回的固定小任务
```

### 阶段负责人

- `research-lead`：大规模、多轮网络研究；
- `code-executor`：仍需连续诊断、实现、整合和验证的代码阶段。

### 执行型角色

- `explorer`：有界本地取证；
- `web-researcher`：有界网络取证；
- `code-reviewer`：独立只读评审；
- `browser-operator`：连续浏览器操作阶段；
- `visual-usability-tester`：截图与坐标驱动的视觉黑盒测试；
- `worker-luna`：做法和验收已经确定的主要执行责任；
- `worker`：Spark 额度可用且速度收益明确时的高速执行责任；
- `default`：兼容叶子入口，不用于自动路由兜底。

Worker Base 的权威文件、内联镜像关系、阶段专属提示词和运行时支持字段见 [`agents/README.md`](agents/README.md)。

## 十二个体系 Skill

- `batch-execution`：控制重复批量操作的扩散风险；
- `code-development`：代码调查、实现、评审和必要验证；
- `code-review`：独立判断代码是否适合合入或交付；
- `company-research-brief`：补全公司公开信息、比较产品线与同业并形成投前初筛；
- `deep-research`：多来源、反例和综合研究；
- `eli5`：视觉优先地解释计划、路线、状态和取舍；
- `product-development`：从客户现实形成产品定义并迭代验证；
- `search-source-registry`：按主张选择权威搜索入口并保留覆盖缺口；
- `workflow-route-mapper`：保存任务分叉、失败路线和下一步；
- `workflow-state-distiller`：恢复多轮任务的可执行当前状态；
- `write-instructions-zh`：创建和维护 Base、Agent、Skill 与长期规则；
- `xy-axis-thinking`：追溯形成原因、明确目标并建立参照。

## 安装

让安装用的 Codex 按 [`INSTALL.md`](INSTALL.md) 合并安装。安装过程必须保留接收环境已有的 Agents、Skills、MCP、插件和项目配置。可以按当次成本和验收需要选择是否创建全新 Root 与命名 subagent 测试；没有执行时明确把真实运行加载标为未验证。

默认模型层级为：Root 使用 `gpt-5.6-sol`，阶段负责人和评审使用 `gpt-5.6-terra`，常规执行和取证使用 `gpt-5.6-luna`，高速 Worker 使用 `gpt-5.3-codex-spark`。目标环境没有对应模型时，应由用户确认能力层级映射。

## 仓库结构

```text
.
├── prompt-lab/                 # Root Base 与公开维护材料
├── global/AGENTS.md            # 所有角色共同读取的执行规则
├── agents/                     # 共享中性 Base、Worker Base 与 10 个角色 TOML
├── skills/                     # 12 个体系 Skill
├── hooks/                      # 强制 fork_turns:none 的 PreToolUse 保护
├── examples/                   # 配置合并与项目 AGENTS 模板
└── INSTALL.md
```

## 版本边界

本仓库 Prompt Lab 中的 Root Base 是当前公开发行权威正文；维护者的私人 Prompt Lab 保存编写与完整演变历史。安装后的 `config.toml` 只保存逐字运行镜像，不承担版本历史。Worker Base 的公开发行文件位于 `agents/`，八个执行角色 TOML 保存运行时需要的内联镜像；两个阶段角色各自维护完整专属提示词。

这套体系不依赖 Python 同步脚本、常驻进程或 Hook 拼接提示词。`hooks/` 只机械保护 subagent 的 `fork_turns:none` 参数，不生成或拼接提示词。发布是一次明确的复制、解析和一致性校验；真实加载验证按当次验收需要执行并单独报告。

## License

[MIT](LICENSE)
