# CLAIM-24 CROSS-FIELD CONSISTENCY DELTA — FALSIFIED AT INTENDED SCOPE

**Frozen 2026-08-23 22:2x EDT. Immutable. Second falsification in this lane.**

**Predecessor falsification:** `CLAIM24_CONSULT_DELTA_FALSIFIED_FREEZE_2026-08-23.md` `9f5fb47d…`
**Successor freeze under test:** `CLAIM24_CONSULT_REASON_CONSISTENCY_DELTA_FREEZE_2026-08-23.md` `c686518a…`

**Falsified by:** the same external analytical seat, again with **no filesystem access**, who
specified all four attacks in advance and predicted the NaN behaviour by reading the implied
comparison. Attacks executed by Ka'el (PHASE 1186). **No code was changed.**

**Not a breaker verdict.** Aethar wrote both freezes and both patches; Ka'el briefed the lane; the
live seat designed the attacks. All three are disqualified.

## What the successor fixed and did not fix

**Held:** notes-grep immunity; `SKIPPED_TTL_EXPIRED` + positive TTL → invalid; `SKIPPED_NO_GRANT`
+ real `grant_id` → invalid; genuinely expired grants at −2.0h still classify `TTL_EXPIRED`.

**Falsified — the enum now agrees with one chosen field while contradicting the rest of the row:**

### D1 — reason validated against TTL only, not against grant existence
```
source_consult = SKIPPED_TTL_EXPIRED, ttl_remaining_hours = -2.0, grant_id = None
→ TTL_EXPIRED
```
No grant exists, so no grant's TTL could have expired. Also reproduces with
`source_snapshot = None`.

### D2 — security classification derived from a lossy representation
`rederivation_gate.py:51,67` stores `round(ttl_remaining, 2)` — **36-second granularity.**

| actually expired by | stored | class |
|---|---|---|
| 1 s | `-0.0` | `INVALID_FOR_CELL_7` |
| 0.1 s | `-0.0` | `INVALID_FOR_CELL_7` |
| 0 s | `0.0` | `INVALID_FOR_CELL_7` |
| 36 s | `-0.01` | `TTL_EXPIRED` |

**`-0.0 >= 0` is `True` in Python.** Every grant expired by under ~18 seconds is misclassified.
`decision_timestamp` and the grant expiry could recompute this exactly; the classifier trusts the
rounded derivative instead. **This is the original defect a third time: a derived value outranking
recoverable evidence.**

### D3 — non-finite TTL yields a confident class
```
ttl_remaining_hours = nan   → TTL_EXPIRED     (nan >= 0 is False)
ttl_remaining_hours = -inf  → TTL_EXPIRED
ttl_remaining_hours = +inf  → INVALID_FOR_CELL_7
```
No finiteness validation. Malformed numeric evidence produces a definite security classification.

### D4 — milder; contradictory partial grant state passes
```
source_consult = SKIPPED_NO_GRANT, grant_id = None, source_snapshot = {...} populated
→ BLOCKED_CONTROL
```
`source_snapshot` originates from a grant. Present without `grant_id` is self-contradictory and is
not flagged.

## The finding, one level above the code

Consistency was implemented **pairwise** — one reason code checked against one field. The rule the
lane is actually reaching for is **total**:

> A fact-asserting reason code must agree with **the entire structured state required for that
> reason to be possible**, and must be validated against the least-derived evidence available,
> not against a rounded or convenience representation of it.

Three iterations, one disease:

| | Where truth lived |
|---|---|
| Original | prose (`event.notes`) |
| First repair | enum (`source_consult`) |
| Second repair | **enum + one rounded field** |
| Not yet built | least-derived evidence, checked across the whole row |

**Test-adequacy note, carried forward:** the predecessor passed 366 tests while its contract
mandated a contradiction. The successor's 13 targeted tests pass while D1–D4 are live. Green tests
from involved seats measure conformance to a specification. They do not measure whether the
specification is right.

## Status

`SECOND REMEDIATION FALSIFIED AT INTENDED SCOPE / NO CODE CHANGED / NOT A BREAKER VERDICT /
NO THIRD DELTA AUTHORIZED FROM THIS DOCUMENT`

Attack B semantics and Attack D replay policy remain deliberately outside this delta.
