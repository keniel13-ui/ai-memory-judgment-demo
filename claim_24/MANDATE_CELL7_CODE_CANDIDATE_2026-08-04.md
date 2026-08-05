# Mandate Cell 7 — Frozen Code Candidate

**Maker:** Kairos  
**Frozen:** 2026-08-04 18:15 EDT  
**Status:** maker verification PASS; independent code breaker pending

## Exact candidate inventory

```text
mandate_cell7.py
f9151500f72c9c8ba72f8ed202947291f29189bff60ed0ba9dfb6e91e75c2330

run_mandate_cell7.py
05c49a2d33b0024643d8ca2d132eaf9fb250952c1ae2a7a9caf40e81f7728987

test_mandate_cell7.py
334b6106c4dcae68f327118df5c95d356ec6034a829c1498d16760321d1757f9
```

The candidate is governed by the frozen body plus addenda v1, v2, and terminal v3.
It implements only CAPTURE, EVALUATE, the bound GET-only Mandate adapter and
normalizer, the exact-delta classifier, a bounded CLI, and counting tests.

## Maker verification

```text
python3 -m py_compile mandate_cell7.py run_mandate_cell7.py test_mandate_cell7.py
PASS

python3 -m unittest -v test_mandate_cell7.py
Ran 20 tests in 0.348s
OK

git diff --check
PASS
```

The suite covers M0–M7 gate/classifier behavior, exact GET origin/path containment,
zero PATCH/request surface, raw-byte retention, canonical private artifacts, recursive
case-insensitive sensitive-key rejection through arrays, carry hash/schema/mode/symlink
attacks, exclusive destinations, exact elapsed-window edges, and zero key loads plus
zero HTTP on invalid carry or expired window.

## Authority and evidence boundary

- No project key was loaded.
- No live FIPSign request was made.
- No Mandate fixture was created or mutated.
- No agent execution authority was opened.
- Passing maker tests do not adjudicate the candidate.
- The live fixture remains forbidden until the independent code breaker returns PASS.

The candidate must not be edited during the breaker attack. A reproducible BLOCK
requires a new maker candidate and new hashes.
