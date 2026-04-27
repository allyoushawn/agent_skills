---
name: fetch-repo-skill
description: |
  Looks up which Claude skills and kb/context docs apply to a named repository and returns the paths. User-invoked at the start of a repo session. Companion to fetch-repo-path. Use when the user says "/fetch-repo-skill <repo>", "load skills for <repo>", or "what skills apply to <repo>?".
---

# Fetch Repo Skill

Companion to `fetch-repo-path`. Given a repo name, reads the registry at `kb/context/registry/repo-skills-registry.md` and returns the paths to the skills and context docs registered for that repo.

## When to use

- User invokes `/fetch-repo-skill <repo_name>` at the start of a repo session
- User asks "what skills apply when working on <repo>?"
- User asks "load context for <repo>"

## When NOT to use

- The user has not specified a repo
- The repo is not registered in `repo-skills-registry.md` (in that case, suggest registering it)

## References

- `kb/context/registry/repo-skills-registry.md` — the registry mapping repo → {skills, context_docs}
- `kb/context/registry/repos.md` — the canonical path registry (use `fetch-repo-path` to resolve actual filesystem paths)

## Steps

1. Read `kb/context/registry/repo-skills-registry.md`
2. Locate the entry for the requested repo by name
3. If not found: report the available registered repos and suggest registering the new one (point to the "How to register a new repo" section of the registry)
4. If found: return a structured result with two lists:
   - `skills`: the names of skills under `~/.claude/skills/` that should be active
   - `context_docs`: the kb/context files that may be relevant; the lead agent reads them on demand (lazy)

## Output format

```
Repo: <name>
Path: <from repos.md>

Skills:
  - <skill1>  (path: ~/.claude/skills/<skill1>/)
  - <skill2>
  ...

Context docs (read on demand, do not pre-load all):
  - kb/context/<doc1>.md
  - kb/context/<doc2>.md
  ...
```

The lead agent then chooses which context docs to `Read` based on the current task — do not pre-load all of them, that would bloat context for nothing.

## Design note

This skill returns paths only, not file contents. Lazy loading on demand is intentional. If a future task needs broader context, the lead agent reads the specific files at that point.
