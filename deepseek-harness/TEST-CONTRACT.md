# 测试合同

安装前静态检查必须确认：模板没有真实用户路径、session id、输出目录或 credential 值；占位符完整；YAML 经当前 DSH 随附 `js-yaml` 解析；plugin 可通过 `node --check`。

隔离安装检查使用显式的临时 `DshHome` 和 `DshModuleRoot`，只验证生成文件和备份计划，绝不触碰真实 `~/.dsh`。实际安装后应运行 `dsh --profile web --dump-config`，并以新会话确认 persona、固定角色模型和工具面。

未由静态检查证明的项目：真实 provider 凭据、六个角色逐一工具调用、浏览器自动化（当前 bundle 不提供 Computer Use）、压缩达到约 200K 后的质量与事件链。
