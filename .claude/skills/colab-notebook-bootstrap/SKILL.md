---
name: colab-notebook-bootstrap
description: |
  Generates a new Jupyter notebook with three Colab bootstrap cells: Drive mount, work directory under Drive, and GitHub clone + branch checkout. Pure scaffolding — does not execute the notebook.
  Triggers: "create a Colab notebook", "bootstrap Colab setup", "new Colab notebook with Drive mount and clone", "scaffold a Colab notebook for this repo".
---

# Colab Notebook Bootstrap

Creates a new `.ipynb` with three code cells for Google Colab + GitHub development. This skill only writes the notebook file; it does not run it. Pair with `run-notebook-on-colab` to execute the resulting notebook on a Colab GPU.

## Inputs

| Input | Description | Example |
|-------|-------------|---------|
| Notebook path | Repo-relative path for the new `.ipynb` | `notebooks/ad_hoc/colab_setup.ipynb` |
| Project name | Used in `WORK_DIR` under Drive | `tiger_semantic_id` |
| Repo URL | GitHub clone URL | `https://github.com/org/repo.git` |
| Repo directory | Local folder name after clone | `recsys_playground` |
| Branch name | Git branch to checkout | `main` or `20260424_feature_x` |

If any input is missing, ask the user.

## References (load when relevant)

- `kb/context/colab/colab-compatibility.md` — papermill compatibility (avoid magics, drive mount guards)
- `kb/context/colab/colab-sync-protocol.md` — scp-only sync rule and "no git inside notebook" policy

## Steps

1. **Resolve repo path** via `fetch-repo-path` if the notebook target is in a registered repo.
2. **Confirm inputs** — gather any missing fields from the user before writing the file.
3. **Delegate write to a `general-purpose` subagent** with a brief that includes the resolved absolute notebook path, the substituted cell contents (templates below), and the instruction to write a valid `.ipynb` JSON. The lead does not write the notebook directly.

## Cell templates

Substitute `<project_name>`, `<repo_url>`, `<repo_dir>`, `<branch_name>`.

### Cell 1 — Mount Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

### Cell 2 — Work dir

```python
import os
assert os.path.exists('/content/drive')
WORK_DIR = '/content/drive/MyDrive/colab/<project_name>'
%mkdir -p $WORK_DIR
%cd $WORK_DIR
```

### Cell 3 — Clone repo + checkout branch

```python
try:
    import google.colab  # type: ignore
    IN_COLAB = True
except Exception:
    IN_COLAB = False

repo_url = '<repo_url>'
repo_dir = '<repo_dir>'
branch_name = '<branch_name>'

import os
if IN_COLAB:
    if os.path.exists(repo_dir):
        !rm -rf {repo_dir}
    !git clone $repo_url
    %cd $repo_dir
    !git fetch --all
    !git checkout $branch_name || echo 'Branch not found; staying on default.'
```

## Notebook format

- `cells`: three code cells with `cell_type: "code"` and `source` as a list of strings.
- Omit `execution_count` and `outputs` (or set to `null` / `[]`).
- Include minimal metadata: `kernelspec` (Python 3) and `language_info`.
- `nbformat: 4`, `nbformat_minor: 5`.

## Output

- Path of the new `.ipynb`, ready to open in Colab or hand off to `run-notebook-on-colab` for execution.
