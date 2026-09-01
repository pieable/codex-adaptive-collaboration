# 提示词历史案例索引

本文件保存会改变规则判断的去重案例。案例证明其直接覆盖的事实和失败机制，不自动证明某一句候选文字就是唯一正确写法。

| ID | 案例与直接结果 | 支持或否决的机制 | 状态 | 主要来源 |
| --- | --- | --- | --- | --- |
| C-01 | 成熟 Root Base 从约 9083 字符整体压到 6403 字符，同时改变人格、写作、协作和交付体验；静态检查没有发现损失，用户要求整体恢复 | 大范围生成式重写不能用字数和结构证明保真 | `user-rejected + experiment-failed` | `prompt-lab/prompt-architecture/test-results.md` 的“整篇分层候选”；`prompt-lab/evolution-map.md` 的统一否决表 |
| C-02 | 主 agent 已读取并声明使用 Skill，却没有完成演变调查和职责继承检查，仍提出偏差删除建议 | 读取或复述 Skill 不等于执行其中的方法 | `current-effective` 的反例 | `prompt-lab/prompt-architecture/test-results.md` 的 Skill 完整读取测试 |
| C-03 | 高风险权限、PowerShell、文件和破坏性操作与普通规则一起被压缩 | 高风险路径需要保留会阻止具体损失的明确顺序和护栏 | `current-effective + conditional` | `prompt-lab/prompt-architecture/test-results.md` 的高风险压缩记录 |
| C-04 | 同一任务中新建角色仍读取启动时缓存的旧 `AGENTS.md`，无法证明磁盘新规则已经加载 | 静态文件和当前任务热加载不能替代 fresh-task 验证 | `unverified` 证据边界 | `prompt-lab/prompt-architecture/test-results.md` 的缓存污染记录 |
| C-05 | 默认路径重写把第一次验证当作停止点，并删弱不扩大授权、无变化不继续和监控语义 | 达到结果、继续、交接、换路和停止必须由可观察结果与新证据决定 | 首轮候选失败，修正版 `current-effective` | `prompt-lab/prompt-architecture/test-results.md`、`prompt-lab/evolution-map.md` |
| C-06 | 同批结构修改遗漏决策支持、偏好边界、Plan mode、成品独立可用、视觉证据和 Skill 资源复用，同时混入三次工具软上限等未经确认规则 | 一批修改失去信任后必须检查全部差异，旧到新和新到来源两个方向都核对 | 已恢复；同批新增被撤回 | `prompt-lab/prompt-architecture/test-results.md` 的保真并集审查 |
| C-07 | 反枚举只把四项缩成两三个概括词，或把并列判断强行改成固定顺序，模型仍需猜共同关系 | 开放现实提炼判断；封闭合同、高风险边界和独立行动项保留完整枚举 | `current-effective` | `skills/write-instructions-zh/MODIFICATION_LOG.md`、评测案例十四至十六 |
| C-08 | Worker 继承最近对话后选错工作区旧副本，补充路径后又擅自新增 `quick-worker` | 执行者用自包含合同和稳定来源，不从最近父对话重新解释目标或新增角色 | `experiment-failed` | `prompt-lab/subagent-architecture/rule-rationale.md` 的 Worker 编辑案例 |
| C-09 | `fork_turns:"all"` 或省略参数把完整 Root 历史带入 subagent，污染角色责任并消耗大量上下文 | 自动委派禁用完整历史继承，必要信息写入合同 | `user-rejected` | `prompt-lab/evolution-map.md` 的上下文继承和统一否决表 |
| C-10 | 有限最近轮次仍按时间截取无关旧路线，形成不可复现的隐式依赖 | 当前自动委派统一 `fork_turns:"none"` | `current-effective + unverified` | `prompt-lab/evolution-map.md` 2026-08-30 校准 |
| C-11 | 长任务中 Root 创建大量 subagent、频繁 wait/followup 并重做读取，出现 14 至 21 个 subagent、43 至 57 次等待，以及约 5758 万输入 Token 的任务 | 阶段负责人吸收阶段内组织、返工和验收，Root 保留整体框架和跨阶段决定 | 失败机制已观察；新结构真实成本仍待验证 | `prompt-lab/subagent-architecture/rule-rationale.md` 的 Root 调用与成本案例 |
| C-12 | 浏览器任务误用 default Sol，出现 15 回合、102 次等待和约 4980 万输入 Token | 浏览器连续阶段交给专业角色，不用 Root 或 default 逐步遥控 | `current-effective + unverified` | `prompt-lab/subagent-architecture/rule-rationale.md` 的浏览器角色案例 |
| C-13 | 半导体新闻两路编排只返回 2 条，直接搜索有 8 条；EDGAR 枚举找回漏掉候选，同时记录 403 和超时 | 搜索覆盖、入口失败和未检查状态必须保留，工具成功不等于研究完整 | 已观察的研究案例 | `prompt-lab/subagent-architecture/rule-rationale.md` 的来源召回案例 |
| C-14 | 一个产品/代码任务在 source of truth 不稳定时继续统计、UI、发布物和评审，局部测试通过后才发现源码、发布物、说明和体验互相不一致 | 局部静态通过不能代替真实入口、端到端结果和用户体验 | 已观察的失败 | `prompt-lab/subagent-architecture/rule-rationale.md` 的结果一致性案例 |
| C-15 | 旧 Reviewer 只列问题，无法区分“没有发现问题”和“证据不足” | Reviewer 必须对准确候选给出可合入、要求修改或证据不足 | `current-effective + unverified` | `agents/PROMPT_HISTORY.md`、`prompt-lab/subagent-architecture/rule-rationale.md` |
| C-16 | RP 记忆任务沿局部 `evidence/append` 路线不断修补，测试全绿却没有证明接入用户真实工作流，用户询问后才承认走偏 | 先验证最小核心用户结果；路线失效时回到问题和产品层，不继续补偿当前方法 | `experiment-failed` | 旧任务“优化Subagent体系”及本轮用户复述 |
| C-17 | Agents 提交 `1283c51` 一次删除 11 个角色提示词共 525 行，随后 `149b30a` 恢复阶段角色 Skill 协议和职责 | 减少重复或建立共享层不授权大规模删除角色专属边界 | 过度修改已回退 | Agents Git `1283c51`、`149b30a` 和 `agents/PROMPT_HISTORY.md` |
| C-18 | 用户多次尝试缩短 Root Base 的官方 Skill 使用章节，实际会漏掉完整读取、引用资源、脚本与资产复用、触发说明等行为；提交 `5befdc3` 的摘要版最终由 `619556e` 恢复，并同步两个阶段角色 | 官方固定协议不能参加普通精简；目标模型需要完整读取的文字必须保持 | 过度压缩已回退，官方严格版本保留 | 私人 Prompt Lab Git `5befdc3`、`619556e`；`prompt-lab/evolution-map.md`；2026-08-30 用户确认 |
| C-19 | 泛化/精简过程中 Ponytail 成熟路线候选和订阅内模型成本比例被删，用户随后分别要求恢复 | 会独立改变路线和调度判断的成熟有界集合、经济背景不能压成宽泛原则 | 已恢复；实际行为仍待验证 | 私人 Prompt Lab 历史、`prompt-lab/evolution-map.md` 的路线和成本条目 |
| C-20 | `write-instructions-zh` 的早期精简删除规则储藏库、保真并集和演变记录，提交 `5fc6724` 回滚并恢复可靠基线 | 运行正文、当前规则原因、历史版本和否决路线必须分层保存 | 已恢复 | `skills/write-instructions-zh/MODIFICATION_LOG.md`、冻结快照 `5fc6724` |
| C-21 | explorer 在完成前用消息发送结论，Root 提前醒来；explorer 又继续读取并补发，最后被中断 | 普通过程消息不替代完成时一次性交回，只有改变上级判断或解除阻碍才提前通信 | 已观察的失败 | `prompt-lab/subagent-architecture/rule-rationale.md` 的内部通信案例 |
| C-22 | 一项测试错误假定仓库根目录存在 `package.json`，失败来自测试设计而非模型退化 | 测试必须对应真实入口，测试错误不能被写成模型长期禁令 | `experiment-failed` 的测试路线 | `prompt-lab/prompt-architecture/test-results.md` 第一轮测试 |
| C-23 | 用户在另一任务中把 Visual Usability Tester 改为只依据截图、坐标和 Computer Use 的低智力黑盒测试者，并加入注意力竞争观察；2026-08-30 确认本机未提交版本是已认可最新版 | UI 测试者不能用源码、DOM、OCR、API 或高推理能力替界面补全操作；人的注意力成本属于可用性结果 | `current-effective + unverified` | 本机 Agents 未提交差异；2026-08-30 用户确认 |
| C-24 | 用户说明创建 Workflow Route Mapper 的首要目的是保存失败：失败可能为成功路线提供灵感，也能告诉后来接力的模型为什么不选旧路线 | 会改变后续判断的失败属于可复用知识；保留失败原因可以防止相同条件下重复无用功 | `current-effective` | 2026-08-30 用户确认；`workflow-route-mapper/SKILL.md` |
| C-25 | Spark Worker 曾以一千多 Token/秒完成确定执行，但独立额度很少；Worker Luna 被专门优化为常用替代品。旧版部分有效减负来自 low reasoning 和关闭无关注入，大量环境、权限与工具字段则从未被运行时读取 | 高速稀缺角色只用于适合的确定合同；无效配置不能被当作速度优化，稳定低价替代角色需要以当前真实速度、质量、返工和 Root 唤醒成本重新验收 | `conditional + unverified` | Agents Git `f6d8ab0`、`479a4ac`；本机 `agents/README.md`；2026-08-30 用户确认 |
| C-26 | Workflow State Distiller 的“决定理解保存在哪里”整章在 2026-08-12 被记录为有意删除，却在 Git `22d1993` 恢复且无原因；2026-08-30 用户确认现章可以保留，但只是附带作用 | 当前正文和旧维护记录冲突时不能任选一边；用后续用户决定解决状态，同时保护 Skill 的蒸馏校准主目的 | `current-effective + conditional` | `workflow-state-distiller/CHANGELOG.md`；Git `22d1993`；2026-08-30 用户确认 |
| C-27 | `fork_turns` Hook 的旧 matcher 没有包含 Desktop 实际调用名 `multi_agent_v1__spawn_agent`，真实测试中 `all` 没有触发 Hook 并成功创建 subagent | Hook 必须根据真实宿主观察到的 canonical tool name 匹配；脚本和配置静态正确不能证明工具调用已经经过 Hook | matcher 已修正；真实拦截仍 `unverified` | rollout `01a04f09-695b-7b70-898b-14173036b94f`；`hooks/`；`runtime-configuration.md` RC-06 |
| C-28 | 用户提出的具体方案可能不适合整体产品，但其不满、直觉和建议出现的原因常能指出真实问题或新方向 | 先恢复用户想改变的体验和底层需要，再结合全局约束设计方案；既不盲从表面方案，也不忽略用户信号 | `current-effective` | Root Base R-17；Mark Rosewater Lesson 19；NN/g User Need Statements 与 Bad Design Suggestions；2026-08-30 用户确认 |
| C-29 | 旧 `company-research-brief` 经多轮实验积累了固定字数、固定标题、强制 report-writer、DeepSeek 润色和 Word 样式等已撤回路线，但真实用途始终是帮助风投同事补全公司信息、比较产品线并作投前初筛 | 重新制作成熟 Skill 时从真实使用决定和有效证据边界重建，不把全部历史文字或已否决实现自动并集回当前正文 | 新稿 `current-effective + unverified` | 旧本机 Skill 与命名备份；企业投研 rollout；`skills/company-research-brief/RULE_RATIONALE.md` |
| C-30 | 当前体系已有 Root 整体理解和五项委派合同，但跨多个阶段或任务接续时，用户校准主要停留在 Root 当前上下文，模块计划、工人合同和 Reviewer 输入没有共同指向一版可更新的需求 | 中大型任务由 Root 维护当前任务规格；阶段负责人导出模块计划，工人只接收相关合同，Reviewer 对照当前规格检查偏差，规格变化只使受影响工作失效 | `current-effective + unverified` | 2026-09-01 用户校准；私人 Prompt Lab `6b08b1d`；Agents `d52a151`；GitHub Spec Kit Agentic SDD、spec template、evolving specs、analyze 与 converge；`subagent-architecture/rule-rationale.md` R39 |

## 仍缺少的真实案例

- 新 Root Base 在 fresh task 中是否稳定加载并形成目标行为。
- `code-executor` 的嵌套委派、评审、返工和一次交回闭环是否实际降低 Root 调用。
- `research-lead` 与 `web-researcher` 的搜索和综合分工在完整研究任务中是否稳定。
- `visual-usability-tester` 的 Browser/Computer Use 真实黑盒路径。
- `fork_turns:"none"` Hook 是否在新 Desktop 任务中真正拦截省略、`all` 和有限轮次。
- ELI5 阶段报告在真实长任务中能否持续让用户快速恢复全局理解。
- 当前任务规格在真实跨阶段任务中能否减少理解漂移、无效返工和 Root 重复解释。
