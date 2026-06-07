# CLAIM-26 Pre-Registration: Paired Authority-Action Events

**Pre-registered:** 2026-06-06
**Status:** Harness built. Not yet run.

---

## The Claim

An action is not audit-safe unless it is paired with an immutable authority event that
records the exact source snapshot used to authorize that action, written before or
atomically with the action event.

This claim is about auditability, not runtime authorization. CLAIM-24 and CLAIM-25
tested whether a gate blocks a stale or replayed grant at execution time. CLAIM-26 tests
whether — after an action has been taken — an auditor can reconstruct from immutable
evidence exactly what authority justified it.

If the answer is no, the system is unauditable. A correct answer may have been produced
for the wrong reasons, or the evidence may have been altered after the fact.

---

## The Problem

Suppose an agent executes an action and logs "decision: ALLOW." An auditor later asks:
what source state authorized this? What policy was in effect? What snapshot was read?

Three common failure patterns:

1. **Decision-only logging:** The log says ALLOW but contains no authority record. The
   auditor cannot reconstruct why.

2. **Mutable pointer logging:** The log contains a source URI or policy reference but no
   snapshot hash. The source may have changed since the decision. The pointer no longer
   proves what was read.

3. **Separate write logging:** The log contains both authority and action records, but
   they were written independently. A crash between writes produces an action with no
   authority event. Write order is not enforced.

---

## The Four Required Properties

A paired authority-action gate must enforce:

1. **Pairing** — an authority event must exist and be linked to the action record by ID.
2. **Write order** — the authority event must be written before or simultaneously with
   the action event. A post-hoc authority event is not evidence; it is reconstruction.
3. **Snapshot binding** — the authority event must contain a snapshot hash, not just a
   mutable source URI or policy pointer. The hash freezes what was read at decision time.
4. **Immutability** — the authority record must be append-only. A mutable authority
   record can be altered to match any subsequent claim.

Two consistency checks follow from these properties:

- **Cross-record hash match:** the snapshot hash in the authority event and the action
  event must agree. If they differ, the action was taken against different evidence than
  what was recorded.
- **Audit gap check:** the authority snapshot hash must match what the source actually
  served at decision time. A hash that does not correspond to any real source state is
  an audit gap.

---

## The Baseline Gates (What These Properties Replace)

| Gate | What it checks | Scenarios it misses |
|---|---|---|
| `DecisionOnlyGate` | authority record exists, decision == ALLOW | post_hoc, mutable_ptr, hash_mismatch, tampered, audit_gap |
| `MutablePointerAuditGate` | authority exists, has source reference (hash OR uri) | post_hoc, mutable_ptr, hash_mismatch, tampered, audit_gap |
| `SeparateWriteAuditGate` | hash present, hashes match, immutable — no write order or audit gap check | post_hoc, audit_gap |

---

## The Seven Scenarios

| ID | Label | Expected | What it tests |
|---|---|---|---|
| 1 | clean | ALLOW | Clean paired action — all properties satisfied |
| 2 | unpaired | REFUSED_UNPAIRED | Action with no linked authority event |
| 3 | post_hoc | REFUSED_POST_HOC | Authority event written after the action |
| 4 | mutable_ptr | REFUSED_MUTABLE_SOURCE | Authority event has source URI but no snapshot hash |
| 5 | hash_mismatch | REFUSED_SNAPSHOT_MISMATCH | Authority and action snapshot hashes disagree |
| 6 | tampered | REFUSED_TAMPERED | Authority record is mutable — not append-only |
| 7 | audit_gap | REFUSED_AUDIT_GAP | Authority hash does not match source state at decision time |

---

## Falsification Conditions

- If `PairedAuthorityActionGate` does not return ALLOW on scenario 1, the gate is too
  strict and blocks legitimate audit-safe actions.
- If `PairedAuthorityActionGate` returns ALLOW on scenarios 2–7, the property it is
  supposed to enforce is not load-bearing in this implementation.
- If `SeparateWriteAuditGate` passes all 7 scenarios, write order enforcement adds no
  value on this packet and CLAIM-26 scope would narrow.

---

## Connection to Prior Claims

| Claim | Layer |
|---|---|
| CLAIM-24 | Re-derivation gate catches stale cached grants at execution time |
| CLAIM-25 | Signed-AND-fresh gate catches replay even on valid signatures |
| CLAIM-26 | Paired authority-action gate makes the decision reconstructible after the fact |

Re-derivation is necessary. Signed freshness is necessary. Paired auditability is
necessary. No layer is sufficient alone.

---

## Code

```bash
cd claim_26
python3 evaluator.py            # PairedAuthorityActionGate on all 7 scenarios
python3 evaluator.py baselines  # all 3 baselines vs all 7 scenarios
python3 evaluator.py full       # all 4 gates, full comparison table
```
