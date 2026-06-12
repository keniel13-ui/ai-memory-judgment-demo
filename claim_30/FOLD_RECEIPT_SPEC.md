# Fold Receipts: Design Spec for the Next CLAIM-30 Artifact Layer

Status: design spec, authored by the audit lane (Fable) on 2026-06-12 from public thread
feedback. This is NOT a pre-registration, NOT a claim, and implies no result. It specifies
an artifact layer the current harness does not have, so the gap is on record before any
implementation exists. If this matures into a claim, it gets its own frozen pre-registration
first, under the house freeze protocol.

## Origin and credit

Ken (Sovereign Synapse) named this layer in a public comment on the CLAIM-30 article on
2026-06-12: treat the fold state itself as an inspectable object, because each local
receipt can be true while the system-level receipt is false. This spec operationalizes
that contribution. It also inherits Norbert Rosenwinkel's earlier as-of-decision freezing
constraint from the CLAIM-24/26 thread: the receipt must pin the policy state that was
actually evaluated, not the policy state at read time.

Current harness state, stated honestly: the CLAIM-30 evaluator folds window state
internally and exports only verdicts and triggered clauses. The fold state is not a
first-class exported artifact. That is the gap.

## Verdict and receipt are different objects

- The verdict is for routing: ALLOW, REFUSE_COMPOSITE_DRIFT, void, challenge. Small,
  operational, consumed at decision time.
- The fold receipt is for replay and review: what accumulated, what joined, what lineage
  carried forward, which window was active, who closed it, and why the composed state was
  or was not admissible.

If the receipt becomes the verdict, it is either too large to route on or too compressed
to audit later. Keeping them separate is the design decision this spec locks.

## Required receipt fields (compact, stable)

One receipt per evaluated sequence, one entry per composition window:

1. `sequence_id` and `window_id`.
2. `envelope_refs`: content hashes of the purpose envelope and composition envelope as of
   decision time. This is the as-of-decision pin; CLAIM-30 ablation 4 showed it is
   load-bearing.
3. `accumulated_sources`: the protected source set folded in this window.
4. `derived_artifacts`: each produced artifact with its inherited source set, as declared
   data-flow lineage. CLAIM-30 ablation 3 showed this closure is load-bearing.
5. `recipients_reached`: recipients receiving any artifact in the window.
6. `threshold_state`: per registered threshold, accumulated magnitude against the frozen
   window bound, including under-threshold values. Under-threshold state is regression
   material, not noise.
7. `window_close`: open, or a close record naming the boundary actor and the close event.
   Self-close voiding must be visible here, not only in the verdict.
8. `triggering_clause`: the frozen clause id that fired, or none for allowed windows.
9. `verdict_ref`: pointer to the verdict this receipt explains. The receipt references the
   verdict; it does not replace it.
10. `chain_anchor`: hash linking the receipt into the append-only evaluation log, so a
    receipt rewrite is detectable. CLAIM-30 ablation 1 showed the tamper-evident substrate
    is load-bearing.

## Receipts for allowed sequences are not optional

The matched twins and controls get receipts too. A receipt that only exists on refusal
cannot support regression: the valuable check is that an allowed twin's fold state stays
allowed for the same reasons across harness versions. Replay means recomputing the fold
from the committed operations and comparing against the stored receipt field by field.

## Size discipline

The receipt is a bounded summary, not a trace dump. Every field above is a set, scalar, or
hash with size bounded by the window's operation count. If a field cannot stay compact, it
stores a hash of the full structure plus the structure's location, and the full structure
lives next to the results file.

## What this spec does not claim

- Not CLAIM-31. A future claim candidate could be receipt soundness (every receipt is
  reproducible from the committed operations, and tampering is detectable through the
  chain anchor), but that requires its own frozen pre-registration before any result.
- No new escape class is addressed. The time-sliced / close-authority question stays open
  and is unaffected by this layer.
- No evaluator change is implied yet. Implementation order, when called: spec review,
  then evaluator export over the existing frozen fixtures and committed sequences with
  zero changes to rows, fixtures, or clauses, then receipts checked against the already
  published verdicts. Divergence between a receipt and a published verdict is a finding
  to report, not to tune away.
