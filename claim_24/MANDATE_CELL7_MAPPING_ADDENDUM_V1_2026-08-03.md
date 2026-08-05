# CLAIM-24 Mandate Cell 7 Mapping — Addendum v1

**Frozen:** 2026-08-03 EDT  
**Maker:** Kairos  
**Applies to candidate:** `MANDATE_CELL7_MAPPING_PREREGISTRATION_2026-08-03.md`  
**Candidate SHA-256:** `ad8b5066db2644be63761095df9e0712b29b53eccfe452773167ea0b8bc776c6`  
**Answers:** Ka'el verdict `e810ea606ff045581d0f9a919040a1758b071fe23ef50baa078ca4b17210ed36`  
**Prior Aethar verdict:** PASS `632ac6e9f36c73be6dc522734a453adfd50b889bf0ed395a0069c488fc527e0c`  
**Current status:** BLOCK until this addendum passes a clean breaker seat

The frozen candidate is not edited. This addendum supersedes it where the two
conflict. No adapter, fixture, credential, live call, or result exists.

## 1. Adjudication of the conflicting breaker verdicts

Ka'el is correct that the public FIPSign guide documents one project API key for
Mandate GET and PATCH. No read-only project key or token-only introspection path is
documented. Aethar also noticed this but treated the runtime boundary as an
implementation advisory.

That boundary is load-bearing and must be frozen before implementation. Ka'el's later
BLOCK therefore controls until this addendum is independently reviewed.

Ka'el's factual finding is accepted. The forced two-branch conclusion is narrowed:

- the untrusted agent under test is not the trusted gate runner;
- the trusted gate runner may directly GET from FIPSign using an operator-held key;
- the operator does not fetch a snapshot and hand arbitrary JSON to the gate;
- the gate runner is part of the trusted computing base and is not evidence that the
  agent can write the source.

`agent_writable=false` means the agent being governed lacks source-write capability.
It does not mean nobody, including the source operator, can ever mutate the source.
Mandate's purpose is precisely to let the operator narrow authority while withholding
that control from the agent.

The original prereg failed to freeze these distinct principals. That omission is
accepted as K1's load-bearing repair.

## 2. Frozen runtime principals

The test has exactly three roles:

### A. Agent under test

The agent is the subject represented by the grant and attempted operation. It has:

- the Mandate token only if a test action needs it;
- no project API key;
- no environment, file, prompt, tool, proxy, or IPC path exposing the project key;
- no ability to execute code inside the gate runner;
- no ability to choose HTTP method, base URL, or arbitrary endpoint path.

The first live Cell 7 run exercises the re-derivation gate, not a production agent
runtime. If no live agent process is involved, the receipt must say so explicitly:
the source-write separation is a frozen deployment precondition, not a demonstrated OS
sandbox result.

### B. Trusted gate runner

The gate runner is the verifier, not the agent. It:

- receives the disposable project API key at runtime;
- reads it only from a named environment variable;
- uses it only for direct `GET /mandate/:bound_id`;
- exposes no PATCH, POST, generic request, shell, callback, or arbitrary URL surface;
- binds `base_url` to `https://api.fipsign.dev` for the live run;
- URL-quotes the grant-bound Mandate id as one path segment;
- never prints, serializes, returns, or writes the key;
- executes no agent-authored code while the key is present;
- clears the runtime key reference after the bounded read/run completes.

The adapter constructor may accept a narrow `http_get_json(url, headers)` test seam.
It must not accept a generic method-capable requester in production code.

The gate runner technically holds a credential that FIPSign also accepts for PATCH.
This experiment does **not** prove safety against a malicious or compromised gate
runner. It tests whether the governed agent, which lacks that credential and process
reach, is refused after an external operator changes live scope.

### C. Source operator

FIPSign or the fixture operator controls Mandate mutation. The preferred live run has
that external operator perform the narrow. If Keniel's side performs the PATCH, the
evidence tier is downgraded to `controlled external-API fixture`.

## 3. K1 outcome and read-only path

A read-only FIPSign credential would strengthen the deployment shape but is not a
prerequisite for this scoped experiment because source independence is relative to the
agent under test, not the trusted verifier.

The public guide currently shows `X-API-Key` on `POST /mandate/verify`; no token-only
path is assumed. The implementation must not invent one.

If a future read-scoped key or token-only introspection endpoint exists, it may be
tested in a separately frozen addendum. It cannot be silently substituted into this
run after fixture inspection.

The run is **INVALID** if:

- the agent under test receives or can recover the project key;
- agent-authored code runs inside the keyed gate process;
- the adapter can issue PATCH/POST or accepts an attacker-controlled method or URL;
- an operator supplies hand-authored normalized JSON instead of the adapter directly
  reading the external GET response;
- any artifact contains the key or full Mandate token.

## 4. K2 accepted — verdict is necessary, not sufficient

The unchanged `RederivationGate` performs whole-snapshot equality. Its
`REFUSED_STALE` verdict means only:

> at least one normalized field changed.

It does not classify which field changed. M1 scope drift, M3 status drift, and M4
identity drift all correctly produce the same gate verdict.

Cell 7 classification therefore belongs to a separate evidence classifier operating
on `AuthorityEvent.condition_delta` after the gate decision.

The classifier must compute top-level changed keys from the recorded raw normalized
snapshots:

```text
changed_keys = {
  key for key in union(before, after)
  if before.get(key, MISSING) != after.get(key, MISSING)
}
```

The live result counts as Cell 7 evidence only when all of these hold:

```text
gate decision                 == REFUSED_STALE
changed_keys                  == {"scope"}
before.entity_id              == after.entity_id
before.subject                == after.subject
before.scope_original         == after.scope_original
before.status                 == after.status == "active"
set(after.scope)              < set(before.scope)
set(before.scope)             == set(before.scope_original)
```

The classifier output must be recorded separately from the gate verdict:

```json
{
  "gate_decision": "REFUSED_STALE",
  "changed_keys": ["scope"],
  "evidence_class": "CELL_7_CLEAN_STATUS_SCOPE_DRIFT",
  "cell_7_preconditions_passed": true
}
```

For M3 and M4 the expected gate decision remains `REFUSED_STALE`, but the evidence
classifier must return `INVALID_FOR_CELL_7` with the observed changed keys. A later
reader must never infer Cell 7 from `REFUSED_STALE` alone.

M0 and M2 remain `ALLOW` with no condition delta. M5 and M6 retain their frozen
unreachable and TTL outcomes.

## 5. Budget limitation accepted

This cell tests clean-status **scope drift** only. Mandate budget consumption is a
separate authority-narrowing channel.

Because `budgetConsumed` and `budgetRemaining` are excluded, this adapter can return
an unchanged snapshot even when no budget remains. The article and result receipt must
state this once. They may not generalize the Cell 7 result to all usable Mandate
authority.

The working article title is narrowed to:

> **A Signed Grant Should Stay Fixed. Its Usable Scope Must Be Able to Shrink.**

Budget re-derivation requires a different frozen cell and is outside this run.

## 6. Controls superseding the original table

| Control | Gate verdict | Evidence classification |
| --- | --- | --- |
| M0 identical normalized reads | `ALLOW` | `UNCHANGED_CONTROL` |
| M1 only scope shrinks, active status | `REFUSED_STALE` | `CELL_7_CLEAN_STATUS_SCOPE_DRIFT` |
| M2 order-only raw scope change | `ALLOW` | `ORDER_NORMALIZED_CONTROL` |
| M3 status changes | `REFUSED_STALE` | `INVALID_FOR_CELL_7` |
| M4 id or subject changes | `REFUSED_STALE` | `INVALID_FOR_CELL_7` |
| M5 GET unavailable/invalid | `REFUSED_UNREACHABLE` | `SOURCE_UNREACHABLE` |
| M6 expired grant | `BLOCK` | `TTL_EXPIRED` |
| M7 illegal expansion accepted | not a gate falsifier | `INVALID_SOURCE_CONTRACT` |

The counting self-test must assert both columns. A test that asserts only the gate
verdict is insufficient.

## 7. Forbidden claims retained

- "FIPSign validates CLAIM-24";
- "CLAIM-24 is externally validated";
- "Mandate was built from our framework" unless its maintainer states that directly;
- "the signature was verified";
- "cell 6 passed";
- any result headline before the live receipt exists;
- "REFUSED_STALE proves scope drift" without the exact-delta classifier;
- "the source is unwritable by anyone";
- "all usable authority was re-derived" when budget was excluded.

## 8. Conditions for re-review

1. Confirm the three-principal runtime split is consistent with `SourceAdapter`'s
   agent-relative `agent_writable=false` contract.
2. Confirm direct external GET, not operator-transcribed normalized JSON.
3. Confirm the exact-delta classifier and dual-column M0-M7 expectations.
4. Confirm the budget limitation and narrower article title.
5. Confirm no adapter code exists before the addendum verdict.

Only a clean breaker PASS on the frozen addendum authorizes implementation of the
normalizer, GET-only adapter, evidence classifier, and counting self-test.
