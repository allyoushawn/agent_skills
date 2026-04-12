# Global Claude Code Instructions

## Confirm Before Deleting Files

Before deleting or removing any file, always ask the user for explicit confirmation first. Never delete a file without approval.

1. List the file(s) that will be deleted, including their full paths.
2. Ask the user for a yes/no confirmation.
3. Only proceed with deletion if the user confirms.

Example: if the user says "clean up the temp files", do NOT immediately delete them. Instead show the list of files that would be deleted, ask "Are you sure you want to delete these files?", and wait for confirmation.

## Agent Behavior Rules

- **Follow all skill steps:** When following a skill, execute every numbered step in order. Do not skip steps even if you believe they are unnecessary. If you think a step can be skipped, state why and ask for confirmation before skipping.
- **Fix root causes, not workarounds:** When something doesn't work as expected (e.g. Skill tool doesn't recognize a skill, Agent tool doesn't list an agent), investigate the root cause. Do not apply workarounds (e.g. creating commands as wrappers, adding manual indexes). Fix the actual artifact or configuration.
- **No redundant duplication:** Never duplicate information into CLAUDE.md or claude-workflow.md that is already discoverable via the Skill tool, Agent tool, or by listing ~/.claude/skills/ or ~/.claude/agents/. If auto-discovery isn't working, fix the discovery mechanism.
- **Proactive KB update:** After completing any non-trivial task (creating/modifying skills, agents, rules, or making design decisions), proactively run the kb-update skill BEFORE the user asks. Do not wait to be prompted. If the user says "save state" or "save status," the KB update must happen first — treat it as a mandatory pre-step to save-to-github. When genuinely unsure whether the task warrants an update, ask — but err on the side of updating rather than silently skipping.
- **Fast-path first:** Before designing any delegation rule, routing condition, or trigger policy, ask: "Is there a 1-call pre-check that resolves the obvious cases mechanically?" Put that check first; apply judgment-based rules only for the ambiguous remainder.

## File Reading — Protect Context Window

Before reading any file, check its size with `ls -la <path>` (one bash call, negligible cost), then apply:

| File size | Action |
|-----------|--------|
| < 5KB | Read directly — no need to delegate |
| 5KB – 50KB | Apply purpose rule: delegate if goal is understanding/extracting; read directly if about to edit a known region |
| > 50KB | Always delegate to `reading-agent`, regardless of purpose |

**When to delegate to `reading-agent`:** understanding how something works, locating a symbol or pattern, extracting config values, summarizing a module, exploring unfamiliar code.

**When to read directly:** about to edit and need exact local syntax/context for a known region.

**If unsure:** delegate. Unnecessary delegation costs a little latency; unnecessary direct reads cost context window.

**How to delegate:** spawn the `reading-agent` with `file_path`, `question`, `task_type` (summarize / locate / explain / extract / verify), and `editing_followup_expected` (true/false).

## Delegate Non-Trivial Editing to Subagent

To preserve the lead agent's context window, delegate editing work to a **general-purpose subagent** whenever the task is non-trivial.

**What counts as non-trivial editing:**
- Changes spanning more than one file
- Any single-file change that requires reading multiple files for context (imports, interfaces, callers)
- Refactors, renames, or restructuring of existing logic
- Adding a new feature or class (not just a small helper)
- Any edit where getting it wrong would require significant re-work

**What can be done inline (trivial):**
- Single-line or single-block fixes (typo, wrong constant, obvious bug)
- Adding/removing one import
- Small config or comment changes

**How to delegate:**
1. Do all research and planning in the lead context first (read files, understand structure, form the plan).
2. Write a self-contained brief for the subagent — include exact file paths, line numbers, what to change, why, and any constraints. Do NOT write "based on what we discussed"; assume the subagent has zero prior context. **End every brief with: "Return only: one sentence confirming the edit was made, or a one-line error description. No other output."**
3. Spawn a `general-purpose` subagent via the Agent tool with that brief.
4. Wait for the result and verify it before proceeding.

The subagent should do the editing (Edit/Write tools); the lead agent should do the reasoning.

## Subagent Output Protocol — Output Tokens Are Expensive

Output tokens cost 3–8x input tokens. Two rules for all subagent interactions:

**When writing briefs:** End every subagent brief with an explicit output instruction:
> "Return only: [YAML schema name / 1–2 sentence result]. No preamble. No recap of the task."

**When receiving results:** A subagent result is a delta — what changed or what the answer is. Do not treat it as a full state snapshot. Do not re-summarize it back into a longer note.

## Subagent Model Routing — Match Capability to Cost

Agent frontmatter sets model defaults. Be aware of the tiers:

- **Haiku** (`$0.25/M`): reading-agent, experiment-analyzer, experiment-scribe, experiment-plan-critic — mechanical, structured-output, or read-only tasks with verifiable outputs
- **Sonnet** (`$3/M`): kb-librarian, experiment-runtime, experiment-planner, experiment-code-change, knowledge-base-house-keeper, general-purpose subagents — semantic judgment, code reasoning, or failure classification
- **Opus**: Reserve for frontier-grade tasks only (security audits, novel architecture design)

Do not override to a higher tier without justification. Save cost via output constraints, not model downgrade, for borderline cases.

## Circuit Breakers — Prevent Stuck Loops

Any agentic loop must have explicit termination guards:

1. **Iteration cap:** Respect the hard `max_rounds` parameter in iterative skills. Do not exceed it.
2. **Replan escape hatch:** If `needs_replan: true` returns from critic on two consecutive rounds, surface to user rather than replanning.
3. **Plateau signal:** If the best metric does not improve over 3 consecutive rounds, pause and surface to user.
4. **No silent recovery:** If a subagent errors on retry 3+, escalate to lead and surface to user.

## Context Window Hygiene

**Lead agent context pruning:** After a subagent result is processed and its key finding noted, treat the raw result block as consumed — do not re-summarize it or re-reference it. For long multi-turn sessions, periodically summarize active state and flush completed subtask histories.

**Skill lazy loading:** Only load skill files (SKILL.md) immediately relevant to the current step. With 17 skills in the system, loading all upfront inflates input context significantly.

**Subagent briefs:** Pass only the relevant subset of prior results in a brief — not a recap of the entire session.

## Effort Parameters (Sonnet agents only)

When spawning Sonnet-tier subagents, set effort to match task complexity:

| Agent / Task type | effort |
|---|---|
| experiment-runtime, kb-librarian | `medium` |
| experiment-planner, experiment-code-change, knowledge-base-house-keeper | `medium` |
| General-purpose editing/research subagent | `medium` |
| Frontier-grade tasks (security, novel architecture) | `high` |

Note: Haiku agents (reading-agent, experiment-analyzer, experiment-scribe, experiment-plan-critic) do not support the `effort` parameter — it is a no-op for them.

`effort` is a hint, not a contract. Claude may still reason deeply on hard problems at `low`.

## LLM Consultants (Gemini / OpenAI second opinions)

When the user asks for a **second opinion**, wants to consult **Gemini**, **ChatGPT/OpenAI**, or requests an **external review** or **model comparison**, follow the skill at `~/.claude/skills/consult-llm/SKILL.md`.

Key points:
- Use `mcp__chat-gemini__chat-with-gemini` for Gemini, `mcp__chat-openai__chat-with-openai` for OpenAI/GPT.
- When consulting both, send the **same** prompt to each in parallel, then summarize agreements, disagreements, and a recommendation — attributed per model.
- If an MCP call fails (auth, quota, model error), report the error and suggest checking `~/.claude/run-gemini-chat-mcp.sh` or `~/.claude/run-openai-chat-mcp.sh`.

## KB Retrieval Before External Research

Before doing a web search, calling an LLM consultant, or reasoning from scratch about a topic the user has worked on before, invoke the **kb-retriever** agent (via Agent tool) with a natural language query describing what you need to know.

- If result is `HIT` or `PARTIAL`: use the returned excerpts as primary context. Cite the source files.
- If result is `MISS`: proceed to external search or reasoning.

**This applies to:** project context questions, past design decisions, known workflows, architecture questions, and user preferences not already covered by memory.

**Do not invoke kb-retriever for:** purely technical questions with no project-specific context (e.g. "how does Python's GIL work"), one-off lookups, or tasks where the KB is clearly irrelevant.

**Model routing:** kb-retriever runs at `sonnet` tier — do not override to opus.
