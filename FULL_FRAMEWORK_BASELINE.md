# Full-Framework Baseline vs Retrieval Baseline

Status: orientation note. This file separates two baseline questions that are easy to confuse.

## Why This Exists

The current public repo focuses on retrieval strategy and action-class consequences. It compares TF-IDF, BM25, and embedding retrieval methods.

That is not the same as testing the whole memory framework against a summary-only baseline.

Both questions matter, but they answer different things.

## Baseline Lane 1 — Full Framework

Question:

> Does layered memory produce better action-class decisions than a strong summary-only memory baseline?

Local artifact:

```text
/Users/kenielmaldonado/ai-memory-six-file-demo/
```

Current local result:

| System | Correct | False-certainty errors | Overblocking errors |
|---|---:|---:|---:|
| layered memory | 10/10 | 0 | 0 |
| strong summary baseline | 7/10 | 0 | 0 |

Interpretation:

- This is the full-framework baseline lane.
- The baseline is a strong generic summary, not an intentionally weak strawman.
- The layered system's edge comes from highest-severity action classes such as `verify_first` and `block`.
- The result is still small, internally authored, and deterministic.
- It is not benchmark-grade evidence.

Safe wording:

> On a small internally authored deterministic policy-decision set, layered memory produced more precise high-severity action classes than a strong summary-only baseline.

Forbidden wording:

> Layered memory is proven better than summaries.

## Baseline Lane 2 — Retrieval Strategy

Question:

> Do retrieval methods differ in exact retrieval accuracy and action-class consequences?

Public artifact:

```text
/Users/kenielmaldonado/ai-memory-judgment-demo-public/
```

Article:

```text
https://dev.to/zep1997/higher-retrieval-accuracy-had-the-worse-safety-result-3l78
```

Current public result family:

- TF-IDF lexical baselines.
- BM25 lexical baselines.
- local Ollama embedding run with `llama3.2:latest`.
- dedicated retrieval embedding run with `nomic-embed-text`.

Current result shape:

- Lexical strategies: high retrieval, one `s02` downgrade miss.
- `llama3.2` metadata embeddings: lower retrieval but no downgrade miss.
- `nomic-embed-text`: high retrieval, same `s02` downgrade miss.

Interpretation:

- This is the retrieval-baseline lane.
- It does not prove the whole framework against summaries.
- It isolates the retrieval layer and asks whether retrieval accuracy tracks action correctness.

Safe wording:

> Article 8 tests retrieval baselines, not the full framework baseline.

Forbidden wording:

> Article 8 proves the whole memory framework.

## Current Honest Map

| Question | Artifact | Current status |
|---|---|---|
| Does layered memory beat summary-only memory? | `ai-memory-six-file-demo` | local/internal baseline exists; not yet packaged publicly like the retrieval repo |
| Do retrieval methods differ in action consequence? | `ai-memory-judgment-demo-public` | public repo/article exists |
| Does the framework generalize externally? | not yet | unproven |
| Does a real LLM obey action classes in generation? | not yet | untested |
| Does top-k aggregation fix s02? | next | untested |

## Next Packaging Fix

The full-framework baseline should be packaged publicly or mirrored into this repo before making stronger claims.

Minimum package:

- summary baseline,
- layered memory files,
- scenario set,
- deterministic evaluator,
- results,
- validity threats,
- allowed/forbidden wording.

