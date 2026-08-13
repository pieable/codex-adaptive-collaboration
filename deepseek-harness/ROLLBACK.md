# 回滚

1. 停止需要重新加载 preset 的 DSH 进程。
2. 在 `<DSH_HOME>/backups/codex-adaptive-collaboration/` 选择本次安装生成的时间戳目录。
3. 恢复其中的 `AGENTS.md` 和（如存在）`dsh-collaboration/` 到 `<DSH_HOME>` 的对应位置；若记录显示原对象不存在，删除本次创建的对应对象即可。
4. 运行 `dsh --profile web --dump-config`，然后创建新会话确认恢复结果。

不要以回滚为由编辑 DSH 的 npm 安装、凭据、sessions 或其他用户 preset。
