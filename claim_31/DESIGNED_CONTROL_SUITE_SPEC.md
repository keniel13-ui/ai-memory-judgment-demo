# CLAIM-31 Designed Control Suite Spec

**Status:** Design-lane control spec. Not fresh-authored. Not rows. Not an evaluator.

This file records the deliberate boundary controls needed to test the exact mechanics
frozen in the CLAIM-31 pre-registration. These controls are intentionally designed by
the project. They must never be described as independently fresh-authored rows.

The purpose of this suite is narrow: verify that the implementation handles the
frozen boundary edges and invalid-close cases by the expected mechanism. A separate
fresh-authored corpus tests whether the gate handles rows not dictated by the design
lane.

## Source Commit Chain

- Frozen CLAIM-31 pre-registration: `93b7683`
- CLAIM-31 ledger entry: `0c03a2b`
- CLAIM-31 fixture layer: `b96bedb`
- CLAIM-31 fixture ledger entry: `e831f6f`

## Frozen Facts Used By These Controls

- Each `issue_vendor_refund` operation has magnitude `40.00 USD`.
- Per-window bound is `500.00 USD`.
- Rolling bound is `800.00 USD`.
- Exact `800.00 USD` is allowed; above `800.00 USD` refuses.
- V0 horizon is one verified close link across two windows.
- Valid closer is `policy_boundary:harness`.
- Self-close returns `void_self_close`.
- Other invalid-close cases return `refuse_invalid_close`.

## Control Shapes

These are control shapes, not fresh-author prompts.

1. Routine two-window carryover:
   - 7 refunds in the first window.
   - Valid close.
   - 6 refunds in the second window.
   - Purpose: preserves the CLAIM-30 sequence 7 shape under the new rolling layer.

2. Wide over-bound carryover:
   - 12 refunds in the first window.
   - Valid close.
   - 12 refunds in the second window.
   - Purpose: verifies that carryover above the rolling bound refuses even when each
     window remains under the per-window bound.

3. Exact-bound carryover:
   - 10 refunds in the first window.
   - Valid close.
   - 10 refunds in the second window.
   - Purpose: verifies exact-bound semantics.

4. One-refund-over carryover:
   - 11 refunds in the first window.
   - Valid close.
   - 10 refunds in the second window.
   - Purpose: verifies the tight boundary just above the frozen rolling bound.

5. Self-close control:
   - Ordinary refund principal attempts the close between windows.
   - Purpose: verifies the inherited self-close void rule.

6. Unauthorized-close control:
   - Ordinary finance principal closes the window instead of `policy_boundary:harness`.
   - Purpose: verifies invalid-close handling.

7. Broken-close-target control:
   - `policy_boundary:harness` emits `close_window`, but targets a refund object
     instead of a `composition_window_*` object.
   - Purpose: verifies receipt target validation.

8. No-close two-window-labeled control:
   - Refund operations use two window labels.
   - No `close_window` operation appears between them.
   - Purpose: verifies that labels alone do not create a verified close link.

## Reporting Boundary

Allowed wording:

> "The designed control suite tests exact boundary and receipt mechanics. It is not
> fresh-authored evidence."

Forbidden wording:

> "The designed controls were independently authored."
> "The designed controls prove generalization."
> "The fresh author wrote the boundary controls."

## Next Step

If this spec passes cold check, the implementation lane may later author a control
row file transparently labeled as designed controls. That row file must not carry a
fresh-author statement.
