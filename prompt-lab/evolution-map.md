# 提示词演变地图

本文件是公开发行仓库按模型行为和功能块整理的演变地图。它不参与运行时加载，也不代替私人维护 Git 中的精确原文。

## 怎样使用这张地图

- 维护者的私人 Prompt Lab 保存完整的编写与演变历史；本文件只公开对理解当前发行版本有用的部分。
- Git 保存每个版本的精确文字、删除内容和快照；本文件解释变化之间的关系。
- GitHub `pieable/dragon-ball-agent` 的 commit 或 tag 表示公开发行版本；私有未发布变化不能冒充公开版本。
- 本机 `config.toml`、全局 `AGENTS.md`、角色 TOML 和已安装 Skill 是运行镜像，不独立维护提示词历史。
- 验证分为 `static`、`mirror/TOML`、`fresh-task-load` 和 `real-behavior`。上一层通过不能证明下一层。

## 状态

| 状态 | 含义 |
| --- | --- |
| `current-effective` | 当前有效 |
| `conditional` | 只在明确条件下适用 |
| `migrated` | 行为仍有效，但已经迁移到其他承载层 |
| `superseded` | 已被后续规则或机制取代 |
| `user-rejected` | 用户明确否决，不得自动恢复 |
| `experiment-failed` | 实验没有达到目标或暴露路线失败 |
| `paused` | 暂停推进，等待条件、授权或新证据 |
| `unverified` | 已形成文字或静态证据，关键运行层尚未验证 |

`user-rejected`、`experiment-failed`、`superseded`、`paused` 和 `unverified` 必须分开记录。被否决的路线不得自动复活；条件发生实质变化时，先重新校准和验证。

## 1. 用户理解、提问与阶段校准

### 当前语义

Root 从用户表达、项目事实和可靠历史中恢复真实目标。未确认判断会改变目的、最小核心成品、路线、完成标准或明显投入时，及时回显理解并提问。能够从项目、Git 和记录恢复的事实不要求用户重复。中大型任务需要跨阶段、跨 agent 或跨任务稳定传递确认时，Root 把当前理解维护成可修正的任务规格；简单任务不增加这层。

### 重要演变

| 日期 / 私人 commit | 变化 | 状态 | 当前承载层 | 验证 |
| --- | --- | --- | --- | --- |
| 2026-08-20 `5cc03f9` | 从执行步骤转向问题和合同驱动 | `current-effective` | Root Base | `static` |
| 2026-08-24 `9203977` | 把需要用户决定的交接判断纳入 Base | `current-effective` | Root Base | `static` |
| 2026-08-24 `fa5e376` | 接续旧项目时先恢复当前项目状态，不让用户重述可恢复历史 | `current-effective` | Root Base | `static` |
| 2026-08-28 `5befdc3` | 将开放判断写成可迁移原则，避免把单次事故写成分类表 | `current-effective` | Root Base | `static` |
| 2026-08-28 本次校准 | 明确小而重要的问题也及时询问；依赖分支暂停，独立工作继续 | `current-effective` | Root Base 保真语义 | 待真实任务观察 |
| 2026-09-01 `6b08b1d` / Agents `d52a151` | 复杂任务由 Root 维护当前规格，用户校准回写后再更新受影响的阶段计划和合同 | `current-effective + unverified` | Root Base / 阶段角色 / Reviewer / 全局共同层 | 静态；真实跨阶段任务待验证 |

## 2. 最小核心 Demo、路线验证与换路

### 当前语义

需要实现来验证路线时，先做能够独立体现核心用户价值的最小完整成品。Demo 可以粗糙，但核心功能、关键真实入口和中心逻辑必须正确。第一次失败后只做能够区分局部缺陷与路线问题的最小实验；没有推进结果或原因判断时缩小或换路。

### 重要演变

| 日期 / 私人 commit | 变化 | 状态 | 当前承载层 | 验证 |
| --- | --- | --- | --- | --- |
| 2026-08-24 `c66f6a3` | 连续工作以最小成品、失败实验和路线切换组织 | `current-effective` | Root Base | `static` |
| 2026-08-24 `38e4b47` | 删除事件特定路线例子，保留可迁移判断 | `superseded`（案例承载） | Root Base | `static` |
| 2026-08-24 `aae266b` | 实验条件不再自动污染长期政策 | `current-effective` | Root Base / test-results | `static` |
| 2026-08-27 `ff03457` | 继续、重试和扩大必须推进结果或产生新证据 | `current-effective` | Root Base / 全局共同层 | `static` |
| 2026-08-28 `e965186` | 恢复 Ponytail 路线选择哲学 | `current-effective` | Root Base | Git diff；真实触发未验证 |

## 3. 反无用功、高成本动作与停止

### 当前语义

下一动作必须直接推进合同内可验收结果，或者产生会改变下一步判断的新信息、反馈或可比较结果。动作后结果、关键未知和路线都没有变化时，不在相同条件下继续。高成本运行、大范围修改或明显增加下属轮次没有得到合同授权时，先交回当前结果、首个缺口、新证据价值、成本、停止条件和替代路线。

### 重要演变

| 日期 / 私人 commit | 变化 | 状态 | 当前承载层 | 验证 |
| --- | --- | --- | --- | --- |
| 2026-08-24 `27c0e4d` | 路线扩大由能否改变判断的证据门控 | `current-effective` | Root Base | `static` |
| 2026-08-25 `9ef1047` | 恢复无依赖工具并行，减少重复模型轮次 | `current-effective` | Root Base / 全局共同层 | `static` |
| 2026-08-27 `ff03457` | 用统一动作门代替更多事故禁令 | `current-effective` | 全局 `AGENTS.md` | `static` |
| 2026-08-28 `de24571` | 阶段负责人连续处理合同内工作，合同外明显投入上交 | `current-effective` | Root Base / 阶段角色 | 待真实长任务验证 |

## 4. 多 Agent 分层、封装与成本

### 当前语义

Root 保存用户目标、整体框架、跨模块取舍和最终验收；复杂任务还把这些确认维护成当前任务规格。阶段负责人掌握完整模块或阶段，从规格相关部分形成模块计划，完成核心判断、组织下属并交回完整代码模块或整合研究报告。工人只接收相关的自包含合同，不重新理解全局。网络来源的发现、收集和路线内核验由 Luna 搜索角色完成；研究阶段负责人组织来源路线、处理冲突和形成阶段综合，只为一个已经定位的具体解释差异读取必要的最小原文片段。代码阶段负责人可以直接完成核心代码，不机械限制其中档成本调用；做法已经能够可靠交接的连续实现由 Luna 承担，让正确路线更快完成，也把错误路线的时间和额度损失控制在较低水平。代码评审者根据准确候选、相关当前规格、期望结果、已接受约束、实际差异和验证证据，检查漏做、部分完成、相反实现和未经确认的增加，再独立判断当前代码“可合入”“要求修改”或“证据不足”。逐级交回用于保持上下文聚焦，并减少昂贵 Root 的反复唤醒。

当前订阅成本背景是：Luna 约为 Root Sol 的 `1/25`，Terra 约为 `2/5`，Spark 按接近 Luna 考虑并使用独立额度，GPT 输出 Token 单价约为输入的六倍。它们是当前订阅路由背景，不使用公开 API 价格替换。

### 重要演变

| 日期 / 私人 commit | 变化 | 状态 | 当前承载层 | 验证 |
| --- | --- | --- | --- | --- |
| 2026-08-16 `bac905d` | 重写 subagent 委派与责任层 | `superseded`（旧装配） | agents / Root Base | Git 历史 |
| 2026-08-17 `f8e9bd3` | 修正含糊的责任所有权文字 | `current-effective` | Root Base / Worker Base | `static` |
| 2026-08-18 `91cd98d` | 明确可扩展委派和拓扑选择 | `current-effective` | Root Base / 阶段角色 | `static` |
| 2026-08-20 `ed3f0c9` | 允许明确的一轮小任务直接交给少量执行角色 | `conditional` | Root Base | 待按任务观察 |
| 2026-08-25 `25ed495` | Root 聚焦整体判断，共同执行规则移出 Root | `migrated` | Root Base → 全局 `AGENTS.md` / agents | `static` |
| 2026-08-28 `3208904` | 取消当前不必要的共同 Stage Base，代码与研究阶段各自自包含 | `current-effective`；未来可重新评估 | 阶段角色 TOML | TOML/静态 |
| 2026-08-28 `3b268d1` | 恢复模型成本背景，避免路由依据被过度压缩 | `current-effective` | Root Base / 基线 | `static` |
| 2026-08-29 本次校准 | Terra 保留核心判断和核心代码，不设机械调用上限；Luna 承担已确定的连续执行，阶段完成后不再通过 followup 扩成整个项目 | `current-effective` | Root Base / `code-executor` / 基线 | RP 任务提供反例；新规则待 fresh-task 行为验证 |
| 2026-08-29 本次校准 | Reviewer 从问题清单角色明确为对当前代码给出“可合入”“要求修改”或“证据不足”的独立评审者 | `current-effective` | `code-reviewer` / `code-executor` / code Skills | `static`；真实评审闭环待验证 |
| 2026-08-29 本次校准 | 来源搜索和路线内核验交给 Luna，`research-lead` 集中处理结构、冲突和阶段综合，Root 不因材料重要而重新搜索 | `current-effective` | `deep-research` / `research-lead` / 基线 | `static`；真实研究任务待验证 |
| 2026-08-29 本次校准 | 可见界面、视觉反馈或完整用户操作路径进入代码阶段验收时，由 `code-executor` 触发 `visual-usability-tester` 完成首次用户视角黑盒验证 | `current-effective` | `code-executor` | `static`；真实代码阶段待验证 |
| 2026-09-01 本次校准 | 已对齐的代码合同写清权威机制、保留与删除边界和失败语义，代码阶段据此形成唯一实现 | `current-effective` | Root Base / `code-executor` / `code-development` | CodexCostMonitor 真实代码阶段已删除竞争加载与宽泛回退路径 |
| 2026-09-01 本次校准 | Reviewer 改用 Terra xhigh，并在每次评审中单列兜底路径必要性审查 | `current-effective` | `code-reviewer` / `code-review` | fresh Terra xhigh reviewer 已单列兜底审查并给出三态结论 |
| 2026-09-01 本次校准 | 代码阶段按未来维护是否依赖不可从代码和测试恢复的稳定信息决定项目资料，并由 Reviewer 检查 | `current-effective` | `code-executor` / `code-reviewer` / code Skills | 当前项目资料已通过 fresh reviewer 审查；跨任务交接继续观察 |

## 5. Root-only 加载与上下文继承

### 当前语义

完整 Root Base 只给主 agent。全局 `model_instructions_file` 只能承载所有责任层都安全的中性 Base。命名角色使用 `fork_turns: "none"` 时，角色 `developer_instructions` 覆盖 Root developer 镜像。运行时虽然支持有限轮次携带最近父对话，当前体系仍把这种按时间截取的隐式依赖排除在自动委派之外；创建者一律显式使用 `none`，用自包含合同和稳定项目来源传递上下文。`all` 与省略参数形成的完整历史继承继续永久禁用。

### 重要演变

| 日期 / 私人 commit | 变化 | 状态 | 当前承载层 | 验证 |
| --- | --- | --- | --- | --- |
| 2026-08-16 `5edcd61` | 停止共享 XML 区块，减少职责混入和镜像漂移 | `current-effective` | agents / Git | `static` |
| 2026-08-25 `5ecfc3e` | 结构重写前保存角色提示词快照 | `current-effective` | backups / Git | Git 快照 |
| 2026-08-27 `9f805d0` | 建立 Root 权威源、运行镜像和加载边界 | `current-effective` | Prompt Architecture | `static` |
| 2026-08-28 本次校准 | 修正“只有 none 才加载命名角色提示词”的错误表述；有限 N 仍加载角色正文 | `current-effective` | 加载说明 | 已有源码/静态证据；真实组合按需验证 |
| 2026-08-28 本次校准 | 因完整历史污染角色职责并造成巨额重复上下文，永久禁用 `fork_turns: "all"` 及省略参数形成的完整历史继承 | `user-rejected`（Full History） / `current-effective`（禁令） | Root Base / 两个阶段角色 | 运行记录已观察到失败；新规则待 fresh-task 行为验证 |
| 2026-08-30 本次校准 | 有限最近轮次也会形成按时间截取、难复现的隐式依赖；全部自动委派改为 `fork_turns: "none"`，必要上下文进入合同或项目权威来源 | `current-effective` | Root Base / 阶段角色 / 项目 `AGENTS.md` 索引 | 长任务轨迹与最近三轮失败案例支持；fresh-task 行为待验证 |

## 6. Worker Base 与执行型角色

### 当前语义

Worker Base 统一工人角色的合同、越界上报、反无用功停止和直接上级交回。角色特有方法留在各自 TOML。工人不重新解释用户目标，不越过直接上级，也不创建或调度 subagent。`worker-luna` 是常规执行者；Spark `worker` 只在额度可用且速度收益明确时使用。

### 重要演变

| 日期 / 私人 commit | 变化 | 状态 | 当前承载层 | 验证 |
| --- | --- | --- | --- | --- |
| 2026-08-25 `53dbae0` | 明确 Worker 上下文和交回路线 | `current-effective` | Worker Base / agents TOML | `static` |
| 2026-08-25 `8b74bf9` | 共同执行、成品和验证规则迁入全局共同层 | `migrated` | Worker Base → 全局 `AGENTS.md` | `static` |
| 2026-08-28 `3208904` | 保留 Worker Base，删除当前无益的共同 Stage Base | `current-effective` | Worker Base / 阶段角色 | TOML/静态 |

## 7. 阶段报告与视觉解释

### 当前语义

阶段结束、路线变化、Demo 完成、准备扩大投入、模块组装或复杂旧任务接续时，Root 使用视觉优先、文字简短的方式帮助用户恢复全局理解。图表解释目标、当前位置和下一步，不代替真实完成证据。普通短进度不强制生成图或 HTML。

### 重要演变

| 日期 / 私人 commit | 变化 | 状态 | 当前承载层 | 验证 |
| --- | --- | --- | --- | --- |
| 2026-08-24 `0a7e9d1` | 使用描述性标题提高结构可读性 | `current-effective` | Root Base | `static` |
| 2026-08-25 `26d8473` | 完善最终视觉验收和角色路由边界 | `current-effective` | Root Base / Skill | `static` |
| 2026-08-28 本次校准 | 明确报告面向不负责实现的成年项目负责人，图先给全局，文字补决定 | `current-effective` | Root Base + ELI5 Skill | 待真实阶段报告观察 |

## 8. Skill 的官方机制与归属

### 当前语义

Root Base 的 Skill 章节保留完整官方中文翻译，不再自行压缩、改写或重新组织。两个阶段负责人各自内联同一完整章节，并仅用一条角色适配把其中的 Root 身份和用户沟通映射到阶段责任链。领域方法仍留在各自 Skill 中。

### 重要演变

| 日期 / 私人 commit | 变化 | 状态 | 当前承载层 | 验证 |
| --- | --- | --- | --- | --- |
| 2026-08-24 `137e58e` | 精简 Base 时恢复 Skill 加载和引用协议 | `current-effective` | Root Base / Skill | `static` |
| 2026-08-24 `aae266b` | 实验结果不自动写成长效 Skill 政策 | `current-effective` | Root Base / test-results | `static` |
| 2026-08-28 `5befdc3` | 泛化 Root 开放判断时误把官方 Skill 章节压缩成摘要 | `superseded`（Skill 章节） | Root Base | 用户指出保真缺口 |
| 2026-08-29 本次校准 | 从保存的官方中文翻译逐字恢复完整 Skill 章节，并把同一章节内联到两个阶段负责人 | `current-effective` | Root Base / 阶段角色 / 翻译源 | 逐字比较与 TOML 解析通过；fresh-task 待验证 |

## 9. 从大到小的规则层级

### 当前语义

提示词按“目的与原则 → 责任与决定权限 → 工作路线与阶段关系 → 具体行动与工具 → 验证、交回与例外”逐层细化。下一层只能落实上一层，不能改变上一层已经确定的结果、权限或适用范围。这个结构首先是冲突处理和解释规则，其次才是排版形式。

### 重要演变

| 日期 / 私人 commit | 变化 | 状态 | 当前承载层 | 验证 |
| --- | --- | --- | --- | --- |
| 2026-08-13 `8619c40` | 四句极简总纲不能承载完整功能面 | `user-rejected` / `experiment-failed` | 历史候选 | Git / test-results |
| 2026-08-14 `aeb4aec` | 建立 Prompt Lab 基线和规则并集 | `current-effective` | Prompt Lab | Git |
| 2026-08-24 `16bfbdc`、`0776bc7` | 机械层级重排导致语义损失并被回退 | `experiment-failed` / `superseded` | Root Base 历史 | Git diff |
| 2026-08-24 `9cf4a78`、`0a7e9d1` | 恢复按语义关系和描述性标题组织 | `current-effective` | Root Base | `static` |
| 2026-08-28 本次校准 | 明确层级的主要作用是避免细节规则把模型带离上位目的 | `current-effective` | 所有可维护提示词块 | 用户确认 |

## 10. 私人编写、公开发行与运行镜像

### 当前语义

私人 Prompt Lab 是编写与演变权威源；GitHub commit 或 tag 是公开发行权威版本；本机配置和已安装提示词是运行镜像。私人源先修改和提交，再明确安装或发布。静态内容、镜像一致/TOML、全新任务加载和真实行为分别验证。

### 重要演变

| 日期 / 私人 commit | 变化 | 状态 | 当前承载层 | 验证 |
| --- | --- | --- | --- | --- |
| 2026-08-27 `9f805d0` | 明确 Root 源文件、`config.toml` 镜像和发布步骤 | `current-effective` | Prompt Architecture | `static` |
| 2026-08-27 `b1278dd` | 保存历史快照并区分 Prompt Lab 与运行配置 | `current-effective` | Prompt Lab | Git |
| 2026-08-28 本次审计 | 发现私人 Root Base 与本机运行镜像实质一致、公开副本落后，并在本次发布中重新同步 | `current-effective` | private / public / runtime | 私人正文与运行镜像规范化哈希一致，私人正文与公开正文文件 SHA 一致；全新任务加载和真实行为未验证 |

## 统一否决、撤回与暂停路线

| 路线 | 状态 | 为什么停止 | 当前替代 | 可以重新考虑的条件 |
| --- | --- | --- | --- | --- |
| 四句全局极简总纲取代全部功能块 | `user-rejected` + `experiment-failed` | 无法承载完整有效行为 | 保留功能块和上位原则 | 新模型或宿主通过代表性真实测试 |
| 6403 字符整篇分层候选 | `experiment-failed` / `user-rejected` | 结构重写造成语义损失 | 从当前有效正文做局部修改 | 用户重新要求且有成对样本和行为证据 |
| 完整系统建成后才测试核心价值 | `experiment-failed` / `user-rejected` | 长时间和大量测试没有产生真实核心成品 | 先做核心正确的最小完整 Demo | 仅当现成系统已证明入口和价值，无需高额前置投入 |
| 相同条件下不断重试直到当前路线跑通 | `user-rejected` | 会钻牛角尖并扩大错误路线成本 | 一次区分性实验后缩小或换路 | 新尝试确实引入能改变判断的新证据 |
| 把问题积累到以后统一询问 | `user-rejected` | 错误假设会继续扩散 | 重要问题及时问，独立工作继续 | 用户明确要求某一阶段集中决策 |
| 依赖 agent TOML 中的 `model_instructions_file` | `experiment-failed` | 当前宿主没有形成有效角色局部加载 | 中性全局 Base + 角色 `developer_instructions` | 宿主明确支持并由新任务验证 |
| 让完整 Root Base 进入所有 subagent | `user-rejected` / `superseded` | 污染角色上下文和责任 | 中性共享 Base、全局共同层和角色专属提示词 | 底层加载机制改变并重新校准 |
| 固定 agent 数量或异步调度循环 | `user-rejected` / `superseded` | 固定拓扑不能适应责任、依赖和成本 | 根据一轮交回能力和阶段判断负担选择结构 | 代表性任务证明固定拓扑稳定更优 |
| 当前只有两个阶段角色时维护共同 Stage Base | `conditional`（当前不采用） | 共同文字会把代码规则压到研究阶段 | 两个阶段角色分别自包含 | 阶段角色增多并形成真实、无冲突的共同规则 |
| 用公开 API 价格替换当前订阅成本比例 | `user-rejected` | 背景不属于用户当前订阅路由 | 使用已确认的订阅内成本比例 | 用户的订阅经济和额度实际变化 |
| 继续自行改写当前官方 Skill 提示词 | `user-rejected` | 实际使用后官方版本更稳定 | 保留当前官方 Skill 提示词 | 用户明确要求针对新证据重新评估 |
| 用 Python、常驻进程或 Hook 自动拼接提示词发布 | `user-rejected` / `superseded` | 增加不必要机制和信任状态 | 直接修改权威文件并明确复制发布 | 宿主提供原生、透明且确有收益的机制并获用户同意 |
| 静态同步或 TOML 解析通过即宣称真实行为完成 | `experiment-failed` / `superseded` | 证据层次不足 | 分开报告静态、镜像、加载和真实行为 | 不适用；只能补足相应真实证据 |
| 用最近有限轮次代替自包含委派合同 | `user-rejected` / `superseded` | 时间邻近不等于责任相关，容易携带旧路线并形成不可复现的隐式依赖 | `fork_turns: "none"` + 完整合同 + 项目稳定来源 | 宿主提供可验证的语义检索式上下文继承并经真实任务证明净收益 |

## 维护规则

1. 新事件先记录它改变了哪个行为，再记录日期和 commit。
2. 删除或取代规则时保留原文、SHA 或可定位的 Git 版本。
3. 用户否决、实验失败、条件适用、暂停和未验证分别记录。
4. 迁移承载层时记录旧层、新层和必须保留的语义。
5. 私有未发布变化不能宣称为公开发行版本。
6. 公开发布时记录私人 commit、公开 commit 或 tag 与运行镜像的对应关系。
