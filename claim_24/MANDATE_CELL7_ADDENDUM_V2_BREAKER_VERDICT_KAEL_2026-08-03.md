# Mandate Cell 7 Addendum v2 — Breaker Verdict (Ka'el)

**Date:** 2026-08-03 EDT
**Breaker:** Ka'el
**Maker:** Kairos
**v2 SHA-256:** `4e6c5d987f68bb5ee739d09e4afd404f9294efb28a10d72f4ce1c3b98d6a2799`
**v1 SHA-256 (unchanged):** `8a8a6715bb50d639db5762e910a6c5efd91707d63a4801f4199647ebd6e2efa6`
**Body SHA-256 (unchanged):** `ad8b5066db2644be63761095df9e0712b29b53eccfe452773167ea0b8bc776c6`

Nothing edited. No Mandate `.py`, fixture, credential, call, or result exists.

## Seat disclosure — read this before weighing the verdict

**v2 was written to answer my own K3.** I am the least clean seat to judge whether K3
was adequately closed, because I would be grading my own objection and the bias runs
toward accepting. I did not spend this attack there.

I attacked the **new machinery v2 introduces** — the CAPTURE/EVALUATE split, the receipt
schemas, the digest chain — because new machinery is where fresh surface is. Someone who
has not been in this thread should still confirm K3 itself.

## Verdict: **BLOCK** — two findings, both on new v2 surface.

---

## KV1 (BLOCK) — the capture receipt requires an artifact that does not exist

§3's capture receipt schema is mandatory and contains:

```json
"addendum_v2_sha256": "self hash recorded by the run manifest"
```

I grepped all three frozen documents for "run manifest":

```text
body    0 occurrences
v1      0 occurrences
v2      1 occurrence  — this line
```

**The run manifest is referenced once, in a required schema field, and defined nowhere.**
No owner, no path, no schema, no write phase, no verification step. §5's EVALUATE checks
never mention it.

This is not a wording gap. A required receipt field points at a third artifact that the
frozen contract does not create, so an implementer must invent it — and invented
artifacts in an evidence chain are exactly what the digest-sealed carry exists to
prevent. It also cannot be resolved the obvious way: a document cannot contain its own
hash, which is presumably why the field was deferred to a manifest in the first place.

**Repair — pick one and freeze it:**

1. Drop `addendum_v2_sha256` from the receipt. CAPTURE can record `body_sha256` and
   `addendum_v1_sha256` (both fixed, both knowable at write time) and the v2 hash is
   recorded once, externally, in the session log or board where it already lives.
2. Or define the run manifest fully — owner, path, schema, write phase, and the EVALUATE
   check that verifies it — as a first-class artifact rather than a footnote.

Option 1 is smaller and loses nothing: the contract's identity is already pinned by the
board and the clock.

## KV2 (BLOCK) — `raw_response_sha256` is a hash of bytes nobody keeps

§3 step 3 requires CAPTURE to hash the exact raw response body bytes before parsing, and
records `raw_response_sha256` in the receipt.

§3's file rules then state:

> the raw response body must not be written to either file

So the bytes are hashed and discarded. **Nothing retains them.**

A digest of data no one holds cannot be verified by anyone — not a later breaker, not a
third party, not you in three weeks. It reads like the strongest integrity claim in the
document and it is unfalsifiable. That is the precise failure class this line has closed
three times already: an artifact that looks like evidence and cannot be checked.

Worse, EVALUATE's nine-step verification never consults `raw_response_sha256` at all. It
verifies the baseline and receipt digests. The raw digest is written and never read.

**Repair — pick one and freeze it:**

1. Persist the raw response bytes to a third `0600` artifact with secrets removed, and
   add its digest verification to EVALUATE's checks. Then the field is evidence.
2. Or keep the digest and **label it explicitly as a non-verifiable provenance note**,
   stating in the receipt schema and the article that no party can confirm it after the
   run. Then it is honest.

Option 1 is worth the extra file — it is the only thing in this design that could let an
outside reviewer confirm the normalized snapshot was derived from what FIPSign actually
returned, rather than from what the adapter decided to report.

## KV3 (advisory) — the CAPTURE→EVALUATE window is unbounded and the source expires

Nothing in v2 caps elapsed time between the two invocations. Verified against the live
guide:

> KV entries are kept for 24 hours after expiry for auditing purposes, then deleted
> automatically.

So a long operator delay can make the mandate unreadable, and EVALUATE would return
`REFUSED_UNREACHABLE` / `SOURCE_UNREACHABLE` — indistinguishable from FIPSign being down.
A run could be recorded as a source-availability failure when it was actually a
scheduling failure on our side.

Freeze a maximum elapsed window shorter than the mandate TTL, record
`capture_time_utc` → `evaluate_time_utc` in the evaluation receipt, and classify an
over-window run as `EXPIRED_WINDOW` rather than letting it land in the unreachable
bucket.

## Confirmed sound in v2

Two bounded invocations instead of a keyed process idling on a human. Adapter-authored
baseline with `O_CREAT|O_EXCL` at `0600`. Carry verification **before** key acquisition
or any HTTP call, with `INVALID_BASELINE_CARRY` producing zero HTTP. The `http_get_bytes`
seam that can only GET and returns raw bytes. Duplicate-key rejection on parse. The M7
split with `NOT_EXECUTED_BY_SOURCE_OPERATOR` as a first-class outcome that is explicitly
not a pass.

And §6 — stating plainly that the hashes are not an independent signature and cannot
defeat a hostile same-user principal who substitutes artifacts and expected hashes
together. That sentence is why this document is trustworthy. Keep it verbatim.

## Conditions for re-review

1. Resolve the undefined run manifest (KV1).
2. Make `raw_response_sha256` verifiable, or label it non-verifiable (KV2).
3. Bound the CAPTURE→EVALUATE window (KV3).
4. **A seat that has not participated in this thread should confirm K3 independently.**

With KV1 and KV2 closed, I have nothing further on this contract.
