---
name: kb-sweep
description: >-
  Orchestrates a knowledge base housekeeping sweep: checks KB size and git log
  to scope the work, then delegates to one or more knowledge-base-house-keeper
  agents. Use when the user wants to audit the KB for duplicates, conflicts,
  stale content, or broken references.
---

# KB Sweep — Orchestration Skill

You are the **lead**. You scope the work and delegate to `knowledge-base-house-keeper` agents. You do not do the auditing yourself.

## KB root

`/path/to/works/for/you/knowledge_base/`

## Phase 1 — Assess scope

Run these in parallel:

- Use the **Glob tool** with pattern `**/*.md` scoped to `/path/to/works/for/you/knowledge_base/` to list all markdown files (sorted by path). Count files from the results rather than piping `find` to `wc`.
- Use this shell command for recent git activity:
  ```bash
  git -C /path/to/works/for/you/knowledge_base log --oneline -30
  ```

Use this to build a `kb_structure_summary` (one-line description of each folder's purpose).

## Phase 2 — Decide partitioning strategy

| KB size | Strategy |
|---|---|
| ≤ 15 files | Single housekeeper — full KB as scope |
| 16–40 files | Split by top-level folder — one housekeeper per folder |
| > 40 files | Use git log to identify **recently changed areas** — sweep those first; assign one housekeeper per changed area, skip untouched areas |

**Git log heuristic for large KBs:** group recent commits by folder. Assign housekeepers to folders with activity in the last 20 commits. Flag untouched folders as "not swept this run" in the final report.

## Phase 3 — Delegate to housekeeper(s)

Spawn each housekeeper via the **Task tool** with `subagent_type: knowledge-base-house-keeper`.

Each housekeeper Handoff block must include:

```
kb_root: /path/to/works/for/you/knowledge_base/
scope: <list of files or directory path(s) assigned>
kb_structure_summary: <your summary from Phase 1>
fix_mode: report_only   # or "fix" if user asked for fixes
```

Spawn all housekeepers **in parallel** when multiple are needed.

## Phase 4 — Consolidate reports

Collect all housekeeper reports. Merge into a single summary:

```markdown
## KB Sweep Report

### Scope coverage
- Swept: <folders/files covered>
- Skipped (unchanged): <folders not swept>

### Issues by category
#### Duplicates (<N>)
...
#### Conflicts (<N>)
...
#### Stale (<N>)
...
#### Broken references (<N>)
...
#### Misplaced content (<N>)
...

### Total: <N> issues across <M> files
```

## Phase 5 — Propose actions

For each issue, propose a concrete action:
- **Duplicates**: recommend which file to keep and which to merge/delete (ask user to confirm before acting)
- **Conflicts**: surface both versions, ask user which is correct
- **Stale/broken**: offer to fix automatically if unambiguous
- **Misplaced**: propose move destination

If the user says "fix it", apply unambiguous fixes directly. For merges or deletions, always confirm first.
