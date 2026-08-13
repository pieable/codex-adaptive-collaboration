# 演变记录

## 2026-08-14：可发布 DSH preset bundle

原实现位于用户的 `~/.dsh`，直接引用本机 skills、plugin 和 profile node_modules 的绝对路径，并混有真实 smoke session 与备份证据，不能直接公开。

本 bundle 保留 DSH 已有的 Root delegation、六个固定 DeepSeek 角色和自定义 compaction；模板以占位符表达安装时才可得的 skills 和 `file:///` 路径。安装脚本在目标 DSH home 备份用户的 AGENTS 与同名 preset，验证精确 DSH 版本后生成部署文件。未复制 Skills，继续引用本仓库的单一来源。

保留边界：custom compaction 仍依赖 DSH 0.1.0-rc.6 的内部 API；模板静态检查不能代替真实模型、工具或长期 compaction 触发验证。
