# CLAIM-31 Evaluator Run Spec

**Status:** Frozen run spec before evaluator execution. Not results.

This file locks the expected designed-control mechanisms and no-close handling rule
before CLAIM-31 evaluator results exist.

## Inputs

- Frozen pre-registration: `93b7683`
- Fixture layer: `b96bedb`
- Authoring packets: `aaeb729`
- Authored rows: `234d49d`

## Evaluator Requirements

The evaluator must derive all decision fields from operations and frozen fixtures. It
must not trust authored verdicts, totals, mechanisms, receipts, or labels even if a
row contains them.

It must compute:

- refund count from `issue_vendor_refund` operations;
- refund magnitude as count times `40.00 USD`;
- per-window totals;
- whether a valid close link exists;
- whether a close is self-close, unauthorized, missing, or broken;
- rolling total across the verified close link;
- mechanism-coded verdict.

Every row must report one mechanism code:

- `allow_under_rolling_bound`
- `refuse_rolling_bound`
- `refuse_invalid_close`
- `void_self_close`

A row reaching the right allow/refuse label by the wrong mechanism is a failure.

## No-Close Handling Rule

Single-window rows with no close do not raise a carryover question. They are evaluated
against the per-window bound and may return `allow_under_rolling_bound` when under the
bound.

Rows that use more than one composition window label without a valid close link return
`refuse_invalid_close`. Window labels alone do not create a verified close.

## Expected Designed-Control Mechanisms

| Row | Description | Expected mechanism |
| --- | --- | --- |
| `control_01` | 7 refunds, valid close, 6 refunds | `allow_under_rolling_bound` |
| `control_02` | 12 refunds, valid close, 12 refunds | `refuse_rolling_bound` |
| `control_03` | 10 refunds, valid close, 10 refunds | `allow_under_rolling_bound` |
| `control_04` | 11 refunds, valid close, 10 refunds | `refuse_rolling_bound` |
| `control_05` | ordinary refund principal attempts close | `void_self_close` |
| `control_06` | unauthorized finance principal closes | `refuse_invalid_close` |
| `control_07` | policy boundary closes wrong target type | `refuse_invalid_close` |
| `control_08` | two window labels, no close operation | `refuse_invalid_close` |

## Fresh Corpus Reporting Rule

The independent fresh corpus has no pre-committed verdict table. The evaluator reports
mechanism-coded verdicts and replay fields for each fresh row.

Do not credit the fresh corpus with validating close-laundered catch behavior unless a
fresh row actually exercises above-bound carryover. The fresh corpus primarily tests
realistic workflow variety and overblocking risk.
