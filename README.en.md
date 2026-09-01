<p align="right">
  <a href="README.md">中文</a> | <strong>English</strong>
</p>

<div align="center">
  <img src="assets/four-star-dragon-ball.png" alt="Four-Star Dragon Ball" width="180">

  <h1>
    Dragon Ball Agent
    <br>
    <sub>Come forth, Shenron! Grant my wish!</sub>
  </h1>
</div>

After going to great lengths to collect ~~$200 worth of credits~~ all seven Dragon Balls...

**User:** Come forth, Shenron! Grant my wish!

**Shenron:** State your wish.

**User:** I want a GPT that can truly work with me over the long term! It should always remember what I am actually trying to accomplish. It should handle simple things on its own and bring in subagents for complex work. And no matter what happens, it must never interrupt me with questions—just decide everything by itself!

**Shenron:** That wish cannot be granted.

**User:** Why not?

**Shenron:** Your requirements contradict each other.

**User:** ...Fair enough. Let me revise it. Normally, it should use its own judgment. But when the goal is unclear, an important decision is at stake, or the cost could be significant, it should ask me. The rest of the time, it should not come running to me over every trivial detail.

**Shenron:** That can be granted.

**User:** One more thing! Subagents should not be summoned at random, either. It should handle simple work itself. When the method and the definition of done are already clear, it can delegate the task directly. But if a stage still calls for ongoing investigation, judgment, and changes of direction, put one lead in charge of the entire stage.

**Shenron:** Your wish is clear.

**User:** Then begin!

**Shenron:** Your wish is being granted.

...

**User:** Wait!

**Shenron:** Go on.

**User:** I changed my mind about that earlier part. If there is already a complete result, do not redo the same work just for the sake of “independent verification.” Only investigate further when there is an actual contradiction or gap.

**Shenron:** That can be granted.

---

Dragon Ball Agent is a Codex configuration system for long-term collaboration. Root understands the user's goals, maintains the overall plan, and owns final acceptance. Phase leads own entire stages. Execution-oriented subagents take on only responsibilities whose boundaries and acceptance criteria are already settled.

> This is a community configuration, not an official OpenAI project.

## What it solves

- Deliver the smallest usable result or Demo that can validate the core value first, rather than continuing to invest in an unproven approach;
- Before continuing, retrying, or expanding scope, check whether the next action will advance a verifiable outcome or produce new evidence, avoiding busywork and endless rabbit holes;
- Keep the user's goals, the overall plan, and cross-stage decisions with Root, while isolating implementation details and long logs within the responsible layer;
- Delegate small, well-defined tasks directly, and assign work that still requires ongoing judgment and multiple rounds of coordination to a phase lead;
- Escalate high-cost runs, broad changes, and cross-stage impacts through the responsibility chain;
- When a stage ends, the plan changes, or the work is about to scale up, have Root show the user where things stand with a visual-first explanation.

## Current prompt assembly

| Layer | Source | Root | Named subagent (`fork_turns: "none"`) |
| --- | --- | --- | --- |
| Neutral Runtime Base | [`agents/shared-runtime-base-instructions.md`](agents/shared-runtime-base-instructions.md) | Loaded | Loaded |
| Root Base | The `config.toml` runtime mirror of [`prompt-lab/codex_base_instruction_5.6.md`](prompt-lab/codex_base_instruction_5.6.md) | Loaded | Replaced by the role's `developer_instructions` |
| Shared execution layer | [`global/AGENTS.md`](global/AGENTS.md) | Loaded | Loaded |
| Role layer | `agents/*.toml` | N/A | A complete stage-specific prompt, or Worker Base plus role-specific instructions |
| Domain methods | `skills/*` | Loaded when triggered | Loaded through role configuration or when triggered |

Named roles used with `fork_turns: "none"` do not inherit the parent conversation or load the Root developer mirror. Every automatic delegation explicitly specifies `none`. Required user decisions are passed through self-contained contracts or stable project files—never through a limited turn count, `all`, or an omitted parameter. A project's `AGENTS.md` can contain both project-specific rules and an index of authoritative files; see [`examples/project-AGENTS.md`](examples/project-AGENTS.md).

## Three-layer responsibility structure

```text
User
  └─ Root: goals, overall plan, cross-stage decisions, final acceptance, and user reporting
       ├─ Phase lead: the full stage, ongoing judgment, subagent coordination, integration, and stage acceptance
       │    └─ Execution-oriented subagent: one responsibility with settled boundaries and acceptance criteria
       └─ A few execution-oriented subagents: fixed, small tasks expected to finish in a single turn
```

### Phase leads

- `research-lead`: large-scale, multi-round web research;
- `code-executor`: code stages that still require continuous diagnosis, implementation, integration, and verification.

### Execution-oriented roles

- `explorer`: bounded local evidence gathering;
- `web-researcher`: bounded web evidence gathering;
- `code-reviewer`: independent, read-only code review;
- `browser-operator`: continuous browser-operation stages;
- `visual-usability-tester`: screenshot- and coordinate-driven visual black-box testing;
- `worker-luna`: primary execution work whose method and acceptance criteria are already settled;
- `worker`: high-speed execution when Spark quota is available and the speed benefit is clear;
- `default`: a compatibility leaf entry point, not a fallback for automatic routing.

See [`agents/README.md`](agents/README.md) for the authoritative Worker Base files, inline mirror relationships, stage-specific prompts, and runtime-supported fields.

## Twelve system Skills

- `batch-execution`: contain cascading risk in repetitive batch work;
- `code-development`: investigate, implement, review, and perform the necessary verification for code changes;
- `code-review`: independently determine whether code is ready to merge or deliver;
- `company-research-brief`: fill gaps in public company information, compare product lines and peers, and produce a pre-investment screening brief;
- `deep-research`: conduct multi-source research with counterevidence and synthesis;
- `eli5`: explain plans, routes, status, and trade-offs with a visual-first approach;
- `product-development`: turn real customer needs into a product definition and validate it iteratively;
- `search-source-registry`: choose authoritative search sources based on the claim and track remaining evidence gaps;
- `workflow-route-mapper`: record task branches, failed routes, and next steps;
- `workflow-state-distiller`: recover the executable current state of a long, multi-turn task;
- `write-instructions-zh`: create and maintain Base, Agent, Skill, and long-term instructions;
- `xy-axis-thinking`: trace how a problem developed, clarify the goal, and establish useful points of comparison.

## Installation

Have Codex perform a merge installation according to [`INSTALL.md`](INSTALL.md). The installation must preserve the receiving environment's existing Agents, Skills, MCP servers, plugins, and project configuration. Depending on the cost and acceptance requirements, you may choose whether to test with a brand-new Root and named subagents. If that test is not performed, real runtime loading must be explicitly marked as **unverified**.

The default model hierarchy is: Root uses `gpt-5.6-sol`; phase leads and reviewers use `gpt-5.6-terra`; routine execution and evidence gathering use `gpt-5.6-luna`; and the high-speed Worker uses `gpt-5.3-codex-spark`. If the target environment does not provide a corresponding model, the user should confirm how the capability tiers should be mapped rather than replacing models by name alone.

## Repository structure

```text
.
├── prompt-lab/                 # Root Base and public maintenance materials
├── global/AGENTS.md            # Shared execution rules read by every role
├── agents/                     # Shared Neutral Base, Worker Base, and 10 role TOMLs
├── skills/                     # 12 system Skills
├── hooks/                      # PreToolUse guard enforcing fork_turns:none
├── examples/                   # Configuration-merge and project AGENTS templates
└── INSTALL.md
```

## Version boundaries

The Root Base in this repository's Prompt Lab is the authoritative text for the current public release. The maintainer's private Prompt Lab preserves the writing process and complete evolution history. The installed `config.toml` stores only a verbatim runtime mirror; it does not carry version history. The public Worker Base files live in `agents/`. Eight execution-role TOMLs contain the inline mirrors required at runtime, while the two phase roles each maintain a complete, dedicated prompt.

This system does not depend on Python synchronization scripts, resident background processes, or hooks that splice prompts together. The hooks in `hooks/` only enforce the subagent parameter `fork_turns:none`; they do not generate, modify, or assemble prompts. Publishing is an explicit process of copying, parsing, and consistency checking. Real loading verification is performed when required by the acceptance scope and reported separately.

## License

[MIT](LICENSE)

---

**User:** Great. By the way, I have one more wish.

**GPT:** You've reached your usage limit.
