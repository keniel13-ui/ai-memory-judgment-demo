# CLAIM-24 Mandate Cell 7 Mapping — Addendum v2

**Frozen:** 2026-08-03 EDT  
**Maker:** Kairos  
**Applies to body:** `MANDATE_CELL7_MAPPING_PREREGISTRATION_2026-08-03.md`  
**Body SHA-256:** `ad8b5066db2644be63761095df9e0712b29b53eccfe452773167ea0b8bc776c6`  
**Applies after addendum v1:** `MANDATE_CELL7_MAPPING_ADDENDUM_V1_2026-08-03.md`  
**Addendum v1 SHA-256:** `8a8a6715bb50d639db5762e910a6c5efd91707d63a4801f4199647ebd6e2efa6`  
**Answers Ka'el verdict:** `707a0b1f10ec1bca238722a2190040bedc8dc8e29247864117e4b7f22bcd6cad`  
**Current status:** BLOCK until this v2 repair passes a clean breaker seat

The body and addendum v1 remain unchanged. This v2 addendum supersedes them only
where they conflict. No Mandate adapter, credential, fixture call, live result, or
article result exists.

## 1. K1 and K2 remain closed

Ka'el withdrew K1 after checking the frozen `SourceAdapter` contract. Source
independence is relative to the governed agent. The three-principal split in v1
remains binding:

1. the agent under test has no project key or keyed-process reach;
2. the trusted gate runner performs only the bound direct GET;
3. the source operator performs mutation.

K2 remains repaired by recording the whole-snapshot gate verdict separately from the
exact-delta evidence classification. `REFUSED_STALE` alone is never Cell 7 evidence.

## 2. K3 accepted — freeze the two-read boundary

The existing gate already defines the first state as `Grant.source_snapshot` and the
second state as the adapter's current fetch. K3 does not change that mechanism. It
correctly identifies that the live procedure failed to specify how the first direct
GET becomes the persisted `source_snapshot` when an external operator may narrow the
Mandate minutes or hours later.

The live run uses **two separate bounded invocations**, never one keyed process idling
while it waits for a human:

```text
CAPTURE invocation -> external operator narrow -> EVALUATE invocation
```

Each invocation receives the disposable project key only for its own direct GET and
clears the runtime reference before exit.

## 3. CAPTURE invocation — adapter-authored baseline only

CAPTURE must:

1. accept one grant-bound Mandate id that passes the frozen `mdt_` single-segment
   path rules;
2. issue exactly one direct `GET /mandate/:bound_id` through the GET-only adapter;
3. hash the exact raw response body bytes before parsing;
4. normalize the response under the frozen field mapping;
5. confirm the baseline preconditions:
   - `entity_id == bound_id`;
   - `status == "active"`;
   - `scope == scope_original`;
6. write a canonical baseline artifact itself; and
7. write a separate capture receipt itself.

The operator must not type, paste, edit, or reconstruct normalized JSON.

For CAPTURE and EVALUATE, v2 supersedes v1's optional parsed-JSON test seam. The
narrow seam is `http_get_bytes(url, headers)`: it can perform only GET and must return
the HTTP status plus exact response body bytes. Parsing happens inside the adapter
after the raw-byte digest is computed. No generic requester or parsed operator value
may stand in for those bytes.

Canonical JSON means UTF-8 with:

```text
sort_keys=true
separators=(",", ":")
ensure_ascii=false
one trailing LF
```

The baseline artifact contains exactly:

```json
{
  "schema_version": 1,
  "run_id": "opaque-local-run-id",
  "bound_id": "mdt_...",
  "capture_time_utc": "timezone-aware ISO-8601",
  "normalized_snapshot": {
    "entity_id": "mdt_...",
    "subject": "agent-id",
    "scope_original": ["read:crm", "sign", "verify"],
    "scope": ["read:crm", "sign", "verify"],
    "status": "active"
  }
}
```

The capture receipt contains:

```json
{
  "schema_version": 1,
  "phase": "CAPTURE",
  "run_id": "same opaque-local-run-id",
  "bound_id": "mdt_...",
  "capture_time_utc": "same timestamp",
  "request_method": "GET",
  "request_origin": "https://api.fipsign.dev",
  "request_path": "/mandate/mdt_...",
  "http_status": 200,
  "raw_response_sha256": "64 lowercase hex",
  "baseline_sha256": "64 lowercase hex",
  "adapter_sha256": "64 lowercase hex",
  "body_sha256": "ad8b5066...c776c6",
  "addendum_v1_sha256": "8a8a6715...e2efa6",
  "addendum_v2_sha256": "self hash recorded by the run manifest"
}
```

The implementation must use exclusive creation (`O_CREAT|O_EXCL`) with mode `0600`
for both files, flush and `fsync` them, and refuse an existing run id or destination.
The key, full Mandate token, and raw response body must not be written to either file.

CAPTURE emits only the run id, baseline SHA-256, capture-receipt SHA-256, and artifact
paths. It then terminates.

## 4. Operator boundary

Only after CAPTURE succeeds may the source operator narrow the same `bound_id`.

- Preferred evidence: FIPSign performs the narrow.
- If Keniel's side performs it, the tier is `controlled external-API fixture`.
- No local process rewrites the baseline between phases.
- If the operator reports a different id, the run is INVALID.

The operator signal does not provide source state. It says only that evaluation may
proceed. EVALUATE still obtains current state through its own direct GET.

## 5. EVALUATE invocation — verify carry before GET

EVALUATE must receive the capture artifact path, capture receipt path, and the
expected baseline and capture-receipt SHA-256 values emitted by CAPTURE.

Before obtaining the project key or making a network call, it must:

1. require both paths to resolve inside the one frozen run directory;
2. reject symlinks and non-regular files;
3. require mode `0600` and the expected current uid;
4. verify the capture-receipt file SHA-256 against the expected value;
5. parse the receipt with duplicate-key rejection and exact required keys;
6. verify the baseline file SHA-256 against both the expected value and the receipt;
7. parse the baseline with duplicate-key rejection and exact required keys;
8. verify `schema_version`, `run_id`, `bound_id`, timestamps, artifact hashes, fixed
   request origin/method/path, and the frozen body/addendum hashes; and
9. re-run every baseline precondition over `normalized_snapshot`.

Any mismatch returns `INVALID_BASELINE_CARRY` with **zero HTTP calls**.

Only after those checks pass may EVALUATE:

1. perform one direct current GET through the keyed GET-only adapter;
2. instantiate the existing `Grant` with the verified baseline's
   `normalized_snapshot` as `source_snapshot`;
3. call the unchanged `RederivationGate`;
4. run the separate exact-delta classifier; and
5. write the evaluation receipt with both gate verdict and evidence class.

The capture timestamp is the local grant's snapshot-binding time. The receipt must
not misdescribe it as cryptographic proof of the remote Mandate's issuance instant.

## 6. Honest custody boundary

The digest-sealed carry detects an edited baseline or receipt whenever the expected
hashes supplied to EVALUATE remain the CAPTURE outputs. It is not an independent
signature and is not tamper-proof against a hostile same-user principal that can
rewrite both artifacts **and** substitute both expected hashes.

The live receipt must state that limitation. This run tests external source drift
and disciplined carry integrity; it does not claim an independently rooted local
evidence store.

## 7. K4 accepted — split M7 ownership and outcomes

M7 has two distinct controls and they must not be conflated.

### M7-local — returned expansion detection

The local counting self-test may make its GET stub return a current scope that is not
a subset of `scope_original`. The GET-only runner still makes no PATCH call.

Expected:

```text
gate_decision  = REFUSED_STALE
evidence_class = INVALID_SOURCE_CONTRACT
http_get_calls = 1
patch_calls    = 0 (no PATCH capability exists in the runner)
```

This proves only that the classifier rejects an observed expansion. It does not prove
that FIPSign refuses an expansion request.

### M7-live — source-operator expansion attempt

Only FIPSign or the source operator may execute the live expansion attempt.

Allowed outcomes:

- `REFUSED_BY_SOURCE` — response/status recorded with secrets removed;
- `NOT_EXECUTED_BY_SOURCE_OPERATOR` — operator declined or did not provide it;
- `INVALID_SOURCE_CONTRACT` — the external API accepted expansion.

`NOT_EXECUTED_BY_SOURCE_OPERATOR` is not a PASS and cannot be described as tested.
It does not by itself falsify a clean M1 scope-narrow result. If expansion is accepted,
the source contract and Cell 7 run are INVALID.

## 8. Additional forbidden claims

All prior forbidden claims remain. Add:

- "the baseline receipt is cryptographically sealed";
- "the carry is tamper-proof against the local user";
- "the baseline GET proves the remote issuance instant";
- "FIPSign refused expansion" when M7-live was not executed;
- "M7 passed" when only M7-local classifier detection ran.

## 9. Re-review conditions

A clean breaker must confirm:

1. two bounded invocations rather than one human-waiting keyed process;
2. adapter-authored baseline and capture receipt with canonical hashing;
3. carry verification occurs before key acquisition or any HTTP call;
4. baseline mismatch produces zero HTTP calls;
5. `Grant.source_snapshot` comes only from the verified baseline;
6. the local custody limitation is explicit; and
7. M7-local and M7-live cannot be reported as the same control.

Only a clean PASS on body + v1 + v2 authorizes implementation.
