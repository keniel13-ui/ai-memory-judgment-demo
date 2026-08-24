# CLAIM-24 CONSULT-REASON DELTA — FALSIFIED AT INTENDED SCOPE

**Frozen 2026-08-23 21:59 EDT. Immutable. Do not rewrite retroactively.**
Purpose: preserve the failed first repair exactly as it existed, so that repairing it later
cannot make this failure hypothetical.

**Falsified by:** an external analytical seat with **no filesystem access**, who predicted the
defect from the shape of the change alone and specified the attacks before any of them were run.
Attacks executed by Ka'el (PHASE 1182) and independently reproduced by Aethar (PHASE 412).

**This is not a breaker verdict.** No qualified breaker has ruled. Aethar wrote the freeze and the
patch; Ka'el wrote the brief that opened the lane. Both are disqualified. The precise state is:
*an adversarial test exposed a contradiction the frozen contract permits.*

---

## 1. State at time of failure

| Artifact | SHA-256 (first 16) |
|---|---|
| `CLAIM24_CONSULT_REASON_DELTA_FREEZE_2026-08-23.md` | `9f3dda8c2bffa506` |
| `claim_24/gate_interface.py` | `94e6cbe3da8f0b81` |
| `claim_24/mandate_cell7.py` | `40c69bce32cad787` |
| `claim_24/rederivation_gate.py` | `9dc272b455da145b` |
| `claim_24/timestamp_only_gate.py` | `acb4efa354566410` |
| Aethar implementation receipt | `a8bf7da96da012e9` |

**Maker tests: 366 passed, 23 subtests.** Recorded here as evidence about **test adequacy**, not
implementation correctness. 366 tests passed while Attack A was live in the code.

## 2. The clause that mandated the defect

`CLAIM24_CONSULT_REASON_DELTA_FREEZE_2026-08-23.md`, **R3**, verbatim:

> R3. `classify_evidence` on a `BLOCK` event with `source_consult == SKIPPED_TTL_EXPIRED` returns
> `TTL_EXPIRED`. Any other `BLOCK` returns `BLOCKED_CONTROL`. It must not read `event.notes` for
> this branch. **`ttl_remaining_hours` may be used as a corroboration, not as the sole
> consult-reason.**

The mapping is unconditional; the raw field is **optional**. The contract required the behaviour
Attack A exploits. This was not an implementation slip against the freeze — the implementation is
faithful to it.

## 3. Attack results, as run

### A — CENTERPIECE. Reproduced.

```
input   source_consult      = SKIPPED_TTL_EXPIRED
        ttl_remaining_hours = +17.4
        decision            = BLOCK
output  evidence_class      = TTL_EXPIRED
```

The reason code asserts the TTL expired. The structured field on the same row says 17.4 hours
remain. **The classifier believes the label and never consults the field.** These cannot both be
authoritative. What the classifier may not legitimately do is silently choose one.

### B — NOT YET A PROVEN DEFECT. Semantics undefined.

```
input   source_consult = CONSULTED, source_current = None, decision = ALLOW
output  evidence_class = UNCHANGED_CONTROL
```

Invalid **only if** the contract requires consultation to yield a non-null `source_current`.
Consultation could legitimately return "no current value." **The contract does not say. Define the
semantics before calling this a bug.**

### C — Strong, conditional on grant semantics.

```
input   source_consult = SKIPPED_NO_GRANT, grant_id = "real-grant-id"
output  evidence_class = BLOCKED_CONTROL   (contradiction not flagged)
```

Strong if `grant_id` present means a grant existed for that event.

### D — DIFFERENT CATEGORY. Schema evolution, not the typed-oracle defect.

```
input   AuthorityEvent constructed with no source_consult
output  TypeError: missing 1 required positional argument
```

Pre-delta serialized rows cannot be constructed. Rejection is defensible; **a constructor crash is
not a chosen replay policy.** Reject / migrate / re-derive must be decided and recorded. **Do not
merge this into the main finding.**

## 4. The finding, stated at the right level

The defect was never about strings. It is about **authority placement**.

| Version | Where truth lived |
|---|---|
| Original | prose determines truth (`"ttl expired" in event.notes.lower()`) |
| First repair | **enum determines truth** (`source_consult == SKIPPED_TTL_EXPIRED`) |
| Correct | **evidence determines truth**; the reason code records *why the system acted* and must remain consistent with evidence wherever that proposition is independently checkable |

**Structure is not evidence merely because it has a schema. A typed field can lie as cleanly as
prose.**

ANP2's June constraint was never "don't use strings." It was: *do not let a derived label outrank
the raw field sitting on the same row.* The first repair satisfied the letter and missed the rule.

## 5. Required invariant for the successor delta

> When a reason code asserts a proposition independently derivable from structured evidence,
> classification MUST validate that proposition against the structured evidence. A contradiction
> MUST NOT produce an ordinary evidence class; it must produce `INVALID_FOR_CELL_7`.

Reason codes split into two kinds, and the contract must say which is which:

- **Cross-checkable** — `SKIPPED_NO_GRANT`, `SKIPPED_TTL_EXPIRED`. Assert facts other fields
  represent. **Must agree or be invalid.**
- **Not derivable from raw state alone** — `CONSULTED`, `UNREACHABLE`,
  `SKIPPED_TIMESTAMP_ONLY`. Record an action or outcome. Consistency rules must be stated
  separately, not assumed.

## 6. Status

`FIRST REPAIR FALSIFIED AT INTENDED SCOPE / NOT A BREAKER VERDICT / SUCCESSOR DELTA AUTHORIZED /
BREAKER PENDING`

The notes-grep removal **holds** and is not falsified. Verified: renaming the note to
`"grant lifetime elapsed"` or `"EXPIRADO"` still yields `TTL_EXPIRED`; the literal string
`"ttl expired"` on a no-grant BLOCK stays `BLOCKED_CONTROL`. That half of the freeze did its job.

Neither Aethar nor Ka'el may clear the successor.
