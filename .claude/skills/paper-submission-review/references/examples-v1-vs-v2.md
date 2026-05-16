# Worked Examples — v1 (Draft) → v2 (Accepted) Diffs

Short worked examples taken from two real ICASSP/INTERSPEECH submissions. Use these as anchors when calibrating findings.

---

## Example 1 — Paper A: Segmental Audio Word2Vec

### Title
- **v1:** *"Segmental Sequence-to-Sequence Autoencoder: Joint Learning of Word Segmentation and Audio Word2Vec Without Supervision"*
- **v2:** *"Segmental Audio Word2Vec: Representing Utterances as Sequences of Vectors with Applications in Spoken Term Detection"*
- **Principle:** P0, P1
- **Diff move:** mechanism-first → named-contribution + payoff. The named artifact ("Segmental Audio Word2Vec") is now repeatable; the application (STD) is named.

### Abstract
- **v1 (opens with):** "we propose segmental sequence-to-sequence autoencoder, to perform unsupervised acoustic word segmentation and compress the word segments into their embeddings together."
- **v2 (opens with):** "While Word2Vec represents words (in text) as vectors carrying semantic information, audio Word2Vec was shown to be able to represent signal segments of spoken words as vectors carrying phonetic structure information."
- **Principle:** P2
- **Diff move:** mechanism dump → background → gap → claim → evidence frame.

### Operational clarity at test time
- **v1:** silent on how the policy is resolved at test time.
- **v2:** "An action a_t is then sampled from this distribution during training to encourage exploration. During testing a_t is 'segment' whenever its probability is higher."
- **Principle:** P5
- **Diff move:** add explicit train-time vs test-time policy.

### Reproducibility anchors added
- v2 adds Table 1 listing actual query words ("fail, simple, military, increases, problems"; "ernennung", etc.) and explains "5 words for each language containing a variety of phonemes were randomly selected."
- v2 adds rationale for λ = 5: "obtained empirically and obviously had to do with the average duration of the segmented spoken words."
- **Principle:** P6, P8 (defends against cherry-picking suspicion).

### Citation upgrades
- v2 swaps arXiv preprints for INTERSPEECH/ICLR venue cites for already-published references.
- v2 adds canonical citations missing in v1: GlobalPhone (Schultz), seq2seq (Sutskever et al., defending the backward decoder), LSTM (Hochreiter & Schmidhuber), Adam (Kingma & Ba).
- **Principle:** P12.

### Result interpretation
- **v2 adds (English):** "many of the word boundaries were actually identified, but many spoken words were in fact segmented into subword units."
- **v2 adds (DTW comparison):** "DTW may not be able to identify the spoken words if the speaker or gender characteristics are very different, but such different signal characteristics may be better absorbed in the audio Word2Vec training."
- **v2 admits anomaly (German):** "The reason is not clear yet, probably due to some special characteristics of the German language."
- **Principle:** P11.

### Notation cleanup
- "Y embeddings" (Y = label in ML convention) → "N segments."
- "r_#embeddings" → "r_{N/T}" (self-documenting).
- "segment gate" → "segmentation gate" (gate's task is named).
- **Principle:** P13.

---

## Example 2 — Paper B: Gate Activation Signals

### Title (the biggest move)
- **v1:** "Gate Activation Signals in Gated Recurrent Neural Networks and its **Application on Blind Phoneme Segmentation**"
- **v2:** "Gate Activation Signal **Analysis** for Gated Recurrent Neural Networks and Its **Correlation with Phoneme Boundaries**"
- **Principle:** P0 (blocker-level reframe).
- **Diff move:** the paper's evidence dominantly supports a correlation observation; v1 promised an application. v2 reframes title, abstract, sections, and conclusion to match the actual evidence. This is the highest-leverage edit observed in this dataset.

### Section reorganization
- **v1 structure:** 1. Intro → 2.1 GAS → 2.2 AE-GRNN for *Blind Phoneme Segmentation* → 2.3 RPM baseline → 3 Experiments.
- **v2 structure:** 1. Intro → 2.1 GAS → 2.2 AE-GRNN → **3. Initial Experiments and Analysis (observation)** → 4. Phoneme Segmentation (baseline + method) → 5. Experiments → 6. Conclusion.
- **Principle:** P4.
- **Diff move:** observation gets its own section before the application/verification arc. Section list now mirrors the claim.

### Abstract reframe
- **v1 (4 sentences, salesy):** "GAS provide crucial temporal information... outperformed the conventional gated recurrent neural networks approach."
- **v2 (3 sentences, calibrated):** "we analyze the gate activation signals... highly correlated with the phoneme boundaries... This correlation is further verified by a set of experiments for phoneme segmentation, in which better results compared to standard approaches were obtained."
- **Principle:** P2, P0.

### Field-appropriate metric justified
- v2 adds: "It is well-known that the F1-score is not suitable for segmentation, because over segmentation may give very high recall leading to high F1-score, even with a relatively low precision. In our preliminary experiments, a periodic predictor which predicted a boundary for every 40 ms gave F1-score 71.07 with precision 55.13 and recall 99.99, which didn't look reasonable."
- **Principle:** P7.
- **Diff move:** when a naive baseline can game the standard metric, justify the chosen metric with a worked counterexample.

### Robustness column added
- v2 Table 2 adds an SNR-6dB column. New row for HAC baseline.
- **Principle:** P8, P9.
- **Diff move:** proactively add the column reviewers would ask for; strengthen baselines.

### Figure consolidation
- v1: separate small plots per gate.
- v2 Figure 3: all five gate types (LSTM forget/input/output; GRU update/reset) as panels (a)–(e) on a shared time axis with the *same* phoneme boundary dashed lines.
- v2 Figure 5: ∆ḡ_t, ∆ḡ_t^j, E_t, E_t^j as panels (a)–(d) of one figure for direct comparison.
- **Principle:** P10.

### Notation cleanup
- v1: per-element notation `f_t^j, i_t^j, c̃_t^j` everywhere.
- v2: vector notation `f_t, i_t, c̃_t`. The per-dimension `j` superscript is reserved for `∆ḡ_t^j` where it actually matters.
- **Principle:** P13.

### Metadata cleanup
- v1 author block: `coauthor@company.com / email@address` (placeholders left in).
- v2 author block: real emails.
- **Principle:** P14.

### Conclusion discipline
- v1: "Conclusions and Future Works" + several speculative paragraphs about applying GAS to spoken term detection, analogy to bottleneck features, etc.
- v2: "6. Conclusions" only, restates the supported claim ("temporal structures highly correlated with the phoneme changes").
- **Principle:** P15.

---

## Cross-paper patterns at a glance

| Move | Paper A | Paper B |
|---|---|---|
| Title reframed | mechanism → contribution+payoff | application → observation/correlation (claim calibration) |
| Abstract restructured | yes (story frame) | yes (calibrated claim) |
| Section reorg | minor | major (observation/verification split) |
| Operational test-time clarity | added | added |
| Reproducibility anchors | major additions (query words, λ rationale) | minor |
| Citation upgrades | major (canonical tools, dataset, defending decisions) | minor |
| Figure consolidation | minor | major (multi-panel aligned figures) |
| Robustness column | — | added (SNR-6dB) |
| Result interpretation | major (anomalies admitted) | minor |
| Notation cleanup | yes | yes |
| Metadata cleanup | minor | major (real emails) |
| Conclusion alignment | tightened | tightened |
