# Fresh Governs Replication Plan

Status: replication procedure for CLAIM-12. Not benchmark-grade.

## Goal

Test whether fresh authors independently produce usable `governs` jurisdiction metadata on the same five-scenario packet.

The first pass is already saved:

```text
external_scenarios/fresh_governs_annotations_v0_1.json
results/fresh_governs_eval_results.md
results/fresh_governs_eval_results.json
```

## Procedure

For each new pass:

1. Open a fresh model/chat with no repo, project, or prior conversation context.
2. Paste the full contents of `EXTERNAL_GOVERNS_REQUEST.md`.
3. Paste the full contents of `external_scenarios/fresh_governs_authoring_packet_v0_1.json`.
4. Ask for only the JSON annotations object.
5. Save each independent output separately.

Recommended filenames:

```text
external_scenarios/fresh_governs_annotations_v0_2.json
external_scenarios/fresh_governs_annotations_v0_3.json
```

## Evaluation Commands

Pass 2:

```bash
python3 run_fresh_governs_eval.py \
  --governs external_scenarios/fresh_governs_annotations_v0_2.json \
  --results-md results/fresh_governs_eval_results_v0_2.md \
  --results-json results/fresh_governs_eval_results_v0_2.json
```

Pass 3:

```bash
python3 run_fresh_governs_eval.py \
  --governs external_scenarios/fresh_governs_annotations_v0_3.json \
  --results-md results/fresh_governs_eval_results_v0_3.md \
  --results-json results/fresh_governs_eval_results_v0_3.json
```

## Claim Upgrade Rule

If two more independent passes also produce 5/5 scoped role-filter results, CLAIM-12 can be upgraded from:

> In one fresh-author pass...

to:

> In three independent fresh-author passes on the same five-scenario packet...

That still would not prove general reliability. It would only establish repeatability on this packet before testing harder stores with unrelated and competing policies already present.
