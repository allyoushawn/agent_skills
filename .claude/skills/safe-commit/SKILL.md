---
name: safe-commit
description: Security-reviewed git commit for the ~/.claude backup repo — scans staged changes for secrets before committing
---

# safe-commit

You are performing a security-reviewed git commit in the `~/.claude` backup repo.

## Steps

1. Run `git -C ~/.claude diff --cached` to see what is staged. If nothing is staged, run `git -C ~/.claude status` and stage appropriate files first (respecting .gitignore).

2. **Security review** — examine every staged change and flag anything that looks like:
   - Passwords, secrets, tokens, API keys (hardcoded values, not references to keyfiles)
   - Private key material (PEM blocks, SSH keys)
   - Personal credentials or auth headers with literal values
   - Environment variable assignments that embed a secret value

3. **Decision**:
   - If any high-risk item is found: **stop**, tell the user what was found, suggest adding it to `.gitignore` or removing it, and do NOT commit.
   - If items are low-risk or safe: summarize what will be committed and why it is safe, then proceed with the commit.

4. Commit with a short, descriptive message. End the commit message with:
   `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`

5. Ask the user if they want to push to `origin main`.
