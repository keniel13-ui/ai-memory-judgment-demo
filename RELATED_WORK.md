# Related Work

Status: working related-work map for a public lab artifact. This is not a completed literature review.

## Contribution Boundary

The broad claim is not original:

> Retrieval accuracy alone is incomplete for evaluating memory-augmented agents.

Existing work already separates retrieval quality from downstream use, task success, faithfulness, and hallucination. This repository should cite that work as prior art.

The narrower contribution explored here is:

> Action-class authority evaluation: evaluating agent memory not only by top-1 retrieval accuracy, but by whether the retrieved memory authorizes the right action class, and whether a failure is in the safe or unsafe direction.

The current taxonomy separates wrong retrievals into:

- `false_certainty_error`: the system acts as if the answer is settled when it should warn, verify, or block.
- `downgrade_miss`: the system retrieves a related protective memory, but one with weaker protection than required.
- `overblocking_error`: the system is more restrictive than needed.
- `benign_retrieval_miss`: the retrieved memory is wrong, but the action class remains correct.

This distinction requires an authority/access-policy layer attached to memory objects. Without action classes, a downgrade miss and a benign retrieval miss can both look like ordinary retrieval errors.

## Closest Prior Work

| Area | Representative work | Overlap | Gap this repo investigates |
|---|---|---|---|
| Retrieval vs. utilization diagnosis | Diagnosing Retrieval vs. Utilization Bottlenecks in LLM-Based Applications, arXiv:2603.02473 | Separates retrieval failure, utilization failure, and hallucination. Establishes that retrieval accuracy is not enough. | Does not classify wrong retrievals by action-class consequence or safe/unsafe direction. |
| Memory-to-action benchmarks | Mem2ActBench, arXiv:2601.19935 | Evaluates whether long-term memory supports downstream task action, not only recall. | Must be compared carefully; current hypothesis is that this repo adds a more explicit authority/action-class failure taxonomy. |
| Verified/provenance memory | TierMem: From Lossy to Verified, arXiv:2602.17913 | Addresses lossy summaries and the need for traceable backing evidence. | Focuses on retrieval completeness, evidence verification, and efficiency more than action authorization or safety-direction classification. |
| RAG evaluation | RAGAS, arXiv:2309.15217; ARES, arXiv:2311.09476 | Scores faithfulness, answer relevance, context relevance, and evaluator reliability. | Evaluates generated answers and retrieved context quality, not whether a memory object was allowed to authorize a specific action. |
| Database provenance | Classical why/how/where provenance and data lineage literature | Tracks where data came from and how outputs were produced. | This repo is closer to judgment provenance: what a memory was allowed to decide, whether it was corrected, and whether a later action respected that authority. |
| Uncertainty calibration | Uncertainty-aware RAG and agent uncertainty work | Measures whether confidence is appropriate. | This repo gates action authority before generation instead of only calibrating output confidence. |

## Positioning

The closest conceptual neighbor is retrieval/utilization diagnosis. That line of work asks:

> Did the application fail because retrieval was wrong, because the model failed to use the right evidence, or because it hallucinated?

This repository asks a narrower policy question:

> If retrieval was wrong, did the wrong memory authorize an action that was too permissive, too restrictive, or still acceptable?

That is why the current result should not be framed as "we discovered retrieval accuracy is incomplete." The stronger and more defensible frame is:

> Existing metrics can tell us that retrieval failed. Action-class authority evaluation tells us whether that failure crossed a decision boundary.

## Current Weaknesses

This artifact is intentionally small and internally authored. The biggest validity risks are:

- The scenario set is too small for statistical claims.
- Scenarios and memory objects were authored by the framework designer.
- The current result depends on one visible hard case: `s02_overclaim_eval_results`.
- The action-class taxonomy is internally defined and has not been externally validated.
- No embedding, hybrid, reranking, or model-in-the-loop baseline is implemented yet.
- Mem2ActBench may already cover part of the action-level evaluation space; it must be read carefully before claiming novelty.

## Next Comparison

The next scientific move is to compare retrieval strategies using the same scenario set and the same action-class labels:

1. TF-IDF lexical baseline.
2. BM25 lexical baseline.
3. Embedding baseline.
4. Hybrid or top-k policy aggregation baseline.

The key table to produce is not only accuracy. It should show whether two methods with similar top-1 retrieval accuracy produce different failure-class distributions.

Example target result shape:

| Strategy | Top-1 accuracy | Action accuracy | False certainty | Downgrade miss | Overblocking | Benign miss |
|---|---:|---:|---:|---:|---:|---:|
| Method A | 8/10 | 8/10 | 1 | 0 | 0 | 1 |
| Method B | 8/10 | 9/10 | 0 | 1 | 0 | 1 |

If that happens, the framework has shown why retrieval accuracy alone loses decision-relevant information.

## References To Verify Before Paper Draft

- Diagnosing Retrieval vs. Utilization Bottlenecks in LLM-Based Applications, arXiv:2603.02473.
- Mem2ActBench, arXiv:2601.19935.
- TierMem: From Lossy to Verified, arXiv:2602.17913.
- RAGAS: Automated Evaluation of Retrieval Augmented Generation, arXiv:2309.15217.
- ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems, arXiv:2311.09476.
