---
name: document-agent-failure
description: Records unexpected agent behavior or failures to a persistent ledger at building_knowledge_and_agent/agents-failure.md. Use when the user reports that an agent, subagent, skill, hook, or the lead agent itself behaved unexpectedly, ignored a rule, produced wrong output, or skipped a documented step. Groups similar failures by a loose fingerprint and prompts the user to fix the root cause once the same failure type has been observed three times.
---

# Document Agent Failure

Maintain a ledger of agent failures so recurring problems become visible and get fixed at the root cause instead of being silently re-encountered.

## Ledger Location

`/path/to/works/for/you/knowledge_base/projects/building_knowledge_and_agent/agents-failure.md`

If the file does not exist, create it from the [Initial Ledger Template](#initial-ledger-template) below before adding the first entry.

## When to Use

Trigger this skill whenever:

- The user complains that an agent / subagent / skill / hook behaved unexpectedly
- An agent ignored a workflow rule, memory item, or CLAUDE.md instruction
- A skill produced wrong output, hallucinated context, or skipped documented steps
- The user says things like "this isn't right", "you shouldn't have done that", "the X agent failed", "you forgot to ..."
- You yourself notice a clear deviation from documented behavior that the user has not yet flagged

Do **not** trigger for:

- Bugs in user code or third-party tools (those are not agent failures)
- One-off LLM nondeterminism the user shrugs off
- Cases where the user explicitly says "don't bother documenting this"

If unsure, ask: "Want me to log this in the agent failure ledger?"

## Workflow

1. **Read the ledger** to load existing failure types and their counts.
2. **Classify** the current failure:
   - Identify the failing component (specific agent name, skill name, hook, or `lead-agent`)
   - Write a one-line normalized summary
   - Generate a fingerprint: `<component>:<short-kebab-slug>` (see [Fingerprint Conventions](#fingerprint-conventions))
3. **Match against existing OPEN entries** using a *loose* heuristic — prefer grouping over splitting. If the same component is failing for what plausibly looks like the same root cause, reuse the existing fingerprint. If clearly distinct, create a new entry.
4. **Update the ledger**:
   - **Match found** → append a new occurrence line (date + brief context) and increment `count`
   - **No match** → create a new entry under `## Open` with `status: open`, `count: 1`
5. **Check the count** for that entry after updating:
   - `count < 3` → save and confirm to user with a one-line note
   - `count == 3` → emit the [Three-Strike Prompt](#three-strike-prompt) inline to the user
   - `count > 3` → also emit the prompt, more urgently, and note in the message that the entry is past the threshold
6. **On confirmed fix** → follow [Retiring an Entry](#retiring-an-entry).

## Entry Schema

Each entry is a level-3 markdown section under `## Open`:

```markdown
### <fingerprint>

- **status**: open
- **component**: <agent / skill / hook name, or `lead-agent`>
- **summary**: <one-line normalized description of the failure>
- **first-seen**: YYYY-MM-DD
- **count**: N
- **occurrences**:
  - YYYY-MM-DD — <one-line context: session topic / triggering prompt / observed behavior>
  - YYYY-MM-DD — <one-line context>
```

## Fingerprint Conventions

Format: `<component>:<short-kebab-slug>`

Examples:

- `kb-librarian:wrong-folder-routing`
- `lead-agent:skipped-fast-path-check`
- `safe-commit:missed-secret-in-diff`
- `paper-reader:hallucinated-citation`
- `kb-update:not-invoked-proactively`

Pick the slug to be specific enough that genuinely different root causes get different fingerprints, but general enough that the *same* root cause maps to one entry. **When unsure, pick the broader slug** — over-grouping surfaces issues sooner; an over-grouped entry can always be split later when the fix is designed.

## Three-Strike Prompt

When `count` reaches 3, surface the entry to the user with a message in roughly this form:

> The failure `<fingerprint>` has now occurred 3 times:
>
> - `<date 1>` — `<context 1>`
> - `<date 2>` — `<context 2>`
> - `<date 3>` — `<context 3>`
>
> Suspected root cause: `<one-sentence hypothesis>`
> Recommended fix: `<concrete suggestion — e.g. tighten skill instructions, add memory item, adjust agent description>`
>
> Options:
> - **(a) fix now** — I'll draft the change
> - **(b) keep observing** — leave entry open, no action
> - **(c) retire (won't fix)** — accept as a known limitation

Do not silently apply a fix. Wait for the user's choice.

## Retiring an Entry

When the user confirms a fix has been deployed (either via this skill's three-strike prompt, or out of band):

1. Set `status: retired`
2. Add a `fix:` field describing what changed, the file paths affected (use repo-relative paths via the `fetch-repo-path` skill, e.g. `paper_reading_repo/...`), and the date
3. **Move the entry** from `## Open` to `## Retired` at the bottom of the ledger, so the active list stays scannable
4. Update the ledger frontmatter `updated:` date

Retired entry shape:

```markdown
### <fingerprint>

- **status**: retired
- **component**: <…>
- **summary**: <…>
- **first-seen**: YYYY-MM-DD
- **count**: N
- **occurrences**:
  - YYYY-MM-DD — <context>
  - …
- **fix**: YYYY-MM-DD — <what changed; file paths; commit/PR if any>
```

If the same fingerprint recurs after retirement, **resurrect** it: move the entry back to `## Open`, set `status: open`, append the new occurrence, and note in the `fix:` field that the previous fix was insufficient. Do not start a fresh entry — the history matters.

## Initial Ledger Template

If `agents-failure.md` does not yet exist, create it with:

```markdown
---
title: Agent Failure Ledger
summary: Append-only ledger of unexpected agent / skill / hook behavior. Failure types observed three times trigger a root-cause fix prompt; fixed entries move to the Retired section. Maintained by the `document-agent-failure` skill.
status: active
updated: <YYYY-MM-DD>
---

# Agent Failure Ledger

Maintained by the `document-agent-failure` skill (`~/.claude/skills/document-agent-failure/`).

## Open

(no entries yet)

## Retired

(no entries yet)
```

## Confirmation Output

After every ledger update, output a short confirmation in this shape:

> Logged `<fingerprint>` (count: N, status: open). [If N==3: see prompt above.]

Keep it to one or two lines — the ledger itself is the durable record.
