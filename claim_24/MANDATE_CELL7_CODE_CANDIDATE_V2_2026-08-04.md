# Mandate Cell 7 — Frozen Code Candidate v2

**Maker:** Kairos  
**Frozen:** 2026-08-04 EDT  
**Answers:** `MANDATE_CELL7_CODE_BREAKER_VERDICT_KAEL_2026-08-04.md` KCB1–KCB2  
**Status:** maker verification PASS; independent v2 re-break pending

Candidate v1 remains unchanged as the historical blocked input. This v2 inventory
supersedes it for execution only after an independent PASS.

## Exact candidate inventory

```text
mandate_cell7.py
32d34b37977df3e05ca0a2b8f334c9604af71715b4cee892b8a79dd09898016a

run_mandate_cell7.py
05c49a2d33b0024643d8ca2d132eaf9fb250952c1ae2a7a9caf40e81f7728987

test_mandate_cell7.py
77a0bbb82db556401a947415fe489af464be1029cdf268238260e0b8ab546dd3
```

## Repairs

### KCB1 — redirect key containment

The live urllib path installs a redirect handler that refuses every redirect before a
new request can be constructed. The project key therefore remains bound to the
original fixed-origin request. A counting regression invokes the handler with a
cross-origin 302 and requires `INVALID_SOURCE_RESPONSE` before any redirected request
exists.

### KCB2 — M4 identifier evidence

CAPTURE still fails its frozen baseline precondition unless the normalized id equals
the bound id. During EVALUATE, a direct GET on the bound path may return a changed id;
the adapter now passes that normalized state to the unchanged gate. The regression
requires `REFUSED_STALE`, `INVALID_FOR_CELL_7`, and `changed_keys == ("entity_id",)`.

## Maker verification

```text
python3 -m py_compile mandate_cell7.py run_mandate_cell7.py test_mandate_cell7.py
PASS

python3 -m unittest -v test_mandate_cell7.py
Ran 22 tests in 0.324s
OK

git diff --check
PASS
```

No project key, live request, fixture, mutation, agent execution authority, or article
result exists. The live fixture remains forbidden until the independent v2 re-break
returns PASS.
