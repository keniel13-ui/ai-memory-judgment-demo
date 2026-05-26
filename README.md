# AI Memory Judgment Demo

Status: sanitized public lab artifact. Not benchmark-grade.

This folder is a small, inspectable demo for testing one idea:

> Agent memory should be evaluated by the consequence of retrieval, not only by top-1 retrieval accuracy.

The demo uses six structured memory files, ten scenarios, and a deterministic evaluator. It does not use an LLM, embeddings, BM25, reranking, or generated answers.

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
- `SCORING_RUBRIC.md` — action classes and metrics.
- `baseline_summary.md` — plain-language summary, not scored by this evaluator.
- `results/retrieval_eval_results.md` — generated Markdown results.
- `results/retrieval_eval_results.json` — generated raw JSON results.

## Method Snapshot

- 10 internally designed scenarios.
- 21 memory objects across 6 files.
- Top-1 retrieval only.
- Deterministic TF-IDF only.
- Three retrieval text strategies:
  - `content_only`
  - `metadata_content`
  - `keyword_expanded`
- No LLM generation scored.
- No embeddings, BM25, hybrid retrieval, or reranking.
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

## Current Result

Generated from the sanitized memory objects:

| Strategy | Retrieval | Action correct | End-to-end | Benign misses | Downgrade misses | FC errors | Overblocking |
|---|---:|---:|---:|---:|---:|---:|---:|
| content_only | 9/10 | 9/10 | 9/10 | 0 | 1 | 0 | 0 |
| metadata_content | 9/10 | 9/10 | 9/10 | 0 | 1 | 0 | 0 |
| keyword_expanded | 9/10 | 9/10 | 9/10 | 0 | 1 | 0 | 0 |

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
- No modern retrieval baselines are tested.
- No cost analysis is included.

## Next Tests

The next meaningful versions should add:

1. A larger external scenario set written by someone who did not design the framework.
2. BM25 and embedding retrieval compared against this TF-IDF baseline.
3. Multi-memory retrieval, because one top-1 memory may be too brittle for judgment-lineage work.
4. Model-in-the-loop generation and blind scoring.

## License

- `run_retrieval_eval.py` — [MIT](LICENSE) — free to use, modify, and redistribute with attribution.
- All documentation and memory files — [CC BY 4.0](LICENSE-DOCS) — free to share and adapt with attribution.

Attribution: Keniel Maldonado (zep1997), AI Memory Judgment Demo, 2026.
