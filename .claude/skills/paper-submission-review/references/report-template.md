# Paper Submission Review — Report Template

Use this structure verbatim. The author should be able to scan the report top-down, fix blockers first, then important, then minor.

---

```markdown
# Paper Submission Review — <paper title>

**Draft:** <file path>
**Reviewed against:** principles P0–P16 / anti-patterns A1–A16

---

## Summary

The 3–5 most important moves the author should make, in priority order. One sentence each. This is what the author will read first.

1. ...
2. ...
3. ...

---

## Blocker findings

(Issues that affect the paper's framing or scope. Fix before any line-editing.)

### Finding B1 — <short name>
- **Principle:** <P0–P16 or A1–A16>
- **Location:** <section / page / sentence / table-figure ref>
- **Quote / observation:**
  > <verbatim text from the draft, OR "missing: <what is missing>">
- **Suggested edit:**
  <concrete rewrite or addition; not vague>
- **Rationale:** <one sentence — why this principle fires here>

### Finding B2 — ...

---

## Important findings

(Concrete editorial moves. Most findings live here.)

### Finding I1 — <short name>
- **Principle:** <code>
- **Location:** <ref>
- **Quote / observation:**
  > <text or "missing: ...">
- **Suggested edit:**
  <concrete rewrite>
- **Rationale:** <one sentence>

### Finding I2 — ...

---

## Minor findings

(Surface-level: typos, capitalization, missing periods, mis-spelled citation key, etc.)

- <Location>: <one-line description and fix>
- <Location>: <one-line description and fix>

---

## Independent reviewer notes (optional)

If a cross-check via `cli-review` (Gemini and/or Codex) was run, list their findings here, grouped by reviewer. Avoid duplicating findings already listed above; only add net-new ones.

### Gemini

- ...

### Codex

- ...

---

## Principle coverage table (optional but recommended)

A quick audit table so the author can see which principles were checked and what the verdict was. Use one row per principle.

| Code | Principle | Verdict | Notes |
|---|---|---|---|
| P0 | Claim–evidence calibration | ✅ / ⚠️ / ❌ | <one-line> |
| P1 | Named contribution | ... | ... |
| ... | ... | ... | ... |
| P16 | Length discipline | ... | ... |
```

---

## Formatting conventions

- Always include the **Quote** when flagging existing text; always include **Suggested edit** as a concrete artifact.
- If an edit is genuinely ambiguous and depends on author intent, write `Suggested edit: needs author input on <specific question>`. Do not fabricate.
- Severity priority order: `blocker` > `important` > `minor`. Within each severity, sort by principle number (lower code = deeper concern → comes first).
- Keep each finding under ~12 lines so the author can act on it without re-reading.
- Do not include a paper summary; the author already knows their paper.
