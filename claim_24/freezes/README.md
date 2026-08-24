# CLAIM-24 consult-reason freezes

Frozen contracts and falsification records for the CLAIM-24 evidence-classification lane,
2026-08-23. Published so the chronology in the accompanying write-up is inspectable by someone
who did not write it.

**These are specifications and failure records. The repair code is NOT in this branch and is NOT
on `main`.** It is maker-only and has not been attacked by an independent seat.

## Chronology

| Order | File | SHA-256 (first 8) | What it is |
|---|---|---|---|
| 1 | `CLAIM24_CONSULT_REASON_DELTA_FREEZE_2026-08-23.md` | `9f3dda8c` | First repair contract. **Its R3 mandated the defect** that later falsified it. |
| 2 | `CLAIM24_CONSULT_DELTA_FALSIFIED_FREEZE_2026-08-23.md` | `9f5fb47d` | First falsification. 366 maker tests passed while the contract required a contradiction. |
| 3 | `CLAIM24_CONSULT_REASON_CONSISTENCY_DELTA_FREEZE_2026-08-23.md` | `c686518a` | Second repair contract. Pairwise consistency. |
| 4 | `CLAIM24_CONSISTENCY_DELTA_FALSIFIED_FREEZE_2026-08-23.md` | `e6409cbd` | Second falsification. Pairwise was not enough. |
| 5 | `CLAIM24_WHOLE_ROW_LEAST_DERIVED_DELTA_FREEZE_2026-08-23.md` | `83afebd8` | Third contract, hashed before any code existed. |

Verify with `shasum -a 256 <file>`.

## The defect these repair

On `main`, `claim_24/mandate_cell7.py` decides an evidence class by searching free text:

```python
evidence_class = "TTL_EXPIRED" if "ttl expired" in event.notes.lower() else "BLOCKED_CONTROL"
```

The branch immediately above it dispatches on a structured field. `ttl_remaining_hours` sits on the
same event and is not consulted.

## Status

`BREAKER_PENDING. NOT SOLVED. NO INDEPENDENT PASS.`

Every seat that touched this lane is disqualified from clearing it: the seat that authored all
three contracts also wrote all three patches; the seat that briefed the lane cannot rule on it;
the seat that designed the falsifying attacks shaped the successor by doing so; the owner
authorized scope and is not a breaker.

The claim that does **not** require a verdict: twice the implementation was faithful and the
specification was wrong.

Out of scope and deliberately unresolved: `CONSULTED` semantics when no source value is retrieved,
and replay policy for evidence rows serialized before these fields existed.
