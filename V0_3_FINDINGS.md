# v0.3 Findings

Status: preregistered dedicated embedding run over the existing 10-scenario diagnostic dataset.

## What Changed

The v0.3 run added a dedicated local retrieval embedding model:

- model: `nomic-embed-text`
- provider: local Ollama
- same 21 memory objects
- same 10 scenarios
- same expected memory labels
- same expected action labels
- same failure taxonomy

This run followed `PREREGISTRATION_v0.3.md`.

## Result

| Strategy | Retrieval | Action correct | End-to-end | Downgrade misses | FC errors | Safety loss |
|---|---:|---:|---:|---:|---:|---:|
| `ollama_embed_content_only` | 8/10 | 9/10 | 8/10 | 1 | 0 | 4 |
| `ollama_embed_metadata_content` | 9/10 | 9/10 | 9/10 | 1 | 0 | 4 |
| `ollama_embed_keyword_expanded` | 9/10 | 9/10 | 9/10 | 1 | 0 | 4 |

## Interpretation Against The Preregistered Hypotheses

### H1 — Dedicated Retrieval Embedding Model

Prediction:

> A dedicated retrieval embedding model will improve top-1 retrieval accuracy over `llama3.2:latest` embeddings, but action-class accuracy may still diverge from retrieval accuracy.

Outcome:

- Retrieval accuracy improved substantially.
- `ollama_embed_metadata_content` moved from `6/10` retrieval to `9/10`.
- The earlier v0.2 divergence pattern did not survive as-is.
- The dedicated model behaved more like the lexical baselines: high retrieval, one downgrade miss.

Read:

> The v0.2 divergence was at least partly model-specific. A stronger retrieval embedding model improved exact retrieval but did not eliminate the s02 downgrade miss.

### H2 — Metadata-Enriched Embeddings

Prediction:

> Metadata-enriched embedding text will produce fewer cross-action-class retrieval errors than content-only embedding text.

Outcome:

- Content-only had one benign miss and one downgrade miss.
- Metadata+content had one downgrade miss and no benign misses.
- Keyword-expanded had one downgrade miss and no benign misses.

Read:

> On this 10-scenario set, metadata enrichment improved exact retrieval but did not improve action safety compared with content-only. All strategies retained the same weighted safety loss because all retained one downgrade miss.

### H3 — Top-K Conservative Aggregation

Prediction:

> Top-k conservative policy aggregation will reduce downgrade misses compared with top-1 retrieval when the stricter memory appears anywhere in the retrieved set.

Outcome:

- Not tested yet in this run.
- The persistence of s02 across TF-IDF, BM25, `llama3.2` content/keyword embeddings, and `nomic-embed-text` embeddings makes top-k coverage the next key question.

## Main Finding

The stronger model changed the v0.2 story:

- `llama3.2` metadata embeddings: lower retrieval, better action behavior.
- `nomic-embed-text` metadata embeddings: higher retrieval, same downgrade miss as lexical retrieval.

That weakens any broad claim that metadata embeddings preserve action-class locality.

It strengthens a different claim:

> The s02 failure is a persistent severity-disambiguation problem across several retrieval methods. The next question is whether the stricter correction appears in top-k, and whether policy aggregation can recover the correct action class.

## Claim Updates

- CLAIM-01 remains demonstrated only for the v0.2 comparison, not as a general method property.
- CLAIM-02 strengthens: s02 is not only a TF-IDF/BM25 problem; it persists under `nomic-embed-text`.
- CLAIM-03 weakens: action-class locality was not reproduced by the dedicated embedding model.
- CLAIM-04 remains unchanged: zero false-certainty errors, still non-adversarial.

## Next Step

Implement top-k retrieval output for lexical and embedding strategies.

The key question:

> Does `correction_no_overclaim_eval` appear in the top-k candidates for s02 even when it is not ranked first?

If yes, conservative policy aggregation can be tested.

If no, the issue is retrieval coverage, not policy aggregation.

