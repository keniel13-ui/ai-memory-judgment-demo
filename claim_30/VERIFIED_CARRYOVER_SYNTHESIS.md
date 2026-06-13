# Verified Carryover and Closes as Authority Events: Design Synthesis

Status: design synthesis, authored 2026-06-12 evening on top of
`CLOSE_AUTHORITY_DESIGN_BRIEF.md`. This is not CLAIM-31, not a pre-registration,
not a result, and does not modify the frozen CLAIM-30 fixtures, rows, evaluator, or
ledger. It records one sharpening of the close-authority brief so a later
pre-registration can be written without guessing.

## Why this synthesis exists

The close-authority brief proposed a rolling or macro-window cap (section 2) and a
carryover-state list (section 4). Review on 2026-06-12 surfaced a missing
constraint: a rolling rule that carries a running total forward is trusting its own
accumulator without checking whether that accumulator is still valid.

The correction: carried state can be stale or corrupted. A macro-window rule must
verify what it is rolling over before it accumulates, or the macro-window becomes
another stale-authority surface wearing a wider label.

This connects the carryover layer directly to CLAIM-24. CLAIM-24 holds that authority
rots and a gate must re-derive from a source the agent cannot write to. The rolling
accumulator is state the gate writes to itself. So the same discipline applies to it:
state the gate carries forward is a memory that can rot, and it has to be verified, not
trusted because it exists in the gate's own record.

## The fused insight

Problem A (cross-window accumulation) and Problem B (influencing an authorized close)
are not separate. Cross-window accumulation is only as trustworthy as the close events
that segment it. You cannot verify what you are rolling over unless each close can
justify itself.

The seed, stated plainly:

> A gate that accumulates across closes must verify each close's receipt and its own
> carried state before trusting either.

This means the next design layer is not rolling totals. It is verified carryover: the
system must show from receipts that the state it carries forward is fresh, valid, and tied to legitimate
close receipts. A close is therefore an authority event in its own right, not an
anonymous boundary.

## Concrete schema

The intent above must not stay abstract. It becomes fields.

### Verified close receipt

Each close emits a receipt that has to stand on its own:

- `close_authority`: the actor or boundary eligible to close, and the rule that made it
  eligible. Reuses `close_actor`, `close_authority_id`, and `close_rule_ref` from the
  brief's registry.
- `close_reason`: a reason code from a closed vocabulary, not free text. Reuses the
  brief's reason codes (`batch_completed`, `human_review_completed`, `timebox_expired`,
  `incident_resolved`, `policy_rotation`, `manual_boundary_override`).
- `state_snapshot_at_close`: the accumulated composition state captured at the moment of
  close, before any reset. Records what the window held when it ended.
- `carryover_amount`: the specific state values declared to survive the close, separated
  from the values declared to reset.
- `receipt_hash`: an immutable hash over the close receipt and the window's fold
  receipt, written at or before close time. Borrows the CLAIM-26 paired
  authority-action pattern. Links to the brief's `prior_window_receipt_ref` and to the
  fold-receipt spec.

### Verified carryover rules

Carryover is governed by three rules that must be frozen with the envelope:

- `freshness_rule`: how recent or how many closes back carried state remains valid.
  State older than the declared horizon is stale and is not trusted as a free reset. It
  is flagged, not silently dropped and not silently accumulated.
- `invalidation_rule`: what makes carried state void. A close whose receipt does not
  verify, a broken receipt-hash chain, a missing or out-of-vocabulary reason code, or a
  self-close that the void-row rule already forbids, all invalidate the carryover that
  depended on that close.
- `replay_rule`: carried state plus the close-receipt chain must be replayable from the
  receipts alone, so a reviewer can reconstruct why a window ended and what survived
  without re-running the agent.

## How this answers the skeptic and sequence 7

The credibility risk is a reader assuming the design forces sequence 7 to lose by
changing the rules until it breaks. Verified carryover answers that without a
hand-written rule.

Under this layer, sequence 7 is not judged by a new rule aimed at its shape. Each of its
two closes is tested against the same frozen close-receipt schema:

- Legitimate two-window workflow: both closes carry verifying receipts, reasons are in
  vocabulary, the receipt-hash chain holds, and the rolling total stays under a rolling
  bound that sits above the per-window bound. Allowed, by the data.
- Laundering through closes: a close cannot justify itself, a receipt fails to verify,
  the chain breaks, or the rolling total exceeds the declared bound. Refused, by the
  data.

Same frozen standard, two outcomes determined by the receipts and the bound, not by
intent and not by a rule written after seeing the row. The rolling bound above the
window bound is what lets legitimate long work survive while laundering through closes
does not.

## Anti-fold-shopping pins

Carried forward from CLAIM-30 lessons so they are not relearned:

1. The rolling horizon, the rolling bound, the close-receipt schema, and the freshness,
   invalidation, and replay rules must be frozen with the envelope before any rows
   exist. Picking a horizon or a bound after seeing rows is fold-shopping.
2. The fresh-author packet must disclose the rolling horizon and bound as authoring
   facts, the same way the threshold disclosure pin saved class 3, or the time-sliced
   class can die by luck rather than by design.

## Boundary

This synthesis makes no new evidence claim. It does not show that verified carryover
can catch time-sliced escape, that a macro-window rule works, or that closes can be made
tamper-evident in practice. It does not change the CLAIM-30 V0 result and does not alter
the frozen fixtures, fresh-authored sequences, evaluator, results, or ledger.

If this becomes CLAIM-31, the next step is a frozen pre-registration before any rows,
fixtures, evaluator changes, or results exist. The honest open class named here remains
the closer's decision rule itself: modeling why an authorized boundary chose to close,
and holding that reasoning accountable, is harder than verifying a close after the fact
and is not solved by this synthesis.
