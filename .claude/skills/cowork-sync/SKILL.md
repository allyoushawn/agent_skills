---
name: cowork-sync
description: Review cowork project outputs and sync the workspace-level README.md and log.md in cowork_projects/. Use when cowork agents have done work and the workspace index needs to be updated, or when the user says "sync cowork", "review cowork status", or "update cowork workspace".
---

# Cowork Sync

Updates the workspace-level index (`cowork_projects/README.md` and `cowork_projects/log.md`) by reading each cowork project's current state. These workspace-level files are Claude Code's responsibility — cowork agents must not touch them.

## When to invoke

- After cowork agents have completed work in one or more project folders
- When the user asks to review cowork status or sync the workspace
- Before running `kb-update` to promote cowork outputs to canonical KB

## Scope boundary reminder

| File | Owner |
|------|-------|
| `cowork_projects/README.md` | **Claude Code** — this skill updates it |
| `cowork_projects/log.md` | **Claude Code** — this skill appends to it |
| `cowork_projects/CONVENTIONS.md` | **Claude Code** — never touch |
| `<project-name>/README.md` | Cowork agent — read-only from this skill's perspective |
| `<project-name>/log.md` | Cowork agent — read-only from this skill's perspective |

## Steps

### 1. Discover projects

List all subdirectories inside `knowledge_base/projects/cowork_projects/`. Ignore files at the workspace root (CONVENTIONS.md, README.md, log.md). Each subdirectory is a cowork project.

### 2. Read each project

For each project folder found, read:
- `<project-name>/README.md` — current state, findings, proposed KB destination, open questions
- `<project-name>/log.md` — append-only event timeline

Classify each project into one of three states based on its README:
- **active** — work is ongoing (including initialized-but-not-yet-started folders with no log entries)
- **pending_promotion** — work is complete; README contains a suggested KB destination
- **stale** — has log entries, but the most recent is older than 14 days and README shows no explicit active status

### 3. Determine what changed

Compare each project's most recent `log.md` date against the last sync entry in `cowork_projects/log.md`. Only projects with new log entries since the last sync need to be reflected in the workspace log.

### 4. Rewrite cowork_projects/README.md

Rewrite the workspace README to reflect the current state of all projects. Use this structure:

```markdown
---
title: Cowork Projects
summary: Sandbox workspace for Claude.ai web ("cowork") task outputs. Claude Code reviews and promotes content from here into the canonical KB.
topics: [cowork, workflow, sandbox]
status: active
updated: <today's date>
---

<!-- BEGIN KB_INDEX -->
# cowork_projects/

Sandbox workspace for Claude.ai web ("cowork") task outputs. Cowork writes here; Claude Code reviews and promotes to canonical KB. See `CONVENTIONS.md` for cowork operating rules.

## Key Topics
cowork, workflow, sandbox, conventions, kb-maintenance

## Files
| File | Summary | Topics | Status | Updated |
|------|---------|--------|--------|---------|
| CONVENTIONS.md | Authoritative operating conventions for cowork agents: boundary rules, per-task folder structure, README vs log.md conventions, and handoff protocol | cowork, workflow, sandbox, conventions, kb-maintenance | active | <date> |
| log.md | Append-only timeline | — | active | <date> |

## Subfolders
| Folder | Description | Key Topics |
|--------|-------------|------------|
<one row per project, summary drawn from project README>
<!-- END KB_INDEX -->

## Active projects

<list each active project: name, one-line status, last log entry date>

## Pending promotion

<list each pending_promotion project with: name, suggested KB destination from project README, any open questions>

## Stale projects

<list stale projects with their last activity date — or omit section entirely if none>
```

### 5. Append to cowork_projects/log.md

For each project that has new activity since the last sync, append one line:

```
## [YYYY-MM-DD] update | <project-name>: <one-liner drawn from most recent project log entry>
```

If multiple projects updated, write one line per project. Always add a final sync line:

```
## [YYYY-MM-DD] sync | cowork-sync ran; <N> project(s) reviewed, <M> updated
```

### 6. Report to user

Summarize:
- How many projects exist and their states (active / pending_promotion / stale)
- Which projects have pending promotion and their suggested KB destinations
- Whether any immediate `kb-update` promotion is recommended
