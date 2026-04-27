---
name: gpu-review
description: |
  Reviews deep learning code (.py files and Jupyter notebooks) to ensure GPU is used when available. Identifies anti-patterns like missing device detection, hardcoded CPU usage, tensors not on GPU, and performance issues. Supports PyTorch, TensorFlow/Keras, and JAX.
  Triggers: "review code for GPU usage", "check GPU utilization", "audit device placement", "ensure DL training runs on GPU".
---

# GPU Code Review

Audits deep learning code for proper GPU utilization against framework-specific anti-patterns.

## Inputs

- Target file(s) — `.py` or `.ipynb`
- Optional: severity scope (default: report Critical + Performance; runtime preflight uses Critical only)

## References (load when relevant)

- `kb/context/colab/gpu-review-patterns.md` — anti-patterns by framework (PyTorch, TensorFlow/Keras, JAX, Colab notebook-specific)

## Steps

1. **Detect framework** — scan imports for `torch`, `tensorflow` / `keras`, or `jax`.
2. **Dispatch a subagent** (`reading-agent` for read-only audit, or `general-purpose` if fixes are also expected) with the file path and the framework's section of `kb/context/colab/gpu-review-patterns.md` as reference. The subagent checks:
   - Device detection exists and uses dynamic selection (not hardcoded CPU).
   - Model is moved to the detected device.
   - All tensors / data are on the same device as the model before forward pass.
   - DataLoader / data pipeline is GPU-optimized (`pin_memory`, prefetch, etc.).
   - Eval / inference paths disable gradients.
   - Mixed precision is considered for training code.
   - Multi-GPU is considered when relevant.
   - For notebooks: an early cell verifies GPU availability (`!nvidia-smi`).
3. **Receive findings** as a structured list with severity (Critical / Performance), the problematic snippet, and a concrete fix.

## Output

```
## GPU Review: <filename>

**Framework:** PyTorch | TensorFlow | JAX
**Device setup found:** Yes / No
**Overall:** Good / Issues found

### Findings

#### [Critical] <title>
- **Line(s):** ...
- **Issue:** ...
- **Fix:** ...

#### [Performance] <title>
- **Line(s):** ...
- **Issue:** ...
- **Fix:** ...

### Summary
- N critical issues, M performance suggestions
- <one-line overall recommendation>
```

## Edge cases

- Code intentionally forces CPU (debugging, small models): note as informational, not Critical.
- No DL framework detected: report no GPU-relevant code found.
- Multi-framework files: audit each framework independently.

## Notes for experiment runtime preflight

When invoked as part of an iterative experiment loop (`experiment-runtime` preflight), apply only **Critical** findings autonomously. Performance items can change training behavior (e.g. mixed precision, `pin_memory`) and are treated as operational downgrades per `kb/context/experiments/experiment-policies.md`.
