---
name: kb-update
description: Use this skill when deciding whether and how to update the knowledge base at /path/to/works/for/you/knowledge_base/ after completing a task.
---

# Knowledge Base Update

## When to update

When this skill should fire is governed by CLAUDE.md § "Proactive KB update" (non-trivial tasks: new skill/agent/rule, design decision, new workflow pattern, or learning that changes future behavior). This skill defines **how** to route and write the update once it has been triggered.

## Where to put what

### `projects/` — progress notes and design context
Use for:
- Recording that something was built, moved, or changed
- Capturing *why* a design decision was made (context that isn't in the code/skill itself)
- Tracking non-trivial session work for future reference

Each project gets its own folder. Add or append a note file per topic or session as needed.

### `user_info/claude-workflow.md` — session-critical defaults only
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

## File management in KB folders

Every folder in the KB has two structural files:

- **`README.md` (Compiled Truth)** — current state, goals, open threads. Rewritable; never use it as a chronological progress log.
- **`log.md` (append-only timeline)** — one line per notable event: `## [YYYY-MM-DD] <type> | <one-liner>`. Types: `init`, `ingest`, `decision`, `refactor`, `experiment`, `feedback`, `lint`. Never rewrite or delete past entries; if a prior entry is wrong, append a new line with type `feedback` describing the correction.

Do not append everything to a single README. Instead, judge:

- **Create a new file** when the update is a distinct topic not yet represented, or when an existing file would become unwieldy. Name it by topic (e.g. `agent-promotion.md`, `kb-update-design.md`), not by date.
- **Append to an existing file** when the update directly extends a topic already covered there.
- **Never write chronological entries into `README.md`.** Put them in `log.md`.

Scan the existing files in the project folder before writing to pick the right target.

## Trigger points

Auto-firing triggers are listed in CLAUDE.md § "Proactive KB update". Skill-specific addenda:

- After a multi-step debugging or investigation session, if the root cause or fix was non-obvious, capture it.
- When user feedback changes a workflow pattern, the feedback itself goes to memory; the broader *why* goes to `projects/`.

If none apply, skip silently — don't ask.

## Process

1. Identify what changed this session that is worth retaining
2. For each piece of content to write, spawn the **kb-librarian** agent (via Agent tool) with a description of the content. The kb-librarian will scan the KB, read candidate files to verify their actual scope, and return a concrete routing recommendation (append to existing file or create new file). Skip pieces that are already captured in a skill or memory, or belong in `claude-workflow.md` only if not captured elsewhere.
3. Present the kb-librarian's routing recommendation(s) to the user: "kb-librarian recommends writing X to file Y because Z." Wait for approval before writing anything.
4. **Write and log** (for each approved write into any KB folder):
   1. Write the topic note to the approved file — include the *why* (design context), not just the *what*.
   2. **Ensure `log.md` exists** in that KB folder. If missing, create it with a single seed line: `## [YYYY-MM-DD] init | <short label from the folder name or README title>`. A missing `log.md` means the folder has not yet been migrated to this convention — create it before appending.
   3. **Append** one line to `log.md`: `## [YYYY-MM-DD] <type> | <one-liner>` where `<type>` is one of `add`, `update`, `remove`, `ingest`, `decision`, `refactor`, `experiment`, `feedback`, `lint` (use the best fit for this session). Use `add`/`update`/`remove` for `context/` and `user_info/` folder changes (file added, significantly revised, or deleted); use the richer project types for `projects/` work. **Never edit or remove prior lines** in `log.md`.
   4. If a past `log.md` entry must be corrected, append a **new** line with type `feedback` — do not rewrite history.

5. After writing, invoke the **kb-organizer** agent (via Agent tool) with `scope = <the folder you just wrote to>`. Wait for its change report. This refreshes the folder's KB_INDEX and propagates topic changes to ancestor READMEs. If kb-organizer reports a "Suggested Reorganization", include it in your summary to the user but do not act on it without explicit instruction.

## Ingest workflow (external sources)

When the material to retain is an **external source** (paper PDF, blog URL, book chapter, repo, transcript) rather than session-only reasoning:

1. **Save the source** under `projects/<name>/sources/` — link in a small `.md` stub, or copy the file with a clear filename. Keep raw sources immutable (do not edit them in place after ingest).
2. **Write a summary note** in the same project (new or existing topic file): at least one paragraph of takeaways; link or path to the raw source.
3. **Cross-link**: update related topic files in that project; if new information **contradicts** an older note, flag the contradiction in the summary or in a short `feedback` line in `log.md` — do not silently overwrite without noting the conflict.
4. **Log**: ensure `log.md` exists (seed `init` if missing), then append `## [YYYY-MM-DD] ingest | <short title or filename>`.

Steps 1–3 may be routed via **kb-librarian** as usual; step 4 is unconditional for any write under `projects/<name>/`, same as Process step 4.
