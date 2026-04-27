---
name: debug
description: Use when the user reports a bug, asks to debug specific behavior, or when an unexpected failure occurs during execution. Applies the standing debugging protocol — reproduce, minimize, validate fix on a single job before scaling.
---

# Debug

Apply the standing debugging protocol when investigating reported bugs or unexpected failures.

## When to use

- User says "debug X" or "X is broken"
- An execution loop hits an unexpected failure and needs structured root-cause analysis
- A test, experiment, or pipeline produces wrong output

## When NOT to use

- The fix is obvious one-line correction (just apply it)
- The user wants exploration ("look at this and tell me what's happening") — that's investigation, not debug

## References

- `kb/context/debugging-protocol.md` — the canonical protocol (reproduce → minimize → validate single → scale; log format; anti-patterns)
- `~/.claude/skills/systematic-debugging/SKILL.md` (obra/superpowers) — 4-phase root-cause structure used *within* this protocol; consult for the formal Hypothesize → Test → Observe → Refine cycle and root-cause-tracing.md
- `~/.claude/skills/verification-before-completion/SKILL.md` (obra/superpowers) — evidence gating before declaring a fix complete

## Steps

1. **Read** `kb/context/debugging-protocol.md` if not already in context
2. **Reproduce** the failure with a minimal trigger; confirm before proposing any fix
3. **Minimize** data size where applicable to shorten turnaround
4. **Form a hypothesis** — write it down with predicted outcome
5. **Validate fix on a single job/instance** before scaling to parallel
6. **Dispatch** the actual code change to a `general-purpose` subagent with a self-contained brief (per CLAUDE.md "Delegate Non-Trivial Editing")
7. **Log** every attempt: hypothesis | action | outcome | next step
8. **If embedded in a milestone** — append the log to the milestone file's Execution Log section

## Output

- A reproduced bug → confirmed working fix → record in execution log
- Or escalation to user after 3 failed hypotheses with no clear next step
