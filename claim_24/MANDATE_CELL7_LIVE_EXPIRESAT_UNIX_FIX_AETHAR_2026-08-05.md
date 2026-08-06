# Mandate Cell 7 — Live defect repair (Aethar maker)

**Date:** 2026-08-05 EDT
**Maker:** Aethar
**Found by:** Ka'el live CAPTURE (first contact with FIPSign API)
**Required next:** Ka'el independent re-break of this fix, then live CAPTURE/EVALUATE
**Do not treat this file as a PASS on the fix.**

## Defect

Live CAPTURE refused with:

```text
INVALID_SOURCE_RESPONSE
mandate.expiresAt must be a timestamp string
```

`normalize_mandate` had already succeeded: `scopeOriginal` three scopes,
`scopeCurrent` `["verify"]`, `status` active — the authority experiment worked.

Failure was **lifecycle metadata only**: FIPSign returns `expiresAt` as a **Unix
epoch integer**. `parse_aware_datetime` accepted only non-empty ISO-8601 strings.

German documented and shipped integers in every fixture message. Our suite never
did: every test used `iso(...)`. Shared false premise → 22 green tests that could
not falsify the live shape.

## Repair (this seat)

`claim_24/mandate_cell7.py` — `parse_aware_datetime` now accepts:

- ISO-8601 strings (receipts and any string source);
- Unix epoch **seconds** as `int` / whole `float` (not `bool`);
- digit-only strings as Unix seconds;
- hard epoch window to reject accidental ms/ns scales.

Receipts still **write** `source_expires_at_utc` as ISO via `iso_utc` (unchanged).

`claim_24/test_mandate_cell7.py` — added
`test_expires_at_unix_integer_is_accepted_like_live_fipsign` so the suite includes
a **reality-shaped** fixture, not only ISO.

## Local suite after first repair

```text
python3 -m unittest test_mandate_cell7 -v
Ran 23 tests in ~0.3s
OK
```

```text
mandate_cell7.py     b4c1f522b2cee0e9b703e59f9abd67674ba6983129482ba8c2d2d6d2e28417b8
test_mandate_cell7.py c70f87ca759a682a8af33b7ea04c8348cbda11c52f42f67e68da6ad45bd264a9
```

(Prior public v2 pin was `32d34b37…016a` / `77a0bbb8…dd3`.)

## K1 close (same maker seat, after Ka'el BLOCK)

Ka'el `MANDATE_CELL7_LIVE_FIX_BREAKER_VERDICT_KAEL_2026-08-05.md` **BLOCKED** first
Unix-epoch repair on:

- `str.isdigit()` true for Unicode digits (`²`, Arabic-Indic, fullwidth) where
  `int()` raises or silently mis-accepts;
- `int(stripped)` outside try → uncaught `ValueError` through CLI (not a
  classified `MandateCell7Error`).

**Repair:** digit branch uses `re.fullmatch(r"-?[0-9]+", stripped)` only; `int`
wrapped; tests assert superscript / Arabic-Indic / fullwidth refuse as
`INVALID_SOURCE_RESPONSE` never bare exception.

```text
mandate_cell7.py      59589a75ba14a96d12bd5f8fc5380664cca78ce8c46f51b71f6d7ae44fc5a762
test_mandate_cell7.py e4436dc2122c900b5c8c03c85cdd5486c1c95bb789670653ab8937a613135a98
23 tests OK (K1 cases inside unix-expires test)
```

Live int control still parses: `1786038601` → `2026-08-06 17:50:01+00:00`.

## Not done by this seat

- Independent re-break of **K1-closed** hash (Ka'el — required before live run)
- Live CAPTURE + EVALUATE against current German fixture
- Public push of the repair commit
- Deleting `~/.fipsign_key` or German's gist (operator after confirmed run)

## Standing lesson (for spine / team)

A suite that shares the code's assumption about **external wire format** is not an
outside test. Wire-format fixtures must include shapes the source has already
documented (integer timestamps, not only our preferred ISO).
