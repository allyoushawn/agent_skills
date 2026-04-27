---
name: run-notebook-on-colab
description: |
  Runs a Jupyter notebook on Google Colab via SSH + papermill. Uses scp for fast file sync (no git round-trip), handles remote execution, and surfaces errors for fix-and-retry loops.
  Triggers: "run notebook on Colab", "run notebook with Colab", "execute notebook on Colab", "test notebook on Colab".
---

# Run Notebook on Colab

Executes a local Jupyter notebook on a Colab GPU runtime via SSH + papermill so the agent can see errors and fix them directly without manual copy-paste. File transfer is `scp` only — no git round-trip.

## Inputs

| Input | Description | Example |
|-------|-------------|---------|
| Notebook path | Repo-relative `.ipynb` | `notebooks/ad_hoc/experiment_foo.ipynb` |
| Colab hostname | User provides after manual bootstrap (Phase 2) | `loud-turkey-abc.trycloudflare.com` |

If the user gives a short name, resolve it by searching the repo's `notebooks/` directory.

## References (load when relevant)

- `kb/context/colab/colab-compatibility.md` — papermill compatibility checklist (drive mount guards, magics, git-sync conflicts)
- `kb/context/colab/colab-sync-protocol.md` — scp-only file sync rule and "no git inside notebook" policy
- `kb/context/colab/gpu-review-patterns.md` — GPU anti-patterns to flag during preflight (Critical only by default)

## Prerequisites (per-repo)

- `cloudflared` installed locally (`brew install cloudflared`)
- SSH key at `~/.ssh/colab_key` matching the public key installed by the bootstrap notebook
- Repo contains `notebooks/ad_hoc/colab_ssh_bootstrap.ipynb` and `scripts/connect_colab.sh` (or equivalent)

## Steps

### Phase 1 — Prepare the notebook (delegate to subagent)

Dispatch a `general-purpose` subagent (or `experiment-code-change` when within an iterative experiment) to:

1. Read the notebook and check it against `kb/context/colab/colab-compatibility.md`.
2. Apply execution-safe fixes (drive mount guard, replace magics with `os.makedirs` / `subprocess.run`, gate any `git reset --hard` cells behind `SKIP_GIT_REPO_SYNC`).
3. Return a one-line summary of what changed.

### Phase 2 — Connect to Colab

Resolve the repo path via `fetch-repo-path` if not already known.

**Automated (preferred):** run the repo's `scripts/trigger_colab_bootstrap.py` to launch Chrome with a saved session, connect a GPU runtime, and relay the hostname back via ntfy.

**Manual fallback:** open the bootstrap notebook in Colab, Run All, and have the user paste the `*.trycloudflare.com` hostname.

Verify connectivity:

```bash
ssh <SSH_OPTS> root@<HOSTNAME> \
  "echo OK && nvidia-smi --query-gpu=name --format=csv,noheader"
```

### Phase 3 — Execute (delegate to subagent)

Dispatch a `general-purpose` subagent (or `experiment-runtime` when within an iterative experiment) to:

1. `scp` the notebook to `<REMOTE_REPO_ROOT>/<NOTEBOOK_PATH>` on Colab.
2. Run via `papermill` (background; poll until `exit_code` appears or 10 min elapses).
3. On non-zero exit: read traceback, dispatch a code-change subagent to fix the failing cell, re-scp, re-run. Up to 3 retries; otherwise escalate.
4. On success: extract metrics / training curves from the papermill output log.

The lead never runs scp/ssh/papermill commands directly.

## SSH/SCP options (subagent applies)

```
-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
-o IdentityFile=~/.ssh/colab_key \
-o ProxyCommand="cloudflared access ssh --hostname <HOSTNAME>"
```

## Paths

| Variable | Default value |
|----------|---------------|
| `<REMOTE_REPO_ROOT>` | `/content/drive/MyDrive/colab/<project_name>/<project_name>` |
| Dataset cache | `/content/drive/MyDrive/colab/data/<project_name>` |
| SSH key | `~/.ssh/colab_key` (key auth only) |

`<project_name>` defaults to the repo directory name; resolve with `fetch-repo-path` and override only if the user specifies one.

## Output

- On success: notebook output path, parsed metrics, runtime in minutes.
- On failure after 3 retries: classified failure (per `kb/context/experiments/experiment-contracts.md` failure classes if within an experiment loop), error trace, suggested next step.
