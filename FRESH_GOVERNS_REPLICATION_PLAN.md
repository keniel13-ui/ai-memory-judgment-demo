# Fresh Governs Replication Plan

Status: completed three-pass replication procedure for CLAIM-12. Not benchmark-grade.

## Goal

Test whether fresh authors independently produce usable `governs` jurisdiction metadata on the same five-scenario packet.

The three passes are saved:

```text
external_scenarios/fresh_governs_annotations_v0_1.json
results/fresh_governs_eval_results.md
results/fresh_governs_eval_results.json
external_scenarios/fresh_governs_annotations_v0_2.json
results/fresh_governs_eval_results_v0_2.md
results/fresh_governs_eval_results_v0_2.json
external_scenarios/fresh_governs_annotations_v0_3.json
results/fresh_governs_eval_results_v0_3.md
results/fresh_governs_eval_results_v0_3.json
```

## Procedure

For each new pass:

1. Open a fresh model/chat with no repo, project, or prior conversation context.
2. Paste the full contents of `EXTERNAL_GOVERNS_REQUEST.md`.
3. Paste the full contents of `external_scenarios/fresh_governs_authoring_packet_v0_1.json`.
4. Ask for only the JSON annotations object.
5. Save each independent output separately.

Filename pattern:

```text
external_scenarios/fresh_governs_annotations_v0_N.json
```

## Evaluation Commands

Example command:

```bash
python3 run_fresh_governs_eval.py \
  --governs external_scenarios/fresh_governs_annotations_v0_N.json \
  --results-md results/fresh_governs_eval_results_v0_N.md \
  --results-json results/fresh_governs_eval_results_v0_N.json
```

## Result

Three independent fresh-author passes produced the same evaluator summary:

- `bm25_metadata_text`: 3/5 target selected, 4/5 action correct, 2 trap failures.
- `role_filter_bm25_metadata_text`: 5/5 target selected, 5/5 action correct, 0 trap failures.
- `scope_role_filter_bm25_metadata_text`: 5/5 target selected, 5/5 action correct, 0 trap failures.

CLAIM-12 can now use:

> In three independent fresh-author passes on the same five-scenario packet...

That still does not prove general reliability. It establishes repeatability on this packet before testing harder stores with unrelated and competing policies already present.
