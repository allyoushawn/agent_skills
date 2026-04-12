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
2. Write a self-contained brief for the subagent — include exact file paths, line numbers, what to change, why, and any constraints. Do NOT write "based on what we discussed"; assume the subagent has zero prior context.
3. Spawn a `general-purpose` subagent via the Agent tool with that brief.
4. Wait for the result and verify it before proceeding.

The subagent should do the editing (Edit/Write tools); the lead agent should do the reasoning.

## LLM Consultants (Gemini / OpenAI second opinions)

When the user asks for a **second opinion**, wants to consult **Gemini**, **ChatGPT/OpenAI**, or requests an **external review** or **model comparison**, follow the skill at `~/.claude/skills/consult-llm/SKILL.md`.

Key points:
- Use `mcp__chat-gemini__chat-with-gemini` for Gemini, `mcp__chat-openai__chat-with-openai` for OpenAI/GPT.
- When consulting both, send the **same** prompt to each in parallel, then summarize agreements, disagreements, and a recommendation — attributed per model.
- If an MCP call fails (auth, quota, model error), report the error and suggest checking `~/.claude/run-gemini-chat-mcp.sh` or `~/.claude/run-openai-chat-mcp.sh`.
