---
name: save-to-github
description: Use this skill when the user says "save the state to github", "save state", "push state to github", or "checkpoint to github". Performs a security risk scan, ignores risky files, stages safe ones, commits, and offers to push. Operates on the knowledge base repo at /path/to/works/for/you/knowledge_base/ AND the Claude config repo at ~/.claude/.
---

# Save State to GitHub

This skill saves state for **two repos** in every run:
1. **Knowledge base repo** — always `/path/to/works/for/you/knowledge_base/`
2. **Claude config repo** — always `~/.claude/`

Run the full pipeline below for each repo. If a repo has no changes, note it as clean and move on.

---

## Dynamic State (injected at skill load)
- Knowledge base branch: !`git -C /path/to/works/for/you/knowledge_base branch --show-current 2>/dev/null || echo "not initialized"`
- Knowledge base status: !`git -C /path/to/works/for/you/knowledge_base status --short 2>/dev/null || echo "not initialized"`
- Claude config branch: !`git -C ~/.claude branch --show-current 2>/dev/null || echo "not initialized"`
- Claude config status: !`git -C ~/.claude status --short 2>/dev/null || echo "not initialized"`

---

## Pipeline (run for each repo)

### Step 1 — Verify Git Repo
If the repo is not a git repository, skip it and notify the user.

### Step 2 — Collect Candidates
Run `git status --short` (or `git -C <path> status --short` for non-cwd repos) to get all untracked (`?`) and modified (`M`) files.

If there are no candidates, note "Nothing new — working tree is clean." and skip to the next repo.

### Step 3 — Privacy & Secrets Risk Scan

For each candidate file, read its content and flag it as **RISKY** if it contains any of the following:

| Risk Pattern | Examples |
|---|---|
| Hardcoded secrets / API keys | `sk-...`, `AKIA...`, `ghp_...`, `xox...` |
| Private key material | `-----BEGIN ... PRIVATE KEY-----`, PEM blocks |
| Auth tokens / Bearer literals | `Authorization: Bearer <literal>`, `token = "..."` |
| `.env` files with assigned values | `DB_PASSWORD=mypass`, `SECRET=abc123` |
| Credentials files | `credentials.json`, `*.pem`, `*.key`, `id_rsa` |
| Connection strings with passwords | `postgresql://user:password@...` |
| Personal identifiable info | SSNs, passport numbers, phone numbers in data files |

Files that match **none** of the above are **SAFE**.

**Note for `~/.claude/`:** API key files (`gemini_api_key`, `openai_api_key`, `*_api_key`, `*_key`) are always RISKY — flag and gitignore them regardless of content.

### Step 4 — Handle Risky Files
For each **RISKY** file:
- Explain what was found (e.g., "Found hardcoded API key in `config.js` line 12")
- Append the file path to `.gitignore` in the relevant repo root (create if it doesn't exist)
- Do NOT stage it

### Step 5 — Stage Safe Files
For each **SAFE** file:
- Run `git add <file>` (or `git -C <path> add <file>` for non-cwd repos)

If `.gitignore` was created/modified in step 4, stage it too.

### Step 6 — Check Staged Set
If nothing was staged (all candidates were risky), report the risky files and skip committing for this repo.

### Step 7 — Commit
Generate a short, descriptive commit message summarizing what was saved.

```
git commit -m "<message>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

For non-cwd repos, use `git -C <path> commit ...`.

### Step 8 — Per-Repo Summary

Print a clear summary for each repo:

```
✅ [repo name] Committed: <commit hash> — <message>

Staged & committed:
  - file1
  - file2

Skipped (added to .gitignore):
  - risky-file1  ← reason
```

---

## Final Prompt — Push All Repos

After processing both repos, ask once:

> "Would you like to push both repos to their remotes?"
> - Knowledge base → origin `<branch>`
> - Claude config → origin `<branch>`

If yes, push both and report results. If no, acknowledge and stop.

If only one repo had changes, only offer to push that one.
