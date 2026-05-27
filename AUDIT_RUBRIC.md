# Audit Rubric

How a serious reviewer attacks this work. What counts as a valid objection. What evidence would change or falsify a claim.

This document is adversarial by design. It exists so the work can be strengthened before a reviewer sees it, not after.

---

## How to use this rubric

For each objection below:
- `fatal` — if true, the claim must be retracted or substantially downgraded
- `serious` — if true, the claim requires a caveat or limitation note
- `addressable` — the objection is valid but the work acknowledges it and names the mitigation path
- `already acknowledged` — the validity threat is already in VALIDITY_THREATS.md

---

## ATTACK 1 — Internal authorship invalidates the results

**Objection:** You wrote both the scenarios and the memory objects. Any system you designed will perform well on tests you designed for it. This is not evaluation — it is self-verification.

**Severity:** `fatal` for generalization claims. `serious` for diagnostic claims.

**What would change the claim:**
- 20+ scenarios written by someone who has not read the memory files
- Blind evaluation: evaluator does not know which strategy produced which output before scoring

**Current status:** `acknowledged` — VALIDITY_THREATS.md names this as the primary threat. The claim is limited to "diagnostic evidence, not benchmark evidence."

**What the work must not say while this threat exists:**
- "The framework generalizes to other agent memory systems."
- "Action-class evaluation improves safety in production."

---

## ATTACK 2 — 10 scenarios is not enough to claim anything

**Objection:** Statistical claims require adequate sample size. Ten scenarios produces confidence intervals so wide that any result is consistent with chance.

**Severity:** `serious` for any quantified claim. `addressable` for taxonomic claims.

**What would change the claim:**
- 50+ scenarios across diverse query types
- Pre-registered scenario types before running the evaluator

**Current status:** `acknowledged` — every result statement includes "10-scenario scale" and "not benchmark-grade."

**Response to this objection:**
> The work does not make statistical claims. It makes taxonomic claims: these failure classes exist and can be distinguished. The 10-scenario dataset is sufficient to demonstrate the existence of a failure class, not to estimate its prevalence.

---

## ATTACK 3 — The action class taxonomy is arbitrary

**Objection:** Who decided that `block` is more protective than `warn`? The severity ordering (answer < answer_context < warn < verify_first < block < archive_only) reflects the authors' judgment, not a validated safety scale. A different severity ordering could produce different results.

**Severity:** `serious` — if the ordering is wrong, downgrade-miss classification changes.

**What would change the claim:**
- External domain expert review of the action class taxonomy
- Comparison to an established harm classification framework
- Sensitivity analysis: does the main finding hold under alternative severity orderings?

**Current status:** `not yet addressed` — this is a gap in the current work.

**Mitigation path:**
- Acknowledge the taxonomy is a proposal, not a standard
- Note that the key finding (divergence between retrieval accuracy and action accuracy) does not require a specific severity ordering — it only requires that `block` and `warn` differ

---

## ATTACK 4 — The embedding model is not a retrieval model

**Objection:** `llama3.2:latest` is a general-purpose language model. Its embeddings are not optimized for retrieval. A proper retrieval embedding model (nomic-embed-text, mxbai-embed-large, text-embedding-3-small) would produce meaningfully different results.

**Severity:** `serious` — the embedding results may not generalize to real RAG systems.

**What would change the claim:**
- Run at least one dedicated retrieval embedding model
- If divergence persists → structural finding, not model artifact
- If divergence disappears → the finding was specific to a weak embedding model

**Current status:** `not yet addressed` — acknowledged in embedding results limitations but no dedicated retrieval model has been tested.

**What to say while this gap exists:**
> "The embedding experiment uses a locally available general model, not a retrieval-optimized embedding model. These results are directional; dedicated retrieval model comparison is planned for v0.3."

---

## ATTACK 5 — The divergence finding may be explained by the embedding model's weaknesses, not the framework's value

**Objection:** `ollama_embed_metadata_content` has 6/10 retrieval. Maybe it just got lucky on action accuracy because its retrieval errors happened to land on safe neighbors. This would mean the framework didn't help — the embedding model just randomly avoided the dangerous case.

**Severity:** `serious` for the divergence finding as stated.

**What would change the claim:**
- Show that the benign misses in `ollama_embed_metadata_content` are not random — that they systematically land on same-action-class memories (CLAIM-03)
- This requires a larger dataset to distinguish systematic locality from chance
- Alternatively: show that across many queries, embedding misses are predictably safer than lexical misses

**Current status:** `partially addressed` — CLAIM-03 observes the pattern but acknowledges it is post-hoc and the sample is too small.

---

## ATTACK 6 — You have not tested whether real LLMs obey the action class output

**Objection:** The evaluator computes an action class deterministically from the memory's metadata. But in a real agent system, the LLM receives the memory as context and generates a response. There is no guarantee the LLM respects the action class. A model might answer confidently even when the retrieved memory says `block`.

**Severity:** `serious` — if LLMs ignore action class labels, the framework provides no practical safety guarantee.

**What would change the claim:**
- Model-in-the-loop generation experiment: retrieve a memory, append the action class to the prompt, evaluate whether the generated response is appropriately uncertain/blocked/verifying
- This is the gap between policy computation and policy enforcement

**Current status:** `acknowledged as future work` — PAPER_OUTLINE.md Section 11 names "model-in-the-loop generation" as a future direction.

**What to say while this gap exists:**
> "The current evaluator tests the policy computation step, not policy enforcement. Whether a language model respects action class constraints in generation is a separate research question."

---

## ATTACK 7 — "Retrieval accuracy is incomplete" is prior work, not your contribution

**Objection:** Mem2ActBench, the Bottlenecks paper, and others already show retrieval accuracy ≠ task accuracy. Your failure taxonomy is an incremental refinement, not a new contribution.

**Severity:** `serious` for the framing, `addressable` for the specific taxonomy.

**Response:**
The contribution is not "retrieval accuracy is incomplete." That is acknowledged as prior work. The contribution is the failure-direction taxonomy: distinguishing whether a retrieval failure is in the safe or unsafe direction. Existing work asks "did the agent succeed at the task?" Our taxonomy asks "if the agent failed, did it fail toward overconfidence or toward overprotection — and which is more dangerous?"

That distinction is not in Mem2ActBench, the Bottlenecks paper, or RAGAS.

**What to say:**
> "The claim that retrieval accuracy is incomplete is established in prior work and is cited as such. Our contribution is the safety-direction taxonomy: a classification of retrieval failures by whether they produce actions that are too permissive (false certainty, downgrade miss) or too restrictive (overblocking), which existing task-accuracy metrics do not distinguish."

---

## ATTACK 8 — The work is self-referential: you built the memory system to test, then tested it

**Objection:** The memory objects describe the authors' own AI memory project. Scenarios query that same project. The system is evaluating its own memory of itself. This creates a circularity: the framework is tested on the exact domain it was designed for.

**Severity:** `serious` for generalization. `addressable` for proof-of-concept.

**What would change the claim:**
- Apply the framework to a different domain (customer support, legal research, medical triage)
- Does the failure taxonomy still apply? Do the action classes transfer?

**Current status:** `not yet addressed` — the work is explicitly scoped to one domain.

**What to say:**
> "The current dataset is drawn from a single domain: the authors' own AI memory research project. Whether the framework and failure taxonomy transfer to other domains is an open question and a necessary validation step."

---

## What a passing audit looks like

A version of this work that survives serious review must:

1. Have at least some externally authored scenarios
2. Not claim generalization beyond the tested scale
3. Acknowledge the action-class taxonomy as a proposal requiring external validation
4. Have at least one dedicated retrieval embedding model tested
5. Clearly separate policy computation (what the evaluator tests) from policy enforcement (what a real LLM does)
6. Cite Mem2ActBench and the Bottlenecks paper as prior work, not overlapping work

The current artifact passes on 1 (partially — one external comment, not scenarios), fails on 4, and passes on all others.
