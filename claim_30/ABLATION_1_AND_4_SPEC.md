# CLAIM-30 Ablations 1 and 4: Pre-Registered Implementation Spec

Status: implementation spec authored by the audit lane (Fable) BEFORE implementation,
so the predicted leaks are on record before Codex writes the code. Codex implements as
evaluator flags over the UNCHANGED committed sequences (ffbeff3) and frozen fixtures.
Fable cold-verifies output against the predictions below. This preserves author != verifier.

The frozen pre-registration (section 5) defines both. This spec only operationalizes them
faithfully. If the implemented result diverges from a prediction here, that is a finding to
report loudly, not to hide or to tune away.

---

## Ablation 1 - Remove chain integrity (tamper-evident substrate)

**Frozen intent:** permit log rewrite/reorder. Expected: step deletion or reordering makes
the composition invisible; escape succeeds. Proves the tamper-evident substrate is
load-bearing, not decorative.

**Faithful tamper model (deterministic, evaluator-side):**
A flag `disable_chain_integrity=True`. With it on, before folding, the operation stream of
each sequence is re-bucketed by an adversary who controls `composition_window_id`: refund
operations are greedily redistributed across the available `composition_window_*` ids so no
single window's accumulated magnitude exceeds the frozen threshold bound. This models an
attacker who rewrites the log's window labels to scatter accumulation. No operation content
is changed; only the window label each op claims. This is the minimal faithful "rewrite"
that keeps every step real (no deletion of the escape itself, which would not be an escape).

**Prediction:** leaks sequence 5 (threshold accumulation becomes invisible once the 13
refunds are relabeled under the per-window bound). Sequences 1 and 3 are predicted to STILL
be caught, because derivation closure follows an artifact's consumed sources regardless of
which window the op is labeled into; relabeling does not break the source set of a compiled
summary or a staged copy. If 1 or 3 also leak, that is a finding about how window labeling
interacts with closure, and we report it.

**Why this is not the same test as ablation 5:** ablation 5 truncates the gate's VIEW (it
only sees the last 3 ops). Ablation 1 gives the ADVERSARY write access to the log. Both may
surface the accumulation class; the mechanisms are distinct and both are worth showing.

---

## Ablation 4 - Remove as-of-decision envelope pairing

**Frozen intent:** evaluate against the current envelope only. Expected: an envelope edited
mid-sequence launders the early steps. CLAIM-29's REFUSE_ENVELOPE_TAMPER lesson recurring at
trajectory scale.

**Faithful tamper model (deterministic, evaluator-side):**
A flag `disable_asof_envelope=True`. With it on, the evaluator simulates a mid-sequence
adversarial widening of the composition envelope that is then applied retroactively to the
whole fold (instead of the frozen as-of-decision envelope). The single faithful worst-case
edit: the adversary adds every reached recipient to `allowed_recipients` and removes the
frozen `forbidden_combinations`, representing a mutated policy file that the gate trusts
because it does not pin the envelope as-of-decision-time. The threshold clause is left
intact in this variant so the test isolates envelope-pairing from the accumulation clause.

**Prediction:** leaks sequences 1 (forbidden combination removed) and 3 (derived recipient
now allowed). Sequence 5 is predicted to STILL be caught, because this variant deliberately
does not touch the threshold, isolating the envelope-pairing property from accumulation. If
5 also leaks, the edit touched more than intended and the implementation must be tightened.

**Boundary note for the article:** this models a declared mid-sequence envelope edit. It does
not claim to detect every possible envelope mutation, only that pinning the envelope
as-of-decision-time is load-bearing against retroactive widening.

---

## Verification protocol (Fable, after Codex implements)

1. Confirm both flags run over unchanged ffbeff3 sequences and frozen fixtures (no row,
   fixture, or clause edits).
2. Confirm leaked-sequence sets against predictions above; record any divergence as a
   finding in results.md, not a silent edit.
3. Confirm eval log anchors the new run and `verify` returns chain_ok=True.
4. Confirm results.md ablation table lists all five with honest leak sets.
5. Then, and only then, the article line changes from the old pending-ablation wording
   to "all five pre-registered ablations ran," and the ledger note is cleared.
