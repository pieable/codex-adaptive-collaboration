# DeepSeek Harness 协作 Preset

这是本仓库面向 DeepSeek Harness（DSH）的可安装 Agent preset bundle，不是独立 agent 平台。它复用 DSH 的会话、工具、subagent、compaction 和 Skills 机制。

## 内容

- `templates/AGENTS.md`：Root 的可移植协作规则；
- `preset/agent.cordis.yml.template`：Root 工具和六个固定角色；
- `preset/plugins/compaction-custom-prompt.mjs.template`：自定义压缩摘要适配器；
- `scripts/Install-DeepSeekHarness.ps1`：生成本机路径后的可运行 preset；
- `scripts/Test-DeepSeekHarnessBundle.ps1`：静态检查与已安装 preset 检查。

六个固定角色都是叶子：explorer、web-researcher、browser-operator、research-lead、worker 使用 `deepseek-official/deepseek-v4-flash`；code-executor 使用 `deepseek-official/deepseek-v4-pro`。Root 保留普通 `subagent`、`subagent_fork` 和控制/编排工具，固定角色不具有下级委派或控制工具。

## 前提与限制

- 需要 DeepSeek Harness **0.1.0-rc.6**，并已安装 `deepseek-official` provider；本 bundle 不写入 API key、settings、sessions 或 node_modules。
- custom compaction 继承 DSH 的内部 `dsh-compaction-basic` / `dsh-llm` API，故该版本精确 pin 是有意的实验性兼容边界；升级 DSH 前先运行测试。
- 模板不含作者机器路径。安装脚本会根据仓库位置、`DSH_HOME` 和已安装 DSH package 生成本机绝对 file URL；生成物不应提交回仓库。
- Skills 仍使用本仓库的 `../skills`，未复制第二份。移动或删除本仓库后应重新运行安装脚本。

## 安装与验证

在仓库根目录执行：

```powershell
pwsh -NoProfile -File .\deepseek-harness\scripts\Install-DeepSeekHarness.ps1 -WhatIf
pwsh -NoProfile -File .\deepseek-harness\scripts\Install-DeepSeekHarness.ps1
pwsh -NoProfile -File .\deepseek-harness\scripts\Test-DeepSeekHarnessBundle.ps1
```

详见 [INSTALL.md](INSTALL.md)、[TEST-CONTRACT.md](TEST-CONTRACT.md) 和 [ROLLBACK.md](ROLLBACK.md)。
