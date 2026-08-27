# 可直接采用的公开测试集

更新日期：2026-08-04

目标是比较不同 agent 组织和执行方式，不自行编写题目。测试时固定模型、预算、并发、随机种子和工具接口，使用测试集自带的成功率或评分，再从本地请求日志补充成本、时间、token、工具调用和失败类型。

## 首选

| 场景 | 测试集 | 适合原因 | 主要限制 |
| --- | --- | --- | --- |
| 角色与组织 | [TeamBench](https://github.com/ybkim95/TeamBench) | 直接提供 solo、受限团队、无规划、无验证和完整团队等消融；记录任务得分、通过率、token、轮数和成本，MIT | 固定为 Planner、Executor、Verifier 三类角色，不能覆盖所有自定义结构 |
| 多代理网络任务 | [AgentWebBench](https://github.com/cxcscmu/AgentWebBench) | 同时支持单代理与 multi-agent 协调，包含搜索、推荐、多跳问答和深度研究；记录交互轮数、联系代理数和检索请求，MIT | 需要锁定数据、模型和检索服务版本；较新，生态仍在形成 |
| 深度研究 | [BrowseComp-Plus](https://github.com/texttron/BrowseComp-Plus) 或 [DeepResearch Bench II](https://github.com/imlrz/DeepResearch-Bench-II) | 前者使用固定语料并记录工具调用，复现性较好；后者用细粒度规则评报告、证据和呈现 | BrowseComp-Plus 全量前沿模型成本高；DRB-II 依赖评审模型，分数会随评审模型变化 |
| 浏览器操作 | [WebArena-Verified](https://github.com/ServiceNow/webarena-verified) 的 hard 子集 | 258 个较难任务，可通过 BrowserGym/AgentLab 使用统一接口，Apache-2.0 | 需要自托管网站和 Docker；公开静态任务存在训练污染风险 |
| 代码库修改 | [SWE-bench-Live](https://github.com/microsoft/SWE-bench-Live) | 持续加入较新的真实仓库任务，比固定旧题更能降低污染，MIT | 环境构建和部分任务质量仍需按版本核对 |
| 终端与工程执行 | [Terminal-Bench 2.0](https://github.com/harbor-framework/terminal-bench) | 每题有隔离容器、测试和参考实现，可以并发运行，Apache-2.0 | 任务耗时长，运行前需要锁定版本和镜像 |

## 备用与研究用途

- [MultiAgentBench/MARBLE](https://github.com/MultiagentBench/MARBLE)：适合比较 star、chain、tree、graph 等通信拓扑，MIT；成本指标需要外部补充。
- [Gaia2/ARE](https://huggingface.co/datasets/meta-agents-research-environments/gaia2)：动态仿真任务包含 Agent-to-Agent、搜索、时间和噪声，能够记录调用、token 和延迟；它不是真实互联网环境。
- [OSWorld](https://github.com/xlang-ai/OSWorld)：可测试主任务的桌面操控，环境完整但部署和运行成本高。当前 Computer Use 保留给主任务，因此不纳入 subagent 首轮测试。

## 不作为首选

- SWE-bench Verified 只保留为历史回归基线。OpenAI 的[审计说明](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/)指出公开仓库污染以及任务和测试质量问题，已经不适合判断前沿代码 agent。
- 原始 [BrowseComp](https://openai.com/index/browsecomp/) 依赖实时网页，适合测最终检索能力，但网站变化会降低不同组织方案之间的可复现性。
- [LiveResearchBench](https://github.com/SalesforceAIResearch/LiveResearchBench) 能评实时深研，也覆盖单代理和多代理系统；数据许可为非商业用途，网页变化和评审模型也会影响复现。

## 实际采用顺序

1. 先运行 TeamBench 的小规模或隐藏种子配置，确认角色分工、规划和验证是否带来净收益。
2. 用 AgentWebBench 子集检查网络搜索与深研组织；需要固定语料时改用 BrowseComp-Plus。
3. 用 Terminal-Bench 2.0 小子集和 SWE-bench-Live 检查代码执行结构。
4. 浏览器执行稳定后再部署 WebArena-Verified hard。
5. OSWorld 留给主任务 Computer Use 的独立评估，不与 Luna 浏览器执行结果合并成一个总分。

不同测试集的动作空间和环境不同，分别报告结果，不计算一个混合总分。
