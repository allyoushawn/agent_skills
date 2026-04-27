---
name: literature-survey-nlm
description: "NotebookLM-backed literature survey skill. Token-efficient alternative to literature-survey: uses NotebookLM notebook_query for per-paper analysis (~95% token savings). Invoke with /literature-survey-nlm <topic> [topic-slug]."
---

# Literature Survey (NotebookLM Edition)

Performs a structured literature survey on a given topic using NotebookLM for per-paper analysis. Saves all outputs under the paper reading repo.

## References (load when relevant)

- `kb/context/literature-survey/literature-survey-priorities.md` — venue list, paper priority rules, topic relevance, method fundamentality weight, accessibility principle
- `kb/context/literature-survey/literature-survey-templates.md` — output file templates (requirements, literature-review, method-tracker, executive-summary) and per-paper additions (Project Relevance, Reverse Citation Map)
- `kb/context/literature-survey/literature-survey-conventions.md` — topic-slug naming, folder structure, queue.md format (incl. NLM `nlm:` column), Phase 0 resume detection, Phase 0.5 README, Phase 1 Must-Include consistency check, Phase 3.5/3.7, Phase 5 coverage evaluation, log.md final entry, writing principles
- `kb/context/literature-survey/literature-survey-discovery.md` — Awesome repo Step 0, web search query patterns, engineering blog list, queue depletion strategy, rate-limit handling
- `~/.claude/skills/notebooklm/SKILL.md` — NotebookLM tools and usage patterns
- `~/.claude/skills/paper-reader/SKILL.md` — filename rules, report template, writing notes (read at runtime, apply latest)
- `~/.claude/skills/cli-review/SKILL.md` — CLI review dispatch via Gemini CLI (large corpus analysis, synthesis); used in Phases 3.7, 4-B, and 5

## Delegation Architecture (Enforced)

This skill processes abundant information across many phases. **Failure to delegate at every level causes the plan to be lost from context.** Two mandatory delegation rules:

**Rule 1 — Lead agent must delegate immediately.** When you (the lead agent) receive this skill, immediately delegate the entire task to a fresh general-purpose subagent via the Agent tool. Pass the topic, topic-slug, and these full skill instructions verbatim. Do not execute any phase yourself.

**Rule 2 — Orchestrator subagent must delegate each phase.** The subagent receiving the delegation acts as an orchestrator only. Its job: read state, determine next phase, write a self-contained brief, dispatch a per-phase subagent, read results, advance state. **Do not execute phases directly in the orchestrator** — as phases accumulate output the plan will be crowded out of context. Delegate each phase:

| Phase | Delegation |
|-------|-----------|
| Phase 0 (state detection) | Inline — read-only and brief |
| Phase 0.5 (ensure README.md) | Inline — interactive prompt + small write |
| Phase 1 (requirements + search strategy) | Delegate to subagent |
| Phase 2 (paper discovery) | Delegate to subagent |
| Phase 3 (per-paper NLM analysis) | Per-batch subagents (3–5 papers each) — follow Phase 3 delegation model exactly |
| Phase 3.5 (finalize method tracker) | Delegate to subagent |
| Phase 3.7 (cross-reference mapping) | Per-group subagents — follow Phase 3.7 instructions |
| Phase 4 (literature review synthesis) | Delegate to subagent |
| Phase 5 (executive summary) | Delegate to subagent |

Each per-phase brief must be fully self-contained: output folder path, `notebook_id` from `notebooklm-state.md`, verbatim content of relevant files (`requirements.md`, `queue.md`), and the specific phase instructions from this document plus the relevant kb/context references. End each brief per CLAUDE.md § "Subagent Output Protocol" (one sentence confirming completion or one-line error).

## Usage

`/literature-survey-nlm <topic> [topic-slug]`

- `<topic>`: topic to investigate (required).
  Examples: `"model cascading in ML systems"`, `"prevalence sampling for imbalanced classification"`
- `[topic-slug]`: folder name for the topic (optional). Topic-slug naming rules in `kb/context/literature-survey/literature-survey-conventions.md`.

Outputs are saved under `[paper-reading-repo]/literature-survey/[topic-slug]/`. Resolve `[paper-reading-repo]` via the `fetch-repo-path` skill.

Examples:
- `/literature-survey-nlm model cascading in ML systems`
  → `literature-survey/model-cascading-in-ml-systems/`
- `/literature-survey-nlm backward compatible embeddings bce`
  → `literature-survey/bce/`

## Prerequisites (checked at the start of every run)

1. **NotebookLM reachability:** Call `notebook_list` (MCP tool from `notebooklm-mcp`). If it fails, print:

   > "NotebookLM MCP not reachable. Run `nlm login`, then call `refresh_auth`. See `~/.claude/skills/notebooklm/SKILL.md`."

   Abort the skill.

2. **Resolve paper-reading repo path:** Read `/path/to/works/for/you/knowledge_base/context/registry/repos.md` and find the "Paper Reading Repo" entry. This is `[paper-reading-repo]`.

3. **Output root:** `[paper-reading-repo]/literature-survey/[topic-slug]/`

## Notebook Lifecycle

One notebook per topic slug. The notebook ID is stored in `notebooklm-state.md` (notebook ID + created date + overflow notebook IDs only — no Source Map; `queue.md` is the sole source of truth for per-paper NLM source IDs).

**On resume:** Read `notebooklm-state.md` → call `notebook_get(notebook_id)` to verify the notebook still exists.

**Source limit guard:** NotebookLM's source cap depends on the account tier. This account is **Google AI Pro**, which supports up to **300 sources per notebook**. Before every `source_add`, count the current sources in the active notebook via `notebook_get`. If count ≥ 290, create an overflow notebook titled `[topic-slug]-overflow-N` (where N increments from 1), record its ID in `notebooklm-state.md`, and switch all subsequent `source_add` calls to it. (The old threshold of 45 was written for the free tier — do not use it.)

### `notebooklm-state.md` format

```markdown
# NotebookLM State — [topic-slug]

notebook_id: <id>
created: <date>
overflow_notebooks:
  - [topic-slug]-overflow-1: <id>
```

## Folder Structure

See `kb/context/literature-survey/literature-survey-conventions.md` for the standard folder layout. The NLM variant adds one extra file at the topic root: `notebooklm-state.md`.

## Phase 0: Detect Existing Outputs and Determine State (Resume Mode)

If the output folder already exists, run this phase first; otherwise skip to Phase 1.
Full procedure (scan files, determine progress state, resume Phase 3 logic, user confirmation): see Phase 0 section in `kb/context/literature-survey/literature-survey-conventions.md`.

NLM-specific addition during 0-1: if `notebooklm-state.md` is present, read the `notebook_id` and verify it via `notebook_get`. Report the NLM notebook status (notebook title, source count, whether it exists) alongside other resume state.

## Phase 0.5: Ensure README.md exists

Runs whether or not the folder is fresh. Supersedes the Phase 1 Step 6 "Project Context" prompt. Full prompt and README.md template: see Phase 0.5 section in `kb/context/literature-survey/literature-survey-conventions.md`.

## Phase 1: Preparation and Search Strategy Setup

1. Create the output folder and the `read-papers/` subfolder if they do not exist.
2. Extract 3–6 core keywords from the topic.
3. Decide the search strategy based on the criteria in `kb/context/literature-survey/literature-survey-priorities.md` (relevant venues by area, paper prioritization, method fundamentality weight).
4. Once the search strategy is decided, immediately create `requirements.md` using the template in `kb/context/literature-survey/literature-survey-templates.md`.
   This file must record the user-requested topic, extracted keywords, selected venues/blogs, search queries, and survey scope constraints.
5. After creating the requirements file, show its contents to the user and get confirmation.
   If the user requests revisions, reflect them and confirm again.
   Only after user approval may you proceed to Phase 2.

6. **Project Context (already collected in Phase 0.5):** Project Context is collected and persisted in `README.md` during Phase 0.5. Do not re-prompt here. In `requirements.md`, include a one-line reference instead of duplicating the section:

   ```markdown
   ## Project Context

   See `./README.md` for the canonical Project Context. This file references it; do not duplicate.
   ```

   All downstream phases that refer to `## Project Context` should read it from `README.md`. The Project Context is the **north star** for the entire survey — it shapes which papers are included, what is extracted from each paper (Phase 3 Query 3), how findings are synthesized (Phase 4 Queries 6–7), and how the executive summary is framed (Phase 5).

7. **Must Include / Project Context consistency check (mandatory):** Procedure in `kb/context/literature-survey/literature-survey-conventions.md` § Phase 1 Must Include / Project Context Consistency Check. Only proceed to Phase 2 after the user has confirmed or revised the Must Include list following this check.

## Phase 2: Collect Seed Papers

Do **not** list all 200 papers at once. First collect 15–25 seed papers, then gradually expand the list in Phase 3 by following related works from each paper.

For Step 0 (Awesome repo scan) and Step 1 (web search query patterns + engineering blog list): see `kb/context/literature-survey/literature-survey-discovery.md`.

### Step 2 (NLM-specific): NLM Research Discovery

1. Create the topic notebook: `notebook_create(title="[topic-slug]")` → save the returned `notebook_id` to `notebooklm-state.md`.
2. Call `research_start(notebook_id=<id>, query="<topic keywords>", source="web", mode="deep")` → record the returned `task_id`.
3. Poll `research_status(notebook_id=<id>, task_id=<id>, compact=True)` until status = complete. Do NOT use `compact=False` during polling.
4. Make one final `research_status` call with `compact=False` to review all hits.
5. Select relevant papers → call `research_import(notebook_id=<id>, task_id=<id>, source_indices=[...])`.
6. Record the returned source IDs for each imported paper.

### Step 3: Deduplicate and Build queue.md

Union all sources from Steps 0, 1, and 2. Deduplicate by title. Apply all priority and relevance rules from `kb/context/literature-survey/literature-survey-priorities.md` verbatim.

`queue.md` format (extends the standard format with an `nlm:` column): see `kb/context/literature-survey/literature-survey-conventions.md` § queue.md Format.

After seed collection, assess whether the target number of papers (200) is appropriate for the topic. If 200 seems excessive, stop at Phase 2 and confirm the target paper count with the user. Proceed with later phases using the approved target count.

Also create an empty `method-tracker.md` (template in `kb/context/literature-survey/literature-survey-templates.md`).

## Phase 3: Per-Paper Analysis via NLM

This is the token-saving core. Instead of reading PDFs into Claude's context, Claude fires structured queries per paper to NotebookLM.

**Delegation model:** Process papers in batches of 3–5. Each batch is delegated to a fresh general-purpose subagent via the Agent tool to prevent context bloat. The brief to each subagent must include: `notebook_id`, the batch paper list with source IDs and URLs, and the output folder path. After the subagent writes the batch outputs to disk, a new subagent is spawned for the next batch.

For each paper in the batch:

### 3-A: URL Normalization

Before ingesting, normalize the URL:

- **arXiv abstract URL** (`arxiv.org/abs/<ID>` or `arxiv.org/abs/<ID>v<N>`): convert to PDF URL → `https://arxiv.org/pdf/<ID>.pdf`
- **Paywalled publisher URL** (IEEE Xplore `ieeexplore.ieee.org`, ACM DL `dl.acm.org`, Springer `link.springer.com`, Elsevier `sciencedirect.com`): do **not** skip immediately. First search for a free version using the four-step search order in `kb/context/literature-survey/literature-survey-priorities.md` § Accessibility Principle.

  If a free URL is found, replace the URL with the free version and continue ingestion normally.
  Only if all four checks return nothing: mark as `nlm:failed:paywall` in queue.md, log the search attempts in the Skipped section as `"paywall — checked arxiv, SSRN, Semantic Scholar, author homepage; no free version found"`, and skip.

### 3-B: Ingest into NLM

- If `nlm` status is `pending`:
  - **Overflow check first:** Count sources in the current active notebook via `notebook_get`. If ≥ 290, create an overflow notebook (see Notebook Lifecycle above) and switch to it.
  - Call `source_add(notebook_id=<id>, source_type="url", url=<normalized_url>, wait=False)` → record the returned `source_id`.
  - Poll `notebook_get(notebook_id)` and check the source's status field until it becomes `ready`. Timeout = 120s. If timeout or error: mark `nlm:failed:<reason>`, add to Skipped section, continue to next paper.
  - On success: update the queue entry from `nlm:pending` to `nlm:<source_id>`.
- If `nlm` status is already `<source_id>`: already ingested — skip directly to 3-C.

### 3-C: Two-Query Structured Extraction

Use **independent queries** — do NOT use `conversation_id` threading. This prevents answer contamination between questions.

**Query 1** — scope with `source_ids=[<source_id>]`:

> "For the paper in this source, provide all of the following clearly labeled:
> (1) Core problem and key contribution
> (2) Proposed method or architecture in detail
> (3) Datasets used for evaluation and comparison baselines"

**Query 2** — scope with `source_ids=[<source_id>]`:

> "For the paper in this source, provide all of the following clearly labeled:
> (1) Key quantitative results and improvements over baselines
> (2) Limitations, failure modes, or negative results noted by the authors
> (3) Top 5–7 most heavily cited prior works named in the related work or introduction"

**Query 3 (project-specific)** — scope with `source_ids=[<source_id>]`:

The batch subagent **dynamically formulates** this query from the `## Project Context` section in `README.md`. It must probe whether and how this paper's method/findings address the project's specific needs — referencing the concrete framing (e.g., label type, noise model, downstream goal, audience questions), not just repeating the topic generically.

This query runs for **all** papers unconditionally. If the answer indicates the paper does not address the project need, that is a useful signal — it flags a retrieval-phase relevance mismatch, not a query design problem.

**NLM refusal handling:** After receiving all three responses, scan for refusal language: phrases like "I cannot answer", "not mentioned in the source", "I don't have enough information", or similar. Replace any such section's content with: `Not specified in source.` Do not copy NLM refusal boilerplate into the markdown output.

### 3-D: Assemble Markdown

Assemble the three Q&A responses into the standard `read-papers/` markdown file.

Follow the **filename rules** and **report template** from `~/.claude/skills/paper-reader/SKILL.md` exactly. Do not copy the template into this skill — read it at runtime and apply it.

When in `read-papers/` mode (as opposed to standalone paper-reader use), leave the Reverse Citation Map section blank — it is filled in during Phase 3.7. The Project Relevance and Reverse Citation Map section formats are in `kb/context/literature-survey/literature-survey-templates.md` § Per-Paper Markdown Additions.

After the standard template sections, add a **Project Relevance** section containing the structured Query 3 answer:

```markdown
## Project Relevance
[Query 3 answer, structured by the subagent]
```

If the Query 3 answer indicates the paper does not meaningfully address the project's needs, prefix the section with: `**Low project relevance.** [reason]`. This makes it scannable during review and serves as a retroactive check on the retrieval phase.

**For Priority 3–4 / Peripheral papers:** write a one-paragraph summary only — do not fill every section. Still include the Project Relevance section.

### 3-E: Update Tracking

- Move paper from "To Process" → "Done" in queue.md, including the `nlm:<source_id>` field.
- Update `method-tracker.md` with any newly observed methods, baseline mentions, variant counts, and component counts.
- After finishing the batch, report a progress summary to the lead agent:
  ```text
  [Batch complete] Processed: X | Skipped: Y | Remaining: Z | NLM sources in notebook: N
  ```

**Note on cross-paper baseline question:** The "is this paper's method used as a baseline by others?" question cannot be answered per-paper because it requires seeing the full notebook. This is addressed in Phase 4-A (Query 5).

### Queue Depletion Strategy

If the queue risks running out before reaching the target paper count, expand it following the Queue Depletion Strategy in `kb/context/literature-survey/literature-survey-discovery.md`. The harvest source for the NLM variant is the markdowns in `read-papers/` (Related Works and Introduction sections), not PDFs.

## Phase 3.5: Finalize Method Tracker

See `kb/context/literature-survey/literature-survey-conventions.md` § Phase 3.5.

## Phase 3.7: Cross-Reference Mapping

After Phase 3.5 is complete, you **must** run this step. Do **not** start Phase 4 until this step is complete.
Full procedure and gating rule: see `kb/context/literature-survey/literature-survey-conventions.md` § Phase 3.7.

**Execution: dispatch to Gemini CLI** (via `cli-review` skill) with all files in `read-papers/` as the file list. Gemini reads the full corpus in one shot and returns the citation map. Do not delegate to a Claude subagent — at 200 papers, the corpus exceeds Claude's practical context for this step.

## Phase 4: Literature Review (NLM-First Hybrid Synthesis)

### 4-A: NLM Generates Core Draft

Query the full notebook with no `source_ids` filter (all papers). Use these 5 queries as building blocks for `literature-review.md`:

1. "What are the dominant methodological approaches across all papers in this notebook? For each approach, summarize it and list representative papers."
2. "What are the most common evaluation datasets and benchmarks used across these papers? Which papers use which datasets?"
3. "What open problems or research gaps are identified most frequently across these papers?"
4. "Which papers appear to be the most foundational — cited by or built upon by many others in this notebook? List them with brief explanations."
5. "Is any paper's method used as a direct baseline by other papers in this notebook? Map method name → list of papers that use it as a baseline."

**Queries 6–7 (project-specific synthesis)** — dynamically formulated by the Phase 4 subagent from the `## Project Context` section in `README.md`. The subagent reads the Project Context and writes 1–2 cross-paper queries (no `source_ids` filter) that synthesize the notebook's papers through the lens of the project's specific needs. Examples: "Which methods in this notebook are applicable when labels are [project-specific label type]?" or "What does the collective evidence say about [project-specific concern]?" These become additional building blocks for `literature-review.md`.

### 4-B: Gemini Structures into literature-review.md

**Execution: dispatch to Gemini CLI** (via `cli-review` skill). Pass the 5–7 NLM query responses from Phase 4-A, the Main Review File Template from `kb/context/literature-survey/literature-survey-templates.md`, and the `## Project Context` from `README.md`. Gemini consolidates the NLM responses into a `literature-review.md` draft. Claude Lead reviews the draft, runs the conflict check (Phase 4-C), and finalizes. Claude does **not** re-read all individual per-paper markdowns at this step.

### 4-C: Conflict Check

Claude spot-checks NLM's cross-paper claims against the per-paper markdowns already written (read only the specific ones relevant to a claimed conflict). If a conflict is found: flag it, re-query NLM with a follow-up question, and resolve before finalizing.

## Phase 5: Write Outputs and Evaluate Coverage

Note: Start this phase only after Phase 3.7 is fully complete.

Complete the four files using the templates in `kb/context/literature-survey/literature-survey-templates.md`:

#### File 1: `requirements.md`

- Created in Phase 1, updated here.
- Fill in the "Summary of Actual Search Results" section.
- Record total number of papers, number of categories, and main findings.

#### File 2: `literature-review.md`

Full paper list and category-wise summary. Each paper entry should include a link to the individual file in `read-papers/`.

#### File 3: `executive-summary.md`

**Execution: dispatch to Gemini CLI** (via `cli-review` skill). Pass `literature-review.md`, `method-tracker.md`, `README.md` (for Project Context), and all files in `read-papers/`. Gemini drafts the executive summary. Claude Lead reviews the draft, runs the optional NLM sanity check query, and finalizes.

A 2–3 page summary for decision-makers.

Every claim and recommendation must explicitly cite sources using the paper's full name. Do not use abbreviations like "the PoLL paper". Use the format: `"Author et al., full paper title, conference year"`.

The executive summary must include a "Most Fundamental Methods" section describing the top 5 methods from the finalized `method-tracker`.

The executive summary must include an **"Implications for [Use Case]"** section (or **"Recommendations"** if the Project Context describes a specific project). This section directly answers the key questions or decision points stated in the `## Project Context` section of `README.md`, citing specific papers. For a general academic survey, this section summarizes the most actionable takeaways for the stated audience.

**Optional NLM sanity check:** After drafting `executive-summary.md`, query NLM with no `source_ids` filter: "Summarize the state of the field based on all sources in this notebook." Compare against the draft and flag any notable discrepancies.

#### File 4: `method-tracker.md`

Gradually filled during Phase 3, finalized in Phase 3.5.

#### Phase 5 Exit Condition: Coverage Evaluation

Full coverage-evaluation procedure (keyword coverage % + Project Context fitness check + actions when below 95%): see `kb/context/literature-survey/literature-survey-conventions.md` § Phase 5 Exit Condition.

## Final: Append to log.md

After Phase 5 completes (whether final completion or paused for user input), prepend a dated entry (newest on top) to `[topic-slug]/log.md`. Entry format and rules: see `kb/context/literature-survey/literature-survey-conventions.md` § Final Append to log.md. Use `<skill-name>` = `literature-survey-nlm` for the run header. The log entry should also include `NLM notebook source count: <N> (added <delta> this run)`.

This section runs unconditionally at the end of every invocation, including resumes and reruns — it's the audit trail.
