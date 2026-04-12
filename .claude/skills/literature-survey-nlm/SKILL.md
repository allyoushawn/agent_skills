---
name: literature-survey-nlm
description: "NotebookLM-backed literature survey skill. Token-efficient alternative to literature-survey: uses NotebookLM notebook_query for per-paper analysis (~95% token savings). Invoke with /literature-survey-nlm <topic> [topic-slug]."
---

# Literature Survey (NotebookLM Edition)

Performs a structured literature survey on a given topic using NotebookLM for per-paper analysis. Saves all outputs under the paper reading repo.

This skill is a large-scale task. You must use the Agent tool and delegate it to a general-purpose agent. Do not handle it directly.

## Usage

`/literature-survey-nlm <topic> [topic-slug]`

- `<topic>`: topic to investigate (required).
  Examples: `"model cascading in ML systems"`, `"prevalence sampling for imbalanced classification"`
- `[topic-slug]`: folder name for the topic (optional). If omitted, it is automatically generated from the topic
  (lowercase, spaces → hyphens, special characters removed).
  Example: `"model cascading in ML systems"` → `model-cascading-in-ml-systems`

Outputs are saved under `[paper-reading-repo]/literature-survey/[topic-slug]/`.

Examples:
- `/literature-survey-nlm model cascading in ML systems`
  → `literature-survey/model-cascading-in-ml-systems/`
- `/literature-survey-nlm model cascading in ML systems model-cascading`
  → `literature-survey/model-cascading/`
- `/literature-survey-nlm backward compatible embeddings bce`
  → `literature-survey/bce/`

---

## Prerequisites (checked at the start of every run)

1. **NotebookLM reachability:** Call `notebook_list` (MCP tool from `notebooklm-mcp`). If it fails, print:

   > "NotebookLM MCP not reachable. Run `nlm login`, then call `refresh_auth`. See `~/.claude/skills/notebooklm/SKILL.md`."

   Abort the skill.

2. **Resolve paper-reading repo path:** Read `/path/to/works/for/you/knowledge_base/context/repos.md` and find the "Paper Reading Repo" entry. This is `[paper-reading-repo]`.

3. **Output root:** `[paper-reading-repo]/literature-survey/[topic-slug]/`

---

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

---

## Folder Structure

```text
[paper-reading-repo]/literature-survey/[topic-slug]/
├── requirements.md
├── notebooklm-state.md          ← NLM notebook state
├── literature-review.md
├── executive-summary.md
├── method-tracker.md
├── queue.md                     ← sole truth for nlm_source_id per paper
└── read-papers/
    └── YYYY_Venue_Method_Title.md
```

PDFs are excluded from git via `.gitignore` (`literature-survey/**/*.pdf`) — only markdown files are tracked.

---

## Phase 0: Detect Existing Outputs and Determine State (Resume Mode)

If the output folder already exists, run this phase first.
If the output folder does not exist, skip this phase and start from Phase 1.

### 0-1. Scan Existing Files

Check whether the following files exist in the output folder:

- `requirements.md`
- `queue.md`
- `notebooklm-state.md`
- `method-tracker.md`
- `literature-review.md`
- `executive-summary.md`
- `read-papers/` folder and the number of `.md` files inside it

If `notebooklm-state.md` is present, read the `notebook_id` and verify it via `notebook_get`. Report the NLM notebook status (notebook title, source count, whether it exists) alongside other resume state.

### 0-2. Determine Progress State

Determine the interrupted phase based on the following criteria:

| Condition | Interpretation | Resume From |
|-----------|---------------|-------------|
| Only requirements exists, no queue | Phase 1 complete, Phase 2 not started | Start from Phase 2 |
| Queue exists, but `read-papers/` is empty or missing | Phase 2 complete, Phase 3 not started | Start from Phase 3 |
| Queue exists, and `read-papers/` contains `.md` files | Phase 3 in progress | Resume Phase 3 (see 0-3 below) |
| `method-tracker` contains a "Top Method Analysis" section | Phase 3.5 complete | Start from Phase 3.7 |
| `read-papers/` `.md` files contain a filled "Reverse Citation Map" table | Phase 3.7 complete | Start from Phase 4 |
| `literature-review` exists, `executive-summary` does not | Phase 4 complete | Start from Phase 5 |
| `executive-summary` exists | Phase 5 complete or in progress | Start with coverage evaluation |

### 0-3. Resume Phase 3 (If Batch Processing Was Interrupted)

If Phase 3 was in progress, determine the exact status:

1. Read `queue.md` and count the number of papers in the "Done" section.
2. Count the number of `.md` files in the `read-papers/` folder.
3. Check the number of remaining papers in the "To Process" section.
4. Report the status to the user:

```text
[Resume] Existing progress detected:
   - Processed: X papers
   - read-papers/ files: Y
   - Remaining: Z papers
   - Target: N papers
   - NLM notebook: [notebook_id] — [source count] sources loaded
   Resuming Phase 3 batch processing.
```

5. Resume Phase 3 batch processing starting from the top papers in the "To Process" list.

### 0-4. User Confirmation

Show the user the result of the state determination and ask whether to continue.

If the user requests "start from scratch," either suggest a new folder name while preserving the existing folder, or reset the existing files with user approval.

---

## Phase 1: Preparation and Search Strategy Setup

1. Create the output folder and the `read-papers/` subfolder if they do not exist.
2. Extract 3–6 core keywords from the topic.
3. Decide the search strategy based on the criteria below.
4. Once the search strategy is decided, immediately create `requirements.md`.
   This file must record the user-requested topic, extracted keywords, selected venues/blogs, search queries, and survey scope constraints.
5. After creating the requirements file, show its contents to the user and get confirmation.
   If the user requests revisions, reflect them and confirm again.
   Only after user approval may you proceed to Phase 2.

6. **Survey purpose prompt (mandatory):** Ask the user:

   > "What is the intended use of this survey?
   > (a) If for a specific project: describe what the project is, how the survey output will be used, what 'relevant' means in your project's terms (e.g., 'a method is useful if its output can serve as continuous training labels'), and any paper types that are especially valuable even if not top-venue (e.g., industry papers from the same domain).
   > (b) If a general academic survey: describe the target audience and what decisions or understanding the survey should support."

   Append a `## Project Context` section to `requirements.md` with the user's response. This section is always present — for a general survey it captures audience and goals; for a project-specific survey it captures the concrete framing.

   This section is the **north star** for the entire survey. It shapes not just which papers are included, but what is extracted from each paper (Phase 3 Query 3), how findings are synthesized (Phase 4 Queries 6–7), and how the executive summary is framed (Phase 5).

- Core keyword groups: different phrasings of the topic, related concepts
- Most relevant venue list (selected from the list below)
- Engineering blogs to search

**Relevant conferences/journals by area:**

- General ML: NeurIPS, ICML, ICLR, MLSys
- Systems: OSDI, SOSP, EuroSys, VLDB, SIGMOD
- Computer Vision: CVPR, ICCV, ECCV
- NLP: ACL, EMNLP, NAACL
- Recommender Systems: RecSys, WWW, KDD
- Software Engineering: ICSE, FSE, ASE
- Signal Processing: ICASSP, Interspeech

### Paper Prioritization Criteria

When processing discovered papers, use the following priority order. Higher-priority papers are analyzed in more depth in Phase 3 (`read-papers/`), while lower-priority ones are mentioned only briefly.

#### Topic Relevance (Highest-Priority Filter)

This takes precedence over venue or citation count. Papers with low relevance should be ranked lower even if they are from top venues.

Relevance levels (judge by title, abstract, and introduction):

- **Core**: directly addresses the survey topic. The keywords specified in `requirements` are central to the paper's contribution.
  → no demotion (default)
- **Related**: adjacent to the topic but does not directly address it. Useful for background understanding or comparison.
  → demote by one level from priorities 1/2/3/4 below
- **Peripheral**: only indirectly connected to the topic.
  → demote by two levels from priorities 1/2/3/4 below. If demotion pushes it below priority 3, treat it as "excluded."

When adding a paper to the queue, mark relevance as `[Core/Related/Peripheral]`. Later, during batch processing, reevaluate based on the actual abstract and adjust priority as needed.

#### Base Priority by Venue / Institution

**Priority 1 — highest priority:**

- Papers published at NeurIPS, ICML, ICLR
- Papers from venues with Google Scholar h5-index ≥ 100
  (e.g. NeurIPS, ICML, ICLR, CVPR, ACL, EMNLP)
- Papers authored by researchers from big tech organizations such as Google, Meta/FAIR, Microsoft Research, DeepMind, Apple, Amazon, OpenAI, etc.

**Priority 2 — next to process:**

- Papers published at CVPR, KDD
- Papers from venues with Google Scholar h5-index ≥ 100 but not already included in Priority 1
- Papers with 100+ citations, regardless of venue

**Priority 3 — supplementary materials:**

- Papers from major venues such as ICCV, ECCV, WWW, RecSys, EMNLP, NAACL, SIGMOD, VLDB
- arXiv preprints with prominent authors or big-tech affiliations and 50+ citations

**Priority 4 — reference-only**
(If any of the following applies, force-assign Priority 4):

- Papers from other venues or low-citation arXiv preprints
- Not published at a top conference (Priority 1 venues) and not affiliated with big tech / well-known research institutions
- Papers authored by researchers from Chinese universities without company affiliation
  (due to reproducibility concerns)
- However, if the paper is published in a conference venue and has 200+ citations, it may be promoted to Priority 3

For each discovered paper, check citation counts via Semantic Scholar or Google Scholar and determine priority.

**Secondary condition by year:**

- Prefer recent papers (within the last 5 years). Within the same priority level, process newer papers first.
- Papers older than 5 years should only be included if they have significantly high citation counts (roughly 500+, or clearly above the field average).
- However, seminal works such as the original ViT paper should be included regardless of year/citations.

### Method Fundamentality Weight

Separately from the priority above, assign the following weights based on data accumulated in `method-tracker` during Phase 3.

A high weight means the paper should be processed earlier within the same priority tier. It may also be promoted to a higher priority tier (e.g. a Priority 3 paper may be promoted to Priority 2 if its weight is +3).

- **+3**: proposes a method used as a baseline by 5 or more other papers
- **+2**: paper has 3 or more derived variants
- **+2**: consistent high performance reported across 3 or more independent papers
- **+1**: achieves strong performance with a simple structure (number of components ≤ 3, number of hyperparameters ≤ 2)
- **-1**: complex structure (number of components ≥ 6 or number of hyperparameters ≥ 5) and described by other papers as difficult to reproduce

This weight is applied dynamically during Phase 3 through `method-tracker` updates. Whenever the queue is reordered, reflect these weights in the updated ordering.

---

## Phase 2: Collect Seed Papers

Do **not** list all 200 papers at once. First collect 15–25 seed papers, then gradually expand the list in Phase 3 by following related works from each paper.

### Step 0 (Always First): Pull and Scan the Local Awesome Recsys Repo

Before doing any web search, pull the latest snapshot of the local curated paper collection and scan it for relevant papers.

1. Pull the latest master branch:
   ```
   git -C [awesome-repo-path] pull origin master
   ```
   Look up `[awesome-repo-path]` from `/path/to/works/for/you/knowledge_base/context/repos.md` ("Awesome Deep Learning Papers" entry).

2. List all PDF files across all category folders.

3. For each PDF whose filename matches the survey topic keywords:
   - Parse the filename: `YYYY (Company) (Venue) [MethodName] Paper Title.pdf`
   - Extract: year, venue, method name, title, company affiliation
   - Papers prefixed with `**` → assign Priority 1 candidate
   - Papers prefixed with `*` → assign Priority 2 candidate
   - Papers with no prefix → assign Priority 3 candidate
   - Adjust priority further using the topic relevance rules (Core/Related/Peripheral)

4. Add matched papers to the seed list. Record source as `"local-awesome-repo: [folder]/[filename]"`. Since PDFs are already downloaded locally, note the local PDF path.

5. If 15+ relevant papers are found in the local repo, you may proceed to Phase 2 Step 2 (NLM Discovery) with those as seeds without web search. If fewer than 15, continue to Step 1 to supplement.

### Step 1: Web Search for Additional Seeds

Collect remaining seed papers via web search. Use the WebSearch and WebFetch tools actively. Combine multiple search engines and academic databases to discover as many papers as possible.

**Search query patterns:**

- `site:arxiv.org [keyword]`
- `site:proceedings.mlr.press [keyword]`
- `site:proceedings.neurips.cc [keyword]`
- `site:openreview.net [keyword]`
- `[keyword] site:dl.acm.org`
- `[keyword] NeurIPS OR ICML OR ICLR 2020 2021 2022 2023 2024`

**Semantic Scholar API** (optimal for paper metadata + citation count collection):
- `https://api.semanticscholar.org/graph/v1/paper/search?query=[keyword]&fields=title,year,venue,citationCount,externalIds,authors`

**Papers With Code** (useful for tracking the latest SOTA):
- `https://paperswithcode.com/search?q_meta=&q_type=&q=[keyword]`

**Engineering blog search** (select those most relevant to the topic):

Big Tech research blogs:
- `site:research.google [keyword]`
- `site:ai.googleblog.com [keyword]`
- `site:deepmind.google [keyword]`
- `site:research.facebook.com [keyword]`
- `site:microsoft.com/en-us/research [keyword]`
- `site:apple.com/research [keyword]`
- `site:machinelearning.apple.com [keyword]`
- `site:amazon.science [keyword]`
- `site:openai.com/research [keyword]`
- `site:anthropic.com/research [keyword]`

Big Tech engineering blogs:
- `site:engineering.fb.com [keyword]`
- `site:netflixtechblog.com [keyword]`
- `site:eng.uber.com [keyword]`
- `site:engineering.linkedin.com [keyword]`
- `site:eng.snap.com [keyword]`
- `site:research.bytedance.com [keyword]`
- `site:engineering.atspotify.com [keyword]`
- `site:doordash.engineering [keyword]`
- `site:eng.lyft.com [keyword]`
- `site:medium.com/airbnb-engineering [keyword]`
- `site:medium.com/pinterest-engineering [keyword]`
- `site:medium.com/twitter-engineering [keyword]`
- `site:shopify.engineering [keyword]`
- `site:stripe.com/blog/engineering [keyword]`

Asian Big Tech:
- `site:d2.naver.com [keyword]`
- `site:tech.kakao.com [keyword]`
- `site:engineering.linecorp.com [keyword]`
- `site:medium.com/coupang-engineering [keyword]`

ML/AI-specialized:
- `site:huggingface.co/blog [keyword]`
- `site:wandb.ai/fully-connected [keyword]`

### Step 2 (NEW): NLM Research Discovery

1. Create the topic notebook: `notebook_create(title="[topic-slug]")` → save the returned `notebook_id` to `notebooklm-state.md`.
2. Call `research_start(notebook_id=<id>, query="<topic keywords>", source="web", mode="deep")` → record the returned `task_id`.
3. Poll `research_status(notebook_id=<id>, task_id=<id>, compact=True)` until status = complete. Do NOT use `compact=False` during polling.
4. Make one final `research_status` call with `compact=False` to review all hits.
5. Select relevant papers → call `research_import(notebook_id=<id>, task_id=<id>, source_indices=[...])`.
6. Record the returned source IDs for each imported paper.

### Step 3: Deduplicate and Build queue.md

Union all sources from Steps 0, 1, and 2. Deduplicate by title. Apply all priority and relevance rules from Phase 1 verbatim.

**`queue.md` format** — extends the standard format with an `nlm` column:

```markdown
# [Topic] Paper Queue

## To Process
- [Title or URL] | [Source] | [Relevance: Core/Related/Peripheral] | [Priority 1/2/3/4] | nlm:pending
- [Title or URL] | [Source] | [Relevance] | [Priority] | nlm:<source_id>   ← already in NLM
- [Title or URL] | [Source] | [Relevance] | [Priority] | nlm:failed:<reason>

## Done
- [filename.md] | [Title] | [processing date] | nlm:<source_id>

## Skipped
- [Title] | [reason]
```

After seed collection, assess whether the target number of papers (200) is appropriate for the topic. If 200 seems excessive, stop at Phase 2 and confirm the target paper count with the user. Proceed with later phases using the approved target count.

Also create an empty `method-tracker.md` (see the template in the original `literature-survey` skill at `~/.claude/skills/literature-survey/SKILL.md`).

---

## Phase 3: Per-Paper Analysis via NLM

This is the token-saving core. Instead of reading PDFs into Claude's context, Claude fires 2 structured queries per paper to NotebookLM.

**Delegation model:** Process papers in batches of 3–5. Each batch is delegated to a fresh general-purpose subagent via the Agent tool to prevent context bloat. The brief to each subagent must include: `notebook_id`, the batch paper list with source IDs and URLs, and the output folder path. After the subagent writes the batch outputs to disk, a new subagent is spawned for the next batch.

For each paper in the batch:

### 3-A: URL Normalization

Before ingesting, normalize the URL:

- **arXiv abstract URL** (`arxiv.org/abs/<ID>` or `arxiv.org/abs/<ID>v<N>`): convert to PDF URL → `https://arxiv.org/pdf/<ID>.pdf`
- **Paywalled publisher URL** (IEEE Xplore `ieeexplore.ieee.org`, ACM DL `dl.acm.org`, Springer `link.springer.com`, Elsevier `sciencedirect.com`): mark as `nlm:failed:paywall` in queue.md, add to Skipped section, skip this paper entirely.

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

The batch subagent **dynamically formulates** this query from the `## Project Context` section in `requirements.md`. It must probe whether and how this paper's method/findings address the project's specific needs — referencing the concrete framing (e.g., label type, noise model, downstream goal, audience questions), not just repeating the topic generically.

This query runs for **all** papers unconditionally. If the answer indicates the paper does not address the project need, that is a useful signal — it flags a retrieval-phase relevance mismatch, not a query design problem.

**NLM refusal handling:** After receiving all three responses, scan for refusal language: phrases like "I cannot answer", "not mentioned in the source", "I don't have enough information", or similar. Replace any such section's content with: `Not specified in source.` Do not copy NLM refusal boilerplate into the markdown output.

### 3-D: Assemble Markdown

Assemble the three Q&A responses into the standard `read-papers/` markdown file.

Follow the **filename rules** and **report template** from `/path/to/works/for/you/.claude/skills/paper-reader/SKILL.md` exactly. Do not copy the template into this skill — read it at runtime and apply it.

When in `read-papers/` mode (as opposed to standalone paper-reader use), leave the Reverse Citation Map section blank — it is filled in during Phase 3.7.

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

**Note on cross-paper baseline question:** The "is this paper's method used as a baseline by others?" question cannot be answered per-paper because it requires seeing the full notebook. This is addressed in Phase 4-B (Query 5).

### Queue Depletion Strategy

If the queue risks running out before reaching the target paper count, expand it in the following order. Always start from Step 0.

**Step 0 (Highest Priority): Harvest Citations from Already Written Markdowns**

Before expanding into adjacent fields, inspect all markdown files in `read-papers/` and harvest new candidate papers.

1. Get the full list of `.md` files in `read-papers/`.
2. Read the Related Works and Introduction sections of each file.
3. Extract all cited paper titles from those sections.
4. Exclude papers already present in the queue (`To Process`, `Done`, or `Skipped`) or already in `read-papers/`.
5. For remaining candidates, check citation count and venue on Semantic Scholar and assign priorities.
6. Re-read the survey scope in `requirements.md` and prioritize papers matching "Must include" criteria; skip papers falling under "Exclude."
7. Add new candidates to `To Process`. Mark source as `"Related Work harvest: [source filename]"`.
8. Reorder the queue by priority + method-tracker weights + requirements fit.

If this yields enough papers (`To Process` > 50), do not continue to adjacent-field expansion.

**Step 1 and Beyond: Expand into Adjacent Fields**

If still insufficient after Step 0:
1. Explore subtopics or specific methodologies within the current topic
2. Explore papers that address the same problem in different domains/modalities
3. Baseline/foundation methodology papers related to the topic
4. Papers that apply or critique the topic

Record expansion details in the "Survey Scope and Constraints" section of `requirements.md`. Mark source as `"Adjacent-field expansion: [reason]"`.

**Queue health rule:** If `To Process` drops below 50, immediately start expansion again from Step 0. Do not wait.

---

## Phase 3.5: Finalize Method Tracker

After Phase 3 ends, finalize `method-tracker.md`:

- Sort the table by descending "baseline mention count"
- Compute simplicity score and performance consistency score, and add a "fundamentality composite score" column
- For the top 10 methods, add a one-line explanation of "why this method is fundamental"

This data is used in the "Most Fundamental Methods" section of the Phase 5 executive summary.

---

## Phase 3.7: Cross-Reference Mapping

After Phase 3.5 is complete, you **must** run this step. Do **not** start Phase 4 until this step is complete.

**Purpose:** Record how papers in `read-papers/` mention and evaluate each other inside the individual markdown files. This allows each paper's markdown file to contain both "how I view other papers" and "how other papers view me."

**Procedure:**

1. Get the list of all `.md` files in the `read-papers/` folder (exclude PDF files).
2. For each paper A's markdown file, read the Introduction and Related Works sections and extract all sentences that mention other papers. Extraction criteria:
   - Sentences that directly mention another paper's title or author name
   - Evaluative mentions such as: `"[X] proposed Y"`, `"Unlike [X], we ..."`, `"Extending the method of [X] ..."`
   - Sentences identifying specific papers as examples of "limitations of prior work"
3. Check whether the mentioned paper exists as a markdown file in `read-papers/`. If yes, add or update the following section in that paper B's markdown file:

```markdown
## Papers That Mention This Paper (Reverse Citation Map)

| Mentioning Paper | Mention Context | Summary of Original Wording |
|------------|----------|----------|
| [Paper A filename.md](./paperAfilename.md) | [which section mentioned it: Related Work / Introduction / Experiments] | [one-line summary of how it was evaluated: "used as a baseline", "pointed out limitations", "starting point of our method", "reported lower performance", etc.] |
| ... | ... | ... |
```

4. Complete this for all markdown files in `read-papers/`. If parallelization is possible, split into 20-paper groups and delegate to subagents via the Agent tool.
5. After completion, output a one-line summary. Example:
   ```text
   [Phase 3.7 complete] Reverse citation map created: X total papers, Y reverse-citation relations recorded
   ```

Only after this step is fully complete may you proceed to Phase 4.

---

## Phase 4: Literature Review (NLM-First Hybrid Synthesis)

### 4-A: NLM Generates Core Draft

Query the full notebook with no `source_ids` filter (all papers). Use these 5 queries as building blocks for `literature-review.md`:

1. "What are the dominant methodological approaches across all papers in this notebook? For each approach, summarize it and list representative papers."
2. "What are the most common evaluation datasets and benchmarks used across these papers? Which papers use which datasets?"
3. "What open problems or research gaps are identified most frequently across these papers?"
4. "Which papers appear to be the most foundational — cited by or built upon by many others in this notebook? List them with brief explanations."
5. "Is any paper's method used as a direct baseline by other papers in this notebook? Map method name → list of papers that use it as a baseline."

**Queries 6–7 (project-specific synthesis)** — dynamically formulated by the Phase 4 subagent from the `## Project Context` section in `requirements.md`. The subagent reads the Project Context and writes 1–2 cross-paper queries (no `source_ids` filter) that synthesize the notebook's papers through the lens of the project's specific needs. Examples: "Which methods in this notebook are applicable when labels are [project-specific label type]?" or "What does the collective evidence say about [project-specific concern]?" These become additional building blocks for `literature-review.md`.

### 4-B: Claude Structures into literature-review.md

Claude takes NLM's 5–7 responses and structures them into `literature-review.md` following the original skill's format (see `~/.claude/skills/literature-survey/SKILL.md` — "Main Review File Template"). The project-specific synthesis (Queries 6–7) feeds into a dedicated section of the review. Claude does **not** re-read all individual per-paper markdowns at this step.

### 4-C: Conflict Check

Claude spot-checks NLM's cross-paper claims against the per-paper markdowns already written (read only the specific ones relevant to a claimed conflict). If a conflict is found: flag it, re-query NLM with a follow-up question, and resolve before finalizing.

---

## Phase 5: Write Outputs and Evaluate Coverage

Note: Start this phase only after Phase 3.7 is fully complete.

Complete the following files:

#### File 1: `requirements.md`

- Created in Phase 1, updated here.
- Fill in the "Summary of Actual Search Results" section.
- Record total number of papers, number of categories, and main findings.

#### File 2: `literature-review.md`

Full paper list and category-wise summary. Each paper entry should include a link to the individual file in `read-papers/`. See the "Main Review File Template" in `~/.claude/skills/literature-survey/SKILL.md`.

#### File 3: `executive-summary.md`

A 2–3 page summary for decision-makers. See the "Executive Summary File Template" in `~/.claude/skills/literature-survey/SKILL.md`.

Every claim and recommendation must explicitly cite sources using the paper's full name. Do not use abbreviations like "the PoLL paper". Use the format: `"Author et al., full paper title, conference year"`.

The executive summary must include a "Most Fundamental Methods" section describing the top 5 methods from the finalized `method-tracker`.

The executive summary must include an **"Implications for [Use Case]"** section (or **"Recommendations"** if the Project Context describes a specific project). This section directly answers the key questions or decision points stated in the `## Project Context` section of `requirements.md`, citing specific papers. For a general academic survey, this section summarizes the most actionable takeaways for the stated audience.

**Optional NLM sanity check:** After drafting `executive-summary.md`, query NLM with no `source_ids` filter: "Summarize the state of the field based on all sources in this notebook." Compare against the draft and flag any notable discrepancies.

#### File 4: `method-tracker.md`

Gradually filled during Phase 3, finalized in Phase 3.5. See the "Method Tracker File Template" in `~/.claude/skills/literature-survey/SKILL.md`.

#### Phase 5 Exit Condition: Coverage Evaluation

After drafting File 2 and File 3, before stopping, evaluate coverage:

1. List all items specified in `requirements.md` under "Request", "Must Include", and "Core Keywords".
2. Evaluate how well `literature-review.md` and `executive-summary.md` cover each item. The criterion for "covered" is whether enough evidence exists for decision-making.
3. Compute overall coverage as a percentage. Example: `"18 covered out of 20 requirement items = 90%"`

**Actions based on coverage:**

- If coverage ≥ 95% and the executive summary alone is sufficient for decision-making: final completion. Report to user.
- If coverage < 95% or some items are too thinly covered:
  1. Specify which requirement items are lacking
  2. Collect an additional 100 papers to fill those gaps
  3. Add them to the queue and repeat from Phase 3
  4. After processing the additional 100 papers, rerun Phases 3.5 → 3.7 → 4 → 5
  5. Reevaluate coverage and stop only once coverage reaches ≥ 95%
- Continue this loop until coverage ≥ 95%.
- However, if the total cumulative number of papers exceeds 500, report the status to the user and confirm whether to continue.

---

## Writing Principles

Follow the "Writing Notes and Cautions" section from `~/.claude/skills/paper-reader/SKILL.md` as the default principles.

Additional principles for this skill:

- Target paper count is 100–300 (default 200). If insufficient, run the adjacent-field expansion strategy. If excessive, eliminate lower-priority papers according to the priority criteria.
- Analyze Priority 1–2 papers deeply; handle Priority 3–4 papers with brief summaries.
- Every claim and recommendation in `executive-summary.md` must cite the paper's full name. No abbreviations. Format: `"author et al., full paper title, conference/journal year"`.
- Before starting the survey, read the current project's `CLAUDE.md` and the upper folder's `CLAUDE.md` to understand the user context.

## Accessibility Principle

Inclusion rule for papers — only include papers whose full text is freely accessible.

Accepted free-access sources:
- `arxiv.org` (preprint or conference version)
- `openreview.net` (ICLR, NeurIPS, and other OpenReview-based conferences)
- Publicly available PDFs on official conference sites (`proceedings.mlr.press`, `proceedings.neurips.cc`, `aaai.org`, `aclanthology.org`, etc.)
- "Open Access PDF" link available on Semantic Scholar / Papers With Code
- PDF publicly available on the author's homepage or institution page

Exclude papers whose full text is inaccessible without payment on ACM DL, IEEE Xplore, Springer, Elsevier, etc. In the queue's `Skipped` section, record the reason as: `paid access only - no free version available`.

How to check: search the paper on Semantic Scholar and check whether an "Open Access PDF" button exists; if not, search `site:arxiv.org [title]` or `site:openreview.net [title]`.

---

## References Used During Execution

- **NotebookLM tools and usage patterns:** `~/.claude/skills/notebooklm/SKILL.md`
- **Filename rules + report template:** `~/.claude/skills/paper-reader/SKILL.md`
- **Repo path lookup:** `~/.claude/skills/fetch-repo-path/SKILL.md` (or directly: `/path/to/works/for/you/knowledge_base/context/repos.md`)
- **Resume logic, Phase 3.5/3.7, priority rules, venue lists, output file templates:** `~/.claude/skills/literature-survey/SKILL.md`
