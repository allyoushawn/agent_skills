---
name: paper-submission-review
description: Reviews a paper draft (PDF, LaTeX source, or extracted text) before submission and returns prioritized editing suggestions with rationales. Use when the user asks to "review a paper draft", "check a paper before submission", "do a pre-submission review", or supplies a paper file with the goal of polishing it for a venue. Findings cover claim–evidence calibration, contribution naming, abstract/intro framing, section structure, operational clarity, reproducibility anchors, metric choice, baseline credibility, table/figure design, result interpretation, citation discipline, notation hygiene, cleanup, conclusion alignment, and length discipline.
---

# Paper Submission Review

Pre-submission review of an academic paper draft. Input: a draft (PDF / .tex / extracted .txt). Output: a prioritized list of edits with concrete suggested rewrites and rationales tied to a fixed principle set.

The principles come from comparing real draft → accepted submission diffs and from independent LLM-reviewer cross-checks. The principle reference is at [references/principles.md](references/principles.md). The expected output structure is at [references/report-template.md](references/report-template.md).

## When to use

- The user asks to "review a paper", "check a draft", "do a pre-submission review".
- The user supplies a PDF or `.tex` file with the goal of polishing it before a venue deadline.
- The user asks "is my paper ready to submit?"

**Do not use** for:
- Reviewing an *already published* paper for understanding — use the `paper-reader` skill instead.
- Reviewing code or notebooks (use `review`, `simplify`, or `cli-review`).
- Generating a *new* paper outline from scratch.

## Input handling

Accept any of: PDF path, `.tex` path, `.txt` path, or a directory containing the manuscript.

1. **PDF input**: extract text with `pdftotext -layout <input>.pdf <out>.txt`. If `pdftotext` is missing, install with `brew install poppler` (macOS) or `apt-get install poppler-utils`.
2. **LaTeX source**: read the main `.tex` and any `\input{...}` / `\include{...}` children. Keep section structure visible.
3. **Extracted text already on hand**: use directly.

For PDFs longer than 20 pages, use `pdftotext` then read the `.txt`. Do not page through the PDF visually.

## Workflow

Run these phases in order. The principles file (`references/principles.md`) defines codes P0–P16 (positive principles) and A1–A16 (anti-patterns). Reference them by code in the output.

### Phase 1 — Read the whole draft once

Read end-to-end before flagging anything. While reading, capture for yourself (in working memory or scratch notes):
- The paper's title and the noun phrase it uses for its own contribution.
- The first sentence of the abstract; the last sentence of the abstract.
- The headline result(s) from the experiments — the specific numbers and what they say.
- The conclusion's first sentence.
- The section list.

### Phase 2 — Run the principle checks

Walk through `references/principles.md` from P0 → P16 in order. For each, decide whether the draft satisfies it, partially satisfies it, or violates it. **Do not skip principles even when they look fine — make the check explicit.** Note the anti-patterns (A1–A16) you observe in passing.

The most important checks, in order:

1. **P0 Claim–evidence calibration.** Compare the verb in the title and abstract ("propose / extend / show / analyze / correlate") against the actual strongest result. If the strongest evidence is a correlation/observation but the paper is framed as a method/application, this is a *blocker* — flag for retitling and reframing.
2. **P1 Named contribution.** Find the noun phrase the paper uses for itself. Does it appear consistently in title, abstract, conclusion, and section heading? If absent or inconsistent, flag.
3. **P2 Abstract structure.** Score the abstract against the background → gap → claim → evidence structure. Flag any abstract that opens with "we propose" or ends with "outperforms baselines" without concrete characterization.
4. **P3–P4 Intro and section structure.** Underline textbook-level sentences in the intro. Check that section structure mirrors the contribution claim (observation papers need an observation section before the verification section).
5. **P5–P7 Operational clarity, reproducibility, metric.** For every stochastic / threshold / hyperparameter, check the paper specifies train- and test-time behavior. List missing reproducibility anchors (chosen items, hyperparameter rationale, normalization, tolerance windows, dataset split). For each metric, check whether a naive baseline could game it; if yes, require a justification.
6. **P8 Baseline credibility.** List the baselines. Flag any missing standard baseline for the field (e.g., DTW for spoken term detection; standard ASR baseline for speech recognition; the obvious published method for the task).
7. **P9–P10 Tables and figures.** For each table, ask which columns/rows discriminate; flag uniform columns and missing robustness columns. For each claimed comparison, locate the figure and check that comparison is visible in one figure on one page with aligned axes.
8. **P11 Interpretation.** For every nontrivial number, check there's a "what this means" sentence. For every anomaly (non-monotonic trend, underperforming row), check it's acknowledged or explained.
9. **P12–P13 Citations and notation.** Check that every standard tool/dataset has a citation; every non-obvious architectural choice has a defending citation; arXiv preprints are upgraded to venue where possible. Flag overloaded symbols (Y as count, etc.) and per-element notation that should be vectorized.
10. **P14 Cleanup.** Sweep for placeholders (`TODO`, `\cite{?}`, `XXX`, draft emails, missing figure captions).
11. **P15 Conclusion alignment.** Check the conclusion echoes the abstract's frame. Flag new claims or future-work fishing that the experiments don't support.
12. **P16 Length discipline.** Identify the lowest-information-density paragraphs as cut candidates if the paper is over its page budget.

### Phase 3 — Produce the report

Use `references/report-template.md`. For each finding:

- **Principle**: code (P0–P16) or anti-pattern (A1–A16).
- **Location**: section / page / sentence / table-figure number.
- **Quote**: the problematic text verbatim, OR a description of what is missing.
- **Suggested edit**: concrete rewrite, reorder, or addition. Do not be vague ("rephrase this") — provide the actual replacement sentence or the actual missing column header. If you cannot propose a concrete edit, mark this finding "needs author input."
- **Rationale**: one sentence pointing back to the principle.
- **Severity**: `blocker` / `important` / `minor`.

Sort by severity, then by principle number (claim-level issues first).

End with a short **Summary** section: the 3–5 most important moves the author should make.

### Phase 4 — Optional cross-check

For high-stakes drafts (e.g. venue with low acceptance rate or the user explicitly asks), dispatch a second independent read via the `cli-review` skill (Gemini for the prose, Codex for the LaTeX source if available). Append the cross-check findings under "Independent reviewer notes."

## Output discipline

- The report is the deliverable. Save it as `paper_review.md` in the working directory if one exists, otherwise return it in the message.
- Do not modify the draft itself.
- Do not write a "summary of the paper" — the author already knows their paper. The report is *only* the prioritized edits.
- Concrete suggested rewrites > vague advice. If a principle is satisfied, do not flag it; only flag actionable problems.

## Calibration

- A typical 4–6 page conference draft yields 15–35 findings.
- A blocker-class finding (P0 / P1 / P15 mismatch) reframes the paper; expect at most 1–2 of these.
- The majority of findings should be `important` (concrete editorial moves) — these are what the author will act on.
- `minor` findings (typo-level, capitalization) are kept terse; group them at the end if there are many.

## References

- [references/principles.md](references/principles.md) — full principle catalog (P0–P16 and anti-patterns A1–A16) with worked examples.
- [references/report-template.md](references/report-template.md) — the output structure.
- [references/examples-v1-vs-v2.md](references/examples-v1-vs-v2.md) — short worked diffs from the two real draft→accepted pairs the principles are derived from.
