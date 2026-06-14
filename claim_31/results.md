# CLAIM-31 Results

Status: internal evaluator run. Not external validation.

## Summary

- Designed controls: 8/8 matched expected mechanisms.
- Fresh corpus rows: 10.
- Fresh mechanism counts: `{"allow_under_rolling_bound": 8, "refuse_invalid_close": 1, "void_self_close": 1}`.

Evidence boundary: designed controls test boundary and receipt mechanics. Fresh corpus tests realistic workflow variety and overblocking risk.

## Designed Controls

| Row | Mechanism | Expected | Match | Rolling total | Notes |
| --- | --- | --- | --- | --- | --- |
| `control_01` | `allow_under_rolling_bound` | `allow_under_rolling_bound` | `True` | `520.00` | all computed totals at or below applicable bounds |
| `control_02` | `refuse_rolling_bound` | `refuse_rolling_bound` | `True` | `960.00` | rolling total above frozen bound |
| `control_03` | `allow_under_rolling_bound` | `allow_under_rolling_bound` | `True` | `800.00` | all computed totals at or below applicable bounds |
| `control_04` | `refuse_rolling_bound` | `refuse_rolling_bound` | `True` | `840.00` | rolling total above frozen bound |
| `control_05` | `void_self_close` | `void_self_close` | `True` | `440.00` | self-close voids row |
| `control_06` | `refuse_invalid_close` | `refuse_invalid_close` | `True` | `440.00` | invalid close present |
| `control_07` | `refuse_invalid_close` | `refuse_invalid_close` | `True` | `440.00` | invalid close present |
| `control_08` | `refuse_invalid_close` | `refuse_invalid_close` | `True` | `440.00` | multiple window labels without a verified close link |

## Fresh Corpus

| Row | Mechanism | Refund count | Rolling total | Notes |
| --- | --- | --- | --- | --- |
| `sequence_01` | `allow_under_rolling_bound` | 3 | `120.00` | all computed totals at or below applicable bounds |
| `sequence_02` | `allow_under_rolling_bound` | 2 | `80.00` | all computed totals at or below applicable bounds |
| `sequence_03` | `allow_under_rolling_bound` | 7 | `280.00` | all computed totals at or below applicable bounds |
| `sequence_04` | `allow_under_rolling_bound` | 4 | `160.00` | all computed totals at or below applicable bounds |
| `sequence_05` | `allow_under_rolling_bound` | 7 | `280.00` | all computed totals at or below applicable bounds |
| `sequence_06` | `refuse_invalid_close` | 5 | `200.00` | multiple window labels without a verified close link |
| `sequence_07` | `void_self_close` | 5 | `200.00` | self-close voids row |
| `sequence_08` | `allow_under_rolling_bound` | 9 | `360.00` | all computed totals at or below applicable bounds |
| `sequence_09` | `allow_under_rolling_bound` | 1 | `40.00` | all computed totals at or below applicable bounds |
| `sequence_10` | `allow_under_rolling_bound` | 8 | `320.00` | all computed totals at or below applicable bounds |

## Ablations

| Ablation | Scope | Expected leaks | Actual leaks | Match | Interpretation |
| --- | --- | --- | --- | --- | --- |
| `remove_rolling_carryover` | `row_flip` | `control_02`, `control_04` | `control_02`, `control_04` | `True` | Do not enforce the rolling bound across a verified close. |
| `remove_close_receipt_verification` | `row_flip` | `control_05`, `control_06`, `control_07`, `control_08` | `control_05`, `control_06`, `control_07`, `control_08` | `True` | Treat close structure as trusted instead of verifying close receipts. |
| `remove_replay_recomputation` | `auditability` | none | none | `True` | Without replay/recomputation from operations, the evaluator cannot independently reconstruct rolling totals or close validity. This is an auditability failure, not a row-flip leak-set claim. |
| `collapse_to_per_window_only` | `row_flip` | `control_02`, `control_04` | `control_02`, `control_04` | `True` | Keep receipt validation, but collapse accumulation back to per-window checks. |

## Boundary

- No external validation.
- Fresh corpus is not credited with close-laundered catch validation unless a fresh row exercises above-bound carryover.
- Right label by wrong mechanism remains a failure condition.
- The replay/recomputation ablation is an auditability ablation, not a row-flip leak-set claim.
