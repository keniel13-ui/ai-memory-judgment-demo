# Mandate Cell 7 — Live Baseline Protocol Correction

**Date:** 2026-08-05 EDT
**Author:** Codex/Kairos, after Keniel required a source check
**Applies to:** the live-protocol paragraph in
`MANDATE_CELL7_LIVE_FIX_BREAKER_VERDICT_KAEL_2026-08-05.md`
**Does not alter:** Ka'el's PASS on parser hash `59589a75…a762`

## Correction

The breaker receipt correctly records that live CAPTURE reached
`INVALID_BASELINE_PRECONDITIONS` because the mandate had already been narrowed before the
first direct GET.

Its suggested fast path — widen the existing mandate back to its issuance scope, capture,
then narrow it again — is withdrawn. The frozen FIPSign mapping preregistration already
records `PATCH ... action:narrow` as a **permanent, one-directional** reduction of
`scopeCurrent` to a subset of `scopeOriginal`.

The valid preferred procedure remains:

1. the source operator issues a fresh mandate and leaves
   `scopeCurrent == scopeOriginal`;
2. this project performs live CAPTURE and confirms success;
3. the source operator narrows the same mandate;
4. this project performs live EVALUATE.

The frozen contract also permits Keniel's side to perform step 3 only with explicit
authorization, but that result must be labeled a `controlled external-API fixture`, not
independently authored lifecycle evidence. No PATCH is authorized by this correction.

No baseline may be reconstructed from operator-provided JSON. No live Cell 7 result has
been obtained or claimed.

## Source

- `MANDATE_CELL7_MAPPING_PREREGISTRATION_2026-08-03.md` lines 59-60, 139-145,
  and 169-174;
- `MANDATE_CELL7_MAPPING_ADDENDUM_V1_2026-08-03.md` lines 81-85;
- `MANDATE_CELL7_MAPPING_ADDENDUM_V2_2026-08-03.md` lines 127-134.
