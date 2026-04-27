---
name: cli-review
description: Dispatch a review task to Gemini CLI (large-context review — plans, docs, large file corpora) or Codex CLI (code review — diffs, PRs, implementation quality). Routes based on the nature of the artifact being reviewed. Use from achieve-goal, literature-survey skills, or any skill that needs a CLI-based review gate.
---

# CLI Review

Dispatches a review to Gemini CLI or Codex CLI. The caller provides what to review and which files to read. This skill handles routing, invocation, and failure handling.

CLIs are **read-only** — they never modify files. They return structured text feedback; the calling skill decides what to act on.

## Routing

| What is being reviewed | Route to |
|---|---|
| Plan, design, architecture, or proposal | Gemini CLI |
| Large corpus of docs/files requiring synthesis | Gemini CLI |
| Literature survey consolidation (phases 3.7, 4, 5) | Gemini CLI |
| Exploration of an unfamiliar codebase or domain | Gemini CLI |
| Code changes, diff, PR, or implementation quality | Codex CLI |

When ambiguous: text/docs/plans → Gemini; code → Codex.

Mixed reviews (e.g. "does this implementation match the plan?") → run both sequentially: Gemini first for plan coherence, Codex for code quality.

## Invocation

### Gemini CLI

```bash
gemini --prompt "<task description>

Read these files:
- /absolute/path/to/file1
- /absolute/path/to/file2

<specific questions or output format>"
```

Claude does not pre-summarize the files. Gemini reads them autonomously — that is the point of the 1M context window.

### Codex CLI

```bash
codex --approval-mode full-auto --quiet "<task description>

Read these files:
- /absolute/path/to/file1
- /absolute/path/to/file2

Return: <expected format — issues, severity, suggestions>.
Do not modify any files."
```

## Failure Handling

- **Non-zero exit (crash):** retry once with a simpler or more constrained prompt; if it fails again, skip the review, note it was skipped, and continue
- **Clean exit, empty output:** treat as "no issues found" — valid result, not an error; do not retry

## Output

Return the CLI's stdout to the calling skill verbatim. The calling skill is responsible for acting on the feedback — this skill only dispatches and returns.
