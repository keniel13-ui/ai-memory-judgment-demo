# CLAIM-24 Grant-Side Schema: Data Layout for the Cells 6/7 Fixture Conversation

**Status:** documentation of the frozen CLAIM-24 harness as it exists at commit `90db04d`.
This file changes nothing. It describes the data layout Ken W Alger asked for so a
deterministic FIPSign test fixture path can be scoped for the two unfinished cells:
recipient-changed (cell 6) and scope-narrowed (cell 7).

**Evidence boundary, stated up front:** cells 1-5 have a live external-source result
against `https://api.fipsign.dev` (append-only log event `9c44ec9a...`). Cells 6 and 7
are mock-validated only. ML-DSA signature fields are preserved but not verified. Nothing
in this document upgrades any of that.

---

## 1. The grant record (written at issue time)

Defined in `gate_interface.py` as `Grant`:

| Field | Type | Meaning |
| --- | --- | --- |
| `grant_id` | string | Unique grant identifier. Doubles as the cert id fallback (see section 4). |
| `recipient` | string | Who the grant authorizes. Example: `agent:worker-6`. |
| `scope` | string | What the grant authorizes. Example: `read:credentials:dev`. |
| `issued_at` | datetime | Issue timestamp. |
| `ttl_hours` | int | Plain expiry window. TTL is checked first and is deliberately not the interesting part. |
| `source_snapshot` | dict | Raw external-source state recorded at issue time, produced by the same normalization function used at re-fetch. This is the field everything else compares against. |

The critical contract: `source_snapshot` must be created by the same normalization that
runs at execution time. The grant does not store interpretations. It stores what the
source said, normalized, at the moment of issue.

## 2. The normalized snapshot shape (what we read from FIPSign)

`fipsign_source_adapter.py` fetches `GET /ca/certificate/:certId` and normalizes the
returned PQCert-like object into:

```json
{
  "cert_id": "...",
  "subject": "...",
  "issuer": "...",
  "scope": "...",
  "status": {
    "revoked": false,
    "expired": false,
    "expires_at": "..."
  },
  "meta": { "...": "raw passthrough, key-sorted" },
  "algorithm": "...",
  "standard": "...",
  "signature": "recorded, not verified",
  "signed_payload": "recorded, not verified"
}
```

Field sourcing is conservative and accepts common key variants (`subject` from
`subject` / `subject_id` / `holder` / `owner`; `scope` from `scope` / `scope_ceiling`
or meta equivalents). No derived labels are ever added during normalization. There is
no `stale` field anywhere in the pipeline.

## 3. The decision record (written at decision time)

`AuthorityEvent`, frozen as of decision time, CLAIM-26 pairing:

| Field | Meaning |
| --- | --- |
| `decision` | `ALLOW`, `BLOCK`, `REFUSED_STALE`, or `REFUSED_UNREACHABLE`. Stale and unreachable are separate cells and are never conflated. |
| `source_snapshot` | What the grant recorded at issue time. |
| `source_current` | What the source returned at execution time. |
| `condition_delta` | `{"before": {...}, "after": {...}}`. Raw values only. Never a derived `stale: true`. |
| `ttl_remaining_hours` | Raw freshness arithmetic at decision time. |

## 4. The comparison rule (why cells 3, 6, and 7 are different evidence)

Order of evaluation in `rederivation_gate.py`:

1. No grant: `BLOCK`.
2. TTL expired: `BLOCK`.
3. Source fetch fails: `REFUSED_UNREACHABLE`. This never falls through to stale.
4. Whole-snapshot equality: if the normalized current state differs from the recorded
   `source_snapshot` in any field, the verdict is `REFUSED_STALE` and the raw
   before/after pair is stored in `condition_delta`.

The verdict for cells 3, 6, and 7 is identical by design. The evidence distinction
lives in `condition_delta`, in which raw field moved:

| Cell | What moved in the delta | Status fields |
| --- | --- | --- |
| 3 (conditions changed) | live run: `status.revoked` flipped true | revoked |
| 6 (recipient changed) | the subject/authorized-recipient field, nothing else | still valid, not revoked, not expired |
| 7 (scope narrowed) | the scope field, nothing else | still valid, not revoked, not expired |

This is exactly why revocation-as-proxy cannot stand in for cells 6 and 7. A revoked
cert produces a delta in the status field. Cells 6 and 7 require a delta in the
recipient or scope field while the status stays clean. Reusing revocation would
collapse three distinct drift families into one and the run would prove nothing the
cell-3 result has not already proven.

## 5. What a deterministic FIPSign fixture path needs to provide

For cell 6, one certificate lifecycle where:

- the cert is issued with a subject/holder/authorized-recipient field visible in
  `GET /ca/certificate/:certId`,
- after issue, that field can change (rebind, reassignment, holder transfer, any
  mechanism) while `status.revoked` remains `false` and the cert is not expired,
- the changed value is returned by the same GET endpoint afterward.

For cell 7, one certificate lifecycle where:

- the cert is issued with a scope or scope-ceiling field visible in the same endpoint,
- after issue, that scope can be narrowed while status stays clean,
- the narrowed value is returned by the same GET endpoint afterward.

Operational requirements for both:

- **Two observable states.** We fetch once at grant-issue time to record
  `source_snapshot`, the mutation happens, we fetch again at execution time. A
  pre-staged pair of states with a trigger, or two fixture cert ids representing
  before/after, both work. It does not need to be a production behavior; an explicit
  test-fixture path is fine and will be labeled as such in the results.
- **Repeatability.** The lifecycle should be reproducible so the run can be re-executed
  and audited.
- **Surface compatibility.** The moving field must appear in the certificate body or
  meta of `GET /ca/certificate/:certId`, because that is all the adapter reads.

If FIPSign already has a real post-issue mechanism that mutates subject or scope
without revocation, that is strictly better than a synthetic fixture and we would
rather use it. The synthetic path is the fallback, not the preference.

## 6. How the result will be labeled

If both cells run against live fixtures: the ledger upgrades CLAIM-24 from
"live external-source mapped subset (cells 1-5)" to "live external-source result,
cells 1-7," with synthetic-fixture caveats named if the lifecycle was test-path rather
than production behavior. Signature verification remains a separate, future claim
either way. Each run gets its own append-only evaluation log event.
