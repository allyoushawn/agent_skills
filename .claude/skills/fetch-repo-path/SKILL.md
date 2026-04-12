---
name: fetch-repo-path
description: Looks up the local path of a named repository by reading the repos registry at /path/to/works/for/you/knowledge_base/context/repos.md. Use this whenever you need a repo's path and don't already know it — do not guess or hardcode paths.
---

# Fetch Repo Path

When you need the local path of a repository and don't already know it, **do not guess**.
Read the registry file and look it up.

## Registry Location

```
/path/to/works/for/you/knowledge_base/context/repos.md
```

## How to Use

1. Read `/path/to/works/for/you/knowledge_base/context/repos.md` using the Read tool.
2. Find the entry matching the repo name or purpose requested.
3. Return the path from the `**Path**` field of that entry.
4. If the repo is not listed, tell the user it's not in the registry and ask them to provide the path — then offer to add it.

## How to Add a New Repo

When the user provides a path for an unlisted repo, append a new entry to `repos.md` following this format:

```markdown
## [Repo Display Name]

- **Path**: `/absolute/path/to/repo`
- **Purpose**: [what this repo is for]
- **Git tracked**: yes / no
- **Used by**: [which skills or workflows reference it]
```

Never add a repo entry with a guessed or unverified path. Only add paths explicitly confirmed by the user.
