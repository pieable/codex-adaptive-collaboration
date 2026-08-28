# Prompt Lab

这个目录保存 Root Base 的公开发行权威版本和当前架构维护材料。维护者的私人 Prompt Lab 保存编写与完整演变历史；个人会话、账户配置、缓存和本机备份不包含在发行仓库中。

## 当前材料

- [`codex_base_instruction_5.6.md`](codex_base_instruction_5.6.md)：本次公开发行的 Root Base 权威正文；
- [`evolution-map.md`](evolution-map.md)：按行为和功能块组织的公开演变地图；
- [`functional-block-baseline.md`](functional-block-baseline.md)：当前功能块的保真基线和快速比较入口，不是完整发布验收；
- [`module-map.md`](module-map.md)：提示词分层、职责归属和维护边界总览；
- [`prompt-architecture/`](prompt-architecture/)：功能块承载层、运行时加载和发布说明；
- [`subagent-architecture/`](subagent-architecture/)：当前多代理规则、形成理由和公共基准。

## 结构原则

每个可维护提示词块都按从大到小的关系组织：**目的与原则 → 责任与决定权限 → 工作路线与阶段关系 → 具体行动与工具 → 验证、交回与例外**。下一层细化和落实上一层，不得改变上一层已经确定的结果、权限或适用范围。

## 版本边界

本文件夹中的 Root Base 是公开发行权威版本。维护者的私人 Prompt Lab 是编写与演变权威源；安装后的 `config.toml` 顶层 `developer_instructions` 是逐字运行镜像，只负责让宿主加载，不承担版本历史。

Worker Base、共享中性 Base、两个自包含阶段角色与其他命名角色 TOML 由 `agents/` 维护。所有角色共同需要的执行规则位于 `global/AGENTS.md`，领域方法位于 `skills/`。修改一层时不把正文复制进其他权威层。

发布不依赖 Python 同步脚本、常驻进程或 Hook。静态文件一致、TOML 可解析、宿主实际加载和真实任务行为是不同证据层，完成声明只覆盖已经验证的部分。
