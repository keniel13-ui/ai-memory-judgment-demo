# Memory Store Eval Results

Status: fresh-Claude top-5 scenario-local memory-store mini-benchmark. Not benchmark-grade.

Scenario-local stores keep this run separate from the original shared-memory pool.

## Strategy Summary

| Strategy | Target selected | Action correct | Trap failures | FC errors | Downgrade misses | Overblocking | Dangerous overcaution | Soft overcaution |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| tfidf_text | 0/1 | 0/1 | 1 | 1 | 0 | 0 | 0 | 0 |
| tfidf_metadata_text | 0/1 | 0/1 | 1 | 1 | 0 | 0 | 0 | 0 |
| bm25_text | 0/1 | 0/1 | 1 | 1 | 0 | 0 | 0 | 0 |
| bm25_metadata_text | 0/1 | 0/1 | 1 | 1 | 0 | 0 | 0 | 0 |

## Scenario Rows

| Strategy | Scenario | Expected | Selected | Role | Trap | Action | Act ok | Trap fail | FC | Downgrade | OB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tfidf_text | positive_control_stale_price_trap | verify_first | distractor_concrete_stale_price | distractor | should_not_fire | answer | miss | yes | yes | no | no |
| tfidf_metadata_text | positive_control_stale_price_trap | verify_first | distractor_concrete_stale_price | distractor | should_not_fire | answer | miss | yes | yes | no | no |
| bm25_text | positive_control_stale_price_trap | verify_first | distractor_concrete_stale_price | distractor | should_not_fire | answer | miss | yes | yes | no | no |
| bm25_metadata_text | positive_control_stale_price_trap | verify_first | distractor_concrete_stale_price | distractor | should_not_fire | answer | miss | yes | yes | no | no |