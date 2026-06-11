# Append-Only Evaluation Log

This folder contains `evaluation_log.jsonl`, a tamper-evident record of selected research runs.

Each event records:

- claim id
- run label
- evidence level
- result artifact hash
- optional scenario/input file hashes
- optional evaluator/code file hashes
- previous event hash
- event hash

The log does not change claim outcomes. It records completed evaluations so later readers can detect edited, missing, or reordered log entries.

## Append A Run

```bash
python3 scripts/append_eval_log.py append \
  --claim CLAIM-29 \
  --label purpose-envelope-v0 \
  --result claim_29/results.json \
  --scenario claim_29/scenarios_control_rows_1_4_11_12.json \
  --scenario claim_29/scenarios_fresh_rows_5_10.json \
  --scenario claim_29/purpose_envelope.json \
  --scenario claim_29/role_profile.json \
  --evaluator claim_29/evaluator.py \
  --summary "PurposeEnvelopeGate V0 result, internally demonstrated."
```

## Verify The Chain

```bash
python3 scripts/append_eval_log.py verify
```

Expected output includes:

```text
chain_ok=True
```

## Evidence Boundary

This is an audit-integrity layer. It proves the log is internally chained. It does not prove that any claim is externally validated.
