---
name: paper-reader
description: Analyzes ML/AI research papers from PDF files or URLs. Summarizes papers, critiques experiment design and statistical validity, assesses industry contribution, compares to prior work via web search, and checks dataset availability. Use when the user asks to read, analyze, or review a paper, provides a PDF path or arxiv/paper URL.
---

# Paper Reader

Analyzes ML/AI research papers and produces structured reports. Supports local PDF paths and URLs (arxiv, direct PDF links).

## Input Handling

- **Local PDF**: Use the Read tool directly on the file path.
- **URL**: Run `python $HOME/.claude/skills/paper-reader/scripts/fetch_paper.py <url>` to download, then Read the returned path.
  - Arxiv abstract URLs (`arxiv.org/abs/...`) are auto-converted to PDF.
  - Direct PDF URLs are downloaded as-is.

## Workflow

Follow these five analysis dimensions in order. Use [references/evaluation-rubric.md](references/evaluation-rubric.md) for experiment critique. Output format: [references/report-template.md](references/report-template.md).

1. **Summarize** — Extract title, authors, abstract, key contributions, methodology, main results.
2. **Experiment critique** — Evaluate experiments for statistical rigor, baselines, ablations, effect sizes, A/B design, biases. See evaluation-rubric.md for detailed criteria.
3. **Industry contribution** — Assess deployability, industry problems solved, engineering cost.
4. **Novelty analysis** — Web search (arxiv, Semantic Scholar, Google Scholar) to verify novelty claims and compare to prior work.
5. **Dataset availability** — Check if paper provides dataset links; report accessibility; flag reproducibility.

## Output

- **Default**: Print the structured report in chat.
- **Save to file**: If user requests, save as markdown to a specified path (default: `./paper-reviews/`).
- **Save to PDF**: If user requests, use reportlab to generate PDF. Default path: `./paper-reviews/`; allow user-specified path.
- **`read-papers/` mode**: When invoked by the `literature-survey` skill, save output as a markdown file to the `read-papers/` folder using the filename rules below. Leave the Reverse Citation Map section blank (filled in during Phase 3.7).
- **Integration**: When datasets are found and accessible, add a callout: "To run experiments on these datasets, use the experiment-runner skill with the dataset URL or info above."

## Dependencies

```
pip install requests reportlab
```

## Filename Rules

When saving output as a file (especially in `read-papers/` mode), use this format:

```
YYYY_Venue_MethodName_Paper-Title.md
```

- `YYYY` — publication year (use arXiv submission year if no venue)
- `Venue` — conference or journal abbreviation (e.g. `NeurIPS`, `ICML`, `ICLR`, `CVPR`, `arXiv`). Use `arXiv` for preprints.
- `MethodName` — the primary method or model name proposed in the paper (e.g. `BERT`, `LoRA`, `DIN`). Use `NA` if the paper proposes no named method.
- `Paper-Title` — shortened paper title: title-cased words, spaces replaced with hyphens, special characters removed, max ~6 words.

Examples:
- `2024_NeurIPS_MethodA_Scaling-Laws-for-Reward-Models.md`
- `2023_ICML_NA_Survey-of-Recommendation-Systems.md`
- `2022_arXiv_LoRA_Low-Rank-Adaptation-Large-Language-Models.md`

PDF files use the same filename with `.pdf` extension.

## How to Find Author Affiliations

Author affiliations determine paper priority (big tech vs. academia). Look them up in this order:

1. **PDF first page** — affiliations are usually listed directly under author names.
2. **Semantic Scholar** — `https://api.semanticscholar.org/graph/v1/paper/search?query=[title]&fields=authors,authors.affiliations`
3. **Google Scholar author profile** — search the author name + institution.
4. **Author's personal/lab homepage** — linked from the PDF or Google Scholar.

Big tech organizations for priority purposes: Google/DeepMind, Meta/FAIR, Microsoft Research, Apple, Amazon, OpenAI, Anthropic, ByteDance, NVIDIA, Adobe Research, Salesforce Research.

If affiliation cannot be determined after these steps, mark as `Unknown`.

## How to Search for Community Reactions

After summarizing the paper, search for how the community received it:

Search queries to run:
- `"{paper title}" site:twitter.com OR site:x.com`
- `"{paper title}" site:reddit.com`
- `"{paper title}" site:news.ycombinator.com`
- `"{paper title}" OR "{method name}" blog review`
- `site:huggingface.co/blog "{method name}"`

Summarize findings in the **Community Reaction** section of the report:
- Any viral discussion, strong praise, or strong criticism
- Notable implementations or reproductions
- If no significant reaction found, state: "No significant community discussion found."

## Writing Notes and Cautions

- Be **factual and precise**: do not editorialize beyond what the paper claims. Distinguish paper claims from your assessment.
- **Cite fully**: when referencing results, always include the dataset name and metric (e.g. "82.3% accuracy on ImageNet").
- **No abbreviations in executive contexts**: write "author et al., full paper title, conference year" — never "the LoRA paper."
- **Relevance framing for recsys**: when assessing industry contribution, explicitly frame applicability in terms of recommendation system engineering — e.g. latency constraints, online serving, feature engineering, embedding lookup, two-tower models, ranking pipelines.
- **Honest about limitations**: if experiments are weak, say so clearly. Do not soften critique.
- **Peripheral papers**: for low-relevance papers, write a one-paragraph summary only — do not fill every section.

## Report Template

See [references/report-template.md](references/report-template.md) for the full structure.
