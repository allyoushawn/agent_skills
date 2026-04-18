# Community Survey Skill

Surveys informal and industry sources for a given topic — covering Hacker News, engineering blogs, ProductHunt, Medium, Substack, X (indirect), and Quora. Complements `literature-survey` (which targets academic papers) with community signal, practitioner discourse, and tooling trends.

## Inputs

- **topic** (required): natural language topic to survey
- **topic_slug** (optional): snake_case slug for file naming; derived from topic if omitted
- **time_window** (optional): recency filter, default `"last 30 days"`. Pass `"last 7 days"`, `"last 3 months"`, etc.
- **delta** (optional): if `true`, load the most recent prior survey for this slug and report only new signal

## Output location

```
/path/works/for/you/paper_reading_repo/community-survey/<topic_slug>/community_survey_YYYYMMDD.md
```

If the `community-survey/<topic_slug>/` folder doesn't exist, create it.

## Steps

### 1. Parse inputs

- Derive `topic_slug`: lowercase, spaces → underscores, strip punctuation
- Resolve today's date (`YYYYMMDD`) from `currentDate`
- Set `time_window` default to `"last 30 days"` if not provided
- If `delta=true`, read the most recent `community_survey_*.md` in the output folder and note its date as `prior_date`

### 2. Search Tier 1 — Hacker News

Run two searches:
```
site:news.ycombinator.com <topic> <time_window>
site:news.ycombinator.com <topic> Show HN OR Ask HN
```
Fetch the top 2 HN threads using WebFetch. Extract: post title, score (if visible), key comment themes, and notable disagreements.

### 3. Search Tier 1 — Engineering Blogs

Run one broad search covering all major tech companies:
```
<topic> site:engineering.fb.com OR site:ai.meta.com OR site:anthropic.com OR site:openai.com OR site:research.google OR site:deepmind.google OR site:machinelearning.apple.com OR site:netflixtechblog.com OR site:engineering.linkedin.com OR site:x.ai <time_window>
```
Fetch top 2 results. Summarize: which company, what they published, key technical claims.

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

Produce a structured synthesis across all sources:

```markdown
# Community Survey: <Topic>

**Date:** YYYY-MM-DD
**Time window:** <time_window>
**Mode:** full | delta (since YYYY-MM-DD)

## Source Snapshots

### Hacker News
[findings]

### Engineering Blogs
[findings — attribute to company]

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
/path/works/for/you/paper_reading_repo/community-survey/<topic_slug>/community_survey_YYYYMMDD.md
```

Report the saved path to the user.

## Source Tier Reference

| Tier | Platform | Access | Notes |
|------|----------|--------|-------|
| 1 | Hacker News | Full | `site:` search + WebFetch threads |
| 1 | Engineering Blogs | Full | Google, Meta, Anthropic, OpenAI, DeepMind, Apple ML, Netflix, LinkedIn, xAI |
| 1 | ProductHunt | Full | Products + community ask threads |
| 1 | Medium / Substack | Full | General search + WebFetch |
| 2 | X / Twitter | Indirect | Search snippets + secondary coverage only |
| 2 | Quora | Partial | URLs accessible; answer depth varies |
| ❌ | Reddit | Blocked | Anthropic crawler denied; revisit if Reddit API credentials added |

## Known Limitations

- **Reddit** not included. Future: add OAuth credentials (`REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`) as env vars to unlock via API.
- **X/Twitter** direct access not available. Future: add X Bearer Token (`X_BEARER_TOKEN`) for API v2 search (Basic tier, ~$100/mo).
- Engineering blog coverage depends on search indexing; very recent posts (< 48h) may not appear.
