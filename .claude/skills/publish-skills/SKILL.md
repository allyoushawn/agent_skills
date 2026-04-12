---
name: publish-skills
description: Scans local Claude skills and agents for sensitive personal information, then syncs clean items to the public agent_skills repo (~/agent_skills/) after user confirmation.
---

# Publish Skills

> **CRITICAL SECURITY WARNING**
> `~/agent_skills/` is a **PUBLIC** GitHub repository visible to anyone on the internet.
> Once pushed, any secrets or PII in a commit are **permanently exposed** — git history
> preserves them even if the file is later deleted or amended. Treat every sync as
> **irreversible**. When in doubt, **do not sync**.

Scans `~/.claude/skills/`, `~/.claude/agents/`, and `~/.claude/CLAUDE.md` for PII or
secrets, then syncs only verified-clean items to the public `~/agent_skills/` repo after
explicit user confirmation. Personal paths and GitHub username are automatically replaced
in published copies (source files in `~/.claude/` are never modified).

## Destination Repo

`~/agent_skills/` — public repo at `git@github.com:YourGithubName/agent_skills.git`

Target structure inside the repo:
- Skills → `.claude/skills/<name>/SKILL.md`
- Agents → `.claude/agents/<name>.md`
- Working principles → `.claude/CLAUDE.md`

---

## Sanitization Rules

Before any file is written to `~/agent_skills/`, apply these substitutions **in order**
(more specific patterns first to avoid partial replacement):

| Pattern (exact string) | Replacement |
|------------------------|-------------|
| `/path/works/for/you` | `/path/works/for/you` |
| `/path/to/works/for/you` | `/path/to/works/for/you` |
| `YourGithubName` | `YourGithubName` |

These replacements apply to **all** files in the sync set — SAFE and user-approved
NEEDS_REVIEW alike. They are applied at write time; source files in `~/.claude/` are
**never modified**.

The sed command to apply all rules at once:
```bash
sed -e 's|/path/works/for/you|/path/works/for/you|g' \
    -e 's|/path/to/works/for/you|/path/to/works/for/you|g' \
    -e 's|YourGithubName|YourGithubName|g' \
    <source_path>
```

---

## Step 1 — Collect Source Files

Run in parallel:
- `ls ~/.claude/skills/` → one subdirectory per skill; the file is `~/.claude/skills/<name>/SKILL.md`
- `ls ~/.claude/agents/` → one `.md` file per agent
- Check `~/.claude/CLAUDE.md` exists

Build a complete list of `(type, name, source_path, dest_path)` tuples where:
- Skills: `dest_path` = `~/agent_skills/.claude/skills/<name>/SKILL.md`
- Agents: `dest_path` = `~/agent_skills/.claude/agents/<name>.md`
- CLAUDE.md: `dest_path` = `~/agent_skills/.claude/CLAUDE.md`

---

## Step 1.5 — Delta Pre-Filter (skip unchanged already-published files)

For each file, compare the **sanitized** source against the destination (since the
destination was written with sanitization applied):

```bash
sed -e 's|/path/works/for/you|/path/works/for/you|g' \
    -e 's|/path/to/works/for/you|/path/to/works/for/you|g' \
    -e 's|YourGithubName|YourGithubName|g' \
    <source_path> | cmp -s - <dest_path> && echo UNCHANGED || echo CHANGED_OR_NEW
```

Bucket each file into exactly one of:
- **UNCHANGED** — destination exists and sanitized source is byte-for-byte identical → skip entirely, no security scan needed
- **MODIFIED** — destination exists but sanitized content differs → must re-scan
- **NEW** — destination does not exist → must scan

Only `MODIFIED` and `NEW` files proceed to Step 2. `UNCHANGED` files are noted in the
final report as "already published, no changes" and require no user action.

If **all** files are `UNCHANGED`, print a short summary ("All skills/agents are already
up to date — nothing to publish.") and stop.

---

## Step 2 — Security Scan (treat this as the most important step)

Read **every file in full** — do not skim. Classify each into exactly one of three tiers.
**Default to BLOCKED when uncertain.** The cost of a false positive (user has to manually
approve) is far lower than the cost of leaking credentials or PII to a public repo.

---

### BLOCKED — Never synced under any circumstances

Flag as BLOCKED if the file contains **any** of the following:

#### Hardcoded secret literals
Values embedded directly as strings (not references to key *files*):
- SSH passwords: `sshpass -p`, `ssh_password`, `sshpass`
- Password assignments: `password\s*[=:]\s*["'][^"']{3,}["']`, `passwd\s*[=:]\s*["'][^"']{3,}["']`
- Token/secret assignments: `token\s*=\s*["'][A-Za-z0-9+/\-_]{8,}["']`, `secret\s*=\s*["'][^"']{6,}["']`
- API key patterns: `sk-[A-Za-z0-9]{20,}` (OpenAI), `AKIA[0-9A-Z]{16}` (AWS), `ghp_[A-Za-z0-9]{36}` (GitHub PAT), `xox[baprs]-[A-Za-z0-9\-]+` (Slack)
- Private key material: `-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----`
- Bearer tokens: `Authorization:\s*Bearer\s+[A-Za-z0-9\-_\.]{16,}`
- Connection strings with passwords: `[a-z]+://[^:]+:[^@]{3,}@` (e.g., `postgresql://user:pass@host`)

#### Personal credentials or auth flows embedded in commands
- Any shell command that passes a credential as a literal argument (e.g., `sshpass -p "cursorssh"`, `curl -u user:password`)
- Hardcoded usernames paired with passwords in any form

#### Personal identifiable information (PII) in data or config values
- Email addresses used as credentials or identifiers (not as examples in documentation)
- Phone numbers, SSNs, passport numbers embedded in data structures
- Personal account numbers or IDs that look like credentials

#### Anything that *looks* like a secret, even if you are unsure
If a value appears to be a credential but doesn't match the patterns above, **flag it as BLOCKED**
and explain why it looks suspicious. Do not give benefit of the doubt to ambiguous values.

---

### NEEDS_REVIEW — Sync only with explicit user opt-in per item

Flag as NEEDS_REVIEW **only** for personal identifiers that are **not** covered by the
Sanitization Rules above. The sanitization rules already handle `/path/to/works/for/you/...` paths
and the `YourGithubName` GitHub username — do **not** flag those as NEEDS_REVIEW.

Flag as NEEDS_REVIEW if the file contains:
- **Hostname or machine-specific identifiers** that reveal infrastructure details
  (e.g., a Colab hostname, a personal server FQDN, an internal company hostname)
- **Personal email addresses** used in documentation or comments (not as credential values — those are BLOCKED)
- **Personal project or internal service names** that are clearly not meant to be public and are not covered by the sanitization rules
- **Any other personal absolute path** that does not start with `/path/to/works/for/you/` and cannot be sanitized by the rules above

For each NEEDS_REVIEW file, list every flagged line with its line number so the user
can make a fully informed decision.

> **Important**: NEEDS_REVIEW is not "probably fine" — it is "only the user can judge
> whether this exposure is acceptable." Do not nudge the user toward approving.

---

### SAFE — Sync after user confirmation

A file is SAFE **only if it passes all of the following** (evaluated on the
post-sanitization content — i.e., after the Sanitization Rules have been applied):
- No hardcoded secret literals of any kind
- No residual personal absolute paths
- No personal usernames in URLs, remotes, or identifiers (beyond what sanitization covers)
- No machine-specific hostnames or internal service names
- No PII in any form

If you are unsure whether something qualifies as SAFE, escalate it to NEEDS_REVIEW.

---

## Step 3 — Build the Report

Print a full structured report before asking for anything:

```
## Publish-Skills Security Scan
## TARGET: PUBLIC repo — git@github.com:YourGithubName/agent_skills.git
## WARNING: Pushing to this repo exposes content to the entire internet permanently.
## NOTE: Personal paths (/path/to/works/for/you/...) and GitHub username are auto-replaced before publishing.

### BLOCKED — will NEVER be synced (hardcoded secrets or credentials)
| File | Type | Finding | Line(s) |
|------|------|---------|---------|
| experiment-runtime | agent | Hardcoded SSH password: `sshpass -p "cursorssh"` | 42 |

### NEEDS_REVIEW — residual personal identifiers NOT covered by sanitization (explicit opt-in required)
| File | Type | Finding | Line(s) |
|------|------|---------|---------|
| some-skill | skill | Internal hostname: `colab-xyz.internal` | 7 |

### SAFE (including auto-sanitized) — no sensitive content after sanitization
| File | Type | Sanitization applied? |
|------|------|-----------------------|
| consult-llm | skill | No |
| fetch-repo-path | skill | Yes — /path/to/works/for/you/... paths replaced |
| kb-sweep | skill | Yes — /path/to/works/for/you/... paths replaced |

### UNCHANGED — already published, sanitized content identical (skipped)
| File | Type |
|------|------|
| loop | skill |
| paper-reader | skill |
```

After the report, ask the user **two separate questions**:

1. For NEEDS_REVIEW items (enumerate each one individually), if any:
   > "The following items have identifiers that are NOT auto-sanitized and will be
   > permanently visible publicly. For each, reply YES to include or NO to skip:
   > - some-skill (exposes internal hostname `colab-xyz.internal` on line 7)
   > - ..."

2. For SAFE items (including auto-sanitized):
   > "The SAFE items listed above will be synced with sanitization applied where noted.
   > Confirm to proceed?"

If there are no NEEDS_REVIEW items, ask only question 2.
**Do not combine these questions.** Do not proceed until all required questions are explicitly answered.

---

## Step 4 — Determine the Sync Set

From the user's responses:
- Include SAFE items only if the user confirmed
- Include NEEDS_REVIEW items **only for each one the user explicitly said YES to**
- BLOCKED items are excluded unconditionally — do not ask, do not include

---

## Step 5 — Final Pre-Copy Check

Before writing any file, do one last check on the exact content that will be written:
re-read each file in the sync set and confirm it still matches SAFE or user-approved
NEEDS_REVIEW classification. If anything changed or looks different on second reading,
stop and report rather than proceeding.

---

## Step 6 — Sync Files (with sanitization)

For each item in the confirmed sync set, write the **sanitized** content to the destination
— do **not** use `cp` directly, as that would copy unsanitized content.

**Skills:**
```bash
mkdir -p ~/agent_skills/.claude/skills/<name>/
sed -e 's|/path/works/for/you|/path/works/for/you|g' \
    -e 's|/path/to/works/for/you|/path/to/works/for/you|g' \
    -e 's|YourGithubName|YourGithubName|g' \
    ~/.claude/skills/<name>/SKILL.md \
    > ~/agent_skills/.claude/skills/<name>/SKILL.md
```

**Agents:**
```bash
mkdir -p ~/agent_skills/.claude/agents/
sed -e 's|/path/works/for/you|/path/works/for/you|g' \
    -e 's|/path/to/works/for/you|/path/to/works/for/you|g' \
    -e 's|YourGithubName|YourGithubName|g' \
    ~/.claude/agents/<name>.md \
    > ~/agent_skills/.claude/agents/<name>.md
```

**CLAUDE.md (working principles):**
```bash
sed -e 's|/path/works/for/you|/path/works/for/you|g' \
    -e 's|/path/to/works/for/you|/path/to/works/for/you|g' \
    -e 's|YourGithubName|YourGithubName|g' \
    ~/.claude/CLAUDE.md \
    > ~/agent_skills/.claude/CLAUDE.md
```

After writing each file, verify the destination contains no residual `/path/to/works/for/you` or
`YourGithubName` strings:
```bash
grep -c 'YOUR_USERNAME\|YourGithubName' ~/agent_skills/.claude/skills/<name>/SKILL.md
# Must output 0
```

If the grep returns non-zero, stop immediately and report which file has residual personal content.

---

## Step 7 — Show Diff and Ask for Commit

Run `git -C ~/agent_skills diff --stat HEAD` and `git -C ~/agent_skills status --short`.

Print the exact list of files that will be committed so the user sees precisely what
is going into the public repo.

Ask:
> "Above is everything that will be committed to the PUBLIC repo. Confirm to commit?"

If confirmed:
1. `git -C ~/agent_skills add .claude/`
2. `git -C ~/agent_skills commit -m "Sync skills and agents: <comma-separated list>"`

Then ask **separately**:
> "Commit is done locally. Push to origin main (this makes it public)?"

Only push if the user explicitly says yes to this second question.

---

## Step 8 — Update the Registry

If `agent_skills` is not already in `/path/to/works/for/you/knowledge_base/context/repos.md`, add it:

```markdown
## Agent Skills (Public)

- **Path**: `/path/to/works/for/you/agent_skills`
- **Purpose**: Public repo sharing reusable Claude skills and agents with the community
- **Git tracked**: yes
- **Remote**: git@github.com:YourGithubName/agent_skills.git
- **Used by**: publish-skills skill
```

---

## Hard Rules (never override these)

- **Never modify source files** in `~/.claude/` — only write sanitized copies to `~/agent_skills/`
- **Never skip the security scan** — even for files you just scanned previously
- **Never skip the residual-content grep** after writing each file (Step 6)
- **Never auto-approve NEEDS_REVIEW** — always require explicit per-item user confirmation
- **Never merge commit + push** into a single user confirmation — they must be two separate approvals
- **Never sync a BLOCKED file** regardless of user instructions — if the user insists, explain the risk and refuse
- If `~/agent_skills/` is not a git repo, stop immediately and tell the user
- For multi-file skills (with auxiliary scripts or subdirectories), flag those auxiliary files separately — do not auto-include them; they need their own scan
