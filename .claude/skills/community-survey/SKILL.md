---
name: community-survey
description: "Surveys informal and industry sources for a given topic — covering Hacker News, engineering blogs, ProductHunt, Medium, Substack, X (indirect), and Quora. Complements literature-survey (which targets academic papers) with community signal, practitioner discourse, and tooling trends. Use when the user wants a community survey, practitioner signal, tooling trends, or runs /community-survey <topic>."
---

# Community Survey Skill

Surveys informal and industry sources for a given topic — covering Hacker News, engineering blogs, ProductHunt, Medium, Substack, X (indirect), and Quora. Complements `literature-survey` (which targets academic papers) with community signal, practitioner discourse, and tooling trends.

## Inputs

- **topic** (required): natural language topic to survey
- **topic_slug** (optional): snake_case slug for file naming; derived from topic if omitted
- **time_window** (optional): recency filter, default `"last 30 days"`. Pass `"last 7 days"`, `"last 3 months"`, etc.
- **delta** (optional): if `true`, load the most recent prior survey for this slug and report only new signal
- **lens** (optional): one-sentence framing for what angle this run cares about (e.g. "evaluating tools to adopt for production"). If not provided, falls back to the `## Lens` section in `<topic_slug>/README.md`. The lens shapes the synthesis section (Step 8) — it is woven into the Key Themes, Notable Tools, and Key Debates summaries.

## Output location

Resolve the paper reading repo path via the `fetch-repo-path` skill (reads `/path/to/works/for/you/knowledge_base/context/registry/repos.md` → "Paper Reading Repo" entry). Do not hardcode the path. Then write to:

```
<paper-reading-repo>/community-survey/<topic_slug>/community_survey_YYYYMMDD.md
```

If the `community-survey/<topic_slug>/` folder doesn't exist, create it.

## Per-topic folder layout

Each topic gets its own folder under `community-survey/`. The canonical layout is:

```
<paper-reading-repo>/community-survey/<topic_slug>/
├── README.md                            ← persistent context for this topic (lens, audience, why tracked)
├── log.md                               ← append-only run journal
├── community_survey_YYYYMMDD.md         ← per-run snapshot
└── community_survey_YYYYMMDD.md
```

- `README.md` is written once on the first run for a topic and read on every subsequent run to recover the lens.
- `log.md` is append-only (newest entry on top) and gives a quick chronological view of all runs for this topic.
- `community_survey_YYYYMMDD.md` is the full per-run snapshot.

## Steps

### 1. Parse inputs

- Derive `topic_slug`: lowercase, spaces → underscores, strip punctuation
- Resolve today's date (`YYYYMMDD`) from `currentDate`
- Set `time_window` default to `"last 30 days"` if not provided
- If `delta=true`, read the most recent `community_survey_*.md` in the output folder and note its date as `prior_date`
- If `lens` parameter not provided, read `<topic_slug>/README.md` and extract the `## Lens` section content as the active lens for this run

### 1.5. Ensure README.md exists

- If `<topic_slug>/README.md` does not exist (first run on this topic):
  - Prompt the user for:
    - (a) why this topic is being tracked
    - (b) audience / who consumes the survey
    - (c) lens — one sentence describing the angle the survey should take (e.g. "evaluating tools to adopt", "tracking competitor moves", "mapping live debates")
  - Write the README.md with these three sections plus a `## Created` date line, using this template:

```markdown
# Community Survey Topic — <Topic>

**Created:** YYYY-MM-DD

## Why tracked
[user's answer to (a)]

## Audience
[user's answer to (b)]

## Lens
[user's one-sentence answer to (c) — this shapes synthesis framing]
```

- If `README.md` already exists: read it and extract the lens for use in Step 8 (synthesis)

### 2. Search Tier 1 — Hacker News

Run two searches:
```
site:news.ycombinator.com <topic> <time_window>
site:news.ycombinator.com <topic> Show HN OR Ask HN
```
Fetch the top 2 HN threads using WebFetch. Extract: post title, score (if visible), key comment themes, and notable disagreements.

### 3. Search Tier 1 — Engineering Blogs

Coverage is split into three category-grouped queries to avoid query-length limits and result dilution.

#### 3a. Big Tech research blogs

```
<topic> site:research.google OR site:ai.googleblog.com OR site:deepmind.google OR site:research.facebook.com OR site:microsoft.com/en-us/research OR site:apple.com/research OR site:machinelearning.apple.com OR site:amazon.science OR site:openai.com/research OR site:anthropic.com/research <time_window>
```
Fetch top 2 results.

#### 3b. Big Tech engineering blogs (Western + Asian)

```
<topic> site:engineering.fb.com OR site:netflixtechblog.com OR site:eng.uber.com OR site:engineering.linkedin.com OR site:eng.snap.com OR site:research.bytedance.com OR site:engineering.atspotify.com OR site:doordash.engineering OR site:eng.lyft.com OR site:medium.com/airbnb-engineering OR site:medium.com/pinterest-engineering OR site:medium.com/twitter-engineering OR site:shopify.engineering OR site:stripe.com/blog/engineering <time_window>
```
Fetch top 2 results.

```
<topic> site:d2.naver.com OR site:tech.kakao.com OR site:engineering.linecorp.com OR site:medium.com/coupang-engineering <time_window>
```
Fetch top 1 result.

#### 3c. ML/AI specialized blogs

```
<topic> site:huggingface.co/blog OR site:wandb.ai/fully-connected <time_window>
```
Fetch top 1 result.

For each fetched result across 3a–3c, summarize: which company, what they published, key technical claims.

### 4. Search Tier 1 — ProductHunt

```
site:producthunt.com <topic> <time_window>
```
Extract: top-launched products, upvote signals, taglines, and any notable discussion in comments.

### 5. Search Tier 1 — Medium & Substack

```
<topic> site:medium.com OR site:substack.com <time_window>
```
Fetch top 2 articles. Extract: author's thesis, key takeaways, community reaction if visible.

### 6. Search Tier 2 — X / Twitter (indirect)

Run general search to surface X posts and secondary coverage:
```
<topic> twitter OR "x.com" discussion <time_window>
```
Also run:
```
<topic> site:x.com <time_window>
```
Do NOT attempt to fetch x.com URLs directly — they will fail. Extract tweet summaries and quote snippets from search result previews and secondary coverage articles only.

### 7. Search Tier 2 — Quora

```
site:quora.com <topic>
```
Surface top question URLs. Fetch the top 1 result. Extract: question framing, top answer summary.

### 8. Synthesize

Produce a structured synthesis across all sources.

All four synthesis subsections (Key Themes, Notable Tools & Projects, Key Debates & Disagreements, Emerging Patterns) must be written through the lens stated in README.md / passed via the `lens` parameter. Do not produce generic summaries — concentrate on signal that matters to the lens.

```markdown
# Community Survey: <Topic>

**Date:** YYYY-MM-DD
**Time window:** <time_window>
**Mode:** full | delta (since YYYY-MM-DD)
**Lens:** <lens text>

## Source Snapshots

### Hacker News
[findings]

### Big Tech Research Blogs
[findings]

### Big Tech Engineering Blogs
[findings]

### ML/AI Specialized Blogs
[findings]

### ProductHunt
[findings]

### Medium / Substack
[findings]

### X / Twitter (indirect)
[findings — note these are snippets from search previews, not direct fetches]

### Quora
[findings]

## Synthesis

### Key Themes
### Notable Tools & Projects
### Key Debates & Disagreements
### Emerging Patterns
### Open Questions

## Limitations This Run
- Reddit: blocked at crawler level (Anthropic user-agent denied). Not included.
- X/Twitter: direct fetch unavailable; coverage is indirect via search snippets and secondary articles.
- Time window is approximate — search engine indexing lag may affect recency.
```

### 9. Delta section (if delta=true)

Append a `## What's New Since <prior_date>` section comparing to the prior survey. Focus on:
- New tools or projects not mentioned before
- Shifted sentiment or consensus
- New debates that emerged
- Topics that went quiet

### 10. Save output

Write the file to:
```
<paper-reading-repo>/community-survey/<topic_slug>/community_survey_YYYYMMDD.md
```
(`<paper-reading-repo>` was already resolved at the start of the run via `fetch-repo-path`.)

Report the saved path to the user.

### 11. Append to log.md

- If `<topic_slug>/log.md` does not exist, create it with header `# Log — <Topic>\n`
- Prepend (newest on top) a new dated entry below the header:

```markdown
## YYYY-MM-DD — community-survey run (<mode: full | delta since YYYY-MM-DD>)
- Lens: <lens used this run>
- Time window: <time_window>
- Sources scanned: HN(N), eng-blogs(N), PH(N), Medium(N), X(snippets), Quora(N)
- Output: community_survey_YYYYMMDD.md
- Notable: <one-line headline of the most significant finding this run>
```

## Source Tier Reference

| Tier | Platform | Access | Notes |
|------|----------|--------|-------|
| 1 | Hacker News | Full | `site:` search + WebFetch threads |
| 1 | Research Blogs | Full | Google Research, Google AI, DeepMind, Meta Research (FAIR), Microsoft Research, Apple Research, Apple ML, Amazon Science, OpenAI Research, Anthropic Research |
| 1 | Engineering Blogs | Full | Meta Eng, Netflix, Uber, LinkedIn, Snap, ByteDance, Spotify, DoorDash, Lyft, Airbnb, Pinterest, Twitter, Shopify, Stripe, Naver D2, Kakao, LINE, Coupang |
| 1 | ML-Specialized | Full | Hugging Face Blog, Weights & Biases (Fully Connected) |
| 1 | ProductHunt | Full | Products + community ask threads |
| 1 | Medium / Substack | Full | General search + WebFetch |
| 2 | X / Twitter | Indirect | Search snippets + secondary coverage only |
| 2 | Quora | Partial | URLs accessible; answer depth varies |
| ❌ | Reddit | Blocked | Anthropic crawler denied; revisit if Reddit API credentials added |

## Known Limitations

- **Reddit** not included. Future: add OAuth credentials (`REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`) as env vars to unlock via API.
- **X/Twitter** direct access not available. Future: add X Bearer Token (`X_BEARER_TOKEN`) for API v2 search (Basic tier, ~$100/mo).
- Engineering blog coverage depends on search indexing; very recent posts (< 48h) may not appear.
