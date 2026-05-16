# Principles: Pre-Submission Paper Review

Synthesized from two real draft → accepted submission pairs (Segmental Audio Word2Vec; Gate Activation Signals) plus independent Gemini and Codex reviews.

These principles are ordered roughly from **deepest** (changes scope) to **surface-level** (changes prose). When reviewing a draft, walk them top-down — fixing a deeper one often makes the lower-level ones easier.

---

## P0. Claim–evidence calibration

**Principle.** The strength and shape of the claim in the title, abstract, and conclusion must not exceed what the experiments actually demonstrate. If the strongest evidence supports an *analysis* or *observation*, do not market the paper as an *application* or *method*.

**Worked example.** Gate Activation Signals v1 title: "*and its Application on Blind Phoneme Segmentation*". v2: "*and Its Correlation with Phoneme Boundaries*". The evidence is dominated by a visual/statistical correlation; segmentation is a sanity-check experiment, not a SOTA bid. The honesty move makes the paper accept-worthy.

**How to check.**
- Read the title alone. Underline the verb of the claim (proposes / extends / shows / analyzes / correlates).
- Read the strongest result in the experiments. Does that verb match?
- If a paper says "we propose a method" but the experiments show "X correlates with Y", recommend retitling and reframing.

## P1. Name the contribution as a concrete artifact

**Principle.** The reader should be able to repeat the name of what you built in five words. "Segmental Audio Word2Vec" beats "a modified seq2seq autoencoder for unsupervised joint segmentation and embedding." A draft that cannot name its artifact cleanly is harder to review positively.

**How to check.**
- Ask: what is the noun phrase the reader leaves the paper with? If there is no answer, the paper is harder to cite, recommend, or reproduce.
- The contribution name should appear in the title, the first sentence of the abstract's claim, the first sentence of the conclusion, and as the name of a section. It should not be different every time.

## P2. Story-frame the abstract: background → gap → claim → evidence

**Principle.** Don't open the abstract with "we propose". Open with the field state, identify the limitation, then state what you do and how strong the evidence is. End with a concrete characterization of the evidence ("significantly better than frame-based DTW") not a generic "outperforms baselines."

**How to check.**
- Cover the back half of the abstract; can the reader infer the gap from the front half?
- Does the last sentence give a *concrete* evidence anchor (named baseline, quantitative gap, robustness condition)?
- Count repeated phrases. If "gate activation signals" appears four times in four sentences, the abstract is doing brand-marking instead of communicating.

## P3. Cut textbook-level background; surface applications early

**Principle.** Introductions should pay reader attention only for content the target reviewer doesn't already have. Reviewers at INTERSPEECH/ICASSP/NeurIPS do not need "speech is a sequence of sounds" or "RNN is a directed cycle". Use the recovered space to mention concrete downstream applications, which makes the contribution feel useful before the technical machinery starts.

**How to check.**
- Underline any sentence in the intro that a first-year grad student in the field already knows. Recommend cutting most of them.
- After the intro, can the reader name at least one concrete application?

## P4. Section structure mirrors the contribution claim

**Principle.** If the contribution is an *observation*, the observation gets its own section *before* the application/verification section. If it is a *method*, the method section is first and applications come after. Don't bury the headline result inside a methods section.

**Worked example.** GAS v2 splits into Section 3 *Initial Experiments and Analysis* (the observation) and Section 4–5 *Phoneme Segmentation* (the verification). v1 had this as a single tangled section.

**How to check.**
- Make a one-line summary of each section. Read the list back. Does the structure tell the same story the abstract just told?
- If yes, good. If the section list looks like a methods-paper but the abstract is observation-led, propose a reorg.

## P5. Operational clarity (especially at inference time)

**Principle.** Whenever the method involves a stochastic component, a threshold, a discrete decision, or a learned hyperparameter, the paper must say *exactly* how that component behaves at training time vs at test time. Reproducibility-checking reviewers look for this first.

**Worked example.** Paper A v2 added: *"An action a_t is then sampled from this distribution during training to encourage exploration. During testing a_t is 'segment' whenever its probability is higher."* v1 was silent on the train/test policy.

**How to check.**
- For every probability distribution, sampling step, threshold, or top-k operation, the paper must specify the training behavior and the test behavior.

## P6. Add the reproducibility anchors

**Principle.** State the choices that are hard to guess from the equations:
- The exact items used (e.g., which query words were chosen; how they were chosen).
- The hyperparameter values and a one-line rationale.
- Standard preprocessing (CMVN, normalization, frame rate).
- The metric's tolerance window where applicable.
- The dataset version / split.

**How to check.** Pretend you are re-implementing the paper from scratch. Make a list of every numerical or categorical decision you would have to guess. The paper should specify each one.

## P7. Use the field-appropriate metric and *justify* it

**Principle.** For tasks where naive baselines can game one common metric, use the metric that resists the naive baseline and *explicitly show* that the naive baseline gets a good score on the lesser metric. In speech segmentation, this means: use R-value, show that a 40 ms periodic predictor gets F1 = 71, conclude that F1 is unsuitable.

**Why.** Reviewers in field venues penalize papers that use the wrong metric, even if the method is good. A short justification paragraph buys disproportionate credibility.

**How to check.** For each reported metric, ask: can a trivial baseline game this metric? If yes, the paper should report that gaming and pick a better metric.

## P8. Baseline credibility — make the comparison set hard to dismiss

**Principle.** A draft is often rejected not because the method is weak, but because the baselines are weak. Include:
- A *recognizable* primary baseline from the field (frame-based DTW for STD; HAC for segmentation).
- A *naive* baseline to anchor the bottom (random; periodic predictor).
- An *oracle* / upper-bound when feasible.
- A *robustness column* (noise injection like SNR-6dB; out-of-domain split) reviewers will otherwise ask for.

**How to check.** List the baselines. Can a reviewer point to a missing standard baseline in the field? If yes, add it.

## P9. Tables — prune redundancy, add discriminating axes

**Principle.** A table column / row earns its space by either (a) discriminating between methods or (b) anchoring the reader (oracle, random). Drop uniform columns. Add columns that proactively answer "is this robust to ___?" Cuts should buy room for higher-value evidence — they're not ends in themselves.

**How to check.** For each column: does it change the ranking? If no, consider collapsing it (e.g., keep F1, drop P/R) for non-headline languages.

## P10. Figures — one figure per comparison the reader needs to make

**Principle.** If the reader's job is to compare across N conditions, those N conditions belong in one figure with a shared axis. Splitting them across pages forces mental alignment and weakens the argument.

**Worked example.** GAS v2 Figure 3 stacks five gates' GAS means in one figure aligned to the same time axis with the *same* phoneme boundary markers. The correlation is now visible at a glance.

**How to check.** For every claimed comparison, locate the figure where the comparison is visible. If it spans pages, propose merging.

## P11. Interpret every result; flag the genuinely unexplained

**Principle.** Every nontrivial number deserves a "what does this mean" sentence. If you cannot explain a result, *say so explicitly*. Reviewers prefer "the reason is not clear yet, probably due to some special characteristics of the German language" over silently moving past an anomaly. Anomaly explanation shifts reviewer perception from "cherry-picking" to "the authors understand their own result."

**How to check.** Walk through every results paragraph. For each numerical claim, is there a sentence explaining what it implies? For each anomaly (an underperforming row, a non-monotonic trend), is it acknowledged?

## P12. Citation discipline

- **Cite the canonical source for every standard tool/dataset** you use (LSTM → Hochreiter & Schmidhuber 1997; Adam → Kingma & Ba 2015; the dataset → the dataset paper; seq2seq → Sutskever et al.).
- **Cite to defend a non-obvious architectural choice.** If you reverse the decoder, cite the paper that established the reverse-decoder convention. This pre-empts the reviewer's "why did you do that?" question.
- **Replace arXiv preprints with the published venue** once it exists.

**How to check.** Walk through every method/data choice; check the citation. Walk through every non-obvious design decision; check there's a citation defending it.

## P13. Terminology and notation hygiene

- Choose the most reader-friendly term that still distinguishes ("segmentation gate" > "segment gate").
- Avoid notation that collides with reader expectation (Y is "label" in ML, not "count of segments" — use N).
- Reserve indexed notation for when you actually index. Use vectors for the general case.
- Names of reward components should encode their meaning (`r_{N/T}` is self-documenting; `r_{#embeddings}` is not).

**How to check.** For each symbol, ask: would a reader from the field confuse this with something else? For each piece of notation more complex than scalar, ask: is the complexity earning its place?

## P14. Cleanup sweep before submission

- Author block: real emails, real affiliations, no `coauthor@company.com`.
- Cite all dataset / tool authors.
- No `TODO`, `\cite{?}`, `XXX`, draft comments.
- All figures referenced from text; all tables labeled and captioned.
- Spelling, hyphenation, and consistent capitalization of method names.

## P15. Conclusion echoes the abstract; no new speculation

**Principle.** The conclusion should restate the *supported* contribution in the same frame as the abstract, with the evidence in hand. It is not the place for new claims, future work fishing, or analogies that the experiments did not test.

**How to check.** Does the first sentence of the conclusion echo the first claim of the abstract? Does the conclusion stop where the evidence stops?

## P16. Length discipline is the consequence, not the cause

**Principle.** Page-limit pressure is relieved by cutting *low-information* prose (textbook background, repetition between sections, future-work speculation, redundant equations, separate figures that should be combined). It is *never* relieved by trimming evidence, baselines, or hyperparameter rationales.

**How to check.** Sort sections by information density. The lowest-density paragraphs are the first cut candidates.

---

## Anti-patterns to flag

(Things a draft tends to do that a reviewer will mark down.)

- **A1.** Title or abstract promises an application but the experiments are dominated by an observation (or vice versa).
- **A2.** No named contribution — the paper refers to its method differently in each section.
- **A3.** The abstract is a mechanism dump with no framing of why the field needs this.
- **A4.** Textbook-level background in the introduction.
- **A5.** A stochastic / threshold component used in the method but no explanation of its train-time vs test-time behavior.
- **A6.** Standard preprocessing or hyperparameters present in the code but not in the paper.
- **A7.** Use of a metric that can be gamed by a naive baseline, with no justification or counterexample.
- **A8.** Missing field-standard baseline.
- **A9.** Tables with high-redundancy columns; figures requiring cross-page mental alignment.
- **A10.** Results paragraphs that are flat lists of numbers with no interpretation.
- **A11.** Results paragraphs that ignore an obvious anomaly (a row that doesn't fit the story).
- **A12.** Missing canonical citation for a standard tool, dataset, or architectural choice.
- **A13.** Notation that overloads field-standard symbols (Y for "count"), or per-element notation used where vector notation suffices.
- **A14.** Author placeholders, dummy emails, TODO markers, `\cite{?}`, leftover draft annotations.
- **A15.** Conclusion that opens new threads or speculation not tested in the experiments.
- **A16.** Page-limit fixed by cutting evidence or hyperparameter detail instead of low-information prose.

---

## Output format the reviewer should produce

When applying these principles to a draft, return:

For each finding:
- **Principle reference** (P0–P16 or A1–A16)
- **Location** (section, sentence, table/figure number)
- **Quote** of the problematic text (or description of the missing element)
- **Suggested edit** (concrete — a new sentence, a reorder, a column to add)
- **Rationale** (one sentence; refer to the principle)
- **Severity**: blocker / important / minor

Sort findings by severity, then by principle number (so claim-level issues come first).
