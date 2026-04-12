---
name: literature-survey
description: "Literature Survey Skill - performs a structured literature survey for a given topic and saves outputs under the paper reading repo's literature-survey/[topic]/ folder. Invoke with /literature-survey <topic> [topic-slug]."
---

# Literature Survey Skill

Performs a structured literature survey on a given topic and saves all outputs under the paper reading repo.

**Before writing any files**, look up the paper reading repo path using the `fetch-repo-path` skill:
→ Read `/path/to/works/for/you/knowledge_base/context/repos.md` and find the "Paper Reading Repo" entry.

Output root: `[paper-reading-repo]/literature-survey/[topic-slug]/`

PDFs are downloaded into each topic's `read-papers/` folder alongside their markdown files.
PDFs are excluded from git via `.gitignore` (`literature-survey/**/*.pdf`) — only markdown files are tracked.

This skill is a large-scale task. You must use the Agent tool and delegate it to a general-purpose agent. Do not handle it directly.

## Usage

`/literature-survey <topic> [topic-slug]`

- `<topic>`: topic to investigate (required).
  Examples: `"model cascading in ML systems"`, `"prevalence sampling for imbalanced classification"`
- `[topic-slug]`: folder name for the topic (optional). If omitted, it is automatically generated from the topic
  (lowercase, spaces → hyphens, special characters removed).
  Example: `"model cascading in ML systems"` → `model-cascading-in-ml-systems`

Outputs are saved under `/path/works/for/you/paper_reading_repo/literature-survey/[topic-slug]/`.

Examples:
- `/literature-survey model cascading in ML systems`
  → `literature-survey/model-cascading-in-ml-systems/`
- `/literature-survey model cascading in ML systems model-cascading`
  → `literature-survey/model-cascading/`
- `/literature-survey backward compatible embeddings bce`
  → `literature-survey/bce/`

### Resume Mode

If existing outputs are already present in `literature-survey/[topic-slug]/`, the skill automatically enters resume mode.

It does not start over. Instead, it inspects the existing progress and resumes from where it stopped.

Conditions for entering resume mode:
- the `literature-survey/[topic-slug]/` folder already exists, and
- at least one of the following exists:
  - `requirements.md`
  - `queue.md`
  - `literature-review.md`

What resume mode does **not** do:
- It does not overwrite or reset existing files.
- It does not rerun already completed phases from scratch.
- It does not reprocess papers that already exist in `read-papers/`.

## Folder Structure

```text
[paper-reading-repo]/literature-survey/
├── [topic-A]/
│   ├── requirements.md                # Survey requirements and search strategy
│   ├── literature-review.md           # Full paper list + summary review
│   ├── executive-summary.md           # Summary for decision-makers
│   ├── method-tracker.md              # Method fundamentality tracking (accumulated from PDFs)
│   ├── queue.md                       # Paper processing queue
│   └── read-papers/                   # Detailed analysis of individual papers
│       ├── 2024_NeurIPS_MethodName_Paper-Title.md
│       ├── 2024_NeurIPS_MethodName_Paper-Title.pdf
│       └── ...
├── [topic-B]/
│   ├── requirements.md
│   ├── ...
│   └── read-papers/
└── ...
```

Since the topic folder name itself represents the topic, filenames inside the folder should not include a topic prefix.

## File Naming Rules

**Follow the "Filename Rules" and "How to Find Author Affiliations" sections from the `paper-reader` skill exactly as-is.**
→ Reference: `/path/to/works/for/you/.claude/skills/paper-reader/SKILL.md`

When running, read that file and apply the latest rules.

## Execution Order

### Phase 0: Detect Existing Outputs and Determine State (Resume Mode)

If the output folder already exists, run this phase first.
If the output folder does not exist, skip this phase and start from Phase 1.

#### 0-1. Scan Existing Files

Check whether the following files exist in the output folder:

* `requirements.md`
* `queue.md`
* `method-tracker.md`
* `literature-review.md`
* `executive-summary.md`
* `read-papers/` folder and the number of `.md` files inside it

#### 0-2. Determine Progress State

Determine the interrupted phase based on the following criteria:

| Condition                                                                | Interpretation                        | Resume From                    |
| ------------------------------------------------------------------------ | ------------------------------------- | ------------------------------ |
| Only requirements exists, no queue                                       | Phase 1 complete, Phase 2 not started | Start from Phase 2             |
| Queue exists, but `read-papers/` is empty or missing                     | Phase 2 complete, Phase 3 not started | Start from Phase 3             |
| Queue exists, and `read-papers/` contains `.md` files                    | Phase 3 in progress                   | Resume Phase 3 (see 0-3 below) |
| `method-tracker` contains a "Top Method Analysis" section                | Phase 3.5 complete                    | Start from Phase 3.7           |
| `read-papers/` `.md` files contain a filled "Reverse Citation Map" table | Phase 3.7 complete                    | Start from Phase 4             |
| `literature-review` exists, `executive-summary` does not                 | Phase 4 complete                      | Start from Phase 5             |
| `executive-summary` exists                                               | Phase 5 complete or in progress       | Start with coverage evaluation |

#### 0-3. Resume Phase 3 (If Batch Processing Was Interrupted)

If Phase 3 was in progress, determine the exact status using the following steps:

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
   Resuming Phase 3 batch processing.
```

5. Resume Phase 3 batch processing starting from the top 20 papers in the "To Process" list.

#### 0-4. User Confirmation

Show the user the result of the state determination and ask whether to continue.

If the user requests "start from scratch," either suggest a new folder name while preserving the existing folder, or reset the existing files with user approval.

---

### Phase 1: Preparation and Search Strategy Setup

1. Create the output folder and the `read-papers/` subfolder if they do not exist.
2. Extract 3–6 core keywords from the topic.
3. Decide the search strategy based on the criteria below.
4. Once the search strategy is decided, immediately create `requirements.md`.
   This file must record the user-requested topic, extracted keywords, selected venues/blogs, search queries, and survey scope constraints.
5. After creating the requirements file, you must show its contents to the user and get confirmation.
   If the user requests revisions, reflect them and confirm again.
   Only after user approval may you proceed to Phase 2.

6. **Survey purpose prompt (mandatory):** Ask the user:

   > "What is the intended use of this survey?
   > (a) If for a specific project: describe what the project is, how the survey output will be used, what 'relevant' means in your project's terms (e.g., 'a method is useful if its output can serve as continuous training labels'), and any paper types that are especially valuable even if not top-venue (e.g., industry papers from the same domain).
   > (b) If a general academic survey: describe the target audience and what decisions or understanding the survey should support."

   Append a `## Project Context` section to `requirements.md` with the user's response. This section is always present — for a general survey it captures audience and goals; for a project-specific survey it captures the concrete framing.

   This section is the **north star** for the entire survey. It shapes not just which papers are included, but what is extracted from each paper (Phase 3 Project Relevance), how the taxonomy is organized (Phase 4), and how the executive summary is framed (Phase 5).

* Core keyword groups: different phrasings of the topic, related concepts
* Most relevant venue list (selected from the list below)
* Engineering blogs to search

Relevant conferences/journals by area:

* General ML: NeurIPS, ICML, ICLR, MLSys
* Systems: OSDI, SOSP, EuroSys, VLDB, SIGMOD
* Computer Vision: CVPR, ICCV, ECCV
* NLP: ACL, EMNLP, NAACL
* Recommender Systems: RecSys, WWW, KDD
* Software Engineering: ICSE, FSE, ASE
* Signal Processing: ICASSP, Interspeech

### Paper Prioritization Criteria

When processing discovered papers, use the following priority order.
Higher-priority papers are analyzed in more depth in Phase 3 (`read-papers/`), while lower-priority ones are mentioned only briefly.

#### Topic Relevance (Highest-Priority Filter)

This takes precedence over venue or citation count.
Papers with low relevance should be ranked lower even if they are from top venues.

Relevance levels (judge by title, abstract, and introduction):

* **Core**: directly addresses the survey topic. The keywords specified in `requirements` are central to the paper's contribution.
  → no demotion (default)
* **Related**: adjacent to the topic but does not directly address it. Useful for background understanding or comparison.
  → demote by one level from priorities 1/2/3/4 below
* **Peripheral**: only indirectly connected to the topic.
  → demote by two levels from priorities 1/2/3/4 below. If demotion pushes it below priority 3, treat it as "excluded."

When adding a paper to the queue, mark relevance as `[Core/Related/Peripheral]`.
Later, during batch processing, reevaluate based on the actual PDF/abstract and adjust priority as needed.

#### Base Priority by Venue / Institution

**Priority 1 — highest priority:**

* Papers published at NeurIPS, ICML, ICLR
* Papers from venues with Google Scholar h5-index ≥ 100
  (e.g. NeurIPS, ICML, ICLR, CVPR, ACL, EMNLP)
* Papers authored by researchers from big tech organizations such as Google, Meta/FAIR, Microsoft Research, DeepMind, Apple, Amazon, OpenAI, etc.

**Priority 2 — next to process:**

* Papers published at CVPR, KDD
* Papers from venues with Google Scholar h5-index ≥ 100 but not already included in Priority 1
* Papers with 100+ citations, regardless of venue

**Priority 3 — supplementary materials:**

* Papers from major venues such as ICCV, ECCV, WWW, RecSys, EMNLP, NAACL, SIGMOD, VLDB
* arXiv preprints with prominent authors or big-tech affiliations and 50+ citations

**Priority 4 — reference-only**
(If any of the following applies, force-assign Priority 4):

* Papers from other venues or low-citation arXiv preprints
* Not published at a top conference (Priority 1 venues) and not affiliated with big tech / well-known research institutions
* Papers authored by researchers from Chinese universities without company affiliation
  (due to reproducibility concerns)
* However, if the paper is published in a conference venue and has 200+ citations, it may be promoted to Priority 3

For each discovered paper, check citation counts via Semantic Scholar or Google Scholar and determine priority.

Secondary condition by year:

* Prefer recent papers (within the last 5 years). Within the same priority level, process newer papers first.
* Papers older than 5 years should only be included if they have significantly high citation counts
  (roughly 500+, or clearly above the field average).
* However, seminal works such as the original ViT paper should be included regardless of year/citations.

### Method Fundamentality Weight

Separately from the priority above, assign the following weights based on data accumulated in `method-tracker` during Phase 3.

A high weight means the paper should be processed earlier within the same priority tier.
It may also be promoted to a higher priority tier
(e.g. a Priority 3 paper may be promoted to Priority 2 if its weight is +3).

* **+3**: proposes a method used as a baseline by 5 or more other papers
* **+2**: paper has 3 or more derived variants
* **+2**: consistent high performance reported across 3 or more independent papers
* **+1**: achieves strong performance with a simple structure
  (number of components ≤ 3, number of hyperparameters ≤ 2)
* **-1**: complex structure
  (number of components ≥ 6 or number of hyperparameters ≥ 5)
  and described by other papers as difficult to reproduce

This weight is applied dynamically during Phase 3 through `method-tracker` updates.
Whenever the queue is reordered, reflect these weights in the updated ordering.

---

### Phase 2: Collect Seed Papers

Do **not** list all 200 papers at once.
First collect 15–25 seed papers, then gradually expand the list in Phase 3 by following related works from each paper.

#### Step 0 (Always First): Pull and Scan the Local Awesome Recsys Repo

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

4. Add matched papers to the seed list. Record source as `"local-awesome-repo: [folder]/[filename]"`.
   Since the PDFs are already downloaded locally, set the PDF path directly — no download needed.

5. If 15+ relevant papers are found in the local repo, you may proceed to Phase 3 with those as seeds without web search.
   If fewer than 15, continue to web search below to supplement.

#### Step 1: Web Search for Additional Seeds

Collect remaining seed papers via web search:
Use the WebSearch and WebFetch tools actively. Combine multiple search engines and academic databases to discover as many papers as possible.

Search query patterns:

* `site:arxiv.org [keyword]`
* `site:proceedings.mlr.press [keyword]`
* `site:proceedings.neurips.cc [keyword]`
* `site:openreview.net [keyword]`
* `[keyword] site:dl.acm.org`
* `[keyword] NeurIPS OR ICML OR ICLR 2020 2021 2022 2023 2024`

Semantic Scholar API
(optimal for paper metadata + citation count collection):

* `https://api.semanticscholar.org/graph/v1/paper/search?query=[keyword]&fields=title,year,venue,citationCount,externalIds,authors`

Papers With Code
(useful for tracking the latest SOTA):

* `https://paperswithcode.com/search?q_meta=&q_type=&q=[keyword]`

Engineering blog search
(select those most relevant to the topic):

Big Tech research blogs:

* `site:research.google [keyword]`
* `site:ai.googleblog.com [keyword]`
* `site:deepmind.google [keyword]`
* `site:research.facebook.com [keyword]`
* `site:microsoft.com/en-us/research [keyword]`
* `site:apple.com/research [keyword]`
* `site:machinelearning.apple.com [keyword]`
* `site:amazon.science [keyword]`
* `site:openai.com/research [keyword]`
* `site:anthropic.com/research [keyword]`

Big Tech engineering blogs:

* `site:engineering.fb.com [keyword]`
* `site:netflixtechblog.com [keyword]`
* `site:eng.uber.com [keyword]`
* `site:engineering.linkedin.com [keyword]`
* `site:eng.snap.com [keyword]`
* `site:research.bytedance.com [keyword]`
* `site:engineering.atspotify.com [keyword]`
* `site:doordash.engineering [keyword]`
* `site:eng.lyft.com [keyword]`
* `site:medium.com/airbnb-engineering [keyword]`
* `site:medium.com/pinterest-engineering [keyword]`
* `site:medium.com/twitter-engineering [keyword]`
* `site:shopify.engineering [keyword]`
* `site:stripe.com/blog/engineering [keyword]`

Asian Big Tech:

* `site:d2.naver.com [keyword]`
* `site:tech.kakao.com [keyword]`
* `site:engineering.linecorp.com [keyword]`
* `site:medium.com/coupang-engineering [keyword]`

ML/AI-specialized:

* `site:huggingface.co/blog [keyword]`
* `site:wandb.ai/fully-connected [keyword]`

After seed collection, assess whether the target number of papers (200) is appropriate for the topic.
Evaluate whether the topic has enough relevant literature, or whether a narrower area would make 50–100 papers more realistic.

If 200 seems excessive, stop at Phase 2 and confirm the target paper count with the user.
Proceed with later phases using the approved target count.

After seed collection, create two files:

1. `queue.md` — paper processing queue
2. `method-tracker.md` — methodology fundamentality tracking table
   (initially an empty table; filled in during Phase 3)

`queue.md` format:

```markdown
# [Topic] Paper Queue

## To Process
- [Title or arXiv URL] | [Source] | [Relevance: Core/Related/Peripheral] | [Final Priority 1/2/3/4]
- ...

## Done
- [filename.md] | [Title] | [processing date]
- ...

## Skipped
- [Title] | [reason for skipping]
- ...
```

### Queue Depletion Strategy

If the queue risks running out before reaching the target paper count (200), expand it in the following order. Always start from Step 0.

#### Step 0 (Highest Priority): Harvest Citations from Already Downloaded PDFs

Before expanding into adjacent fields, first inspect all already downloaded PDFs in `read-papers/` and harvest new candidate papers.
This step takes precedence over web search.

Harvest procedure:

1. Get the full list of PDF files in `read-papers/`.
2. Open each PDF with the Read tool and read the Introduction and Related Works sections.
3. Extract all cited paper titles from those two sections.
   Include papers mentioned in forms like `"[paper title] [citation number]"` in the body text, as well as entries listed in the References section.
4. Exclude papers already present in the queue (`To Process`, `Done`, or `Skipped`) or already existing in `read-papers/`.
5. For the remaining new candidate papers, check citation count and venue on Semantic Scholar and assign priorities according to the paper priority criteria.
6. Re-read the survey scope and requirements in the `requirements` file, and prioritize papers that better match those criteria.

   * Papers related to topics listed under "Must include" in `requirements` should move forward within the same priority level.
   * Papers that fall under "Exclude" should be moved to `Skipped`.
7. Add the new candidate papers to the queue under `To Process`.
   Mark the source as `"PDF harvest: [source PDF filename]"`.
8. Reorder the queue according to priority criteria + `method-tracker` weights + requirements fit.

If this step yields enough papers (`To Process` > 50), do not continue to Step 1 or below.
If still insufficient, continue to Step 1.

#### Step 1 and Beyond: Expand into Adjacent Fields

If the queue is still insufficient after Step 0, expand into adjacent fields in the following order:

1. Explore subtopics or specific methodologies within the current topic
2. Explore papers that address the same problem in different domains/modalities

   * Example: if `"recommender system scaling law"` is insufficient → expand to `"general scaling law"`
   * Domain priority here: non-NLP domains such as vision/speech first, NLP last
   * Reason: NLP scaling law literature is too large and may dilute relevance
   * Focus on how core principles discovered in NLP propagated into other domains
3. Baseline/foundation methodology papers related to the topic
4. Papers that apply or critique the topic

When expanding, record the expansion details in the "Survey Scope and Constraints" section of `requirements.md`.

When adding to the queue, mark the source as `"Adjacent-field expansion: [reason]"`.

Queue health rule:

* If `To Process` drops below 50, immediately start expansion again from Step 0 (PDF harvesting). Do not wait.

---

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
     * filename rules (the full "Filename Rules" section from `/path/to/works/for/you/.claude/skills/paper-reader/SKILL.md`)
     * markdown file format (the full report template from `/path/to/works/for/you/.claude/skills/paper-reader/references/report-template.md`)
     * PDF download instructions (the full "PDF Download Instructions" section from this document)
     * the `## Project Context` section from `requirements.md` (verbatim) — the subagent uses this to write the Project Relevance section for each paper
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

   * check citation count and venue via Semantic Scholar or Google Scholar and assign priority
   * if the paper proposes a method with high baseline mention count in `method-tracker`, raise its priority
   * add newly discovered papers to `To Process`
   * mark the source as `"Related Work harvest: [source paper filename]"`

5. Reorder the queue:

   * reorder the full `To Process` list by priority criteria
   * adjust rankings by applying the weights from `method-tracker`
   * if the queue exceeds 200 papers, move the lowest-priority items to `Skipped` to keep it at 200
   * if the queue falls below 50 papers, immediately run the "Queue Depletion Strategy" to replenish it

6. Update `queue.md`:
   move the 20 completed papers to `Done`, and reflect the reordered queue.

7. Output a one-line progress update. Example:

```text
[Progress] Done 40 / Waiting 160 / Target 200 | Top tracker methods: MethodA(5), MethodB(4)
```

8. Move to the next batch.

For low-relevance papers, instead of generating an individual markdown file, leave a one-line memo in the queue's `Skipped` section.

Once all 200 papers are processed or the queue is fully exhausted, proceed to Phase 3.5.

---

### Phase 3.5: Finalize Method Tracker

After Phase 3 ends, finalize `method-tracker.md`:

* sort the table by descending `"baseline mention count"`
* compute simplicity score and performance consistency score, and add a `"fundamentality composite score"` column
* for the top 10 methods, add a one-line explanation of `"why this method is fundamental"`

This data is used in the `"Most Fundamental Methods"` section of the Phase 5 executive summary.

---

### Phase 3.7: Cross-Reference Mapping

After Phase 3.5 is complete, you **must** run this step.
Do **not** start Phase 4 until this step is complete.

Purpose:
Record how papers in `read-papers/` mention and evaluate each other inside the individual markdown files.

This allows each paper's markdown file to contain both:

* "how I view other papers"
* "how other papers view me"

Procedure:

1. Get the list of all `.md` files in the `read-papers/` folder (exclude PDF files).
2. For each paper A's markdown file, read the Introduction and Related Works sections and extract all sentences that mention other papers.
   Extraction criteria:

   * sentences that directly mention another paper's title or author name
   * evaluative mentions such as:

     * `"[X] proposed Y"`
     * `"Unlike [X], we ..."`
     * `"Extending the method of [X] ..."`
   * sentences identifying specific papers as examples of `"limitations of prior work"`
3. Check whether the mentioned paper exists as a markdown file in `read-papers/`.
   If yes, add or update the following section in that paper B's markdown file:

```markdown
## Papers That Mention This Paper (Reverse Citation Map)

| Mentioning Paper | Mention Context | Summary of Original Wording |
|------------|----------|----------|
| [Paper A filename.md](./paperAfilename.md) | [which section mentioned it: Related Work / Introduction / Experiments] | [one-line summary of how it was evaluated: "used as a baseline", "pointed out limitations", "starting point of our method", "reported lower performance", etc.] |
| ... | ... | ... |
```

4. Complete this for all markdown files in `read-papers/`.
   If parallelization is possible, split into 20-paper groups and delegate to subagents via the Agent tool.
5. After completion, output a one-line summary. Example:

```text
[Phase 3.7 complete] Reverse citation map created: X total papers, Y reverse-citation relations recorded
```

Only after this step is fully complete may you proceed to Phase 4.

---

### Phase 4: Build Taxonomy

Note: Start this phase only after Phase 3.7 is fully complete.

Classify the collected papers into categories appropriate to the topic:

* read the `## Project Context` section from `requirements.md` before defining categories
* define categories around the core dimensions of the topic, informed by the project's specific needs and decision points — categories should map to aspects the project cares about, not just generic academic groupings
* place 5–15 papers in each category
* separate low-relevance papers into a `"References"` category

---

### Phase 5: Write Outputs and Evaluate Coverage

Note: Start this phase only after Phase 3.7 is fully complete.
Do not write the summary/review files while the reverse citation map is incomplete.

Complete the following four files:

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

The executive summary must include an **"Implications for [Use Case]"** section (or **"Recommendations"** if the Project Context describes a specific project). This section directly answers the key questions or decision points stated in the `## Project Context` section of `requirements.md`, citing specific papers. For a general academic survey, this section summarizes the most actionable takeaways for the stated audience.

#### File 4: `method-tracker.md` (Methodology Fundamentality Tracking)

* gradually filled during Phase 3
* follow the format included below in the folder structure

#### Phase 5 Exit Condition: Coverage Evaluation

After drafting File 2 and File 3, before stopping, you must evaluate coverage.

Evaluation method:

1. List all items specified in the `requirements` file under `"Request"`, `"Must Include"`, and `"Core Keywords"`.
2. Evaluate how well the written `literature-review` and `executive-summary` cover each item.

   * The criterion for "covered" is whether enough evidence exists for decision-making
     (sufficient number of papers, sufficient analysis depth).
3. Compute overall coverage as a percentage.
   Example: `"18 covered out of 20 requirement items = 90%"`

Actions based on coverage:

* If coverage ≥ 95% and the executive summary alone is sufficient for decision-making:
  final completion. Report completion to the user.
* If coverage < 95% or some items are too thinly covered:

  1. specify which requirement items are lacking
  2. collect an additional 100 papers to fill those gaps
  3. add them to the queue and repeat from Phase 3
  4. after processing the additional 100 papers, rerun Phases 3.5 → 3.7 → 4 → 5
  5. reevaluate coverage and stop only once coverage reaches ≥ 95%
* Continue this loop until coverage ≥ 95%
* However, if the total cumulative number of papers exceeds 500, report the status to the user and confirm whether to continue

---

## PDF Download Instructions

For every paper, actively attempt to download the PDF. Do not skip this.

### PDF Search Order

0. **Check the local Awesome Recsys repo first** — look up its path from `repos.md`.
   Search all category folders for a filename containing the paper title or method name.
   If found, copy it directly:
   ```
   cp "[awesome-repo-path]/[folder]/[filename].pdf" "read-papers/[output-filename].pdf"
   ```
   No download needed. Record source as `"local-awesome-repo"` in the Meta Information section.

1. If there is an arXiv ID:
   `curl -L https://arxiv.org/pdf/{id} -o "read-papers/{filename}.pdf"`
2. If it is on OpenReview:
   download directly using the OpenReview PDF URL
3. Official conference proceedings websites:
   `proceedings.mlr.press`, `proceedings.neurips.cc`, `openaccess.thecvf.com`, etc.
4. Search directly for PDF links via WebSearch:
   `"{paper title}" filetype:pdf`
   or
   `"{paper title}" site:arxiv.org OR site:openreview.net`
5. Semantic Scholar's `"Open Access PDF"` link:
   `https://api.semanticscholar.org/graph/v1/paper/search?query=[title]&fields=title,openAccessPdf`
6. Explore author homepages, institution pages, ResearchGate, etc. using WebFetch

### If the PDF Is Not Freely Accessible

If the paper requires payment
(ACM DL, IEEE Xplore, Springer, Elsevier, etc.):

* give up on downloading the PDF and explicitly state the following in the markdown file's `"Meta Information"` section:

`PDF download unavailable: paid access required ([ACM DL / IEEE Xplore / other]). No free version available.`

* still write the markdown file using whatever is accessible, such as the abstract and information retrieved via WebFetch

### Important

* Do not proceed with only a markdown file and no PDF unless all routes above have been attempted.
* If download succeeds:
  save it to the `read-papers/` folder with the same filename as the markdown file, only changing the extension to `.pdf`.
* Example PDF filename:
  `2025_NeurIPS_MethodName_Paper-Title.pdf`
  if the markdown filename is
  `2025_NeurIPS_MethodName_Paper-Title.md`

---

## Individual Paper Markdown File Format

**Follow the report template and writing notes from the `paper-reader` skill exactly as-is.**
→ Reference: `/path/to/works/for/you/.claude/skills/paper-reader/SKILL.md`

When running, read that file and apply the latest template.

### Additional Sections for `literature-survey`

In the `paper-reader` report template, ensure the following sections are present after `"Community Reaction"` and before `"Meta Information"`:

```markdown
## Project Relevance

[Assessment of how this paper's method/findings address the project's specific needs
as described in the Project Context section of requirements.md.
If the paper does not meaningfully address the project's needs, prefix with:
**Low project relevance.** [reason]]
```

```markdown
## Papers That Mention This Paper (Reverse Citation Map)

Automatically filled in during Phase 3.7. Initially left blank.

| Mentioning Paper | Section | Summary of Mention |
|------------|------|--------------|
| (To be filled in during Phase 3.7) | | |
```

For Priority 3–4 / Peripheral papers (one-paragraph summary only), still include the Project Relevance section.

## Output Formats

### Requirements File Template

```markdown
Date: YYYY-MM-DD
Topic: [topic]

# [topic] - Survey Requirements

## Request

[Record exactly what the user requested. If there are additional constraints or context, record them as well.]

## Core Keywords

- [keyword 1]
- [keyword 2]
- [keyword 3]
...

## Target Conferences / Journals

[List of conferences/journals judged to be highly relevant to the topic, and why they were selected]

## Target Engineering Blogs

[List of blogs to search]

## Search Query List

[List the actual search queries to be used in advance]

## Survey Scope and Constraints

- Target number of papers: 200 (range 100–300)
- Year range: after [reference year] (except for special seminal works)
- Must include: [subtopics or methodologies especially relevant to the topic]
- Exclude: [anything decided to be out of scope]
- Adjacent-field expansion plan: [list of areas to expand into if the queue dries up]

## Project Context

[Always present. Written from the user's response to the Phase 1 Step 6 purpose prompt.
For a project-specific survey: what the project is, how the survey output will be used, what 'relevant' means in project terms, valuable paper types.
For a general academic survey: target audience, what decisions or understanding the survey should support.
This section is the north star for extraction (Phase 3), taxonomy (Phase 4), and executive summary framing (Phase 5).]

## Summary of Actual Search Results

[Section to be filled in after survey completion]

- Total papers: [number]
- Number of categories: [number]
- Key findings: [brief summary]
```

### Main Review File Template

```markdown
Date: YYYY-MM-DD
Topic: [topic]
Paper count: [total number of papers]

# [topic] Literature Review

## Executive Summary

[Summarize the key findings of the field in 3–5 sentences]

### Most Promising Approaches

1. [Approach 1]: [one-line explanation]
2. [Approach 2]: [one-line explanation]
3. [Approach 3]: [one-line explanation]

### Practical Recommendations

Short term (1–3 months):
- [recommendation]

Mid term (3–6 months):
- [recommendation]

---

## 1. [Category 1] ([paper count] papers)

[Category description: why this category is relevant to the topic]

### [Paper Title] ([conference/journal] [year])

- Source: [conference/journal name] [year]
- Detailed analysis: [read-papers/filename.md](./read-papers/filename.md) (if available)

Relevance to [topic]:
[1–2 sentences on how this paper connects to the survey topic]

---

[other papers...]

## References (Low Relevance)

[Low-relevance papers that are still useful as background knowledge — briefly list title/source only]
```

### Method Tracker File Template

```markdown
Date: YYYY-MM-DD (last updated)
Topic: [topic]

# [topic] - Methodology Fundamentality Tracking

This file is accumulated automatically while reading PDFs during Phase 3 batch processing.
Update after each batch. Final sorting happens in Phase 3.5.

## Methodology Table

| Method Name | Proposal Paper (Year) | Baseline Mention Count | Derived Variant Count | Independent Measured Performance (Dataset: metric | source) | Component Count | Simplicity Score (1-5) | Performance Consistency Score (1-5) | Fundamentality Composite Score |
|---------|----------------|-------------------|----------------|--------------------------------------|-------------|-----------------|----------------------|----------------|
| [MethodA] | [Author et al., year] | 8 | 5 | ImageNet: 82.3% (Paper X), 82.1% (Paper Y) | 2 | 5 | 5 | 38 |
| [MethodB] | [Author et al., year] | 5 | 2 | ... | 3 | 4 | 4 | 22 |
| ... | | | | | | | | |

## How to Compute the Fundamentality Composite Score

Composite score = (baseline mention count × 3) + (derived variant count × 2) + (simplicity score × 1) + (performance consistency score × 2)

- baseline mention count: in how many other papers this method was used as a comparison baseline
- derived variant count: number of papers that directly modified/extended this method
  (mentions such as "based on X", "variant of X" in Related Work)
- simplicity score: 5 = 1–2 components, 4 = 3 components, 3 = 4 components, 2 = 5 components, 1 = 6+ components
- performance consistency score: higher when reported numbers across independent papers have lower variance
  (5 = stddev < 0.5%, 1 = > 3%)

## Top Method Analysis (Written in Phase 3.5)

After Phase 3 completes, for the top 10 methods by composite score:

### Rank 1: [Method Name] (Composite Score: N)

- Why fundamental: [one-line explanation]
- Representative paper: [author et al., title, conference year]
- Which papers used this method as a baseline: [list]
- Known variants: [list]
- Independent measured performance range: [min] ~ [max] (N papers)

...
```

### Executive Summary File Template

```markdown
Date: YYYY-MM-DD

# [topic] - Executive Summary

## Key Questions

Questions this literature survey is trying to answer:
- [question 1]
- [question 2]

## Main Findings

[Based on analysis of X total papers]

1. [finding 1]
2. [finding 2]
3. [finding 3]

## Most Fundamental Methods (based on method-tracker)

This section summarizes the top 5 methods from `method-tracker.md` by composite score.
Criteria for "fundamental":
(1) adopted as a baseline by many papers,
(2) many variants derived from it,
(3) performance is consistent in independent measurements,
(4) structure is simple.

1. [Method Name] (Composite Score N): [one-line reason it is fundamental]. Proposed in: author et al., full paper title, conference year.
2. [Method Name] (Composite Score N): [one-line reason it is fundamental]. Proposed in: author et al., full paper title, conference year.
3. [Method Name] (Composite Score N): ...
4. ...
5. ...

## Approach Comparison

| Approach | Pros | Cons | Related Paper |
|--------|------|------|-----------|
| [Approach 1] | [pros] | [cons] | author et al., [full paper title], [conference] [year] |
| [Approach 2] | [pros] | [cons] | author et al., [full paper title], [conference] [year] |

## Implications for [Use Case]

[Read the ## Project Context section from requirements.md. Write 2–3 paragraphs directly answering the project's key questions or decision points, citing specific papers.
For a general academic survey, summarize the most actionable takeaways for the stated audience.
For a project-specific survey, frame recommendations around the project's practical constraints and goals.]

## Next Steps

- [ ] [action item 1]
- [ ] [action item 2]

## Search Scope

- Survey period: [date range]
- Total papers: [number]
- Major conferences: [list]
- Search keywords: [list]
```

## Writing Principles

**Use the "Writing Notes and Cautions" section from the `paper-reader` skill as the default principles.**
→ Reference: `/path/to/works/for/you/.claude/skills/paper-reader/SKILL.md`

### Additional Principles for `literature-survey`

* Target paper count is 100–300 (default 200).
  If insufficient, run the adjacent-field expansion strategy.
  If excessive, eliminate lower-priority papers according to the priority criteria.
* Analyze Priority 1–2 papers deeply, and handle Priority 3–4 papers with brief summaries.
* Every claim and recommendation in `executive-summary.md` must cite the paper's full name.
  No abbreviations. Format:
  `"author et al., full paper title, conference/journal year"`
* Before starting the survey, read the current project's `CLAUDE.md` and the upper folder's `CLAUDE.md` to understand the user context.

## Accessibility Principle (Required)

Inclusion rule for papers:
Only include papers whose full text is freely accessible.

Accepted free-access sources:

* `arxiv.org` (preprint or conference version)
* `openreview.net` (ICLR, NeurIPS, and other OpenReview-based conferences)
* publicly available PDFs on official conference sites
  (`proceedings.mlr.press`, `proceedings.neurips.cc`, `aaai.org`, `aclanthology.org`, etc.)
* `"Open Access PDF"` link available on Semantic Scholar / Papers With Code
* PDF publicly available on the author's homepage or institution page

Exclude:

* papers whose full text is inaccessible without payment
  on ACM DL, IEEE Xplore, Springer, Elsevier, etc.

How to check:

* search the paper on Semantic Scholar and check whether an `"Open Access PDF"` button exists
* if not, search `site:arxiv.org [title]` or `site:openreview.net [title]`

In the queue's `Skipped` section, record the reason as:
`paid access only - no free version available`

## Rate Limit Handling

Do not artificially delay or throttle requests in advance just to avoid rate limits. Just proceed normally.

If you encounter:

* 429 errors
* "Too Many Requests"
* empty results
* delayed responses

follow the steps below.

### Response Order When Rate Limited

1. Check the backoff file:
   read `[output folder]/rate-limit-backoff.md`

   If there is a recorded last successful wait time for the service, start with that value.
   If the file does not exist or no record exists, start with 30 seconds.

2. Wait and retry:
   run `sleep [N]` via the Bash tool, then retry the same request.

3. Record results and adjust:

   * if retry succeeds:
     record in `rate-limit-backoff.md`
     `service: [service name] | wait time: [N] sec | result: success | date: [date]`
     Next time a rate limit occurs, start from this value.
   * if retry fails:
     double the wait time
     `(30 → 60 → 120 → 300 sec, max 300 sec)`
     then wait and retry again.
   * if it still fails even at 300 seconds:
     abandon that source and switch to an alternative source

`rate-limit-backoff.md` format:

```markdown
# Rate Limit Backoff Log

| Service | Last Successful Wait Time (sec) | Last Attempt Date |
|--------|------------------------------|-------------|
| google-search | 60 | 2026-03-25 |
| semantic-scholar | 30 | 2026-03-25 |
| arxiv | 30 | 2026-03-25 |
```

### Switching Search Sources (If Rate Limits Cannot Be Resolved)

If a specific source remains blocked, switch to the following alternatives:

* Google search blocked → Semantic Scholar API, direct arXiv search, Papers With Code
* Semantic Scholar API blocked → Google Scholar WebSearch, direct arXiv search
* arXiv blocked → `openreview.net`, direct conference proceedings access

Leave a memo in the queue item:
`access blocked - rate limit, switched to alternative source`

Then continue.
