---
name: community-survey-nlm
description: "Community survey skill backed by a persistent NotebookLM notebook per topic. Same source platforms as community-survey, plus cross-run trajectory queries (how has X shifted, what's gone quiet, what's new since N months ago). Use when the user wants to track a topic's community signal over time."
---

# Community Survey (NotebookLM Edition)

Same source platforms as `community-survey` (Hacker News, big-tech research/engineering blogs, ProductHunt, Medium/Substack, X indirect, Quora), but maintains a **persistent NotebookLM notebook per topic-slug** that accumulates community sources across runs.

The value of this skill is **persistent topic memory**, not single-run token efficiency. Typical community surveys touch 10–20 sources, so the per-paper extraction savings that motivate `literature-survey-nlm` (~95% on 200 papers) do not apply here. The reason to use NLM is to enable **trajectory queries** that the lightweight skill cannot answer:

- "How has the consensus on X shifted between Q1 and Q2?"
- "Which projects mentioned in early threads have died, and which are still being discussed?"
- "What new debates have emerged that didn't exist N months ago?"

## Inputs

- **topic** (required)
- **topic_slug** (optional): snake_case slug; derived from topic if omitted
- **time_window** (optional): default `"last 30 days"`
- **delta** (optional): if `true`, load the most recent prior snapshot for this slug and report only new signal in the per-run snapshot
- **lens** (optional): one-sentence framing; falls back to `<topic_slug>/README.md` `## Lens` section
- **trajectory_query** (optional): if provided, after the standard run, fire this as a 5th NLM query against the full accumulated notebook. Example: `"How has the dominant view on tool X shifted in the last 6 months?"`

## Output location

Resolve the paper reading repo path via the `fetch-repo-path` skill (reads `/path/to/works/for/you/knowledge_base/context/registry/repos.md` → "Paper Reading Repo" entry). Do not hardcode the path. Then write under:

```
<paper-reading-repo>/community-survey/<topic_slug>/
```

Same folder as `community-survey`. The two skills share one folder per topic.

## Per-topic folder layout

```
<topic_slug>/
├── README.md                            ← persistent context (lens, audience, why tracked) — added as NLM source
├── log.md                               ← append-only run journal (entries from BOTH skills)
├── notebooklm-state.md                  ← NLM notebook ID + created date
├── community_survey_YYYYMMDD.md         ← per-run snapshot
└── community_survey_YYYYMMDD.md
```

## Prerequisites (run at start of every invocation)

Call `notebook_list` (MCP tool from `notebooklm-mcp`). If it fails, print:

> "NotebookLM MCP not reachable. Run `nlm login`, then call `refresh_auth`. See `~/.claude/skills/notebooklm/SKILL.md`."

Abort the skill.

## Notebook lifecycle

- One notebook per `topic_slug`, persistent across all runs of `community-survey-nlm` on that topic.
- Notebook ID stored in `<topic_slug>/notebooklm-state.md`.
- On every run: read `notebooklm-state.md`, call `notebook_get(notebook_id)` to verify the notebook still exists. If missing or no state file, create a new notebook titled `<topic-slug>-community` and write the state file.
- **Source overflow:** Google AI Pro caps notebooks at 300 sources. Before every `source_add`, count current sources via `notebook_get`. If ≥ 290, create an overflow notebook titled `<topic-slug>-community-overflow-N` (N increments from 1), record its ID in `notebooklm-state.md`, and switch subsequent `source_add` calls to it. Community surveys will rarely hit this, but include the guard.

### `notebooklm-state.md` format

```markdown
# NotebookLM State — <topic-slug> (community)

notebook_id: <id>
created: <date>
readme_ingested_on: <date>
overflow_notebooks:
  - <topic-slug>-community-overflow-1: <id>
```

## Steps

### Step 1. Parse inputs and ensure README.md

Same as `community-survey` Steps 1 and 1.5 in `~/.claude/skills/community-survey/SKILL.md`:

- Derive `topic_slug` (lowercase, spaces → underscores, strip punctuation)
- Resolve today's date as `YYYYMMDD`
- Resolve `time_window` (default `"last 30 days"`)
- If `delta=true`, read the most recent `community_survey_*.md` and note its date as `prior_date`
- If `<topic_slug>/README.md` does not exist, prompt the user for (a) why tracked, (b) audience, (c) lens, then write the README using the template documented in `community-survey` Step 1.5
- Resolve the active lens: prefer the `lens` parameter, otherwise read the `## Lens` section in `README.md`

### Step 2. NLM prereq check + notebook ensure

- Run the prerequisites above (`notebook_list`).
- Resolve or create the topic notebook per the lifecycle above.
- **README ingest:** if `README.md` was just created in Step 1, OR its file mtime is newer than `readme_ingested_on` in `notebooklm-state.md` (or that field is missing), add it as a source via `source_add(notebook_id=<id>, source_type="text", text=<readme contents>, title="README — <topic-slug>")`. Then update `notebooklm-state.md` with `readme_ingested_on: <today>`. This bakes the lens/context into queries.

### Step 3. Run community-survey source-gathering steps

Run Steps 2–7 from `~/.claude/skills/community-survey/SKILL.md` to gather sources (Hacker News, the three engineering-blog query groups, ProductHunt, Medium/Substack, X indirect, Quora). Do not duplicate the queries here.

### Step 4. Ingest gathered sources into the notebook

For each source URL collected in Step 3 (excluding x.com URLs, which NLM cannot ingest):

- **Skip if already a source** in the notebook (check via `notebook_get` and compare URL/title).
- **Overflow check first:** count current sources; if ≥ 290, switch to a fresh overflow notebook before adding.
- Call `source_add(notebook_id=<active>, source_type="url", url=<url>, wait=False)` and record the returned `source_id`.
- Poll source status until `ready`. Timeout = 60s per source. On timeout/error, log the URL under a `## Skipped sources` section in the per-run snapshot (with the failure reason) and continue — do not fail the whole run.

X snippets and Quora answer text (when fetched directly) can optionally be ingested as `source_type="text"` with the snippet text plus a citation header. Mark these in the notebook with a `[snippet]` prefix in the title so trajectory queries can distinguish them from full sources.

### Step 5. Synthesize per-run snapshot

Same as `community-survey` Step 8: produce the standard sections (`Source Snapshots`, `Synthesis` through the lens — Key Themes, Notable Tools & Projects, Key Debates & Disagreements, Emerging Patterns, Open Questions — and `Limitations This Run`). If `delta=true`, also append the `## What's New Since <prior_date>` section per `community-survey` Step 9.

### Step 6. Trajectory queries (the value-add of this skill)

Fire these queries against the **full accumulated notebook** (no `source_ids` filter):

1. "Looking at all sources in this notebook by date, how has the dominant view on the topic evolved over time? Identify any clear shifts in consensus."
2. "Which tools, projects, or names mentioned in earlier sources have stopped appearing in more recent sources? List them with the date of last mention."
3. "What new tools, projects, debates, or themes appear in the most recent sources that did not appear in older sources?"
4. "What questions or open problems are repeatedly raised across sources from different time periods, suggesting they remain unresolved?"

If the `trajectory_query` parameter was passed, fire it as a 5th query.

Append the responses to the per-run snapshot under a new top-level section:

```markdown
## Trajectory (from accumulated notebook of N sources spanning <oldest_date> → <newest_date>)

### Consensus shifts over time
[Q1 answer]

### What's gone quiet
[Q2 answer]

### What's newly emerging
[Q3 answer]

### Persistent open questions
[Q4 answer]

### User-defined trajectory query
[Q5 answer, only if trajectory_query was passed]
```

**NLM refusal handling:** scan responses for refusal phrases (`"I cannot answer"`, `"not enough information"`, `"not mentioned in the source"`, etc.). Replace any such section's content with: `Not enough longitudinal signal yet — need more runs over a longer period.`

### Step 7. Save snapshot

Save the assembled snapshot to:

```
<paper-reading-repo>/community-survey/<topic_slug>/community_survey_YYYYMMDD.md
```
(`<paper-reading-repo>` was already resolved at the start of the run via `fetch-repo-path`.)

Report the saved path to the user.

### Step 8. Append to log.md

Same format as `community-survey` Step 11, but mark the run type as `community-survey-nlm`. The `log.md` is shared with `community-survey` runs — both skills append to the same file, giving a unified per-topic timeline. Prepend (newest on top):

```markdown
## YYYY-MM-DD — community-survey-nlm run (<full | delta since YYYY-MM-DD>)
- Lens: <lens>
- Time window: <time_window>
- Sources scanned: HN(N), eng-blogs(N), PH(N), Medium(N), X(snippets), Quora(N)
- Sources added to NLM notebook: N (total now: M)
- Output: community_survey_YYYYMMDD.md
- Trajectory: <one-line headline of the strongest trajectory finding>
```

## Non-goals

This skill explicitly does **not** do:

- **Per-source structured extraction** (Q1/Q2-style queries from `literature-survey-nlm`). Discourse artifacts don't have consistent shape — over-structured extraction adds noise.
- **Method tracker.** Not applicable to discourse.
- **Reverse citation map.** Not applicable to discourse.
- **Cross-paper baseline mapping.** Not applicable.
- **Reddit ingestion.** Still blocked at crawler level.
- **Direct X/Twitter URL ingestion.** Still blocked.

## Known limitations

Same set as `community-survey` (Reddit blocked, X indirect, search indexing lag), plus:

- NLM cannot ingest `x.com` URLs — X signal stays in the per-run snapshot only, not in the notebook. Trajectory queries therefore under-weight X discourse.
- HN and ProductHunt threads ingested into NLM are static snapshots — comments added after ingestion are not reflected in trajectory queries.

## References used during execution

- NotebookLM tool patterns: `~/.claude/skills/notebooklm/SKILL.md`
- Source-gathering steps (search queries, blog roster, snapshot template): `~/.claude/skills/community-survey/SKILL.md`
- NLM lifecycle, prereq message, overflow handling: `~/.claude/skills/literature-survey-nlm/SKILL.md`
