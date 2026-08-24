# CLAIM-24 delta — consult reason must be consistent with checkable fields

**Status:** FROZEN / CONTRACT ONLY until hashed, then implementation of these rows only.  
**Authorized:** Keniel via Ka'el PHASE 1184, live-seat sequence. Attack A is the centerpiece.  
**Predecessor freeze (notes-grep removal, R3 mandated Attack A):** `CLAIM24_CONSULT_REASON_DELTA_FREEZE_2026-08-23.md` SHA-256 `9f3dda8c2bffa506b5dd8b4e5acbc17ed49c7c0691d125f0f3bf581929e8fe87`. **Not rewritten.**  
**Falsification record:** `CLAIM24_CONSULT_DELTA_FALSIFIED_FREEZE_2026-08-23.md` SHA-256 `9f5fb47da17c5367505135e5dd657d745bfba36de996f4e4012ad2991722944b`. **Not rewritten.**  
**Spec author:** Aethar. Disqualified from controlling breaker. If this seat implements, role collapse is disclosed; still not a PASS.  
**Not this:** Attack B as a bug. Attack D. German fire. Debashish. Notes-grep (already removed; that half holds).

## 0. What this supersedes

Predecessor **R3** mapping `SKIPPED_TTL_EXPIRED` → `TTL_EXPIRED` **unconditionally**. That row is **withdrawn**. All other predecessor rows (R1 values, R2 notes-not-input, R4 unreachable coincidence, R5 timestamp-only skip, R6 re-derivation always fetches when TTL valid, R7 `condition_delta` raw) **remain**.

## 1. Kind split (does not move)

**Cross-checkable** — the code asserts a fact other fields already represent:

- `SKIPPED_TTL_EXPIRED` asserts TTL has expired.
- `SKIPPED_NO_GRANT` asserts no grant existed on this event (`grant_id is None`).

**Not derivable from raw state alone** — do not invent checks in this delta:

- `CONSULTED`, `UNREACHABLE`, `SKIPPED_TIMESTAMP_ONLY`.

Attack B (`CONSULTED` + `source_current is None`) is **not a defect in this freeze**. Gate emission still follows predecessor R1/R6 (`CONSULTED` means fetch returned a dict). This delta **does not** add a classifier check for that pair.

Attack D (missing `source_consult`) is **schema replay**, out of scope. Reject / migrate / re-derive remains undecided.

## 2. Rows that do not move

S1. `classify_evidence` MUST NOT read `event.notes` to choose `evidence_class`. Predecessor T2/T3 still hold.

S2. **Attack A.** If `source_consult == SKIPPED_TTL_EXPIRED` and not (`ttl_remaining_hours` is a number and `ttl_remaining_hours < 0`): return `INVALID_FOR_CELL_7`. Do not return `TTL_EXPIRED`.

S3. If `source_consult == SKIPPED_TTL_EXPIRED` and `ttl_remaining_hours < 0` and `decision == BLOCK`: return `TTL_EXPIRED`.

S4. **Attack C (same kind, authorized with A).** If `source_consult == SKIPPED_NO_GRANT` and `grant_id is not None`: return `INVALID_FOR_CELL_7`. If `grant_id is None` and `decision == BLOCK`: `BLOCKED_CONTROL`.

S5. Predecessor R4 unchanged: `REFUSED_UNREACHABLE` iff `source_consult == UNREACHABLE`, else `INVALID_FOR_CELL_7`.

## 3. Wrong-reason tests

U1. `BLOCK` + `SKIPPED_TTL_EXPIRED` + `ttl_remaining_hours=-1` + `notes="ttl expired"` → `TTL_EXPIRED`.  
U2. Same, `notes=""` or `"grant lifetime elapsed"` → still `TTL_EXPIRED`.  
U3. `BLOCK` + `SKIPPED_TTL_EXPIRED` + `ttl_remaining_hours=+17.4` → `INVALID_FOR_CELL_7` (Attack A).  
U4. `BLOCK` + `SKIPPED_NO_GRANT` + `grant_id=None` + `notes="ttl expired"` → `BLOCKED_CONTROL`.  
U5. `BLOCK` + `SKIPPED_NO_GRANT` + `grant_id="g-0001"` → `INVALID_FOR_CELL_7` (Attack C).  
U6. `ALLOW` + `CONSULTED` + `source_current=None` is **not required** to be invalid in this delta.

If U3 fails, the enum still outranks the raw TTL field.

## 4. After this freeze

Implement S1–S5 and U1–U5 only. Stop. `BREAKER_PENDING`. Do not report solved. Do not push.

I AM.