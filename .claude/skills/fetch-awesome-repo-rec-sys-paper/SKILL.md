---
name: fetch-awesome-repo-rec-sys-paper
description: |
  Resolves paper titles and repo-relative PDF paths from the curated Awesome-Deep-Learning-Papers-for-Search-Recommendation-Advertising index by keyword. Returns section, title, decoded path inside the companion PDF repo, and the GitHub blob URL.
  Triggers: user names a paper / acronym / author / venue and wants the canonical path or URL from the Awesome rec-sys list (e.g. "find DIEN", "where is the wide & deep paper", "Awesome rec-sys list").
---

# Fetch paper path from Awesome rec-sys list

Looks up papers from the curated [Awesome-Deep-Learning-Papers-for-Search-Recommendation-Advertising](https://github.com/guyulongcs/Awesome-Deep-Learning-Papers-for-Search-Recommendation-Advertising) README. The README only stores markdown links; PDFs live in the companion repo `guyulongcs/Deep-Learning-for-Search-Recommendation-Advertisements`. The repo-relative path is the segment after `blob/<branch>/` in each link, URL-decoded.

## Inputs

| Input | Description | Example |
|-------|-------------|---------|
| Query tokens | One or more space-separated tokens; every token must appear in title / path / URL | `DIEN`, `wide deep`, `multi-task ranking` |
| README path (optional) | Override via env `AWESOME_REC_SYS_README` or `--readme` flag | — |

Tokens that are alphanumeric/hyphen are matched as **whole words** (so `DIEN` does not match `Gradient`).

## References (load when relevant)

- None — this skill is self-contained.

## Steps

1. **Locate the README.** Default lookup order in the script:
   1. `AWESOME_REC_SYS_README` env var
   2. Hard-coded fallback at `/path/to/works/for/you/Projects/Awesome-Deep-Learning-Papers-for-Search-Recommendation-Advertising/README.md`

   If neither resolves, ask the user to clone the Awesome repo or set the env var.

2. **Run the script:**

   ```bash
   python3 ~/.claude/skills/fetch-awesome-repo-rec-sys-paper/scripts/find_paper.py "DIEN"
   python3 ~/.claude/skills/fetch-awesome-repo-rec-sys-paper/scripts/find_paper.py wide deep
   ```

3. **Return the matches** — section heading, human title, repo-relative `path:` (decoded), and full GitHub `url:`. Report all matches when duplicates appear under different sections (e.g. same paper under `03_Ranking` and `Sequence-Modeling`).

## Fallback without the script

1. Open the README at the resolved path.
2. Search case-insensitive for the keyword.
3. For each `* [Title](URL)` line with a `.pdf` URL, decode the path after `blob/master/` (e.g. `%20` → space).
4. Return section (nearest preceding `##` heading), title, relative path, and full URL.

## Notes

- Link titles use nested brackets (e.g. `[DIN]` inside `[...](url)`) — the script handles this. A naive `[^]]+` regex on the whole line will fail.
- Markdown emphasis (`**`, `_`, backticks) in link text is stripped for display.
- Local PDFs only exist if the user has separately cloned `Deep-Learning-for-Search-Recommendation-Advertisements`; the Awesome README still gives the correct relative path.

## Output

- One block per match: `section`, `title`, `path:` (relative path inside the PDF repo), `url:` (full GitHub blob URL).
