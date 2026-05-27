# Embedding Findings

Status: first local semantic-retrieval run. Not benchmark-grade.

## Setup

Runner:

```bash
python3 run_embedding_eval.py
```

Provider:

- Local Ollama.
- Model: `llama3.2:latest`.
- Same 21 memory objects.
- Same 10 internal scenarios.
- Same action-class policy and failure taxonomy.

## Summary

| Strategy | Retrieval | Action correct | End-to-end | Benign misses | Downgrade misses | FC errors | Overblocking |
|---|---:|---:|---:|---:|---:|---:|---:|
| lexical best/current | 9/10 | 9/10 | 9/10 | 0 | 1 | 0 | 0 |
| ollama_embed_content_only | 5/10 | 8/10 | 5/10 | 3 | 1 | 0 | 1 |
| ollama_embed_metadata_content | 6/10 | 10/10 | 6/10 | 4 | 0 | 0 | 0 |
| ollama_embed_keyword_expanded | 4/10 | 7/10 | 4/10 | 3 | 1 | 0 | 2 |

## s02 Result

The lexical methods all missed `s02_overclaim_eval_results` the same way:

- expected memory: `correction_no_overclaim_eval`
- retrieved memory: `correction_strawman_baseline`
- expected action: `block`
- computed action: `warn`
- failure class: downgrade miss

The embedding run split:

- `ollama_embed_content_only` also missed s02 and produced the same downgrade miss.
- `ollama_embed_metadata_content` retrieved `correction_no_overclaim_eval` and produced the correct `block` action.
- `ollama_embed_keyword_expanded` missed s02 and retrieved `uncertainty_speculative_theory`, producing `verify_first` instead of `block`.

## Interpretation

The cleanest read is:

> Semantic retrieval can fix the s02 lexical failure, but only when the structured metadata is included in the embedded text.

That means s02 is not purely unsolvable by retrieval. However, the wider result is more important than the one scenario:

> The best embedding strategy had lower top-1 retrieval accuracy than lexical retrieval, but higher action accuracy.

`ollama_embed_metadata_content` scored only 6/10 on top-1 retrieval but 10/10 on action correctness. Four retrieval misses were benign because they still produced the right action class.

That is direct evidence for the framework's central claim:

> Retrieval accuracy and action-class correctness can diverge. The failure class matters.

## Row-Level Secondary Finding

The strongest row-level result is in `ollama_embed_metadata_content`.

That strategy had four top-1 retrieval misses:

| Scenario | Expected memory | Retrieved memory | Expected action | Retrieved action |
|---|---|---|---|---|
| `s01_public_post_url` | `public_post_live_url` | `next_artifact_public_harness` | `answer` | `answer` |
| `s07_next_artifact` | `next_artifact_public_harness` | `current_system_overview` | `answer` | `answer` |
| `s08_speculative_theory` | `uncertainty_speculative_theory` | `uncertainty_public_claims` | `verify_first` | `verify_first` |
| `s09_latest_instruction` | `authority_user_latest_steers` | `recovery_startup_order` | `answer` | `answer` |

Every miss landed in a memory with the same action class as the expected memory.

Preliminary interpretation:

> Metadata-enriched embeddings may preserve action-class locality under some retrieval errors. In this run, wrong top-1 retrievals were still policy-compatible, which let the authority layer remain correct even when exact retrieval failed.

Do not overstate this. The dataset is too small to claim that metadata embeddings generally cluster by action class. The honest claim is narrower: this run exposes a case where action correctness survived retrieval error, and ordinary top-1 retrieval accuracy would hide that distinction.

## Limits

- This uses a local general-purpose Ollama model, not a dedicated embedding benchmark model.
- The dataset is still only 10 internal scenarios.
- The result should not be generalized beyond this sanitized demo.
- External scenarios and a stronger embedding model are needed before stronger claims.
