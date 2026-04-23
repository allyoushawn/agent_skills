---
name: save-to-github
description: Use this skill when the user says "save the state to github", "save state", "push state to github", or "checkpoint to github". Performs a security risk scan, ignores risky files, stages safe ones, commits, and offers to push. Operates on three repos in every run: the knowledge base repo at /path/to/works/for/you/knowledge_base/, the Claude config repo at ~/.claude/, and the paper reading repo at /path/to/works/for/you/Projects/paper_reading_repo/.
---

# Save State to GitHub

This skill saves state for **three repos** in every run:
1. **Knowledge base repo** — always `/path/to/works/for/you/knowledge_base/` (registered in `knowledge_base/context/repos.md`)
2. **Claude config repo** — always `~/.claude/` (not in the repo registry; it's the AI config itself)
3. **Paper reading repo** — always `/path/to/works/for/you/Projects/paper_reading_repo/` (registered in `knowledge_base/context/repos.md` as `paper_reading_repo`)

Run the full pipeline below for each repo. If a repo has no changes, note it as clean and move on.

> Note: this skill is the *source of truth for save scope* — it explicitly enumerates which repos get checkpointed. That makes hardcoding the paths here appropriate (an exception to the general "never hardcode registered-repo paths" rule). If a path here drifts from `repos.md`, fix `repos.md` and this file together.

---

## Dynamic State (injected at skill load)
- Knowledge base branch: !`git -C /path/to/works/for/you/knowledge_base branch --show-current 2>/dev/null || echo "not initialized"`
- Knowledge base status: !`git -C /path/to/works/for/you/knowledge_base status --short 2>/dev/null || echo "not initialized"`
- Claude config branch: !`git -C ~/.claude branch --show-current 2>/dev/null || echo "not initialized"`
- Claude config status: !`git -C ~/.claude status --short 2>/dev/null || echo "not initialized"`
- Paper reading branch: !`git -C /path/to/works/for/you/Projects/paper_reading_repo branch --show-current 2>/dev/null || echo "not initialized"`
- Paper reading status: !`git -C /path/to/works/for/you/Projects/paper_reading_repo status --short 2>/dev/null || echo "not initialized"`

---

## Pipeline (run for each repo)

### Step 1 — Verify Git Repo
If the repo is not a git repository, skip it and notify the user.

### Step 2 — Collect Candidates
Run `git status --short` (or `git -C <path> status --short` for non-cwd repos) to get all untracked (`?`) and modified (`M`) files.

If there are no candidates, note "Nothing new — working tree is clean." and skip to the next repo.

### Step 3 — Privacy & Secrets Risk Scan (tiered)

The scan tier depends on the repo. The global secrets policy (`~/.claude/CLAUDE.md` § "Secrets Policy — One Sanctioned Home") declares `~/.claude/<service>_api_key` as the **only** sanctioned home for credentials and the other two repos as **key-free zones by design**. Step 3 enforces that policy, not arbitrary content review.

#### Tier A — `~/.claude/` (deep per-file review)

Read each candidate diff/file and flag it as **RISKY** if it matches any of the patterns below. The changeset here is small, so per-file review is cheap.

| Risk Pattern | Examples (`secret-scan: example`) |
|---|---|
| Hardcoded API keys | `sk-...`, `AKIA...`, `ghp_...`, `xox...` |
| Private key material | `-----BEGIN ... PRIVATE KEY-----`, PEM blocks |
| Auth tokens / Bearer literals | `Authorization: Bearer <literal>`, `token = "..."` |
| `.env`-style assignments | `DB_PASSWORD=mypass`, `SECRET=abc123` |
| Credentials filenames | `credentials.json`, `*.pem`, `id_rsa` |
| Connection strings with passwords | `postgresql://user:password@...` |
| PII | SSNs, passport numbers, phone numbers in data files |

**Filename rule (always RISKY regardless of content):** `gemini_api_key`, `openai_api_key`, `*_api_key`, `*_key`. These are gitignored in `~/.claude/.gitignore`.

#### Tier B — `knowledge_base/` and `paper_reading_repo/` (mechanical scan)

These repos are **declared key-free zones**. Run the canonical scanner — it is the **single source of truth** for patterns. Do not duplicate patterns into prose or per-repo scripts.

```bash
~/.claude/tools/secret-scan.sh /path/to/works/for/you/knowledge_base
~/.claude/tools/secret-scan.sh /path/to/works/for/you/Projects/paper_reading_repo
```

The scanner enumerates the union of (modified-vs-HEAD) and (untracked, gitignore-respecting) files, runs one pass per file, honors the per-repo `.secret-scan-allowlist` and inline `secret-scan: example` markers, and exits **0 = clean** / **1 = matches found**.

**Retroactive audit (covering a batch of commits, not just uncommitted changes):**

```bash
# Audit everything touched since 5 commits ago (modified + still-untracked):
~/.claude/tools/secret-scan.sh /path/to/works/for/you/knowledge_base HEAD~5
```

Use this when the previous checkpoint pre-dates the tiered scan, or when a large drop was committed in a single shot and you want to verify retroactively.

- **Exit 0** → proceed to Step 5 (no per-file content reading required by Claude).
- **Exit 1** → review each match. For true positives, follow the secret-handling policy in `~/.claude/CLAUDE.md`: stop, never echo the value, prompt the user to relocate to `~/.claude/<service>_api_key`, do **not** stage the file. For false positives in documentation, add `# secret-scan: example` to that line (or add the path to `.secret-scan-allowlist`) and re-run the scanner.

**Why tiered:** the deep per-file review on a 5000-file literature-survey drop would cost thousands of tokens for near-zero added safety — those repos already have a "no credentials, ever" invariant. The mechanical scan verifies the invariant held this session at near-zero token cost (only matching lines enter Claude's context).

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

After processing all three repos, ask once:

> "Would you like to push these repos to their remotes?"
> - Knowledge base → origin `<branch>`
> - Claude config → origin `<branch>`
> - Paper reading → origin `<branch>`

If yes, push all that had commits and report results. If no, acknowledge and stop.

Only list repos in the prompt that actually had a commit this run. If none did, skip the push prompt entirely.
