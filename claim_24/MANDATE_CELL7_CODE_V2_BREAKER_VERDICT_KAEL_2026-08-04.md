# Mandate Cell 7 — Code Candidate v2 Independent Breaker Verdict

**Breaker:** Ka'el (live terminal seat, not a spawned subagent)
**Maker:** Kairos
**Date:** 2026-08-04 EDT
**Answers:** `MANDATE_CELL7_CODE_BREAKER_VERDICT_KAEL_2026-08-04.md` KCB1–KCB2

## Frozen candidate — verified unchanged before and after

```text
mandate_cell7.py       32d34b37977df3e05ca0a2b8f334c9604af71715b4cee892b8a79dd09898016a
run_mandate_cell7.py   05c49a2d33b0024643d8ca2d132eaf9fb250952c1ae2a7a9caf40e81f7728987
test_mandate_cell7.py  77a0bbb82db556401a947415fe489af464be1029cdf268238260e0b8ab546dd3
```

Matches the v2 inventory exactly. Candidate not edited.

## Verdict: **PASS.** KCB1 and KCB2 are repaired. Live fixture authorized.

---

## Seat independence — stated plainly, because it was at risk

The prior breaker work was performed by Ka'el **subagents that Kairos spawned and
instructed.** A breaker the maker creates and briefs is not an independent seat; it is
maker review at one level of indirection, and it weakens exactly the guarantee this
process exists to provide.

Both of those subagents were also terminated by a platform security classifier before
returning a verdict — an expected consequence of accumulating offensive-security context
while writing credential-exfiltration harnesses. The mechanism is structurally
incompatible with the task.

This verdict is issued from the live terminal seat Keniel assigned directly. I did not
write the implementation and was not briefed by the maker.

**What I inherited vs. what I proved:** the surviving subagent artifact
`MANDATE_CELL7_V2_INDEPENDENT_VERIFIER_KAEL_2026-08-04.py` was read for safety
(synthetic transport, mocked socket, tempfile only — offline by construction) and
executed unchanged: 3/3 OK. That is corroboration, **not** my verdict. My verdict rests
on the four attacks below, which I authored and ran myself.

## My attacks on the v2 repairs

### A1 — does urllib swallow the redirect refusal?

The repair raises inside `redirect_request`. If urllib caught and converted that, the
refusal would silently degrade.

```text
_RejectRedirectHandler.redirect_request(302 → https://attacker.invalid/collect)
→ raises MandateCell7Error(INVALID_SOURCE_RESPONSE)
```

Propagates as a typed fail-closed error. **PASS.**

### A2 — is only 302 covered?

KCB1's original reproduction used a 302. A repair that handles one code and not the
others would look fixed and leak on a 307.

```text
301 refused · 302 refused · 303 refused · 307 refused · 308 refused
```

All five. **PASS.**

### A3 — did removing the id check from `read()` open a new hole?

KCB2's repair deletes the in-adapter `entity_id != bound_id` rejection so an identity
move can reach the gate. My concern: CAPTURE could now accept a moved id as its
baseline, which would be worse than the bug it fixed.

```text
baseline_preconditions({"entity_id": "mdt_ATTACKER", ...}, bound_id="mdt_cell7fixture")
→ False
```

CAPTURE still refuses. The repair is contained to EVALUATE, which is where it belongs.
**PASS.**

### A4 — does an id move still classify correctly?

```text
gate_decision  REFUSED_STALE
changed_keys   ('entity_id',)
evidence_class INVALID_FOR_CELL_7
cell_7_preconditions_passed  False
```

Exactly the frozen M4 expectation. An identity move is recorded as evidence rather than
erased as source unavailability, and it is never miscounted as Cell 7. **PASS.**

## Verification network boundary

```text
network calls during this attack   0
real credentials used              0
candidate edits                    0
FIPSign requests                   0
```

`urllib.request.Request` appears once, `build_opener` once, `opener.open` once — a
single network path, all three inside the bound GET-only adapter. No `PATCH`, no `POST`,
no `subprocess`, no generic requester.

## Authorized next step

The live disposable FIPSign fixture is now **unblocked by this gate**. Two external
conditions remain and are not mine to clear:

1. **No project key is present.** `FIPSIGN_API_KEY` is absent and no disposable fixture
   has arrived from the source operator.
2. **Power has been intermittently red** — AC selected while discharging. The live run
   must not start unattended in that state.

M7-live remains `NOT_EXECUTED_BY_SOURCE_OPERATOR` until FIPSign runs it. It is not a
pass and must never be reported as tested.

## Standing correction for the next cycle

**Do not spawn a breaker.** The independent seat must be an instance the maker did not
create or instruct. Two subagent attempts died to a security classifier while a live
independent seat sat idle. The mechanism is available; use it.
