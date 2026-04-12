---
name: promote-to-claude-skill
description: Use this skill when the user wants to "promote", "move", "upgrade", or "migrate" a project-level skill, agent, or rule (e.g. a Cursor rule, a project-local AI rule, or any .md skill/agent file) into a global Claude scope. By default always promotes to global (~/.claude/skills/, ~/.claude/agents/, ~/.claude/CLAUDE.md) unless the user explicitly says "project-level". Moves the file so it is shared across all projects and symlinks it back so the original project is not broken.
---

# Promote a Project Skill/Agent/Rule to Global Claude Scope

## Default scope: GLOBAL

When the user says "promote" (or "move", "upgrade", "migrate") without specifying scope, **always promote to global** (`~/.claude/`):

| Artifact type | Global destination |
|---|---|
| Skill | `~/.claude/skills/<name>/SKILL.md` |
| Agent | `~/.claude/agents/<name>.md` |
| Rule / always-on instruction | `~/.claude/CLAUDE.md` (append) |

Only promote to project-level (`.claude/` inside the repo) if the user explicitly says so.

The goal: move the file to its global destination, then leave a symlink at the original location so the project continues to work without any changes to its tooling (Cursor, etc.).

**Why symlink instead of delete?** The project's tool (e.g. Cursor) still reads the file at the original path. The symlink is transparent — reads and writes go to the global copy. All projects that consume the skill via symlink stay in sync automatically.

## Steps

### 1. Identify the Source File

The source path comes from `$ARGUMENTS`. Resolve it to an absolute path.

- If the path does not exist, stop and tell the user.
- If it is already a symlink, stop — it has already been promoted. Tell the user where it points.

### 2. Determine the Skill Name

Derive the Claude skill name from the filename (strip extension, kebab-case). For example:
- `python-best-practices.md` → `python-best-practices`
- `MyRule.md` → `my-rule`

Show the user the proposed name and ask if they want a different one before proceeding.

### 3. Check for Conflicts

Check if `~/.claude/skills/<name>/SKILL.md` already exists.

### 3b. Check for Skill Dependencies

Scan the source file for references to other skills, scripts, or local paths:

- **Relative script paths** (e.g. `python scripts/foo.py`): flag each one — it must be made absolute (pointing to its new global location) or co-promoted. Do not proceed until resolved.
- **References to other project/Cursor skills by name**: check whether each referenced skill has already been promoted to `~/.claude/skills/`. If not, warn the user and offer to promote it too before continuing.
- **Absolute paths and already-global skills**: note as resolved, no action needed.

If any unresolved dependencies are found, list them clearly and ask the user how to proceed before writing any files.

- If it does, show its contents and ask the user: **overwrite**, **rename** (prompt for new name), or **cancel**.

### 4. Read and Adapt the Content

Read the source file. Inspect the frontmatter (if any):

- If it has Cursor-style frontmatter (`description`, `globs`, `alwaysApply`, etc.), convert it to Claude skill frontmatter:
  ```yaml
  ---
  name: <derived-name>
  description: <original description, or ask user to provide one if missing>
  ---
  ```
- If it already has Claude-style frontmatter (`name`, `description`), keep it and update the `name` field.
- If there is no frontmatter, prepend:
  ```yaml
  ---
  name: <derived-name>
  description: Use this skill when working on tasks related to <derived-name>. Migrated from <original-project-relative-path>.
  ---
  ```

### 5. Write the Global Skill File

Create the directory `~/.claude/skills/<name>/` and write the (adapted) content to `~/.claude/skills/<name>/SKILL.md`.

### 5b. Verify Registration

After writing the skill, confirm it appears correctly. For skills, check that the Skill tool recognizes it (the skill should be listable). For agents, verify the agent type appears in the Task/Agent tool description. If it doesn't register, the structure or frontmatter is wrong — fix before proceeding to step 6.

### 6. Delete the Original File

Delete the original file at the source path (this is a move, not a copy).

### 7. Create the Symlink

Create a symlink at the original path pointing to the global skill:

```bash
ln -s ~/.claude/skills/<name>/SKILL.md <original-path>
```

Use the expanded absolute path for `~` (i.e. `$HOME/.claude/skills/<name>/SKILL.md`) so the symlink works regardless of shell context.

### 8. Handle the Project's Git State

Check if the source file's directory is inside a git repo (`git -C <dir> rev-parse --git-dir`).

If yes:
- Run `git -C <project-root> status --short <original-path>` to see how git sees the symlink.
- Inform the user:
  > "Git now tracks a symlink at `<original-path>`. You can commit this symlink — git stores it as a pointer, not the content — so teammates will see the symlink but need `~/.claude/skills/<name>.md` to exist locally for it to resolve. Alternatively, add `<original-path>` to `.gitignore` if you don't want the symlink tracked."
- Ask: **commit the symlink**, **add to .gitignore**, or **leave as-is**.
  - If commit: `git -C <project-root> add <original-path>` and commit with message `Move <original-filename> to global Claude skill (symlink)`
  - If gitignore: append the relative path to `<project-root>/.gitignore`

### 9. Add the Skill to ~/.claude Git Backup

Check if `~/.claude` is a git repo (`git -C ~/.claude rev-parse --git-dir`).

If yes, stage and commit the new skill:
```bash
git -C ~/.claude add skills/<name>/
git -C ~/.claude commit -m "Add promoted skill: <name> (from <original-project-relative-path>)"
```

Then ask the user if they want to push to `origin main`.

### 10. Summary Report

Print:
```
✅ Promoted: <original-path>
   → ~/.claude/skills/<name>/SKILL.md  (global skill)
   → <original-path>                   (symlink, transparent to Cursor/other tools)

Next steps:
  - Any project that needs this skill can symlink it:
    ln -s ~/.claude/skills/<name>/SKILL.md <target-path>
  - Edit ~/.claude/skills/<name>/SKILL.md to update the skill everywhere at once.
```
