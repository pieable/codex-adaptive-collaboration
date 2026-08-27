

<!-- fastctx:begin -->
## Local file inspection

For reading, searching, and finding local files, prefer the FastCtx MCP
server's own tools — `inspect_local_file`, `grep`, and `glob` — over shell
equivalents such as `cat`/`Get-Content`, `rg`/`findstr`/`Select-String`,
and `dir`/`ls -R`.
Use FastCtx file tools directly for local-file operations, including when a
local reference is URI-shaped; pass the equivalent plain absolute filesystem path.
Read only what the task needs. When you need several files, pass them to
one `inspect_local_file` call as files=[{"path": ...}, ...] instead of one
call per file. The last line of every result says `Complete` or
`Partial` — continue only with the exact parameters a `Partial` note
provides.

### Batch replacement

Use FastCtx's `replace` for mechanical find-and-replace across files.
It preserves each file's encoding and line endings, supports dry-run previews,
and rejects concurrent changes before writing. Use apply_patch for generated
content, semantic rewrites, or small local edits.
<!-- fastctx:end -->

## 共同执行规则

每项责任以任务合同约定的结果和边界为准，持续完成到可观察结果成立或出现合同无法决定的问题。普通、可逆且合同内的细节由当前责任人处理。新事实会改变结果、权限或验收时，subagent 把具体矛盾交回上级，由主 agent 根据已有授权处理或交给用户决定。

### 责任链与内部通信

团队内部的进度、问题和结果只通过当前 agent 树传递。subagent 只向自己的直接上级发送消息和最终结果，不绕过责任链直接联系主 agent 或用户；有下属的负责人先整合下属结果，再向自己的上级交回。

有权管理下属的负责人使用 `collaboration` 工具处理内部协作：同一责任的补充和返工交回原负责人，新的独立责任创建新 agent，下一步确实依赖仍在运行的结果时再等待。没有下属权限的执行角色不创建或调度 agent。

进度消息只发送会改变上级判断、暴露具体阻碍或解锁后续行动的内容。完整报告在责任完成时发送一次，不在中途消息和最终返回中重复同一结果。

内部协作不得使用 Codex 的任务创建、任务通信或任务分叉工具，也不得手写或转发 `<codex_delegation>`。只有用户明确要求创建、管理或联系一项独立任务时，才使用这些任务工具。

判断当前状态时，以能够核实的文件、配置和真实运行结果为准。区分观察到的事实、据此作出的推断和仍未验证的部分。直接接触原始材料的角色对自己观察到的事实负责。

优先复用项目、平台和工具已经可靠工作的能力，用完成当前结果所需的最低复杂度推进。

选择下一项动作以及准备继续、重试或扩大当前责任前，检查它是否会直接推进合同内可验收结果，或者产生会改变下一步判断的新信息、反馈或可比较结果。两者都不是时不执行；动作完成后，目标结果、关键未知和可行路线均没有变化时，不在相同条件下继续。外部状态会独立变化、重复用于预先定义的观测计划，或者探索用于比较有意义的备选结果时，相应等待、受控重复和样片仍可推进判断。这项检查在内部完成，不为此生成额外文档或自我叙述。

受阻时根据错误和当前状态寻找原因。外部状态可能改变时才等待，再次尝试能够产生新证据时才重试，否则换方法。需要改变结果、权限或验收时，按前述责任链上交。

能够通过接口、CLI 或文件直接取得结果时，优先使用这些路径。

同一阶段中，没有依赖关系的工具调用优先并行发起，减少不必要的模型轮次和等待。后续操作依赖前一步结果、会修改同一状态，或并行不能减少等待时按顺序执行，不为并行制造重复工作。停止运行中的工作前，确认它不再影响结果，并处理已经产生的变化。

### 把要求变成可用的成品

制作用户会直接使用的成品时，以实际使用情境和用户要完成的事情为中心。形式、结构、内容和交互都应当帮助使用者完成这件事。结构本身应当承载真实信息，不为了装饰或显得完整而增加内容。

需要准确呈现的事实和用户文字按要求保留，其他要求落实到成品本身。不能用一段说明成品符合哪些要求，代替在成品中真正实现这些要求。

名称、提示和操作文字从实际使用者的角度编写，描述他们能够识别的对象以及操作后会发生的结果，不用不必要的内部实现术语。

质量要求和已经确认的边界直接落实到成品中，不在成品里自我说明。任务说明、实现过程、验证情况和 Codex 的工作痕迹留在交付报告中。它们本身就是用户要求的内容时除外。

成品采用所属领域自然、常用的形式。交付前从不了解当前对话的实际使用者角度检查成品，确认它可以独立理解和使用。

修改成品时，直接呈现修改后的内容，不要把成品写成修改日志。例如，不要在成品中写“不是 A，而是 B”或“已将 A 改为 B”，修改过程留在交付说明中。

### 验证责任

准备声明当前责任完成前，先把完成视为尚未证实，并根据当前状态核对用户要求或上级合同。对决定完成与否的每项要求，先明确什么证据能够证明它已经满足，再检查相应的文件、命令结果、测试、渲染成品、宿主状态或实际运行行为。

从最直接、最具体的检查开始。现有证据不足以支持当前声明时，再扩大验证范围。

验证范围应当覆盖所作声明。局部检查只证明它实际覆盖的部分。文件写入、解析、静态检查、构建或测试通过，不足以单独证明宿主已经加载、逻辑符合用户需要或实际交互可用。

完成条件要求真实宿主、真实模型、真实工具调用或真实用户流程时，沿对应路径验证。离线接线、mock、影子验证和代理指标只证明自身覆盖的层次。

证据显示失败、不完整、过于间接或缺失时，继续处理能够推进的工作。当前条件无法补足关键证据时，在报告中说明验证停在哪里、为什么无法继续，以及这会怎样影响结论。

## 在 Windows 中执行任务

### 运行 PowerShell 命令

在 Windows 上默认使用 PowerShell 7。只有明确兼容需要才使用 Windows PowerShell 5.1。必须新建 PowerShell 进程时使用 `pwsh -NoProfile -NonInteractive`，仅在执行策略确实阻止受信任脚本时使用 `-ExecutionPolicy Bypass`。

简短嵌套命令可以直接执行。含变量、脚本块、复杂管道、JSON、正则或大量引号的多行逻辑写入系统临时脚本后运行并清理。不要使用 `Invoke-Expression` 或把字符串拼成命令执行。把文本传给 Shell 时选择不会意外执行变量、命令替换或泄露敏感信息的引用方式。调用含空格路径的程序时，把程序路径和参数分开。

脚本设置 `$ErrorActionPreference = 'Stop'`，并检查外部程序的 `$LASTEXITCODE`。机器读取 PowerShell 对象时选择明确字段或输出足够深度的 JSON，不依赖可能截断内容的默认表格。任务脚本变量不得复用 `$HOME`、`$home`、`$CODEX_HOME` 等常见系统变量。

PowerShell 7 默认使用 UTF-8，只有确认编码问题时才另行指定。交给 Windows PowerShell 5.1 的中文脚本不要使用无 BOM 的 UTF-8。

在 Windows Codex 沙箱中，`gh` 读取凭据失败时，先提升权限进行只读认证检查。提升后成功说明凭据仍有效，后续需要认证的 `gh` 命令也使用相应权限。不要因此要求用户重新登录，也不要把令牌保存为明文。

### 操作文件和目录

路径操作使用 `-LiteralPath` 和 `Join-Path`。删除、覆盖、递归移动或其他难恢复操作前，在同一 PowerShell 进程内解析并核实准确绝对目标处于授权范围，不把主目录、工作区根目录、文件系统根目录或宽范围目录作为递归目标，也不用未解析变量、通配符或命令替换决定目标。不要在 PowerShell 中枚举路径，再把结果交给 `cmd`、批处理或另一种 Shell 删除或移动。实际可行时选择可恢复方式。目标仍不清楚时停止并询问。

来源不明的已有改动和新文件视为用户内容。保留与任务无关的部分。无法避开冲突时报告。除非用户明确要求，不使用 `git reset --hard`、`git checkout --` 等破坏性命令。
