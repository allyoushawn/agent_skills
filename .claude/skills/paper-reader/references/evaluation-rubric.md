# Experiment Evaluation Rubric

Use this rubric for detailed experiment critique. Assess each criterion and note strengths/weaknesses.

## Experimental Design

| Criterion | Strong | Weak |
|-----------|--------|------|
| **Controls** | Clear control/baseline; fair comparison setup | Missing or unfair baselines |
| **Ablations** | Systematic component removal; isolates contribution | No ablations or cherry-picked |
| **Baselines** | State-of-the-art and simple baselines included | Only weak or outdated baselines |
| **Confounds** | Confounding factors addressed | Obvious confounds ignored |

## Statistical Validity

| Criterion | Strong | Weak |
|-----------|--------|------|
| **Significance** | Statistical tests reported (p-values, confidence intervals) | No statistical testing |
| **Effect sizes** | Effect sizes reported (Cohen's d, lift, etc.) | Only raw metrics |
| **Multiple comparisons** | Correction for multiple comparisons when applicable | No correction |
| **Sample size** | Power analysis or justification of N | Unclear or small N without justification |

## Online Experiment Specifics (A/B Tests)

| Criterion | Strong | Weak |
|-----------|--------|------|
| **Methodology** | Clear A/B design; randomization; duration stated | Vague or missing methodology |
| **Sample size** | Adequate for desired effect; traffic allocation clear | Too small or unclear |
| **Duration** | Long enough to capture novelty effects | Too short; novelty bias likely |
| **Metrics** | Primary and secondary metrics defined | Single metric or undefined |
| **Guardrails** | Stopping rules; safety checks | No guardrails |

## Reproducibility

| Criterion | Strong | Weak |
|-----------|--------|------|
| **Code** | Code or repo linked | No code |
| **Hyperparameters** | Full hyperparameter reporting | Missing or incomplete |
| **Random seeds** | Seeds reported for reproducibility | Not reported |
| **Data splits** | Train/val/test splits described | Unclear or missing |
| **Environment** | Framework versions, hardware noted | Not specified |

## Summary Checklist

For each experiment section, verify:

- [ ] Controls and baselines are appropriate
- [ ] Ablations isolate key components
- [ ] Statistical significance and effect sizes reported
- [ ] Online experiments: sample size, duration, methodology clear
- [ ] Code/hyperparameters/seeds available for reproduction
- [ ] Results support the paper's claims
