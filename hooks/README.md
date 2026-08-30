# Fork Turns Guard

这个 Hook 在 subagent 创建前检查 `fork_turns`。只有显式的 `"none"` 放行；省略、`"all"`、有限轮数和其他值都会被拒绝。

Hook 会检查每一次 subagent 创建，但允许的 `"none"` 调用不显示常驻状态提示；只有真正拒绝不合规调用时才向模型和界面返回原因。

安装时把 `{{CODEX_HOME}}` 替换为真实绝对路径，并把这一项合并进现有 `hooks.json`，不要覆盖无关 Hook。Hook 文件变化后让 Codex 正常显示信任确认，不复制或伪造其他机器上的 `trusted_hash`。

当前 matcher 同时保留历史别名和已在真实 Desktop rollout 中观察到的 `multi_agent_v1__spawn_agent`。宿主工具名变化后，先从新任务日志确认 canonical name，再更新 matcher 和脚本中的同一名称集合。

离线脚本测试只能证明输入解析和拒绝 JSON，不能证明宿主实际把协作工具调用交给了 Hook。安装报告应把静态测试和 fresh-task 拦截分开说明。
