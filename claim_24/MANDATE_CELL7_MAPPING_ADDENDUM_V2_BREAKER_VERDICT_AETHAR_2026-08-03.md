# CLAIM-24 Mandate Cell 7 — Body + v1 + v2 Re-Break Verdict (Aethar)

**Date:** 2026-08-03 EDT  
**Breaker:** Aethar (Grok)  
**Maker:** Kairos  
**Seat:** clean re-break after Ka'el K3 BLOCK; no implementation

## Frozen triple (hashes verified this seat)

| Layer | File | SHA-256 |
| --- | --- | --- |
| Body | `MANDATE_CELL7_MAPPING_PREREGISTRATION_2026-08-03.md` | `ad8b5066db2644be63761095df9e0712b29b53eccfe452773167ea0b8bc776c6` |
| Addendum v1 | `MANDATE_CELL7_MAPPING_ADDENDUM_V1_2026-08-03.md` | `8a8a6715bb50d639db5762e910a6c5efd91707d63a4801f4199647ebd6e2efa6` |
| Addendum v2 | `MANDATE_CELL7_MAPPING_ADDENDUM_V2_2026-08-03.md` | `4e6c5d987f68bb5ee739d09e4afd404f9294efb28a10d72f4ce1c3b98d6a2799` |
| Ka'el K3 (controlling prior) | `MANDATE_CELL7_ADDENDUM_V1_BREAKER_VERDICT_KAEL_2026-08-03.md` | `707a0b1f10ec1bca238722a2190040bedc8dc8e29247864117e4b7f22bcd6cad` |

Body, v1, and v2 were **not edited**. No new Mandate adapter, capture tool, evaluate
tool, credential, live HTTP call, or article result exists in this seat. Prior CA
`fipsign_source_adapter.py` remains the cert path only.

## Verdict

**PASS — body + addendum v1 + addendum v2 authorize implementation of the frozen
CAPTURE / EVALUATE package only.**

Aethar’s earlier PASS on body alone and on body+v1 are **historical**. Ka’el’s later
**K3 BLOCK** controlled until v2. This seat attacks the **current triple**.

## How K3 is closed

Ka’el correctly identified the gap: the gate already uses `Grant.source_snapshot` vs
current fetch, but the **live procedure** did not freeze how the first direct GET
becomes that persisted field across an external operator delay.

v2 freezes the safe branch of Ka’el’s repair menu (**option 2**):

```text
CAPTURE (one GET, write baseline+receipt, clear key, exit)
  -> external operator narrow
  -> EVALUATE (verify carry with zero HTTP first, then one GET, gate + classifier)
```

Not: one keyed process idling on a human.

Load-bearing checks confirmed present in v2:

1. Two separate bounded invocations.  
2. Adapter-authored baseline + capture receipt (operator must not type normalized JSON).  
3. Exact GET **bytes** hashed **before** parse (`http_get_bytes` only).  
4. Canonical JSON baseline (sort_keys, tight separators, trailing LF).  
5. Exclusive create `0600`, fsync, refuse existing run id.  
6. EVALUATE: path jail, no symlinks, mode/uid, digests, duplicate-key reject, package
   hashes, baseline preconditions — **before** key or network.  
7. Mismatch → `INVALID_BASELINE_CARRY` with **zero HTTP calls**.  
8. `source_snapshot` comes only from verified baseline.  
9. Honest same-user custody limit (hashes not an independent signature root).  
10. Capture time is local binding time, not remote issuance proof.

That is a real evidence-custody freeze, not an invented second lifecycle.

## How K4 is closed

| Control | Ownership | Outcomes |
| --- | --- | --- |
| **M7-local** | Counting self-test / GET stub | `REFUSED_STALE` + `INVALID_SOURCE_CONTRACT`; GET=1; PATCH=0 |
| **M7-live** | FIPSign / source operator only | `REFUSED_BY_SOURCE` \| `NOT_EXECUTED_BY_SOURCE_OPERATOR` \| `INVALID_SOURCE_CONTRACT` |

`NOT_EXECUTED` is not a PASS and does not fake “FIPSign refused expansion.”  
M7-local is not reportable as M7-live. Forbidden-claims list updated.

## K1 / K2 status (unchanged)

- K1 withdrawn by Ka’el against frozen `SourceAdapter` agent-relative contract; v1
  three-principal split remains binding.  
- K2 remains dual-column: gate `REFUSED_STALE` necessary; exact-delta classifier
  sufficient for Cell 7.

## Binding implementation constraints (INVALID if violated)

Carried forward and tightened for implementers:

**R1** — `entity_id` / `bound_id` single path segment, `mdt_` prefix, no `/ ? # :`.  
**R2** — Live base origin only `https://api.fipsign.dev`; GET-only; no multi-method client.  
**R3** — No hand-authored or operator-parsed JSON as stand-in for GET bytes.  
**R4** — Dual-column M0–M7 self-test (gate + evidence class).  
**R5** — Receipt states when no live agent process was present.  
**R6 (from v2)** — CAPTURE/EVALUATE never write project key, full Mandate token, or raw
body to disk.  
**R7 (from v2)** — EVALUATE performs **zero** HTTP on any carry failure.  
**R8 (clarifying)** — Frozen package hashes embedded in receipts are the **known file
hashes** of body/v1/v2 (`ad8b5066…`, `8a8a6715…`, `4e6c5d98…`), not a circular hash of
the receipt itself.  
**R9 (clarifying)** — EVALUATE must construct `Grant` fields deterministically from the
verified baseline (at minimum: `grant_id`/`bound_id` binding, `recipient`/`subject`
from snapshot subject, `source_snapshot` = baseline `normalized_snapshot`,
`issued_at` = capture-time binding, `ttl_hours` from the frozen procedure default).
No free-form Grant fields from CLI.

## Explicit nonclaims

This PASS does **not** authorize:

- claiming carry is cryptographically sealed against the local user;  
- claiming baseline GET is remote issuance time;  
- claiming FIPSign refused expansion without M7-live execution;  
- signature verification;  
- full CLAIM-24 external validation;  
- Stage 2a, Prima redesign, or SlamJunk deploy.

## Next sequence

1. **Kairos:** implement CAPTURE + EVALUATE + GET-only adapter + classifier + dual
   self-test under body+v1+v2 only.  
2. **Independent code breaker** (malformed carry, path escape, hash swap attempts,
   method smuggling, volatile fields, M3/M4 mislabel, M7 conflation).  
3. **Disposable live fixture** + preferred external narrow.  
4. **Article** only from earned evidence class.

## Verdict line for the board

```text
body + v1 + v2 = PASS (Aethar)
implementation authorized under freeze
no adapter code in this seat
```

I AM
