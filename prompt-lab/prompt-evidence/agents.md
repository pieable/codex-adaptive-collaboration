# Agent `developer_instructions` 规则理由

本文件不参与运行。它覆盖 Shared Runtime Base、Worker Base 和每个 Agent TOML 的 `developer_instructions`。角色说明、模型、工具开关和正文共同决定实际角色；只核对正文而不看完整 TOML 不足以判断角色。

## 共同装配层

### A-01 Shared Runtime Base 只保留规则层级

- **对象：** `agents/shared-runtime-base-instructions.md`
- **状态：** `current-effective`
- **行为：** 同一提示词层内按“目的/原则 → 责任/权限边界 → 工作路线 → 具体行动 → 验证/交回”理解；下位规则落实上位规则，不改变上位结果、权限或边界。
- **理由：** 命名 subagent 不应继承 Root 的用户理解和整体路线，但仍需一个中性原则处理细则冲突。这个 Base 越中性，越不污染角色职责。
- **案例：** C-17；共同层曾混入无关职责并导致角色大规模删改。
- **来源：** `agents/PROMPT_HISTORY.md` 2026-08-28；Git `89ebad2`。
- **验证：** 静态装配已确认；宿主实际注入仍需 fresh task。
- **改变条件：** 只有运行时提供明确等价的层级解释且所有角色稳定获得时才能迁移。

### A-02 Worker Base 保护有界执行责任

- **对象：** `agents/worker-subagent-base-instructions.md`
- **状态：** `current-effective`
- **行为：** 执行型角色只完成合同已确定的一项责任；合同不足、需要扩大结果/权限/验收或高成本路线时上交；普通可逆细节自主完成；无结果和新证据时停止；向直接上级一次紧凑交回。
- **理由：** 多个执行角色共享同一种责任边界，逐份复制易漂移。Worker Base 数量足够多，保留共享层能降低维护成本；阶段负责人不适用这套约束。
- **案例：** C-08、C-11、C-21。
- **来源：** `agents/PROMPT_HISTORY.md` 保真并集、2026-08-28；Git `424ebec`、`89ebad2`。
- **验证：** 八个执行型 TOML 前缀静态一致；真实遵守度未统一验证。
- **改变条件：** 只有角色真正不再共享合同边界时才拆分；不能把 Worker Base 套到 code/research 阶段负责人。

## 基础执行角色

### A-03 Explorer 只回答一个本地证据问题

- **对象：** `agents/explorer.toml`
- **状态：** `current-effective`
- **行为：** 只读、不产生持久修改；以合同问题作为读取边界，从项目权威索引和最相关入口开始，只补查会改变答案的缺口，交回观察事实、推断、未知和证据位置。
- **理由：** Explorer 用来隔离原始材料，不是提供产品路线建议。它虽然只读，但仍需判断哪些文件、入口和证据真正回答合同问题，因此使用 Luna medium；按“可能相关”无限读取会浪费上下文，按最近对话猜责任又会读错副本。与它不同，Worker Luna 收到的做法、结果和验收已经确定，使用 low 连续执行即可。
- **案例：** C-08；C-21。
- **来源：** `agents/PROMPT_HISTORY.md` 2026-08-30；Git `6a25aa8`、`479a4ac`；2026-08-30 用户确认模型区别。
- **验证：** 权限和正文静态明确；真实宿主只读行为待验证。
- **改变条件：** 需要写入或连续实现时换角色，不扩大 Explorer 权限。

### A-04 Worker Luna 连续完成已经定型的实现

- **对象：** `agents/worker-luna.toml`
- **状态：** `current-effective + unverified`
- **行为：** 在合同内连续完成读取、实现、测试和普通修正，不因文件数或工作量停下；接口、结果语义或权限需要改变时上交；交回可验收结果。
- **理由：** Spark Worker 的 GPT-5.3 Codex Spark 独立额度很少，无法作为稳定主力；Worker Luna 被设计成同类确定执行的常用替代品。过去曾专门优化它的提示词和工作方式，希望在使用更稳定额度的同时尽量保留 Spark 一千多 Token/秒带来的低等待体验。Luna 便宜且快速，即使阶段理解有偏差，时间和额度损失也更可接受；它仍不能承担开放式架构判断。
- **案例：** 固定多文件合同能完成，开放式全仓诊断漏跨文件问题；见 `subagent-architecture/rule-rationale.md` R10、R31。
- **来源：** Git `f6d8ab0`、`424ebec`、`479a4ac`；`agents/PROMPT_HISTORY.md` 2026-08-30；2026-08-30 用户对 Spark 额度、速度目标和历史优化的确认。
- **验证：** 静态规则明确；过去的优化方法是否仍适合当前 Luna、宿主和工具尚未重新测试，大规模代码阶段的连续执行、速度和成本收益均待验收。
- **改变条件：** 结果含义、做法或验收仍需持续判断时，责任应留给 Code Executor，而不是让 Luna 猜。

#### 旧速度优化的当前审计

- Git `f6d8ab0` 的早期版本使用 Luna low，并关闭 apps、plugins、memories、Skill 注入等无关上下文；这些仍是当前运行时支持的有效减负手段。
- 早期版本还写入 `include_environment_context`、`include_permissions_instructions`、`[agents]`、`[tools]`、`[memories]`、`sandbox_mode`、`web_search` 等大量字段。当前 Codex `rust-v0.150.0-alpha.8` 的源码审计和本机 `agents/README.md` 说明这些字段不会按角色产生相应控制；删除它们不是行为弱化。
- Git `479a4ac` 恢复了 Worker Luna 必需的连续执行、最小实验、普通修正和一次交回语义。它增加了一些有效正文 Token，但防止上级逐步遥控和反复唤醒，不能仅为追求单次输出速度删除。
- 当前能确认的是配置支持面和历史语义，不能据此宣称 Luna 已接近 Spark 的一千多 Token/秒。需要用同一组确定合同，对速度、输入与输出 Token、正确率、返工次数和 Root 唤醒次数重新测量。

### A-05 Spark Worker 只在确定责任和独立额度收益成立时使用

- **对象：** `agents/worker.toml`
- **状态：** `conditional`
- **行为：** 与 Worker Base 相同，只承担已经划定的高速执行；是否选 Spark 由上级根据额度和速度收益判断，不由角色启动后自选。
- **理由：** Spark 在确定合同上极快，历史速度可达一千多 Token/秒，但独立额度很少，不能承担常态执行；开放诊断也容易漏项。角色选择条件放在 description 和调度者，避免正文重复与漂移，额度不足时由 Worker Luna 接替同类责任。
- **案例：** Spark 固定多文件实现通过五项验收，开放诊断漏跨文件问题。
- **来源：** `agents/PROMPT_HISTORY.md`；`subagent-architecture/rule-rationale.md` R10、R17、R28；2026-08-30 用户确认。
- **验证：** 既有实验支持边界；当前额度和服务状态每次由运行时判断。
- **改变条件：** Spark 能力、额度或价格变化时更新注册说明，不把动态价格写成角色自判流程。

### A-06 Default 只是兼容叶子入口

- **对象：** `agents/default.toml`
- **状态：** `conditional + unverified`
- **行为：** 未指定命名类型时作为兼容执行角色，只使用 Worker Base；不自行派生、不重新选择角色。
- **理由：** default 曾误路由到 Sol 并造成巨额上下文成本。保留是为了宿主兼容，不代表上级可以依赖它做自动路由。
- **案例：** C-12；浏览器任务误用 default Sol，约 4980 万输入 Token。
- **来源：** `subagent-architecture/rule-rationale.md` R17；Git `424ebec`、`89ebad2`。
- **验证：** 文件静态存在；宿主未指定类型时的真实模型和行为未知。
- **改变条件：** 宿主不再需要兼容入口时可删除；在此以前不得把它当专业角色替代品。

## 阶段负责人

### A-07 Code Executor 对一个代码模块或阶段负完整责任

- **对象：** `agents/code-executor.toml`
- **状态：** `current-effective + unverified`
- **行为：** 掌握模块目标、接口、核心判断、核心实现、整合和阶段验收；把已定型且可独立验收的工作用自包含合同和 `fork_turns:"none"` 交 Explorer 或 Worker Luna；阶段外决定上交 Root。
- **理由：** Terra high 当前不能可靠承担全部用户历史和大型任务取舍，但能完成中型代码责任并组织更便宜角色。它保留核心代码是为了让设计和实现判断不被切碎；较高推理强度用于模块接口、实现取舍、整合和验收，不要求它像 Root 一样反复审查整个用户历史。
- **案例：** C-11；Root 过度接管阶段；Terra 阶段曾积累过多轮询和 followup。
- **来源：** `agents/PROMPT_HISTORY.md` 2026-08-30；`subagent-architecture/rule-rationale.md` R29、R31；当前 TOML。
- **验证：** 静态职责和模型配置已确认；嵌套委派—整合—评审—返工—一次交回闭环待真实任务验证。
- **改变条件：** 模型能力和价格改变时可重新划分，但阶段必须仍由一个负责人维护接口、共享状态和完成判断。

### A-08 Code Executor 组织独立评审和视觉黑盒验证

- **对象：** `agents/code-executor.toml`
- **状态：** `current-effective + unverified`
- **行为：** 候选整合后按风险集中交 Reviewer；“要求修改”必须返工或证据反驳，“证据不足”不能通过。完成声明涉及可见界面、反馈或完整用户路径时，运行后委派 Visual Usability Tester 并安排复测。
- **理由：** 阶段负责人负责准备准确候选和闭环，Reviewer/视觉测试者提供独立证据，Root 不逐轮处理阶段内问题。
- **案例：** C-14、C-15；历史 UI 完成缺少首次用户视角证据。
- **来源：** `agents/PROMPT_HISTORY.md` 2026-08-29；`subagent-architecture/rule-rationale.md` R21、R25、R33。
- **验证：** 静态存在；真实代码阶段尚未完成全闭环。
- **改变条件：** 纯后台或无可见路径的任务不触发视觉测试；风险很低时评审范围可缩小，但不能把缺证据当通过。

### A-09 Research Lead 负责研究结构和综合，不亲自重复搜索

- **对象：** `agents/research-lead.toml`
- **状态：** `current-effective + unverified`
- **行为：** 掌握研究问题、覆盖结构、冲突、反例、竞争解释和阶段报告；把网络发现/收集/路线核验交 Web Researcher，把本地材料取证交 Explorer。只在报告已定位具体原文且一个明确差异会改变判断时读最小片段。
- **理由：** Terra high 的价值在中型研究综合、冲突处理和结论边界，不在执行大量来源搜索。让 lead “亲自接触一手资料”会诱发它重复搜索并压缩综合上下文；较高推理强度用于整合多条已经取回的证据路线，不用于替代 Web Researcher。
- **案例：** C-13；旧研究规则把搜索与上层判断混在一起。
- **来源：** `agents/PROMPT_HISTORY.md` 2026-08-29；`subagent-architecture/rule-rationale.md` R34；Git `aea9980`。
- **验证：** 责任静态清楚；完整多路线研究的稳定性和成本待验收。
- **改变条件：** 仅当具体矛盾无法由报告解决时读取最小原文，不扩展成新搜索路线。

### A-10 两个阶段角色完整内联官方 Skill 使用章节

- **对象：** `agents/code-executor.toml`、`agents/research-lead.toml`
- **状态：** `current-effective + unverified`
- **行为：** 两个阶段负责人像 Root 一样完整读取并执行适用 Skill，只作角色责任链适配，不压缩官方正文。
- **理由：** 阶段负责人也曾跳过或不完整读取 Skill。用户对 Root 章节做过多轮缩减实验，最终确认官方严格版本才能稳定保护完整读取、引用资源、脚本和资产复用及触发协议；阶段角色不能再使用自写摘要。
- **案例：** C-02、C-18。
- **来源：** Git `5befdc3`、`619556e`；`agents/PROMPT_HISTORY.md` R32 相关记录。
- **验证：** 当前两个 TOML 都含完整块；需用权威官方文本正式 diff，并在 fresh task 验证行为。
- **改变条件：** 只随官方协议更新，不参加普通 Agent 精简。

## 独立检查和操作角色

### A-11 Code Reviewer 对准确候选作三种结论

- **对象：** `agents/code-reviewer.toml`
- **状态：** `current-effective + unverified`
- **行为：** 只读核对准确基线、合同、候选、差异和证据，给出“可合入”“要求修改”或“证据不足”；沿调用关系和系统边界定向补查，不写补丁、不重定整体路线。
- **理由：** Reviewer 获得的是 Root 下放的局部判断权，必须有足够上下文并明确结论；旧版只列问题，无法区分无问题与证据不足。Terra high 用于沿真实调用关系、状态变化和系统边界判断候选能否交付，但它只审查一个准确候选，因此不需要 Root 的全任务上下文。
- **案例：** C-15。
- **来源：** `agents/PROMPT_HISTORY.md` 2026-08-29；DeepSeek Harness `dsh-code-review` 的公开思路；Git `86b6468`。
- **验证：** 静态合同完整；真实通过、打回和证据不足三条路径待验证。
- **改变条件：** Reviewer 可判断当前代码是否适合合入或交付，不获得修改代码、决定用户目标或宣布整个任务完成的权限。

### A-12 Web Researcher 负责一条网络取证路线

- **对象：** `agents/web-researcher.toml`
- **状态：** `current-effective + unverified`
- **行为：** 按主张、时间和来源距离搜索；来源只支持直接记载内容；记录日期、冲突、反例、覆盖范围、入口失败和未检查部分；区分路径内未发现与能力不足未覆盖。
- **理由：** 搜索工具成功或单一路径无结果不能证明候选完整。执行角色必须保留上级综合所需的覆盖和缺口证据。Luna medium 用于判断主张与来源距离、日期、冲突和覆盖缺口；它不承担跨路线综合，因此无需使用 Terra。
- **案例：** C-13。
- **来源：** `deep-research`；`search-source-registry`；`subagent-architecture/rule-rationale.md` R14、R16、R34。
- **验证：** 历史来源召回实验支持；当前完整联网研究尚未统一验收。
- **改变条件：** 研究路线和最终采用由 Research Lead/Root 决定，Web Researcher 不越权综合整个任务。

### A-13 Browser Operator 连续完成有界网页操作阶段

- **对象：** `agents/browser-operator.toml`
- **状态：** `current-effective + unverified`
- **行为：** 上级给出清楚的页面目标、操作边界和完成结果后，Browser Operator 保留页面状态，连续完成点击、输入、等待和页面结果确认；以真实外部后果判断授权。接口或 CLI 可以辅助，但完成条件是页面流程时不能替代真实页面。
- **理由：** 浏览器操控本身低效、交互往返多，却通常不需要上级 Agent 的高阶整体判断。专门角色把这段高操作成本工作从 Root 或阶段负责人隔离出去，避免上级逐步遥控、频繁被页面状态唤醒并重复支付昂贵上下文。Luna medium 用于保证它能可靠理解页面状态并完成操作；它以完成操作为目标，不承担 Visual Usability Tester 的界面易用性判断。
- **案例：** C-12。
- **来源：** `subagent-architecture/rule-rationale.md` R21；当前 TOML；2026-08-30 用户对创建目的的确认。
- **验证：** 角色边界静态明确；真实浏览器任务待验证。
- **改变条件：** 若任务只要语义数据且接口能直接给结果，可以不用浏览器；涉及真实 UI/登录态/外部动作时仍走页面路径。

### A-14 Visual Usability Tester 只做首次用户视角黑盒测试

- **对象：** `agents/visual-usability-tester.toml`
- **状态：** `current-effective + unverified`；本机未提交版本已由用户确认为最新版，本轮已同步到公开仓库
- **行为：** 不改产品、不设计修复；模拟没有源码知识的真实用户，只依据截图、坐标和人类可见的 Computer Use 路径完成入口、主流程、结果与失败反馈测试，报告可见缺陷、误解、阻塞、注意力竞争和证据。
- **理由：** 源码、DOM、OCR、API 或 Shell 会暴露普通用户没有的信息，使模型替界面补全操作。Luna low 是有意降低测试者的推理补偿能力：智力过高的模型可能绕过多数用户会遇到的理解障碍。人的注意力被视为宝贵资源；依赖费力搜索、记忆、排除干扰或在竞争元素间反复辨认，本身就是可用性成本。它与使用 Luna medium、以可靠完成操作为目标的 Browser Operator 有意区分。
- **案例：** C-14、C-23；历史 UI 验收缺失。
- **来源：** `agents/PROMPT_HISTORY.md` 2026-08-29；`subagent-architecture/rule-rationale.md` R25；2026-08-30 用户对本机未提交版本及设计目的的确认。
- **验证：** 本机 `agents` 工作区、运行副本和公开仓库现在包含字节一致的用户确认文字；真实 UI 路径和 Luna low 是否稳定暴露目标问题尚未验证。
- **改变条件：** 只有黑盒工具实际能力变化时调整证据手段；发现问题后修复责任回 Code Executor。

## 模型与能力开关

### A-15 角色配置只关闭不需要的上下文和能力

- **对象：** 全部 `agents/*.toml` 及 `agents/README.md`
- **状态：** `current-effective + conditional`
- **行为：** 角色配置用当前运行时支持的字段选择模型、推理强度和显式关闭项。TOML 只能关闭父配置已有的能力，不能为角色凭空开启权限、工具、MCP、环境或协作能力；不写运行时忽略的伪配置。
- **理由：** 叶子角色的上下文越集中，越能快速完成合同；但把无效字段当作能力控制会产生虚假安全感。早期 Worker Luna 的部分减负来自 low reasoning 和关闭无关注入，另一部分字段从未被宿主读取。
- **案例：** C-25；旧版曾使用 `include_environment_context`、`[tools]`、`sandbox_mode` 等无效字段，源码审计后删除。
- **来源：** 本机 `agents/README.md` 的运行时支持面；Agents Git `f6d8ab0`、`479a4ac`；当前 TOML。
- **验证：** 当前支持面来自 Codex `rust-v0.150.0-alpha.8` 源码审计和 TOML 静态检查；版本变化后必须重新核对。
- **改变条件：** 宿主新增或删除角色级字段时按当前源码和真实探针更新，不能从字段名称猜测其效果。

当前配置的作用分工如下。它记录字段的设计意图和静态状态，不把字段存在当作 fresh-task 已实际加载的证据：

| 角色 | 模型/推理 | 当前显式关闭 | 保留原因 |
|---|---|---|---|
| Code Executor | Terra high | apps、plugins、memories、bundled skills | 保留模块级代码判断和阶段内组织；避免无关外部上下文，配置没有关闭普通 Skill 指令注入 |
| Research Lead | Terra high | apps、plugins、memories | 保留研究结构、冲突处理和综合，并继续读取适用研究 Skill |
| Code Reviewer | Terra high | apps、plugins、memories、bundled skills | 需要可靠作出局部交付判断，不需要外部应用、记忆或无关 bundled Skill；配置没有关闭普通 Skill 指令注入 |
| Explorer | Luna medium | apps、plugins、memories、全部 Skill 指令 | 合同已限定本地证据问题；保留证据选择判断，减少无关方法注入 |
| Web Researcher | Luna medium | apps、plugins、memories、全部 Skill 指令 | 合同已限定取证路线；保留来源判断，研究方法由上级合同和角色正文给出 |
| Worker Luna | Luna low | apps、plugins、memories、全部 Skill 指令 | 结果、做法和验收已经确定，优先连续、低价执行 |
| Spark Worker | Spark high | apps、plugins、memories、全部 Skill 指令 | 在独立额度和速度收益成立时完成确定合同 |
| Browser Operator | Luna medium | 无角色级关闭项 | 需要继承父配置已经提供的浏览器能力并保持页面状态 |
| Visual Usability Tester | Luna low | memories、shell tool | 保留 Browser/Computer Use，阻止 Shell 证据破坏黑盒条件 |
| Default | 由宿主兼容入口决定 | 无角色级关闭项 | 仅保留兼容性，不把未验证的继承行为写成专业角色保证 |

表中“保留 Browser/Computer Use”只说明角色没有关闭父配置已有能力，不表示 TOML 自己能够开启它。具体模型价格与调度取舍仍由 Root Base 处理。

## 当前文件覆盖索引

| 运行文件 | 主要规则理由 |
|---|---|
| `shared-runtime-base-instructions.md` | A-01 |
| `worker-subagent-base-instructions.md` | A-02 |
| `explorer.toml` | A-02、A-03、A-15 |
| `worker-luna.toml` | A-02、A-04、A-15 |
| `worker.toml` | A-02、A-05、A-15 |
| `default.toml` | A-02、A-06、A-15 |
| `code-executor.toml` | A-07、A-08、A-10、A-15 |
| `research-lead.toml` | A-09、A-10、A-15 |
| `code-reviewer.toml` | A-02、A-11、A-15 |
| `web-researcher.toml` | A-02、A-12、A-15 |
| `browser-operator.toml` | A-02、A-13、A-15 |
| `visual-usability-tester.toml` | A-02、A-14、A-15 |

## 当前不应恢复或合并的旧结构

- 共同 Stage Base 当前没有必要：只有两个阶段负责人且领域方法不同。未来阶段角色显著增多并出现真实共享规则时可以重新评估，但这不是永久禁令。
- 共享 XML 大段拼接已被自包含角色替代；不得为减少几句重复重新混入无关职责。
- `worker`、`worker-luna`、`default` 不在启动后判断自己是否该被选择；选择权在注册说明和有调度权的上级。
- Agent TOML 不请求宿主注入环境或权限；这些由运行时和全局层提供。
- `visual-usability-tester.toml` 的本机未提交改动已由用户确认为最新版，本轮已从本机向公开仓库同步；以后仍不得用更旧的公开或安装副本反向覆盖。
