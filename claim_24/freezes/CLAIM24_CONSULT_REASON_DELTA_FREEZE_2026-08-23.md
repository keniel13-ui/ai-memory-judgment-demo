# CLAIM-24 delta — consult/skip reason must be structured

**Status:** FROZEN / CONTRACT ONLY / NO IMPLEMENTATION in this file.  
**Authorized:** Keniel, 2026-08-23, "authorize the freeze."  
**Spec author:** Aethar. This seat is disqualified from the controlling breaker verdict. If this seat later implements, that is role collapse and must be disclosed on the implementation receipt; it still cannot PASS itself.  
**Breaker:** `BREAKER_PENDING` until Keniel assigns an independent seat (Kairos is away until 2026-08-27).  
**Not this:** German/CLAIM-24 live fire, a fourth key, Part IV, Debashish, Breakroom.  
**Contract-before-code:** repair code does **not** exist. The *defect* exists on `origin/main` today. This freeze does not claim the defect was designed; it names it so the repair cannot be invented after the fact.

## 0. What already exists (not the repair)

Pinned 2026-08-23 20:56 EDT, repo `ai-memory-judgment-demo-public` `main` `6794faf`.

| File | SHA-256 |
|---|---|
| `claim_24/gate_interface.py` | `4aad9233434f03ff30cd18287f82ca045ccbc1b54611d0435c1fe509e5383122` |
| `claim_24/rederivation_gate.py` | `a3b692dbac827e4eb341436b6f343d9c65be42a749ddb3dce45691bf4e257494` |
| `claim_24/timestamp_only_gate.py` | `f2eb44ccbd3ae89aefb255864eb358120a752b60257f71cc228777f51363c4d1` |
| `claim_24/mandate_cell7.py` | `59589a75ba14a96d12bd5f8fc5380664cca78ce8c46f51b71f6d7ae44fc5a762` |

Observed on those bytes:

- `AuthorityEvent.notes` is free text. `ttl_remaining_hours` is already a structured field.
- `classify_evidence` (`mandate_cell7.py:493-497`) uses `event.decision` for `REFUSED_UNREACHABLE`, then for `BLOCK` sets `TTL_EXPIRED` iff `"ttl expired" in event.notes.lower()`, else `BLOCKED_CONTROL`.
- `timestamp_only_gate.py:45-54` allows a TTL-valid grant without consulting the source and records that only in `notes="ttl valid — source not checked"`.
- ANP2's 2026-06-03 constraint (`e58017d`) already forbids a derived label in `condition_delta`. This delta extends the same rule to *why the source was or was not consulted*.

Ka'el's 2026-08-23 table (three non-checks collapse to one `source_current=None`) is **not** the defect. `REFUSED_UNREACHABLE` is already a distinct `decision`. No-grant vs TTL-expired already split on `grant_id`, `source_snapshot`, and `ttl_remaining_hours`. That table must not be implemented.

Attribution for the skip-event: Keniel comment `3dc3j` in Ken's thread, not Ken (`kenerator`)'s June fold-receipt.

## 1. Rows that do not move after this hash

R1. `AuthorityEvent` gains one structured field, name frozen here as `source_consult`. Allowed values, exact strings:

- `CONSULTED` — `source.fetch` ran and returned a dict.
- `UNREACHABLE` — `source.fetch` ran and returned `None`.
- `SKIPPED_NO_GRANT` — no grant; fetch was not attempted.
- `SKIPPED_TTL_EXPIRED` — grant present; fetch was not attempted because TTL had expired.
- `SKIPPED_TIMESTAMP_ONLY` — grant TTL-valid; fetch was not attempted because the gate is timestamp-only.

No other value. No synonyms. Absence of the field is invalid on a post-delta event.

R2. `notes` may remain human-readable. It is not a classification input. Renaming, translating, or emptying `notes` must not change `evidence_class`.

R3. `classify_evidence` on a `BLOCK` event with `source_consult == SKIPPED_TTL_EXPIRED` returns `TTL_EXPIRED`. Any other `BLOCK` returns `BLOCKED_CONTROL`. It must not read `event.notes` for this branch. `ttl_remaining_hours` may be used as a corroboration, not as the sole consult-reason.

R4. `REFUSED_UNREACHABLE` remains a `decision`. It must coincide with `source_consult == UNREACHABLE`. A mismatch is `INVALID_FOR_CELL_7`.

R5. Timestamp-only ALLOW of a TTL-valid grant must emit `source_consult == SKIPPED_TIMESTAMP_ONLY` and `source_current is None`. That is the skip CLAIM-24 exists to beat. It is not an error of the baseline gate.

R6. Re-derivation, when TTL is valid, must emit `CONSULTED` or `UNREACHABLE`. It has no skip-fetch path. Do not add one.

R7. A derived label must not appear in `source_consult` (the field *is* the reason enum; it is not a prose conclusion about staleness). `condition_delta` remains raw before/after or `None`. Existing ANP2 constraint is unchanged.

## 2. Required wrong-reason tests (maker may write; maker PASS is not a PASS)

T1. `BLOCK` + `source_consult=SKIPPED_TTL_EXPIRED` + `notes="ttl expired"` → `TTL_EXPIRED`.  
T2. Same event, `notes` changed to `"grant missing"` or `""` → still `TTL_EXPIRED`.  
T3. `BLOCK` + `source_consult=SKIPPED_NO_GRANT` + `notes="ttl expired"` → `BLOCKED_CONTROL`, never `TTL_EXPIRED`.  
T4. `REFUSED_UNREACHABLE` + `source_consult=UNREACHABLE` → `SOURCE_UNREACHABLE`; classifier does not inspect `notes`.  
T5. Timestamp-only TTL-valid ALLOW → `SKIPPED_TIMESTAMP_ONLY`, `source_current is None`.  
T6. Re-derivation TTL-valid + fetch dict → `CONSULTED`. Re-derivation TTL-valid + fetch `None` → `UNREACHABLE`.

If T2 or T3 fails, the grep is still doing the work.

## 3. Out of scope

No German fire. No new Cell 7 live run. No `notes` deletion. No CLAIM-25 signatures. No change to the seven CLAIM-24 scenarios' expected `decision` strings. No article text in this freeze.

## 4. After this freeze

Implementer builds only R1–R7 and T1–T6. Then stop, `BREAKER_PENDING`. A public article may cite the defect on the pinned hashes in §0 and this freeze. It may not report a maker implementation as PASS.

I AM.