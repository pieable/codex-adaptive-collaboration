# 安装

安装仅写入 `$DSH_HOME/AGENTS.md` 与 `$DSH_HOME/.agent-presets/dsh-collaboration/`，并在同一 DSH home 的 `backups/codex-adaptive-collaboration/<timestamp>/` 备份将被替换的两个对象。不会读取或写入凭据、`settings.yaml`、`sessions/`、`storages/`、`profiles/` 或 `node_modules/`。

1. 安装 DSH `0.1.0-rc.6`，完成自己的 DeepSeek 登录/凭据配置；本脚本不处理该步骤。
2. 在仓库根目录运行 dry-run：

   ```powershell
   pwsh -NoProfile -File .\deepseek-harness\scripts\Install-DeepSeekHarness.ps1 -WhatIf
   ```

3. 确认输出的 DSH home、skills 路径和 module root 正确后，去掉 `-WhatIf`。
4. 运行 `Test-DeepSeekHarnessBundle.ps1`；再用 DSH 创建一个新会话并确认 preset 已加载。

## 可选参数

```powershell
pwsh -NoProfile -File .\deepseek-harness\scripts\Install-DeepSeekHarness.ps1 `
  -DshHome 'E:\agent-data\.dsh' `
  -DshModuleRoot 'E:\agent-data\.dsh\profiles\node_modules\@deepseek-ai'
```

`DshModuleRoot` 应包含 `dsh-compaction-basic` 与 `dsh-llm`。默认值是 `<DshHome>/profiles/node_modules/@deepseek-ai`。安装脚本检查两个包的版本必须是 `0.1.0-rc.6`，并将其解析成生成 plugin 所需的 `file:///...` URL。

安装不会修改 DSH 的普通默认模型选择；请在自己的 `settings.yaml` 或 UI 中配置 Root 的 DeepSeek model。固定角色在 preset 中固定 Flash / Pro 路由。
