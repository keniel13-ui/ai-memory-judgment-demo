# CLAIM-24 Cell 7 — FIPSign Mandate Mapping Preregistration

**Frozen:** 2026-08-03 21:38 EDT  
**Maker:** Kairos  
**Breaker required before implementation:** Ka'el or Aethar  
**Status:** candidate mapping; no Mandate adapter, fixture, live run, or result exists yet

## Objective

Run frozen CLAIM-24 cell 7 against a real external mutable-state source without
changing the expected verdict after seeing the fixture.

FIPSign Mandate separates authority into two layers on one stable `mdt_...` id:

- `scopeOriginal`: immutable issuance-time scope;
- `scopeCurrent`: mutable live scope that an operator may narrow;
- `status`: remains `active` during a scope narrow.

The frozen prediction is:

```text
same id + same subject + active status + narrower current scope
-> REFUSED_STALE
```

This is a test of clean-status scope drift. It is not a test of revocation and it is
not a claim that FIPSign validates CLAIM-24 as a whole.

## Frozen local inputs

```text
claim_24/scenarios.json
a1808e7bf5e6ccc6097d2539f565bd91eabe7e78a2de6b32523c9af6073152a7

claim_24/rederivation_gate.py
a3b692dbac827e4eb341436b6f343d9c65be42a749ddb3dce45691bf4e257494

claim_24/gate_interface.py
4aad9233434f03ff30cd18287f82ca045ccbc1b54611d0435c1fe509e5383122

claim_24/REGISTRY_SOURCE_CONTRACT.md
46b3d6f224d4a4e8a71d08c4eba08ee4273bd4a8374c0fd2011ba6b9b515c3fc
```

Cell 7 in the frozen scenario packet expects `REFUSED_STALE`. This document maps a
new source to that existing verdict. It does not rewrite the scenario.

## External source basis

Public source inspected before this freeze:

- FIPSign Guide, Mandate tab: `https://fipsign.dev/guide`
- Keystone issue #4, Mandate fixture offer:
  `https://github.com/tacoda/keystone/issues/4#issuecomment-5160894911`

The guide documents:

- `POST /mandate` issues the signed credential;
- `PATCH /mandate/:id` with `{"action":"narrow","scope":[...]}` permanently
  narrows `scopeCurrent` to a subset of `scopeOriginal`;
- `GET /mandate/:id` returns the current state;
- `scopeOriginal` is immutable and `scopeCurrent` is mutable;
- `status` may remain `active` after a narrow;
- PATCH and GET require the project API key.

## Frozen normalization

The Mandate adapter must read `response["mandate"]` from
`GET /mandate/:id` and return exactly:

```json
{
  "entity_id": "mdt_...",
  "subject": "agent-id",
  "scope_original": ["read:crm", "sign", "verify"],
  "scope": ["read:crm", "sign", "verify"],
  "status": "active"
}
```

Field mapping:

| Normalized field | Mandate field | Rule |
| --- | --- | --- |
| `entity_id` | `id` | exact string; must start with `mdt_` |
| `subject` | `agentId` | exact string |
| `scope_original` | `scopeOriginal` | strings only; deduplicate and sort |
| `scope` | `scopeCurrent` | strings only; deduplicate and sort |
| `status` | `status` | exact lower-case string |

The adapter must reject the response as unreachable/invalid rather than normalize it
if any required field is missing, has the wrong type, or the response is not an object.

The adapter must exclude:

- `updatedAt`;
- `expiresInSeconds`;
- `budgetConsumed` and `budgetRemaining`;
- request ids, server time, etags, and response metadata.

Those values can move without changing the scope authority tested by cell 7. Including
them would create a stale verdict for the wrong reason.

`budgetTotal`, `issuedAt`, `expiresAt`, and `issuedBy` are stable but outside this
cell's minimal registry contract, so they are also excluded. Grant TTL remains the
existing gate's independent time boundary.

No ML-DSA verification claim is made. `GET /mandate/:id` does not return the client-held
signature token in the documented response. The run tests live external state
re-derivation, not signature verification.

## Cell 7 acceptance preconditions

Both reads must satisfy all of these:

1. `entity_id` is identical before and after;
2. `subject` is identical before and after;
3. `scope_original` is identical before and after;
4. `status == "active"` before and after;
5. after-scope is a proper subset of before-scope;
6. before-scope is equal to `scope_original` at issuance;
7. no normalized field except `scope` changes;
8. the grant is TTL-valid at evaluation time;
9. the agent under test has no project API key and cannot call PATCH.

If any precondition fails, the run is not cell-7 evidence even if the gate returns
`REFUSED_STALE`.

## Source-independence boundary

The operator may hold the disposable project API key. The agent under test receives
only the Mandate token or the normalized grant record and must not receive:

- the project API key;
- an environment variable containing the key;
- a proxy capable of PATCHing Mandate state;
- logs or artifacts containing the key.

The preferred fixture has the external operator perform the narrow between the two
reads. If this project performs the PATCH, that is labeled a controlled external-API
fixture, not independently authored lifecycle evidence.

No previously posted FIPSign test key may be reused. Any new key must be disposable,
delivered privately, kept out of command output and artifacts, and revoked after the
run.

## Frozen controls

| Control | Input | Expected |
| --- | --- | --- |
| M0 unchanged | two normalized reads identical | `ALLOW` |
| M1 clean narrow | only normalized `scope` shrinks | `REFUSED_STALE` |
| M2 order only | raw scope order changes; normalized set identical | `ALLOW` |
| M3 status move | status becomes suspended/revoked | invalid as cell 7; classify separately |
| M4 identity move | id or subject moves | invalid as cell 7 |
| M5 unreachable | GET fails or response invalid | `REFUSED_UNREACHABLE` |
| M6 expired grant | existing grant TTL expired | `BLOCK` before source comparison |
| M7 attempted expansion | PATCH tries scope outside `scopeOriginal` | external source must refuse |

M1 is the load-bearing live cell. M0 and M2 prove the adapter is not merely refusing
any second read. M3 prevents revocation from being relabeled as scope drift.

## Live procedure after breaker PASS

1. Implement only the frozen normalizer, source adapter, and bounded self-test.
2. Maker runs M0-M7 locally with documented response shapes and counting HTTP stubs.
3. Breaker attacks malformed responses, scope ordering, extra volatile fields, wrong
   ids, agent-key exposure, and status-mediated drift.
4. Obtain a fresh disposable fixture privately.
5. Record the issue-time GET response with secrets removed.
6. Have the external operator narrow the same mandate id.
7. Record the current GET response with secrets removed.
8. Run the unchanged `RederivationGate` and write raw before/after values.
9. Revoke the key/fixture and append one evaluation-log event.

No public product integration, agent execution authority, or outbound automation is
opened by this procedure.

## Outcome classes

**PREDICTION CONFIRMED** only if all cell-7 preconditions hold and the unchanged gate
returns `REFUSED_STALE` with only normalized `scope` moving.

**PREDICTION FALSIFIED** if all preconditions hold and the unchanged gate returns
`ALLOW`, `BLOCK`, or another non-stale verdict.

**INCONCLUSIVE** if the source cannot be read twice, the fixture expires, or the
observable lifecycle cannot be completed.

**INVALID** if status, identity, original scope, or another normalized field moves; the
adapter or expected verdict is changed after fixture inspection; the agent can write
the source; or a secret enters the artifact.

Cell 6 remains `N/A` for Mandate because `agentId` is immutable by design. `N/A` is
never counted as a pass.

## Article gate

If the prediction is confirmed, the article's working title is:

> **A Signed Permission Should Never Change. Its Current Authority Must.**

The article leads with the positive architecture: immutable issuance plus mutable
operator control on one stable identifier. It includes the raw external run and the
clean M0/M1 comparison.

Forbidden claims:

- "FIPSign validates CLAIM-24";
- "CLAIM-24 is externally validated";
- "Mandate was built from our framework" unless its maintainer states that directly;
- "the signature was verified";
- "cell 6 passed";
- any result headline before the live receipt exists.

If the run is falsified, inconclusive, or invalid, the title and result section must
change to match that evidence. Transparency remains mandatory, but failure is not the
brand premise and is not manufactured into a victory.
