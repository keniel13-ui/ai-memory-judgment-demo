# Mandate Cell 7 — Terminal v3 Bounded Breaker Verdict (Ka'el)

**Date:** 2026-08-04 EDT
**Breaker:** Ka'el
**Maker:** Kairos
**v3 SHA-256:** `4033e3674e7e7997cf7ed2473648874e2724ea497a986ad514541cf7d9471dc3`
**Scope:** the six checks v3 §4 authorizes. Nothing else was attacked.

Nothing edited. No Mandate `.py`, credential, fixture call, or result exists.

## Verdict: **PASS.** Implementation is authorized under the frozen scope.

---

## The six bounded checks

| # | Check | Result |
|---|---|---|
| 1 | Undefined manifest removed; three prior hashes exact | **PASS** — verified by recomputation |
| 2 | Retained bytes hashed, re-read, renormalized, compared before HTTP | **PASS** |
| 3 | Sensitive-key response stops before raw persistence | **PASS**, with one binding code case below |
| 4 | Stale/tampered raw or baseline carry → zero HTTP | **PASS** |
| 5 | Window/expiry → `EXPIRED_WINDOW` before HTTP | **PASS** |
| 6 | No implementation exists | **PASS** — no `mandate*.py` |

**Check 1 verified by recomputation, not by reading:**

```text
ad8b5066db2644be63761095df9e0712b29b53eccfe452773167ea0b8bc776c6   body
8a8a6715bb50d639db5762e910a6c5efd91707d63a4801f4199647ebd6e2efa6   v1
4e6c5d987f68bb5ee739d09e4afd404f9294efb28a10d72f4ce1c3b98d6a2799   v2
```

All three match v3's pins exactly. `self hash recorded by the run manifest` appears zero
times in v3 — superseded and gone, not merely deprecated.

**Check 2 is the repair I wanted and it went further than I asked.** I proposed either
persisting the raw bytes or labelling the hash non-verifiable. v3 persists them *and*
requires EVALUATE to reparse and renormalize the retained bytes and assert equality with
the canonical baseline. That converts the digest from a provenance note into a
reproducible derivation an outside reviewer can check. It also extends the same treatment
to the second GET.

**Check 5** correctly refuses to let an over-window run masquerade as `SOURCE_UNREACHABLE`,
and correctly separates FIPSign's 24-hour audit retention from the experiment window.
The pre-flight refusal — CAPTURE declining a fixture whose `expiresAt` cannot survive the
window plus margin — closes the failure before it can be recorded as a source problem.

## Binding code-breaker case, not a design reopen

§2's sensitive-key screen lists forbidden key names but does not state whether the scan
is **recursive**. A shallow scan over the top-level object would miss a nested
`mandate.metadata.token`.

Per §4 this does not reopen design — it is exactly the class that "becomes a code-breaker
case or advisory." Recording it as **binding on implementation**:

> The forbidden-key scan must walk the entire parsed structure, including nested objects
> and objects inside arrays, and must match key names case-insensitively at every depth.
> A shallow top-level scan fails this case.

The code breaker must include a fixture with a forbidden key nested two levels deep inside
an array element and assert `INVALID_SENSITIVE_SOURCE_RESPONSE` with no raw artifact
written.

I am not blocking on it. The screen exists, the intent is unambiguous, and the fix is one
sentence in the implementation — blocking a terminal contract over a word would be the
exact expansion §4 rules out, and §4 is right to rule it out.

## On terminality

§4's closing rule is the strongest governance sentence produced in this line:

> a new artifact invented solely to audit another artifact does not reopen design.

That is aimed squarely at my KV1, and correctly. I found a run manifest that existed only
to hash a document, and the right answer was to delete it rather than specify it. The rule
now prevents that class of growth structurally.

Four contract rounds, four breaker seats across two agents, ten findings, zero lines of
code, and zero false claims shipped. The next artifact is executable.

## Authorized next step

Implementation only, under the frozen scope: CAPTURE/EVALUATE, the GET-only raw-bytes
adapter, sealed-carry verification, the exact-delta classifier, and the dual-column
counting self-test. Maker does not self-close. An independent code breaker attacks the
implementation before any credential or live fixture is requested.

**No addendum v4.**
