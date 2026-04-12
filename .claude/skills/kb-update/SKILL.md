---
name: kb-update
description: Use this skill when deciding whether and how to update the knowledge base at /path/to/works/for/you/knowledge_base/ after completing a task.
---

# Knowledge Base Update

## When to update

Update the KB after **non-trivial** tasks:
- New agent, skill, or rule created or promoted
- Design decision or architectural choice made
- New workflow pattern established
- Something learned that would change future behavior

**Do not** update after trivial tasks (lookups, one-liners, repeating a documented workflow).

When genuinely unsure, ask: "Should I update the knowledge base with anything from this session?"

## Where to put what

### `projects/` — progress notes and design context
Use for:
- Recording that something was built, moved, or changed
- Capturing *why* a design decision was made (context that isn't in the code/skill itself)
- Tracking non-trivial session work for future reference

Each project gets its own folder. Add or append a note file per topic or session as needed.

### `preference/claude-workflow.md` — session-critical defaults only
This file is **loaded every session** — keep it lean.

Only update it when:
- A genuinely new workflow default is established that isn't captured in any skill or memory
- A new session startup step is needed

**Do NOT add to `claude-workflow.md`** if:
- The rule is already in a skill file (redundant — the skill is the authoritative source)
- The rule is already in memory (redundant — memory persists it)
- It is project-specific progress or context (belongs in `projects/` instead)

### Skills and memory — behavior rules
Skills (`~/.claude/skills/`) and memory (`~/.claude/memory/`) are the authoritative place for behavior rules. Never duplicate them into `claude-workflow.md`.

## File management in `projects/`

Do not append everything to a single README. Instead, judge:

- **Create a new file** when the update is a distinct topic not yet represented, or when an existing file would become unwieldy. Name it by topic (e.g. `agent-promotion.md`, `kb-update-design.md`), not by date.
- **Append to an existing file** when the update directly extends a topic already covered there.
- **README.md** in a project folder should stay as an overview/goal document — not a progress dump.

Scan the existing files in the project folder before writing to pick the right target.

## Trigger points

The kb-update process should fire automatically at these moments — do not wait for the user to ask:

1. **After creating or modifying a skill, agent, or rule** — capture the design rationale in the relevant projects/ note
2. **After a design decision or architectural choice** — even if the decision is encoded in a skill, the *why* behind it belongs in projects/
3. **Before save-to-github** — if the user says "save state", run kb-update first. The save skill should checkpoint what was learned, not just what was coded
4. **After a multi-step debugging or investigation session** — if the root cause or fix was non-obvious, it's worth capturing
5. **When the user provides feedback that changes a workflow pattern** — the feedback itself goes to memory, but the broader context (what changed and why) goes to projects/

If none of these triggers apply, skip silently — don't ask.

## Process

1. Identify what changed this session that is worth retaining
2. For each piece of content to write, spawn the **kb-librarian** agent (via Agent tool) with a description of the content. The kb-librarian will scan the KB, read candidate files to verify their actual scope, and return a concrete routing recommendation (append to existing file or create new file). Skip pieces that are already captured in a skill or memory, or belong in `claude-workflow.md` only if not captured elsewhere.
3. Present the kb-librarian's routing recommendation(s) to the user: "kb-librarian recommends writing X to file Y because Z." Wait for approval before writing anything.
4. Write the update to the approved location — include the *why* (design context), not just the *what*

5. After writing, invoke the **kb-organizer** agent (via Agent tool) with `scope = <the folder you just wrote to>`. Wait for its change report. This refreshes the folder's KB_INDEX and propagates topic changes to ancestor READMEs. If kb-organizer reports a "Suggested Reorganization", include it in your summary to the user but do not act on it without explicit instruction.
