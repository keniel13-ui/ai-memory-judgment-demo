# CLAIM-24 FIPSign SourceAdapter Notes

Status: adapter implemented, live external run waiting on FIPSign CA base URL and live certificate IDs.

## What Exists

- `fipsign_source_adapter.py`
  - Implements the `SourceAdapter` interface from `gate_interface.py`.
  - Reads `GET /ca/certificate/:certId`.
  - Exposes `fetch_public_key()` for `GET /public-key`.
  - Returns `agent_writable = False`.
  - Normalizes PQCert-like certificate state into stable raw snapshots for `RederivationGate`.

- `run_fipsign_adapter_selftest.py`
  - Local contract test only.
  - Does not contact FIPSign.
  - Proves unchanged, changed, and unreachable FIPSign-shaped states produce `ALLOW`, `REFUSED_STALE`, and `REFUSED_UNREACHABLE` through the existing gate.

- `run_fipsign_live_eval.py`
  - Live runner for a real FIPSign CA base URL.
  - Writes result artifacts to `results/claim24_fipsign_*`.
  - Accepts an optional scenario file with `--scenarios`.

## What Does Not Exist Yet

- A pinned public FIPSign CA base URL in this repo.
- Live certificate IDs mapped to the seven frozen CLAIM-24 scenarios.
- Cryptographic signature verification against ML-DSA-65.

The adapter preserves returned signature fields, but it does not mark signatures verified. Do not claim signature verification until the exact PQCert signing payload and public-key format are pinned and tested.

## Live Run Shape

Once the base URL and cert IDs exist:

```bash
python3 claim_24/run_fipsign_live_eval.py \
  --base-url https://example-fipsign-ca \
  --scenarios claim_24/fipsign_live_scenarios.json \
  --operation-time 2026-06-05T12:00:00Z \
  --label live
```

The live scenario file should keep the original seven CLAIM-24 cells:

1. TTL-valid + conditions unchanged -> `ALLOW`
2. TTL-expired -> `BLOCK`
3. TTL-valid + conditions changed -> `REFUSED_STALE`
4. Source unreachable -> `REFUSED_UNREACHABLE`
5. No grant -> `BLOCK`
6. Recipient changed -> `REFUSED_STALE`
7. Scope narrowed -> `REFUSED_STALE`

For each FIPSign-backed grant, `source_snapshot` should be the output of `normalize_pqcert()` at issue time, and the live adapter should fetch the current state at execution time.

## Evidence Boundary

Current evidence tier after this implementation:

> Adapter implemented and harness-compatible; external-source run pending live CA inputs.

Allowed future wording only after a successful live run:

> CLAIM-24 was exercised against a real external FIPSign CA source for the mapped scenarios.

Forbidden until signature verification is implemented:

> CLAIM-24 cryptographically verified FIPSign signatures.
