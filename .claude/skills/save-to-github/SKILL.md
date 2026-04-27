---
name: save-to-github
description: Use this skill when the user says "save the state to github", "save state", "push state to github", or "checkpoint to github". Performs a security risk scan, ignores risky files, stages safe ones, commits, and offers to push. Operates on four repos in every run: the knowledge base repo at /path/to/works/for/you/knowledge_base/, the Claude config repo at ~/.claude/, the paper reading repo at /path/to/works/for/you/Projects/paper_reading_repo/, and the public agent skills repo at ~/agent_skills/.
---

# Save State to GitHub

This skill saves state for **four repos** in every run:
1. **Knowledge base repo** — always `/path/to/works/for/you/knowledge_base/` (registered in `knowledge_base/context/registry/repos.md`)
2. **Claude config repo** — always `~/.claude/` (not in the repo registry; it's the AI config itself)
3. **Paper reading repo** — always `/path/to/works/for/you/Projects/paper_reading_repo/` (registered in `knowledge_base/context/registry/repos.md` as `paper_reading_repo`)
4. **Agent skills repo** — always `~/agent_skills/` (**public** repo; content is pre-sanitized by `publish-skills` before landing here)

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
- Agent skills branch: !`git -C ~/agent_skills branch --show-current 2>/dev/null || echo "not initialized"`
- Agent skills status: !`git -C ~/agent_skills status --short 2>/dev/null || echo "not initialized"`

---

## Pipeline (run for each repo)

### Step 1 — Verify Git Repo
If the repo is not a git repository, skip it and notify the user.

### Step 2 — Collect Candidates
Run `git status --short` (or `git -C <path> status --short` for non-cwd repos) to get all untracked (`?`) and modified (`M`) files.

If there are no candidates, note "Nothing new — working tree is clean." and skip to the next repo.

### Step 3 — Privacy & Secrets Risk Scan (tiered)

Step 3 enforces the global secrets policy — see CLAUDE.md § "Secrets Policy — One Sanctioned Home" for the canonical rule (`~/.claude/<service>_api_key` is the only sanctioned home; the other two repos are key-free zones by design). The tiered scan below is the enforcement mechanism.

#### Tier A — `~/.claude/` (deep per-file review)

Read each candidate diff/file and flag it as **RISKY** if it matches any of the patterns enumerated by `~/.claude/tools/secret-scan.sh` (single source of truth for patterns) — covers hardcoded API keys, private key material, auth tokens, `.env` assignments, credentials filenames, connection strings with passwords, and PII. The changeset here is small, so per-file review is cheap.

**Filename rule (always RISKY regardless of content):** `gemini_api_key`, `openai_api_key`, `*_api_key`, `*_key`. These are gitignored in `~/.claude/.gitignore`.

#### Tier B — `knowledge_base/`, `paper_reading_repo/`, and `agent_skills/` (mechanical scan)

These repos are **declared key-free zones**. Run the canonical scanner — it is the **single source of truth** for patterns. Do not duplicate patterns into prose or per-repo scripts.

`~/agent_skills/` is a **public** repo. Content is pre-sanitized by `publish-skills` before landing here, but the mechanical scan still runs as a safety net — stakes are higher for public repos.

```bash
~/.claude/tools/secret-scan.sh /path/to/works/for/you/knowledge_base
~/.claude/tools/secret-scan.sh /path/to/works/for/you/Projects/paper_reading_repo
~/.claude/tools/secret-scan.sh ~/agent_skills
```

The scanner enumerates the union of (modified-vs-HEAD) and (untracked, gitignore-respecting) files, runs one pass per file, honors the per-repo `.secret-scan-allowlist` and inline `secret-scan: example` markers, and exits **0 = clean** / **1 = matches found**.

**Retroactive audit (covering a batch of commits, not just uncommitted changes):**

```bash
# Audit everything touched since 5 commits ago (modified + still-untracked):
~/.claude/tools/secret-scan.sh /path/to/works/for/you/knowledge_base HEAD~5
```

Use this when the previous checkpoint pre-dates the tiered scan, or when a large drop was committed in a single shot and you want to verify retroactively.

- **Exit 0** → proceed to Step 5 (no per-file content reading required by Claude).
- **Exit 1** → review each match. For true positives, follow the secret-handling protocol in CLAUDE.md § "Secrets Policy" (do not stage the file). For false positives in documentation, add `# secret-scan: example` to that line (or add the path to `.secret-scan-allowlist`) and re-run the scanner.

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

After processing all four repos, ask once:

> "Would you like to push these repos to their remotes?"
> - Knowledge base → origin `<branch>`
> - Claude config → origin `<branch>`
> - Paper reading → origin `<branch>`
> - Agent skills → origin `<branch>`

If yes, push all that had commits and report results. If no, acknowledge and stop.

Only list repos in the prompt that actually had a commit this run. If none did, skip the push prompt entirely.
