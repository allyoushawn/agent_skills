---
name: achieve-goal
description: |
  Generic skill for tasks that require planning, debugging, or iteration before they can be completed. Three modes — execute / optimization / orchestrate — selected by the request shape.
  Discriminator: does the task require planning? If the request is unambiguous and mechanical ("run this notebook with python3"), do NOT use this skill — direct execution is correct. If achieving the goal requires planning, recovery from failures, or iterating toward a target, this skill applies.
  Triggers: "use achieve-goal to X", "iterate to achieve metric Y", "execute this multi-milestone plan", or any goal that needs planning + recovery.
---

# Achieve Goal

Generic goal-oriented skill that plans, executes, debugs, and (when needed) iterates until the goal is met or stop conditions fire.

## Modes

| Mode | Trigger style | Behavior |
|------|--------------|----------|
| **execute** | "use achieve-goal to run X" | Plan how to achieve the goal, execute, debug failures using `debugging-protocol.md`, recover, retry until goal is met. Differs from direct execution: this loop continues *through* failures rather than reporting and stopping. |
| **optimization** | "run the experiment and iterate to achieve metric < target" | Loop: try → measure → propose new approach → repeat until metric goal met or stop condition. Absorbs the previous `iterative-experiment` use case. References repo-specific strategy docs (e.g. `recsys-experiment-strategies.md`) surfaced via `fetch-repo-skill`. |
| **orchestrate** | "execute this multi-milestone plan" (after plan confirmation) | Create one `milestone_N.md` per milestone per `milestone-execution-protocol.md`, embed autonomous prompt, run end-to-end with re-read guard at each step. |

Modes are not strictly mutually exclusive. Orchestrate may dispatch to itself in execute or optimization mode for individual milestones.

## When NOT to use

- Request is unambiguous and mechanical ("run this notebook with python3", "rename function X to Y")
- Task is exploratory ("look at this and tell me what you see")
- User explicitly waives planning ("just do it")

## References

- `kb/context/agent-design/clarification-protocol.md` — used in the planning phase of all modes
- `kb/context/agent-design/debugging-protocol.md` — used on failure in any mode
- `kb/context/agent-design/milestone-execution-protocol.md` — used in orchestrate mode
- `kb/context/agent-design/autonomous-behavior.md` — embedded at the top of milestone files and any execution document
- Repo-specific context docs (e.g. `kb/context/experiments/experiment-policies.md`, `kb/context/experiments/recsys-experiment-strategies.md`) — surfaced via `fetch-repo-skill` when working on a registered repo
- `~/.claude/skills/dispatching-parallel-agents/SKILL.md` (obra/superpowers) — methodology for concurrent subagent workflows; consult before scaling out parallel work in execute or optimization mode
- `~/.claude/skills/verification-before-completion/SKILL.md` (obra/superpowers) — evidence gating before declaring a milestone or goal met
- `~/.claude/skills/cli-review/SKILL.md` — CLI-based review gates via Gemini CLI (plans, large corpora) and Codex CLI (code); consult for routing and invocation patterns
- For ML benchmarks: `kb/context/experiments/dataset-sources.md` + scripts at `~/.claude/tools/experiment-tools/` (download_dataset.py, train_mlp.py)

## Steps

### Phase 1 — Clarify (all modes)

1. Apply `kb/context/agent-design/clarification-protocol.md` — close ambiguity in goal, success criteria, scope, constraints, failure handling, interaction expectations
2. Detect mode from clarified goal:
   - Single-stage goal with potential failures → **execute**
   - Iteration toward a metric target → **optimization**
   - Multi-milestone with checkpoints → **orchestrate**
3. State the chosen mode and the plan back to the user; wait for confirmation before proceeding to Phase 2

### Phase 2 — Plan

- For **execute**: lay out the steps and known risk points; identify dispatch targets (which subagents/skills will run each step)
- For **optimization**: define the metric, the iteration unit, the proposal strategy (reference `recsys-experiment-strategies.md` if recsys), and stop conditions
- For **orchestrate**: enumerate milestones, success criteria for each, and any cross-milestone state

**CLI Review Routing** (apply to every plan before confirming with user):
```
Is the plan large, cross-cutting, or uncertain?
  → add a Gemini CLI review gate before Phase 3 (see cli-review skill)

Will implementation touch non-trivial code across multiple files?
  → add a Codex CLI review gate after Phase 3 execution (see cli-review skill)
```
Reviews are optional gates — include them when task risk or complexity justifies the overhead. Reference `~/.claude/skills/cli-review/SKILL.md` for routing rules and invocation patterns.

### Phase 3 — Execute

- Dispatch to subagents (no single-agent execution loops)
- Embed `autonomous-behavior.md` NEVER STOP prompt at the start of execution
- On failure → apply `debugging-protocol.md` (reproduce → minimize → validate single → scale)
- For **orchestrate** specifically: create `milestone_N.md` files per `milestone-execution-protocol.md`; write to the active project folder

### Phase 4 — Stop conditions

| Condition | Action |
|-----------|--------|
| Goal met | Report; close milestone files if any; summarize |
| 3 consecutive failures with no path forward | Escalate to user |
| Hard iteration cap reached (configurable, default 10) | Surface to user |
| User interrupts | Pause, summarize state |

## Output

- Goal achieved → summary of what was done, key decisions, any open follow-ups
- Or: structured escalation to user with current state, blockers, and proposed next steps
