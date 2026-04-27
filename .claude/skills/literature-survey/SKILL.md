---
name: literature-survey
description: "Literature Survey Skill - performs a structured literature survey for a given topic and saves outputs under the paper reading repo's literature-survey/[topic]/ folder. Invoke with /literature-survey <topic> [topic-slug]."
---

# Literature Survey Skill

Performs a structured literature survey on a given topic and saves all outputs under the paper reading repo.

**Before writing any files**, look up the paper reading repo path using the `fetch-repo-path` skill:
→ Read `/path/to/works/for/you/knowledge_base/context/registry/repos.md` and find the "Paper Reading Repo" entry.

Output root: `[paper-reading-repo]/literature-survey/[topic-slug]/`

## References (load when relevant)

- `kb/context/literature-survey/literature-survey-priorities.md` — venue list, paper priority rules, topic relevance, method fundamentality weight, accessibility principle
- `kb/context/literature-survey/literature-survey-templates.md` — output file templates (requirements, literature-review, method-tracker, executive-summary) and per-paper additions (Project Relevance, Reverse Citation Map)
- `kb/context/literature-survey/literature-survey-conventions.md` — topic-slug naming, folder structure, queue.md format, Phase 0 resume detection, Phase 0.5 README, Phase 1 Must-Include consistency check, Phase 3.5/3.7, Phase 5 coverage evaluation, log.md final entry, writing principles
- `kb/context/literature-survey/literature-survey-discovery.md` — Awesome repo Step 0, web search query patterns, engineering blog list, queue depletion strategy, PDF download instructions, rate-limit handling
- `~/.claude/skills/paper-reader/SKILL.md` — filename rules, report template, writing notes (read at runtime, apply latest)
- `~/.claude/skills/cli-review/SKILL.md` — CLI review dispatch via Gemini CLI (large corpus analysis, synthesis); used in Phases 3.7, 4, and 5

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
| Phase 3 (batch processing) | Per-batch subagents — follow Phase 3 instructions exactly |
| Phase 3.5 (finalize method tracker) | Delegate to subagent |
| Phase 3.7 (cross-reference mapping) | Per-group subagents — follow Phase 3.7 instructions |
| Phase 4 (literature review synthesis) | Delegate to subagent |
| Phase 5 (executive summary) | Delegate to subagent |

Each per-phase brief must be fully self-contained: output folder path, verbatim content of relevant files (`requirements.md`, `queue.md`), and the specific phase instructions from this document plus the relevant kb/context references. End each brief per CLAUDE.md § "Subagent Output Protocol" (one sentence confirming completion or one-line error).

## Usage

`/literature-survey <topic> [topic-slug]`

- `<topic>`: topic to investigate (required).
  Examples: `"model cascading in ML systems"`, `"prevalence sampling for imbalanced classification"`
- `[topic-slug]`: folder name for the topic (optional). Topic-slug naming, folder structure, and resume mode behavior live in `kb/context/literature-survey/literature-survey-conventions.md`.

Examples:
- `/literature-survey model cascading in ML systems`
  → `literature-survey/model-cascading-in-ml-systems/`
- `/literature-survey model cascading in ML systems model-cascading`
  → `literature-survey/model-cascading/`
- `/literature-survey backward compatible embeddings bce`
  → `literature-survey/bce/`

### Resume Mode

If existing outputs are already present in `literature-survey/[topic-slug]/`, the skill automatically enters resume mode. See Phase 0 in `kb/context/literature-survey/literature-survey-conventions.md` for full state-detection rules and resume behavior. Conditions for entering resume mode: the folder exists AND at least one of `requirements.md`, `queue.md`, or `literature-review.md` exists. Resume mode does not overwrite, reset, rerun completed phases, or reprocess papers already in `read-papers/`.

## Folder Structure & File Naming

See `kb/context/literature-survey/literature-survey-conventions.md` for the full folder layout and `kb/context/paper-reader/SKILL.md` reference for filename rules.

## Execution Order

### Phase 0: Detect Existing Outputs and Determine State (Resume Mode)

If the output folder already exists, run this phase first; otherwise skip to Phase 1.
Full procedure (scan files, determine progress state from the resume table, resume Phase 3 logic, user confirmation): see Phase 0 section in `kb/context/literature-survey/literature-survey-conventions.md`.

### Phase 0.5: Ensure README.md exists

Runs whether or not the folder is fresh. Supersedes the Phase 1 Step 6 "Project Context" prompt.
Full prompt and README.md template: see Phase 0.5 section in `kb/context/literature-survey/literature-survey-conventions.md`.

### Phase 1: Preparation and Search Strategy Setup

1. Create the output folder and the `read-papers/` subfolder if they do not exist.
2. Extract 3–6 core keywords from the topic.
3. Decide the search strategy based on the criteria in `kb/context/literature-survey/literature-survey-priorities.md` (relevant venues by area, paper prioritization, method fundamentality weight).
4. Once the search strategy is decided, immediately create `requirements.md` using the template in `kb/context/literature-survey/literature-survey-templates.md`.
   This file must record the user-requested topic, extracted keywords, selected venues/blogs, search queries, and survey scope constraints.
5. After creating the requirements file, you must show its contents to the user and get confirmation.
   If the user requests revisions, reflect them and confirm again.
   Only after user approval may you proceed to Phase 2.

6. **Project Context (already collected in Phase 0.5):** Project Context is collected and persisted in `README.md` during Phase 0.5. Do not re-prompt here. In `requirements.md`, include a one-line reference instead of duplicating the section:

   ```markdown
   ## Project Context

   See `./README.md` for the canonical Project Context. This file references it; do not duplicate.
   ```

   All downstream phases that refer to `## Project Context` should read it from `README.md`. The Project Context is the **north star** for the entire survey — it shapes which papers are included, what is extracted from each paper (Phase 3 Project Relevance), how the taxonomy is organized (Phase 4), and how the executive summary is framed (Phase 5).

7. **Must Include / Project Context consistency check (mandatory):** Procedure in `kb/context/literature-survey/literature-survey-conventions.md` § Phase 1 Must Include / Project Context Consistency Check. Only proceed to Phase 2 after the user has confirmed or revised the Must Include list following this check.

### Phase 2: Collect Seed Papers

Do **not** list all 200 papers at once.
First collect 15–25 seed papers, then gradually expand the list in Phase 3 by following related works from each paper.

For seed collection procedure (Awesome repo Step 0, web search Step 1, engineering blog list, target paper count assessment): see `kb/context/literature-survey/literature-survey-discovery.md`.

After seed collection, create two files:

1. `queue.md` — paper processing queue (format in `kb/context/literature-survey/literature-survey-conventions.md`)
2. `method-tracker.md` — methodology fundamentality tracking table (template in `kb/context/literature-survey/literature-survey-templates.md`; initially an empty table; filled in during Phase 3)

For Queue Depletion Strategy (when `To Process` drops below 50): see `kb/context/literature-survey/literature-survey-discovery.md`.

### Phase 3: Repeated Batch Processing + Queue Updating (`read-papers/` folder)

Maintain the queue at roughly 200 papers at all times.

Repeat the cycle of reading 20 papers, then updating the queue using related works from those papers.
Continue until all 200 papers are processed.

Batch procedure (20 papers at a time):

1. Take the top 20 highest-priority papers from the queue under `To Process`.
2. Split them into 4–5 groups and delegate them in parallel to subagents via the Agent tool.

   * Each subagent independently processes 4–5 papers.
   * The subagent prompt must include:

     * the list of papers to process (title, URL, priority)
     * output folder path (absolute path to `read-papers/`)
     * filename rules (the full "Filename Rules" section from `~/.claude/skills/paper-reader/SKILL.md`)
     * markdown file format (the full report template from `~/.claude/skills/paper-reader/references/report-template.md`)
     * PDF download instructions (full section in `kb/context/literature-survey/literature-survey-discovery.md`)
     * the `## Project Context` section from `README.md` (verbatim) — the subagent uses this to write the Project Relevance section for each paper
     * data to extract for `method-tracker` updates:
       baseline list, variant list, performance numbers, number of components
     * project relevance extraction instructions:
       after extracting the standard sections, write a `## Project Relevance` section assessing whether and how this paper's method/findings address the project's specific needs as described in the Project Context.
       If the paper does not meaningfully address the project's needs, prefix the section with: `**Low project relevance.** [reason]`.
     * instructions to extract new candidate papers:
       while reading each paper's Introduction and Related Works, collect all cited papers relevant to this batch topic and include them in the response
       Format:
       `[Paper Title] | [arXiv/URL if available] | [Relevance: Core/Related/Peripheral]`
       The main agent will decide whether they are duplicates in the queue, so the subagent should not filter them.
3. Wait for all subagents to complete.

Then collect two types of data from the subagent results:

**[`method-tracker` data]**

* the list of methods used as baselines in experiments (Experiments or Comparison section)
* methods mentioned in Related Work as "a variant of XX" or "an extension of XX"
* reported baseline performance numbers (which dataset, what score)
* how simple the method is (number of core components, number of added hyperparameters)

Update `method-tracker.md`:

* add newly appeared methods to the table
* if an existing method was used as a baseline in this paper, increment `"baseline mention count"` by 1
* if this paper is a derived variant of an existing method, increment the original method's `"derived variant count"` by 1
* add baseline performance numbers to the `"independent measured performance"` column

**[New candidate paper data]**

* merge all new paper candidate lists returned by subagents
* remove papers already present in the queue (`To Process`, `Done`, `Skipped`) or already in `read-papers/`
* pass the remaining candidates to Step 4

4. Add the new candidate papers collected in Step 3 to the queue:

   * check citation count and venue via Semantic Scholar or Google Scholar and assign priority (rules in `kb/context/literature-survey/literature-survey-priorities.md`)
   * if the paper proposes a method with high baseline mention count in `method-tracker`, raise its priority
   * add newly discovered papers to `To Process`
   * mark the source as `"Related Work harvest: [source paper filename]"`

5. Reorder the queue:

   * reorder the full `To Process` list by priority criteria
   * adjust rankings by applying the weights from `method-tracker`
   * if the queue exceeds 200 papers, move the lowest-priority items to `Skipped` to keep it at 200
   * if the queue falls below 50 papers, immediately run the Queue Depletion Strategy in `kb/context/literature-survey/literature-survey-discovery.md` to replenish it

6. Update `queue.md`:
   move the 20 completed papers to `Done`, and reflect the reordered queue.

7. Output a one-line progress update. Example:

```text
[Progress] Done 40 / Waiting 160 / Target 200 | Top tracker methods: MethodA(5), MethodB(4)
```

8. Move to the next batch.

For low-relevance papers, instead of generating an individual markdown file, leave a one-line memo in the queue's `Skipped` section.

Once all 200 papers are processed or the queue is fully exhausted, proceed to Phase 3.5.

### Phase 3.5: Finalize Method Tracker

See `kb/context/literature-survey/literature-survey-conventions.md` § Phase 3.5.

### Phase 3.7: Cross-Reference Mapping

After Phase 3.5 is complete, you **must** run this step. Do **not** start Phase 4 until this step is complete.
Full procedure and gating rule: see `kb/context/literature-survey/literature-survey-conventions.md` § Phase 3.7.

**Execution: dispatch to Gemini CLI** (via `cli-review` skill) with all files in `read-papers/` as the file list. Gemini reads the full corpus in one shot and returns the citation map. Do not delegate to a Claude subagent — at 200 papers, the corpus exceeds Claude's practical context for this step.

### Phase 4: Build Taxonomy

Note: Start this phase only after Phase 3.7 is fully complete.

**Execution: dispatch to Gemini CLI** (via `cli-review` skill). Pass the `## Project Context` from `README.md` and all files in `read-papers/`. Gemini reads the full paper corpus and returns a draft taxonomy (category names, paper assignments, rationale). Claude Lead reviews the draft, adjusts categories if needed, and writes the final taxonomy into `literature-review.md`.

Classify the collected papers into categories appropriate to the topic:

* read the `## Project Context` section from `README.md` before defining categories
* define categories around the core dimensions of the topic, informed by the project's specific needs and decision points — categories should map to aspects the project cares about, not just generic academic groupings
* place 5–15 papers in each category
* separate low-relevance papers into a `"References"` category

### Phase 5: Write Outputs and Evaluate Coverage

Note: Start this phase only after Phase 3.7 is fully complete.
Do not write the summary/review files while the reverse citation map is incomplete.

**Execution for File 2 and File 3: dispatch to Gemini CLI** (via `cli-review` skill). Pass `method-tracker.md`, `README.md` (for Project Context), and all files in `read-papers/`. Gemini drafts both `literature-review.md` and `executive-summary.md`. Claude Lead reviews the drafts, applies the coverage evaluation, and finalizes. Files 1 (`requirements.md`) and 4 (`method-tracker.md`) are updated by Claude Lead directly as they are already mostly complete.

Complete the following four files using the templates in `kb/context/literature-survey/literature-survey-templates.md`:

#### File 1: `requirements.md` (Requirements)

* created in Phase 1, updated here
* fill in the `"Summary of Actual Search Results"` section
* record total number of papers, number of categories, and main findings

#### File 2: `literature-review.md` (Main Review)

Full paper list and category-wise summary.
Each paper entry should include a link to the individual file in `read-papers/`.

#### File 3: `executive-summary.md` (Executive Summary)

A 2–3 page summary for decision-makers.

Every claim and recommendation must explicitly cite sources using the paper's full name.
Do not use abbreviations like `"the PoLL paper"`.
Use the format:
`"Author et al., full paper title, conference year"`

The executive summary must include a `"Most Fundamental Methods"` section.
Describe the top 5 methods based on the finalized `method-tracker` data.

The executive summary must include an **"Implications for [Use Case]"** section (or **"Recommendations"** if the Project Context describes a specific project). This section directly answers the key questions or decision points stated in the `## Project Context` section of `README.md`, citing specific papers. For a general academic survey, this section summarizes the most actionable takeaways for the stated audience.

#### File 4: `method-tracker.md` (Methodology Fundamentality Tracking)

* gradually filled during Phase 3
* template in `kb/context/literature-survey/literature-survey-templates.md`

#### Phase 5 Exit Condition: Coverage Evaluation

Full coverage-evaluation procedure (keyword coverage % + Project Context fitness check + actions when below 95%): see `kb/context/literature-survey/literature-survey-conventions.md` § Phase 5 Exit Condition.

## Final: Append to log.md

After Phase 5 completes (whether final completion or paused for user input), prepend a dated entry (newest on top) to `[topic-slug]/log.md`. Entry format and rules: see `kb/context/literature-survey/literature-survey-conventions.md` § Final Append to log.md. Use `<skill-name>` = `literature-survey` for the run header.

This section runs unconditionally at the end of every invocation, including resumes and reruns — it's the audit trail.
