# Claim Ledger

Every claim this work makes. Each claim is tracked with evidence, current status, known weakness, next test, and wording rules.

Status levels:
- `demonstrated` — shown in the current dataset at the scale tested
- `preliminary` — directionally supported, needs external replication
- `structural` — definitional / framework claim, not empirically provable
- `forbidden` — do not make this claim

---

## CLAIM-01

**Claim:** Retrieval accuracy and action-class accuracy can diverge.

**Evidence:**
- `ollama_embed_metadata_content`: 6/10 retrieval, 10/10 action
- All 6 lexical strategies: 9/10 retrieval, 9/10 action (1 downgrade miss)
- Best lexical retrieval score is higher, but worst safety outcome

**Status:** `demonstrated` — at 10-scenario scale, internally authored

**Weakness:**
- The divergence is a single comparison between two method classes
- The embedding method uses `llama3.2:latest`, not a retrieval-optimized model
- If a proper embedding model (nomic-embed, mxbai-embed) produces 9/10 retrieval AND 10/10 action, the divergence disappears

**Next test:**
- Run dedicated retrieval model (nomic-embed-text or mxbai-embed-large)
- If divergence persists → structural property
- If divergence disappears → artifact of weak embedding model

**Allowed wording:**
> "In our small dataset, the embedding strategy with lower retrieval accuracy produced no unsafe failures, while all lexical strategies with higher retrieval accuracy produced one downgrade miss."

**Forbidden wording:**
> "Embedding retrieval is safer than lexical retrieval."
> "Higher retrieval accuracy produces worse safety results."
> "This proves the divergence is general."

---

## CLAIM-02

**Claim:** The s02 downgrade miss is a class-level lexical limitation, not a TF-IDF artifact.

**Evidence:**
- All 6 lexical strategies (3 TF-IDF + 3 BM25) miss s02 identically
- `ollama_embed_metadata_content` fixes s02 by retrieving `correction_no_overclaim_eval` (block) instead of `correction_strawman_baseline` (warn)

**Status:** `demonstrated` — within this dataset and these strategies

**Weakness:**
- Only 2 lexical method families tested (TF-IDF and BM25)
- Sparse retrieval methods like SPLADE or ColBERT not tested
- The two competing memories may share vocabulary that both TF-IDF and BM25 weight similarly — this could be a dataset artifact, not a general lexical failure

**Next test:**
- Examine the TF-IDF/BM25 scoring of `correction_strawman_baseline` vs `correction_no_overclaim_eval` directly — if the scores are very close, that confirms the disambiguation problem
- Test BM25 with different hyperparameters (k1, b) — if tuning fixes s02, it was a hyperparameter problem, not a class limitation

**Allowed wording:**
> "Both TF-IDF and BM25 fail s02 identically, suggesting the failure is a property of lexical retrieval on this memory pair, not of any specific lexical implementation."

**Forbidden wording:**
> "Lexical retrieval cannot fix this class of failure."
> "Only semantic retrieval can resolve competing corrections."

---

## CLAIM-03

**Claim:** Metadata-enriched embeddings preserve action-class locality under retrieval errors.

**Evidence:**
- All 4 benign misses in `ollama_embed_metadata_content` retrieved a memory in the same action class as expected
- s01: wrong URL memory → action still `answer`
- s07: wrong artifact memory → action still `answer`
- s08: wrong uncertainty memory → action still `verify_first`
- s09: wrong authority memory → action still `answer`

**Status:** `preliminary` — pattern observed in 4 cases, not statistically significant

**Weakness:**
- 4 cases is too few to claim locality is a structural property
- This is a post-hoc observation, not a pre-registered prediction
- Could be explained by the small memory pool: if most memories share an action class (most are `answer`), co-class retrieval is base-rate likely

**Next test:**
- Expand memory pool to 50+ memories with balanced action-class distribution
- Pre-register: does metadata embedding produce fewer cross-class benign misses than content-only?
- If yes at larger scale → legitimate finding

**Allowed wording:**
> "We observed that all four retrieval misses in the best embedding strategy landed in the same action class as the expected memory. This pattern is consistent with metadata encoding preserving action-class proximity, but the observation is post-hoc and the sample is too small to confirm it."

**Forbidden wording:**
> "Metadata embeddings preserve action-class locality."
> "The policy layer provides retrieval robustness."

---

## CLAIM-04

**Claim:** Gating rules are the safety floor — they prevent false-certainty errors regardless of retrieval strategy.

**Evidence:**
- 0 false-certainty errors across all 9 retrieval strategies (6 lexical + 3 embedding)
- Gating rules block `answer` or `answer_context` when memory has epistemic flags (correction, unresolved, superseded, verification_required)

**Status:** `demonstrated` — within this dataset; structurally supported by the gating rule design

**Weakness:**
- 0/0 is not a meaningful statistic without a positive control
- We have not tested whether the gating rules fail under adversarial conditions
- A scenario designed to produce false certainty via a gap in the gating rules might succeed
- The gating rules are our own design — we have not had them audited by a safety reviewer

**Next test:**
- Build adversarial scenarios specifically designed to bypass gating rules
- Example: a query that retrieves a memory with no epistemic flags, where the correct behavior should be `verify_first` but nothing in the memory schema requires it
- If gating rules hold under adversarial pressure → stronger claim
- If they fail → the safety floor finding is false

**Allowed wording:**
> "In the current dataset and strategy set, gating rules produced zero false-certainty errors across all strategies. This is consistent with gating rules functioning as a safety floor, but the dataset was not designed adversarially."

**Forbidden wording:**
> "Gating rules guarantee no false-certainty errors."
> "The system is safe against false confidence."

---

## CLAIM-05

**Claim:** Agent memory should be evaluated by what the retrieved memory is authorized to let the agent do.

**Status:** `structural` — this is a framework argument, not an empirical claim

**Evidence:** The framework provides a vocabulary (action classes, failure taxonomy) that existing retrieval-accuracy metrics do not. The empirical results show that the vocabulary distinguishes cases where retrieval-accuracy metrics cannot (CLAIM-01).

**Weakness:**
- "Should be evaluated" is a normative claim
- The action class taxonomy (answer, warn, verify_first, block, archive_only) is internally defined
- There is no external validation that this taxonomy maps to real-world safety consequences
- A reviewer could accept all empirical results and still reject the normative claim

**Next test:**
- External domain expert review of the action class taxonomy
- Comparison to existing safety classification frameworks (e.g., AI incident databases, harm taxonomies)
- Case study: show a real agent failure that would have been predicted by the downgrade-miss category but missed by retrieval accuracy

**Allowed wording:**
> "We propose that agent memory evaluation should include action-class authorization as a dimension alongside retrieval accuracy. Our preliminary results show this dimension captures failure cases that retrieval accuracy alone cannot."

**Forbidden wording:**
> "Retrieval accuracy is the wrong metric."
> "The framework solves the agent memory evaluation problem."

---

## CLAIM-06 — FORBIDDEN

The following claims must not appear in any public artifact:

- "We invented action-class authority evaluation." — Prior work on task-oriented memory exists (Mem2ActBench). The contribution is the safety-direction taxonomy, not action-level evaluation itself.
- "Our framework is benchmark-grade." — Internally authored, 10 scenarios, single model family.
- "Lexical retrieval is unsafe." — The claim is that one specific case fails in one direction, not a general indictment of lexical retrieval.
- "Embeddings fix the downgrade miss problem." — Only `ollama_embed_metadata_content` fixes s02. Two other embedding strategies do not.
- "The gating rules prevent all dangerous failures." — Not tested adversarially.
