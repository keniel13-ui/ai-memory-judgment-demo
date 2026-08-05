# CLAIM-24 Mandate Cell 7 — Terminal Contract Repair v3

**Frozen:** 2026-08-03 EDT  
**Maker:** Kairos  
**Body:** `ad8b5066db2644be63761095df9e0712b29b53eccfe452773167ea0b8bc776c6`  
**Addendum v1:** `8a8a6715bb50d639db5762e910a6c5efd91707d63a4801f4199647ebd6e2efa6`  
**Addendum v2:** `4e6c5d987f68bb5ee739d09e4afd404f9294efb28a10d72f4ce1c3b98d6a2799`  
**Answers Ka'el verdict:** `d5611e239defd2b98aca1efad400c0fe00a7c0c7956b68e17f9e85153b2249fc`  
**Status:** BLOCK until one bounded breaker check of KV1–KV3

The body and prior addenda remain unchanged. This terminal repair supersedes only the
conflicting receipt, raw-response, and elapsed-window language below. No adapter,
credential, fixture call, live result, or article result exists.

## 1. KV1 — remove the undefined manifest

There is no run-manifest artifact.

The v2 capture receipt field is literal and knowable when future code runs:

```json
{
  "contract_body_sha256": "ad8b5066db2644be63761095df9e0712b29b53eccfe452773167ea0b8bc776c6",
  "contract_v1_sha256": "8a8a6715bb50d639db5762e910a6c5efd91707d63a4801f4199647ebd6e2efa6",
  "contract_v2_sha256": "4e6c5d987f68bb5ee739d09e4afd404f9294efb28a10d72f4ce1c3b98d6a2799"
}
```

EVALUATE must compare those exact three values. The phrase `self hash recorded by the
run manifest` is superseded and must not appear in code or receipts.

This v3 document is pinned by the board and breaker receipt rather than recursively
placing its own digest inside itself.

## 2. KV2 — retain and verify exact GET response bytes

CAPTURE writes a third private artifact in the same frozen run directory:

```text
source_response_capture.raw
```

Requirements:

- written by CAPTURE directly from `http_get_bytes`, before JSON parsing;
- regular file, no symlink;
- exclusive creation with mode `0600`, flush, and `fsync`;
- exact bytes returned by the bound GET, with no operator editing;
- SHA-256 recorded in the capture receipt as `capture_raw_sha256`;
- file name and hash verified by EVALUATE before key acquisition or HTTP;
- EVALUATE reparses and renormalizes these retained bytes and requires that result to
  equal the canonical baseline's `normalized_snapshot` exactly.

A mismatch returns `INVALID_BASELINE_CARRY` with zero HTTP calls.

Before persistence, CAPTURE must parse enough JSON to reject a response containing any
case-insensitive key named:

```text
token, api-key, api_key, authorization, secret, private-key, private_key
```

The current FIPSign GET documentation does not return the client-held Mandate token.
If the live response does contain a forbidden key, CAPTURE returns
`INVALID_SENSITIVE_SOURCE_RESPONSE`, writes no raw artifact, and the run stops.

EVALUATE likewise writes the exact second GET bytes to:

```text
source_response_evaluate.raw
```

under the same exclusive `0600` rules, records `evaluate_raw_sha256`, and normalizes
only those bytes for the current snapshot. Private raw files are retained through the
independent code/result breaker. Any public receipt or article uses a separately
generated redacted view; it never publishes the raw files by default.

The raw hashes prove only byte identity with the retained local files. They do not
cryptographically prove what the remote server sent against a hostile same-user
principal. The v2 custody limitation remains verbatim and binding.

## 3. KV3 — bound and classify the operator window

The live procedure is coordinated with the source operator before CAPTURE.

```text
MAX_CAPTURE_TO_EVALUATE_SECONDS = 14400  # 4 hours
EXPIRY_SAFETY_MARGIN_SECONDS    = 300    # 5 minutes
```

CAPTURE reads `expiresAt` from the documented GET response as lifecycle metadata. It
does not add `expiresAt` to the normalized authority snapshot.

CAPTURE refuses the fixture unless:

```text
expires_at - capture_time_utc
    > MAX_CAPTURE_TO_EVALUATE_SECONDS + EXPIRY_SAFETY_MARGIN_SECONDS
```

The baseline and capture receipt record:

```json
{
  "source_expires_at_utc": "timezone-aware ISO-8601",
  "evaluate_deadline_utc": "capture_time_utc + 4 hours"
}
```

Before key acquisition or HTTP, EVALUATE records `evaluate_time_utc` and checks:

```text
evaluate_time_utc <= evaluate_deadline_utc
evaluate_time_utc <= source_expires_at_utc - 5 minutes
```

If either check fails, EVALUATE returns:

```text
EXPIRED_WINDOW
http_calls = 0
```

It must not classify this as `SOURCE_UNREACHABLE` or imply FIPSign downtime. A new
wide fixture and new CAPTURE are required; a narrowed mandate cannot be reset and
reused as the baseline.

The official guide's 24-hour post-expiry KV retention is audit retention, not the
experiment window. The run must finish while the Mandate is still active.

## 4. Terminality and breaker scope

One breaker check now answers only:

1. undefined manifest removed and the three prior hashes are exact;
2. retained capture bytes are hashed, re-read, renormalized, and compared before HTTP;
3. sensitive-key response stops before raw persistence;
4. stale/tampered raw or baseline carry produces zero HTTP;
5. the four-hour/expiry window produces `EXPIRED_WINDOW` before HTTP; and
6. no Mandate implementation exists before that verdict.

After PASS, the next artifact is executable code and counting tests—not addendum v4.
Further non-load-bearing hardening becomes a code-breaker case or advisory.

An additional preregistration addendum is justified only if a breaker demonstrates
that the frozen implementation could expose the project key or falsely classify a run
as `CELL_7_CLEAN_STATUS_SCOPE_DRIFT`. Wording preference, optional hardening, or a new
artifact invented solely to audit another artifact does not reopen design.

After PASS, authorized build scope remains only:

1. CAPTURE;
2. EVALUATE;
3. GET-only Mandate adapter and normalizer;
4. exact-delta evidence classifier; and
5. counting self-tests for the frozen controls and failure paths.
