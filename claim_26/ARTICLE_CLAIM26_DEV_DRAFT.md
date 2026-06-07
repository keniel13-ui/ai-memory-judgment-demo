# The Agent Was Allowed to Act. The Log Could Not Prove Why.

*AI Memory Judgment - CLAIM-26*

---

CLAIM-24 tested stale cached grants.

CLAIM-25 tested signed responses that were authentic but not fresh.

Both were runtime authorization problems. The question was: should the agent be allowed to act right now?

CLAIM-26 moves one layer later.

After the action is taken, can an auditor reconstruct exactly what authority justified it?

If the answer is no, the action may have been correct, but the system is not audit-safe.

That distinction matters.

A log that says `ALLOW` is not the same as evidence. A source URI is not the same as the source state that was read. A matching pair of records is not enough if one was written after the fact.

That is the CLAIM-26 finding:

> An action is not audit-safe unless it is paired with an immutable authority event that records the exact source snapshot used to authorize that action, written before or atomically with the action event.

---

## The Failure

Imagine an agent takes a sensitive action.

Later, an auditor asks:

```text
Why was this action allowed?
What source state was read?
What policy version was active?
Was that evidence frozen before the action, or reconstructed later?
```

A weak system answers:

```text
decision: ALLOW
```

That is not enough.

Another weak system answers:

```text
source_uri: https://policy-store.internal/policies/active
```

That is better, but still not enough. The URI can point to a policy that changed after the action. It proves where the system might have looked. It does not prove what the system actually read at decision time.

A stronger-looking system writes both records:

```text
authority event
action event
```

But if those records are written separately, the system can still fail. A crash, reorder, retry, or manual reconstruction can leave the action record paired with authority evidence that was written after the action.

That is the subtle case. It looks like what a real engineer might ship.

And it is the interesting baseline in this result.

---

## What CLAIM-26 Tests

The packet tests seven scenarios:

| ID | Label | Expected | What it tests |
|---|---|---|---|
| 1 | clean | `ALLOW` | Clean paired action |
| 2 | unpaired | `REFUSED_UNPAIRED` | Action with no linked authority event |
| 3 | post_hoc | `REFUSED_POST_HOC` | Authority event written after the action |
| 4 | mutable_ptr | `REFUSED_MUTABLE_SOURCE` | Source URI exists, but no frozen snapshot hash |
| 5 | hash_mismatch | `REFUSED_SNAPSHOT_MISMATCH` | Authority and action hashes disagree |
| 6 | tampered | `REFUSED_TAMPERED` | Authority record is mutable |
| 7 | audit_gap | `REFUSED_AUDIT_GAP` | The recorded hash does not match the source state at decision time |

The closing gate is `PairedAuthorityActionGate`.

It requires:

1. A linked authority event
2. Authority written before or atomically with the action
3. A frozen source snapshot hash
4. Matching authority/action snapshot hashes
5. Immutable authority evidence
6. A snapshot hash that matches the source state at decision time

This is not trying to prove production completeness. It is testing the structural audit boundary.

---

## The Result

First run:

```text
PairedAuthorityActionGate: 7/7
DecisionOnlyGate:          2/7
MutablePointerAuditGate:   2/7
SeparateWriteGate:         5/7
```

Full comparison:

| Gate | Score | What it misses |
|---|---:|---|
| `PairedAuthorityActionGate` | 7/7 | nothing on this packet |
| `DecisionOnlyGate` | 2/7 | post_hoc, mutable_ptr, hash_mismatch, tampered, audit_gap |
| `MutablePointerAuditGate` | 2/7 | same failures; accepts URI in place of frozen hash |
| `SeparateWriteGate` | 5/7 | post_hoc and audit_gap; hash is present but write order and source verification are not enforced |

The `SeparateWriteGate` result is the important one.

It passes five out of seven scenarios. It has hashes. It checks immutability. It catches unpaired actions, mutable pointers, hash mismatches, and tampered records.

That sounds strong.

But it still accepts:

```text
post_hoc
audit_gap
```

Those two failures are the claim.

---

## Why Separate Writes Are Not Enough

In the `post_hoc` scenario, the action is written first.

The authority event appears later.

The records may look consistent after the fact, but the authority event did not exist before the action. That is not prior authorization. That is reconstruction.

An auditor should reject it.

The `SeparateWriteGate` accepts it because it checks the shape of the records, not the write order.

In the `audit_gap` scenario, the authority and action records agree with each other. The snapshot hashes match. The record is immutable.

But the hash does not match what the source was actually serving at decision time.

On this packet, the verification context provides the ground truth directly. In a real deployment, this requires either a time-indexed source log or an independent snapshot registry. That is a next layer, not a hidden assumption.

The audit trail is internally consistent and externally unverifiable.

That is the other failure.

If a system cannot prove that the frozen evidence corresponds to the real source state at the moment of decision, the audit trail can still be wrong while looking clean.

---

## Why This Is Different From CLAIM-24 and CLAIM-25

CLAIM-24 asked:

```text
Did the source conditions still hold at execution time?
```

CLAIM-25 asked:

```text
Was the signed source response fresh enough to trust?
```

CLAIM-26 asks:

```text
After the action, can we prove what authority evidence justified it?
```

These are different layers.

A gate can block stale grants and still leave a weak audit trail.

A source response can be signed and fresh and still fail to produce reconstructible evidence.

An action can be correct and still unauditable.

That is the point.

---

## The Minimum Audit-Safe Shape

For this packet, the minimum shape is:

```json
{
  "authority_event_id": "auth-001",
  "grant_id": "grant-abc",
  "decision": "ALLOW",
  "snapshot_hash": "sha256:policy_v21_sequence_42",
  "source_sequence": 42,
  "policy_version": "v2.1",
  "run_id": "run-001",
  "is_immutable": true,
  "written_at": "2026-06-06T12:00:01Z"
}
```

And the action must point back to it:

```json
{
  "action_id": "act-001",
  "authority_event_id": "auth-001",
  "run_id": "run-001",
  "snapshot_hash": "sha256:policy_v21_sequence_42",
  "written_at": "2026-06-06T12:00:02Z"
}
```

The important parts:

- The action references the authority event.
- The authority event was written first or atomically with the action.
- The same snapshot hash appears in both records.
- The authority record is immutable.
- The snapshot hash matches what the source served at decision time.

If any of those fail, the record may still be useful operationally, but it is not audit-safe under CLAIM-26.

---

## What This Does Not Claim

This is not a full compliance framework.

The packet is internally authored. The logs, hashes, source states, and records are simulated. The result validates the gate structure on seven scenarios. It does not prove that this is sufficient for SOC 2, HIPAA, finance, legal discovery, or any production audit requirement.

It also does not solve:

- distributed transaction design
- real append-only storage selection
- hash canonicalization
- source compromise
- multi-source authority records
- privacy rules for storing audit snapshots
- retention windows

Those are next layers.

The narrower claim is this:

If an agent takes an action and the system cannot pair that action with immutable authority evidence containing the exact source snapshot used to authorize it, written before or atomically with the action, the action is not audit-safe.

---

This claim was pre-registered before the harness was built. Pre-registration file is in the repo: `claim_26/CLAIM_26_PREREGISTRATION.md`.

---

## Reproduce It

The harness is in the public repo:

```bash
cd claim_26
python3 evaluator.py full
```

Result:

```text
Paired       7/7
Decision     2/7
MutPtr       2/7
SepWrite     5/7
```

The surprising result is not that the strongest gate wins.

The useful result is that the good-looking baseline still fails in two places.

Separate writes are not enough.

The authority event has to be paired with the action event, bound to the same snapshot, and written before or atomically with the action.

Otherwise, the log may say `ALLOW`.

But the audit trail cannot prove why.

---

*CLAIM-26 pre-registered on June 6, 2026. Harness built and first run completed the same day. Results are reproducible from the repo.*

*This is part of an ongoing series: falsifiable claims about AI agent memory and authority, tested publicly, with limits stated up front.*
