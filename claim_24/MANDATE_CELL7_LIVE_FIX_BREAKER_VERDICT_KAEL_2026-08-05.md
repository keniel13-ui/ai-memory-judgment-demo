# Mandate Cell 7 — Live Repair Breaker Verdict (Ka'el)

**Breaker:** Ka'el (live terminal seat)
**Maker:** Aethar
**Repairs:** `MANDATE_CELL7_LIVE_EXPIRESAT_UNIX_FIX_AETHAR_2026-08-05.md`
**Date:** 2026-08-05 EDT

```text
mandate_cell7.py       b4c1f522b2cee0e9b703e59f9abd67674ba6983129482ba8c2d2d6d2e28417b8
test_mandate_cell7.py  c70f87ca759a682a8af33b7ea04c8348cbda11c52f42f67e68da6ad45bd264a9
```

Candidate not edited during this attack. Suite re-run in this seat: **23 tests, OK** —
the maker's count is confirmed, not taken on report.

## Verdict: **BLOCK — one finding.** The repair is correct on every shape the live
## source produces, and it breaks the fail-closed contract on one it does not.

Do not run live CAPTURE on this hash. The required repair is a two-line change.

---

## What the repair gets right

The live defect is genuinely fixed. Verified against the real response body, not a
paraphrase of it:

```text
live integer (control)   -> OK, expires 2026-08-06 17:50:01+00:00
```

Twenty adversarial shapes, all correct, zero mismatches:

```text
bool True / False        -> REFUSE   (bool is an int subclass; explicitly handled)
NaN / inf                -> REFUSE
fractional float         -> REFUSE   whole seconds only
whole float              -> ACCEPT
ms scale (x1000)         -> REFUSE   outside accepted range
ns scale                 -> REFUSE
negative / zero          -> REFUSE
digit string in range    -> ACCEPT
"20260805" (date-like)   -> REFUSE   outside accepted range
ISO with Z               -> ACCEPT
naive ISO (no tz)        -> REFUSE   still requires tz-awareness
None / "" / list / dict  -> REFUSE
"+1786038601"            -> REFUSE
```

The `bool` case matters and was not missed — `True` is an `int` in Python and would
otherwise have parsed as epoch second 1. The epoch window correctly bounds a
millisecond or nanosecond accident. The string path still refuses naive datetimes, so
timezone discipline did not regress.

**Blast radius is one function.** The diff is a single hunk at `parse_aware_datetime`.
I checked directly for any change to `normalize_mandate`, `_normalize_scope`,
`_mandate_object`, `baseline_preconditions`, `changed_keys`, or the scope/status
fields: **none.** The authority path — the actual experiment — is untouched, and it
already succeeded against the live source before this repair existed.

---

## Finding K1 (BLOCK) — the digit branch breaks fail-closed on Unicode digits

`str.isdigit()` returns `True` for characters `int()` refuses. The digit branch calls
`int(stripped)` **outside any `try`**, so the failure escapes as a bare `ValueError`
instead of a classified `MandateCell7Error`.

Proven through the real adapter, with a passing control in the same run:

```text
live integer (control)   -> OK, expires 2026-08-06 17:50:01+00:00
superscript digit "²"    -> *** UNCAUGHT ValueError ***
```

Every affected shape:

```text
"²"  "³"  "¹"  "⁴⁵"  "1786038601²"     -> UNCAUGHT ValueError
"١٧٨٦٠٣٨٦٠١" (Arabic-Indic)            -> silently ACCEPTED as epoch
"１７８６０３８６０１" (fullwidth)          -> silently ACCEPTED as epoch
```

**Why this is a BLOCK and not a nit.** `run_mandate_cell7.py:57` catches
`MandateCell7Error` and nothing else:

```python
except MandateCell7Error as exc:
    print(json.dumps({"status": "REFUSED", "code": exc.code}), file=sys.stderr)
```

So a source emitting `"expiresAt": "²"` produces a Python traceback and an
unclassified exit instead of `{"status": "REFUSED", "code": "INVALID_SOURCE_RESPONSE"}`.
This codebase's entire premise is that every refusal is a stable, non-secret code. An
uncaught exception is not a refusal — it is the absence of one, and it is exactly the
class of "the error path was never exercised" that the last two runs were about.

The lower-severity half is the same root cause: Arabic-Indic and fullwidth digits are
*accepted*, meaning the wire-format check is not byte-exact against a source we have
documented as emitting ASCII integers.

**Required repair — one change closes both:**

Replace the `.isdigit()` test with an ASCII-only match and keep the conversion inside
the guarded path:

```python
if re.fullmatch(r"-?[0-9]+", stripped):
    return parse_aware_datetime(int(stripped), field, error_code=error_code)
```

`re.fullmatch(r"-?[0-9]+", ...)` refuses superscripts (no `int()` call is ever
reached) and refuses non-ASCII digit forms, so the crash and the silent-acceptance
findings close together. Any remaining `ValueError` should still be wrapped rather
than allowed to escape.

No contract change. No addendum. No design reopening. This is a code-breaker case.

---

## What must not change in the repair

- the epoch window, the `bool` rejection, the whole-seconds rule, and the
  timezone-awareness requirement on the string path — all verified correct;
- anything in the authority path;
- receipts must keep writing `source_expires_at_utc` as ISO via `iso_utc`.

## Re-review conditions

1. Close K1.
2. Re-run the suite and add a case asserting a **classified refusal** (not a crash)
   for a Unicode-digit `expiresAt`.
3. Report the new hashes. I re-attack, then live CAPTURE/EVALUATE.

## Standing note for the spine

Aethar's lesson is right and I would sharpen it. The suite did not merely share the
code's assumption about wire format — **the suite was written from the same document
the code was written from, by the same line of reasoning.** Twenty-two green tests and
two independent breaker seats could not catch an integer, because none of us was ever
in contact with the thing being modeled. The live source found it in one call.

That is the argument for the outside-run counter in one sentence, and it is why
"22 tests pass" was never the same claim as "this works."

---

**Live mandate is still valid** (`mdt_31c42fd9…`, expires 2026-08-06 ~15:30 UTC).
There is time to close K1 properly. Do not burn German's third fixture on this hash.

---

# ADDENDUM — K1 closed, PASS, and the live protocol finding

**Date:** 2026-08-05 EDT (same seat, same session)

```text
mandate_cell7.py       59589a75ba14a96d12bd5f8fc5380664cca78ce8c46f51b71f6d7ae44fc5a762
test_mandate_cell7.py  e4436dc2122c900b5c8c03c85cdd5486c1c95bb789670653ab8937a613135a98
```

Hashes verified in this seat, not taken from the maker's report. Suite re-run here:
**23 tests, OK.**

## Verdict on the repaired hash: **PASS.**

K1 is closed. Every shape that previously escaped as an uncaught `ValueError` now
returns a classified refusal, and the non-ASCII digit forms that were silently
accepted are now refused:

```text
'²' '³' '¹' '⁴⁵' '1786038601²'    -> clean refusal INVALID_SOURCE_RESPONSE
'١٧٨٦٠٣٨٦٠١' (Arabic-Indic)        -> clean refusal INVALID_SOURCE_RESPONSE
'１７８６０３８６０１' (fullwidth)      -> clean refusal INVALID_SOURCE_RESPONSE
'٣'  '½'  'Ⅻ'  '１2３'              -> clean refusal INVALID_SOURCE_RESPONSE

uncaught crashes: 0
```

The prior twenty-shape sweep re-run against the new hash: **zero regressions.**

End-to-end through the real adapter, with a passing control in the same run:

```text
live integer (control)  -> OK   expires 2026-08-06 17:50:01+00:00
                               scope=['verify']  orig=['read:crm','sign','verify']
superscript '²' (K1)    -> REFUSED (clean) INVALID_SOURCE_RESPONSE
ISO string (legacy)     -> OK   expires 2026-08-06 15:30:00+00:00
```

Regression on the v1 defects: the redirect refusal is still wired
(`build_opener(_RejectRedirectHandler())`, line 697) and its test still passes.
Diff scope is a single hunk at `parse_aware_datetime`; `normalize_mandate`,
`_normalize_scope`, `_mandate_object`, `baseline_preconditions`, `changed_keys`,
and the scope/status fields are untouched.

## Live CAPTURE result: `INVALID_BASELINE_PRECONDITIONS` — correct behavior, not a bug

The timestamp parse now succeeds against the live source. CAPTURE refuses one step
later, and it is right to:

```text
set(snapshot)==SNAPSHOT_KEYS : True
entity_id matches            : True
status == active             : True
scope == scope_original      : False   <-- fails here

  scope          : ['verify']
  scope_original : ['read:crm', 'sign', 'verify']
```

`baseline_preconditions` requires the baseline read to be in **issuance state**.
Both fixtures were narrowed roughly 90 seconds after issuance
(`issuedAt 1785952201` -> `updatedAt 1785952288`), and the live GET only ever exposes
current state. The "before" half of the before/after pair is gone by the time we read.

**This is a coordination protocol gap between two parties, not a defect in either
side's code.** The mechanism fail-closed exactly as designed on an unmet precondition.

There is deliberately no baseline-override flag, and none should be added.
Constructing the baseline from the JSON in an operator's message rather than from the
live source would make the result true by construction — the same failure that killed
five designs in the sequence-attack line and is recorded in `RESEARCH_SPINE.md` §3.

## What the live run requires

1. mandate observed live with `scopeCurrent == scopeOriginal` -> CAPTURE baseline
2. operator narrows `scopeCurrent`
3. re-read -> EVALUATE -> frozen prediction `REFUSED_STALE`

Requested from FIPSign: either PATCH the existing live mandate's `scopeCurrent` back
to the full set so the baseline can be captured, then re-narrow; or issue a fresh
mandate and leave it at issuance state until capture is confirmed.

## Status

Code: **PASS on `59589a75…`.** Live result: **not yet obtained.** No result is
claimed. Outside-substrate reproduction of the sequence-attack suite remains **zero**;
that counter is separate from this lane and is not advanced by anything here.
