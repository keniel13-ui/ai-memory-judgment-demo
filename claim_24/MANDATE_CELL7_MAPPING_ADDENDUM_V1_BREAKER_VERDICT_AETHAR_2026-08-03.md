# CLAIM-24 Mandate Cell 7 — Addendum v1 Re-Break Verdict (Aethar)

**Date:** 2026-08-03 EDT  
**Breaker:** Aethar (Grok)  
**Maker:** Kairos  
**Seat:** clean re-break of frozen body + addendum (no implementation)

## Frozen inputs attacked

| Artifact | SHA-256 |
| --- | --- |
| Body `MANDATE_CELL7_MAPPING_PREREGISTRATION_2026-08-03.md` | `ad8b5066db2644be63761095df9e0712b29b53eccfe452773167ea0b8bc776c6` |
| Addendum v1 `MANDATE_CELL7_MAPPING_ADDENDUM_V1_2026-08-03.md` | `8a8a6715bb50d639db5762e910a6c5efd91707d63a4801f4199647ebd6e2efa6` |
| Prior Aethar PASS (superseded by Ka'el) | `632ac6e9f36c73be6dc522734a453adfd50b889bf0ed395a0069c488fc527e0c` |
| Controlling Ka'el BLOCK | `e810ea606ff045581d0f9a919040a1758b071fe23ef50baa078ca4b17210ed36` |

Hashes verified on disk this seat. Body and addendum **not edited**. No Mandate
adapter module, credential, live GET/PATCH, or article result was opened.

## Verdict

**PASS — body + addendum v1 authorize implementation of the frozen package only.**

Allowed after this PASS:

1. GET-only Mandate normalizer/adapter (`base_url` pinned to `https://api.fipsign.dev`);
2. exact-delta **evidence classifier** (dual column with gate verdict);
3. counting self-test asserting **both** gate verdict and evidence class for M0–M7;
4. later: independent code breaker → disposable live fixture → earned article.

Not authorized: Stage 2a, Prima redesign, SlamJunk deploy, or any credibility-section
rebuild.

## Adjudication of the prior conflict

| Prior seat | Finding | This seat |
| --- | --- | --- |
| Aethar PASS | Mapping architecture sound; key custody as advisory | Superseded on independence freeze |
| Ka'el BLOCK K1 | Same project key does GET+PATCH; independence underspecified | **Accepted then repaired** by three-principal freeze |
| Ka'el BLOCK K2 | `REFUSED_STALE` ≠ “scope drifted” | **Accepted then repaired** by exact-delta classifier |
| Ka'el advisory | Budget excluded is authority-incomplete | **Accepted** in addendum §5 + title narrow |

Ka'el's **facts** were right. The **forced dilemma** (key → agent can PATCH **or**
operator hands JSON) is **not** forced once the **trusted gate runner** is a third
principal that may GET with the project key while the **agent under test** never holds
it and never runs inside that process. That matches `RederivationGate`'s
`agent_writable=false` as **agent-relative**, not “nobody on earth can mutate the
source.” Mandate’s operator narrow **is** the intended mutator.

`agent_writable=false` without the three-role freeze was assertion. With the freeze,
it is a deployment precondition that can still be **INVALID** if violated — not a
silent PASS.

## What the addendum freezes correctly

### K1 repair — three principals

- **Agent under test:** no project key; no method/URL control; no code in gate process.
- **Trusted gate runner:** key only for `GET /mandate/:bound_id`; no PATCH/POST surface;
  fixed base URL; no key in artifacts; no agent-authored code while keyed.
- **Source operator:** preferred external narrow; Keniel-side PATCH downgrades tier.

INVALID if agent recovers key, agent code runs in keyed process, adapter accepts
generic method/URL, or operator feeds hand-authored normalized JSON instead of
adapter-parsed GET.

### K2 repair — dual column

Gate: whole-snapshot inequality → `REFUSED_STALE` (necessary).  
Classifier: `changed_keys == {"scope"}` plus active/id/subject/original preconditions
→ `CELL_7_CLEAN_STATUS_SCOPE_DRIFT` (sufficient for Cell 7).

M3/M4 still `REFUSED_STALE` at the gate but **`INVALID_FOR_CELL_7`** in the
classifier. Self-test must assert both columns.

### Budget + title

Scope-only cell; budget not re-derived; working title narrowed to usable **scope**
shrink, not all authority.

### Forbidden claims

Retained and extended (“REFUSED_STALE alone proves scope drift” forbidden).

## Remaining nonclaims (honest)

A PASS here does **not** prove:

- the gate runner is immune to compromise (it holds a PATCH-capable key);
- OS isolation beyond process/env policy;
- ML-DSA verification;
- full CLAIM-24 external validation;
- FIPSign built Mandate from this framework;
- cell 6 evidence.

Those remain outside the package.

## Binding implementation constraints (INVALID if violated)

These are not new research claims; they prevent a sloppy implementer from voiding the
PASS:

**R1 — Identity path hygiene.**  
`entity_id` used in the path must match a frozen pattern (at minimum starts with
`mdt_` and is a single URL path segment with no `/`, `?`, `#`, or scheme). Reject
before request. Base URL is literal `https://api.fipsign.dev` only for the live run.

**R2 — GET-only HTTP seam.**  
Production code must not accept a generic multi-method client. Test seam
`http_get_json(url, headers)` only. Any production path that can PATCH is a contract
breach.

**R3 — Direct GET bytes.**  
Issue-time and current snapshots come from adapter-normalized GET responses only. No
operator-typed JSON “as if” GET.

**R4 — Dual assertions.**  
Counting tests fail if they check only `gate_decision` without `evidence_class` /
`changed_keys`.

**R5 — Receipt honesty.**  
If no live agent process is present, the receipt must state that
source-write separation is a **deployment precondition**, not a demonstrated sandbox
result against a hostile agent binary.

## Adapter existence check

No Mandate-specific adapter implementation exists in this seat’s inventory beyond the
older CA `fipsign_source_adapter.py` (certificate path). Cell 7 remains
**unimplemented**. This PASS is the first authorization to build the Mandate GET-only
path under body + addendum.

## Next sequence (unchanged)

1. Kairos implements normalizer + GET-only adapter + classifier + dual-column self-test.  
2. Independent breaker attacks the **code** (malformed bodies, volatile fields, URL
   injection, method smuggling, key leakage, M3/M4 misclassification).  
3. Disposable FIPSign fixture; external operator narrow preferred.  
4. Earned article only if classifier shows Cell 7; working title only if CONFIRMED.

## SlamJunk / Prima

Outside this lane. Prima parked after rollback. SlamJunk client-complete locally only.

I AM
