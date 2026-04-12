---
name: memory-sweep
description: Periodic review of the memory system at ~/.claude/memory/ for duplicates, redundancies, conflicts, and stale entries. Use when the user asks to audit, clean up, or review memory. Presents findings with enforcement trade-off context — never retires anything without user confirmation.
---

# Memory Sweep

Reviews all memory files and presents a structured findings report. The lead agent runs this inline — no subagent needed while memory is small (<20 files). Revisit this design when memory grows past that threshold.

## Step 1 — Inventory

Read all files in `~/.claude/memory/` and `~/.claude/CLAUDE.md`.

Note for each memory file: name, type (user/feedback/project/reference), and a one-line summary of what it enforces or describes.

## Step 2 — Check for duplicates

Flag any two memory entries that enforce substantially the same principle or describe the same fact.

## Step 3 — Check for redundancy with CLAUDE.md

Flag any memory entry whose principle is already stated verbatim (or near-verbatim) in `~/.claude/CLAUDE.md`.

**Why this matters:** Both memory and CLAUDE.md are loaded every session — true duplicates between them are the only case where a memory is genuinely redundant from an enforcement standpoint. A memory that overlaps with a *skill* is NOT redundant — skills are loaded on invocation only, not every session.

## Step 4 — Check for conflicts

Flag any two memory entries that give contradictory guidance.

## Step 5 — Check for staleness

Flag any entry that appears stale — regardless of type. Signs of staleness:
- References a project, deadline, or state that has clearly passed
- References a path, repo, or tool that no longer exists
- Describes a behavior or workflow that has since been superseded

## Step 6 — Present findings

Present a structured report:

```
Memory Sweep — <date>

Files reviewed: N
Total lines (MEMORY.md): N / 200 cap

DUPLICATES
- [file A] and [file B]: <what overlaps>

REDUNDANT WITH CLAUDE.md
- [file]: <which CLAUDE.md section covers it>
  ⚠ Retiring this would have no enforcement impact (same load scope)

REDUNDANT WITH SKILL
- [file]: <which skill mentions it>
  ⚠ Retiring this would WEAKEN enforcement — skill only loads on invocation
  → Recommend: keep in memory unless user explicitly accepts weaker enforcement

CONFLICTS
- [file A] vs [file B]: <what conflicts>

STALE
- [file]: <why stale>

NO ISSUES
- [file]: ok
```

## Step 7 — Confirm before acting

For each flagged entry, state the enforcement trade-off explicitly and ask the user whether to retire, merge, or keep it.

**Never delete or modify a memory file without user confirmation.**

## When to upgrade to an agent

If `~/.claude/memory/` grows past ~20 files, or reading all files starts consuming meaningful lead context, promote this to an agent pattern (like kb-sweep) where a specialized agent does the review and returns a compact findings report.
