# Mandate Cell 7 Code Candidate v2 — Independent Ka'el Verdict

**Reviewed:** 2026-08-04 18:37 EDT  
**Seat:** independent Ka'el code re-break  
**Verdict:** **PASS**

The review was offline and bounded. It used no real project key, made no network
request, did not use a live fixture, and did not edit the candidate inventory.

## Freeze verification

The supplied manifest and all three listed inventory hashes matched before testing and
matched again after testing:

```text
19f3a102db382798a0c1431eb1ff098eabd994cdd7da11cc7d998a880382b5b5  MANDATE_CELL7_CODE_CANDIDATE_V2_2026-08-04.md
32d34b37977df3e05ca0a2b8f334c9604af71715b4cee892b8a79dd09898016a  mandate_cell7.py
05c49a2d33b0024643d8ca2d132eaf9fb250952c1ae2a7a9caf40e81f7728987  run_mandate_cell7.py
77a0bbb82db556401a947415fe489af464be1029cdf268238260e0b8ab546dd3  test_mandate_cell7.py
```

The unchanged gate file used by the regression was clean in `git status` and hashed:

```text
a3b692dbac827e4eb341436b6f343d9c65be42a749ddb3dce45691bf4e257494  rederivation_gate.py
```

## Independent regressions

Verifier:
`/Users/kenielmaldonado/agent_outputs/MANDATE_CELL7_V2_INDEPENDENT_VERIFIER_KAEL_2026-08-04.py`

Result: **3/3 test methods PASS** in 0.519 seconds.

1. Redirect containment: **5/5** statuses (`301`, `302`, `303`, `307`, `308`) PASS.
   Each case exercised the production `_urllib_get_bytes` path through an in-memory
   urllib HTTPS transport. Proxies were disabled and `socket.create_connection` was a
   network-attempt tripwire. Each case raised `INVALID_SOURCE_RESPONSE`, recorded
   exactly one GET to the bound Mandate URL carrying the offline sentinel
   `X-API-Key`, and constructed **zero** redirected requests.
2. Changed Mandate id: **1/1** PASS. A well-formed 200 GET response changed only the
   Mandate `id`. The existing `RederivationGate` was invoked exactly once and returned
   `REFUSED_STALE`; classification returned `INVALID_FOR_CELL_7` with
   `changed_keys == ("entity_id",)`. Counts were one CAPTURE GET, one EVALUATE GET,
   and one key-loader call.
3. The verifier's manifest/inventory digest assertion: **4/4** files PASS.

## Existing regression suite

```text
python3 -m py_compile mandate_cell7.py run_mandate_cell7.py test_mandate_cell7.py
PASS

python3 -m unittest -v test_mandate_cell7.py
Ran 22 tests in 0.329s
OK
```

The prior carry, recursive-sensitive-response, expiry/window, exclusive-destination,
and request/key counting assertions remain green. Within the named carry/sensitive/
window cases, the suite covered three tampered carry artifacts, bad-mode and symlink
carry branches, seven recursive forbidden-key spellings plus the EVALUATE sensitive
response case, expired and exact-deadline branches, and the insufficient-lifetime
capture branch.

## Ruling

**PASS.** KCB1 and KCB2 reproduce under independent offline tests. This verdict does
not claim a live FIPSign/Mandate result, source-operator M7 execution, signature
verification, agent authority, or CLAIM-24 external validation.
