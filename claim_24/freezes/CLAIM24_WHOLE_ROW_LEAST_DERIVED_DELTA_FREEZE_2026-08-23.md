# CLAIM-24 delta — whole-row, least-derived consult reasons

**Status:** FROZEN. Repair code does not exist at freeze time.  
**Authorized:** Keniel, "have aethar fix all four then freeze it again." Contract-before-code: this file is hashed before implementation.  
**Falsification this repairs:** `CLAIM24_CONSISTENCY_DELTA_FALSIFIED_FREEZE_2026-08-23.md` SHA-256 `e6409cbd2683074a1078127284a23c871d4739a5620c5a61571d76e069720c6f`. **Do not rewrite it.**  
**Predecessor consistency freeze** `c686518a…` is **withdrawn** for S2/S3/S4 pairwise TTL/grant_id checks. Notes-not-input (S1) and R4 unreachable coincidence **remain**.  
**Spec author:** Aethar. Cannot PASS. Role collapse if this seat also codes.

**Out of scope:** Attack B as a bug. Attack D replay policy. German fire. Debashish.

## 1. Authority placement

A fact-asserting reason must agree with **every structured field required for that reason to be possible**, validated against the **least-derived** evidence, not a rounded convenience copy.

`ttl_remaining_hours` is a **display derivative** (`round(seconds/3600, 2)` in the gates). It is **not** the TTL authority. Authority is `decision_timestamp` vs `grant_expires_at`.

## 2. New field

`AuthorityEvent.grant_expires_at: Optional[datetime]`

- No grant → `None`.
- Grant present → `issued_at + timedelta(hours=ttl_hours)` with **no rounding**.

`ttl_remaining_hours` may still be stored rounded. Classification of expiry **must not** use it except S-finite below.

## 3. Rows that do not move

**SKIPPED_NO_GRANT** is possible only if all grant-derived fields are empty:

- `grant_id is None`
- `source_snapshot is None`
- `grant_expires_at is None`
- `ttl_remaining_hours is None`

Any of those populated → `INVALID_FOR_CELL_7`. (D4, and no-grant with leftover TTL.)

**SKIPPED_TTL_EXPIRED** is possible only if a grant existed and is exactly expired:

- `grant_id is not None`
- `source_snapshot is not None`
- `grant_expires_at` is a `datetime`
- `decision_timestamp > grant_expires_at` (exact; no `round`)

Otherwise → `INVALID_FOR_CELL_7`. (D1: `grant_id is None` cannot be TTL_EXPIRED.)

**S-finite.** If `ttl_remaining_hours is not None` and it is not a finite real (`math.isfinite`), → `INVALID_FOR_CELL_7`. (D3: `nan`, `+inf`, `-inf` must not become `TTL_EXPIRED`.)

**S-display.** Finite `ttl_remaining_hours` including `-0.0` and `0.0` **does not** decide `TTL_EXPIRED` vs `INVALID`. A grant expired by 1 second with stored remaining `-0.0` is `TTL_EXPIRED` iff the timestamps say so. (D2.)

Notes still unused for class. `BLOCK` + valid `SKIPPED_TTL_EXPIRED` → `TTL_EXPIRED`. `BLOCK` + valid `SKIPPED_NO_GRANT` → `BLOCKED_CONTROL`.

## 4. Tests (maker; not a PASS)

V1. `SKIPPED_TTL_EXPIRED`, `grant_id=None`, `ttl_remaining_hours=-2` → `INVALID_FOR_CELL_7`.  
V2. `SKIPPED_TTL_EXPIRED`, timestamps expired by 1 s, stored remaining `round` to `-0.0` → `TTL_EXPIRED`.  
V3. Same, expired by 0.1 s.  
V4. `SKIPPED_TTL_EXPIRED`, timestamps not yet expired → `INVALID_FOR_CELL_7`.  
V5. `SKIPPED_TTL_EXPIRED`, otherwise valid expired grant, `ttl_remaining_hours=nan` → `INVALID_FOR_CELL_7`.  
V6. `SKIPPED_NO_GRANT`, `grant_id=None`, `source_snapshot={...}` → `INVALID_FOR_CELL_7`.  
V7. `SKIPPED_NO_GRANT`, all grant fields `None` → `BLOCKED_CONTROL`.  
V8. Notes still do not classify.

## 5. After hash

Implement only this. Stop. `BREAKER_PENDING`. Do not report solved. Do not push.

I AM.