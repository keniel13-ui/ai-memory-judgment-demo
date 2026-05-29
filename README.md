# AI Memory Judgment Demo

Status: sanitized public lab artifact. Not benchmark-grade.

This folder is a small, inspectable demo for testing one idea:

> Agent memory should be evaluated by the consequence of retrieval, not only by top-1 retrieval accuracy.

The demo uses six structured memory files, ten scenarios, and a deterministic evaluator. It does not use an LLM, embeddings, reranking, or generated answers.

## What This Is

This is a public, sanitized version of a private diagnostic harness used while developing the article:

> [I Tested Three AI Memory Retrieval Strategies. The Hard Failure Was Semantic](https://dev.to/zep1997/i-tested-three-ai-memory-retrieval-strategies-the-hard-failure-was-semantic-28nb)

The private harness contained project-specific memory objects. This public version replaces them with generic long-running-agent examples.

Because the memory objects were sanitized and rewritten, this artifact does **not** reproduce the private article table exactly. It preserves the evaluation structure and a representative semantic hard case.

## Files

Memory layers:

1. `01_persistence.md`
2. `02_corrections.md`
3. `03_uncertainty.md`
4. `04_failure_recovery.md`
5. `05_authority_policy.md`
6. `06_access_policy.md`

Supporting files:

- `scenarios/retrieval_scenarios.json` — 10 scenario labels.
- `run_retrieval_eval.py` — deterministic TF-IDF evaluator.
- `run_embedding_eval.py` — local Ollama embedding evaluator.
- `run_topk_inspection.py` — deterministic top-k inspection for the s02 downgrade miss.
- `run_topk_aggregation_eval.py` — conservative top-k action aggregation evaluator.
- `run_aligned_topk_aggregation_eval.py` — query-aligned top-k block-elevation evaluator.
- `SCORING_RUBRIC.md` — action classes and metrics.
- `RESEARCH_PROTOCOL.md` — formal research question, variables, metrics, validity threats, and reproducibility notes.
- `RELATED_WORK.md` — honest map of closest prior work and contribution boundary.
- `POSITIONING_NOTES.md` — public-framing guardrails that separate empirical results, framework claims, and speculation.
- `VALIDITY_THREATS.md` — explicit risk register for the current demo and next experiments.
- `FULL_FRAMEWORK_BASELINE.md` — separates the full-framework baseline from the retrieval-baseline article.
- `METRICS.md` — current and planned metrics for comparison.
- `EXPERIMENT_PLAN.md` — staged upgrades from demo to stronger evaluation.
- `v0.2_experiment_plan.md` — next semantic-retrieval comparison plan.
- `PREREGISTRATION_v0.3.md` — frozen hypotheses before dedicated embedding/top-k experiments.
- `CLAIM_LEDGER.md` — claim status, evidence, weaknesses, and allowed/forbidden wording.
- `AUDIT_RUBRIC.md` — adversarial objections and evidence needed to change claims.
- `REVIEWER_PANEL.md` — reviewer personas used to pressure-test the work.
- `EMBEDDING_FINDINGS.md` — first local embedding run and interpretation.
- `V0_3_FINDINGS.md` — preregistered `nomic-embed-text` run and claim updates.
- `TOPK_FINDINGS.md` — top-k inspection and conservative aggregation results for the s02 downgrade miss.
- `PAPER_OUTLINE.md` — paper-style report structure for future writeup.
- `baseline_summary.md` — plain-language summary, not scored by this evaluator.
- `results/retrieval_eval_results.md` — generated Markdown results.
- `results/retrieval_eval_results.json` — generated raw JSON results.

## Method Snapshot

- 10 internally designed scenarios.
- 21 memory objects across 6 files.
- Top-1 retrieval only.
- Deterministic lexical retrieval only.
- Two retrieval methods:
  - TF-IDF
  - BM25
- Three text-construction strategies for each retrieval method:
  - content only
  - metadata + content
  - metadata + content + retrieval terms
- No LLM generation scored.
- No embeddings, hybrid retrieval, or reranking.
- Each memory object carries structured fields that determine its action/access policy.
- The evaluator retrieves one memory, computes an action class, and compares it with the expected action.

## Action Classes

- `answer`: safe to answer directly.
- `answer_context`: safe to provide background, but not final authority.
- `warn`: answer with caution or limitation.
- `verify_first`: check the current record before answering.
- `block`: do not make the claim or take the action.
- `archive_only`: memory should not steer the current action.

## Run

```bash
python3 run_retrieval_eval.py
```

The command regenerates:

- `results/retrieval_eval_results.md`
- `results/retrieval_eval_results.json`

For the local embedding experiment, run:

```bash
python3 run_embedding_eval.py
```

This requires Ollama running locally and regenerates:

- `results/embedding_eval_results.md`
- `results/embedding_eval_results.json`

## Current Result

Generated from the sanitized memory objects:

| Strategy | Retrieval | Action correct | End-to-end | Benign misses | Downgrade misses | FC errors | Overblocking |
|---|---:|---:|---:|---:|---:|---:|---:|
| tfidf_content_only | 9/10 | 9/10 | 9/10 | 0 | 1 | 0 | 0 |
| tfidf_metadata_content | 9/10 | 9/10 | 9/10 | 0 | 1 | 0 | 0 |
| tfidf_keyword_expanded | 9/10 | 9/10 | 9/10 | 0 | 1 | 0 | 0 |
| bm25_content_only | 9/10 | 9/10 | 9/10 | 0 | 1 | 0 | 0 |
| bm25_metadata_content | 9/10 | 9/10 | 9/10 | 0 | 1 | 0 | 0 |
| bm25_keyword_expanded | 9/10 | 9/10 | 9/10 | 0 | 1 | 0 | 0 |

## Interpretation

The sanitized demo is intentionally small and should not be read as validation.

The useful result is the remaining hard case:

> A query asking whether an internal eval "proves" the framework works retrieves a related baseline-fairness correction instead of the stricter overclaiming correction.

That produces a `warn` when the expected action is `block`.

This is a **downgrade miss**:

- the retrieved memory is protective,
- the system does not confidently answer,
- but the protection level is too weak.

In other words:

> Right neighborhood, wrong severity.

That is the core failure this demo is meant to expose.

## Not Claimed

Do not treat this as:

- benchmark evidence
- external validation
- proof that structured memory generalizes
- proof that TF-IDF is enough
- proof that retrieval terms solve semantic retrieval
- evidence about LLM generation behavior

## Known Limitations

- Scenarios are internally designed.
- Memory objects are authored by the framework designer.
- Retrieval terms are internal semantic labels, not externally validated query expansions.
- The memory pool is tiny.
- The evaluator is deterministic.
- Retrieval and memory-object design are entangled.
- No semantic retrieval baseline is tested.
- No cost analysis is included.

## Next Tests

The next meaningful versions should add:

1. A larger external scenario set written by someone who did not design the framework.
2. Embedding retrieval compared against the lexical baselines.
3. Multi-memory retrieval, because one top-1 memory may be too brittle for judgment-lineage work.
4. Model-in-the-loop generation and blind scoring.

## License

- `run_retrieval_eval.py` — [MIT](LICENSE) — free to use, modify, and redistribute with attribution.
- All documentation and memory files — [CC BY 4.0](LICENSE-DOCS) — free to share and adapt with attribution.

Attribution: Keniel Maldonado (zep1997), AI Memory Judgment Demo, 2026.
