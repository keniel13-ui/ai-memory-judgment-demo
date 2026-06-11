"""
Local self-test for the FIPSign CLAIM-24 adapter.

This does not contact the real FIPSign CA and does not create external-source
evidence. It proves the adapter satisfies the SourceAdapter contract and that the
existing RederivationGate can consume normalized FIPSign-shaped certificate state.
"""

from datetime import datetime, timezone

from fipsign_source_adapter import FIPSignSourceAdapter, normalize_pqcert
from gate_interface import Grant
from rederivation_gate import RederivationGate


def make_grant(snapshot: dict) -> Grant:
    return Grant(
        grant_id="cert-001",
        recipient="agent:worker-1",
        scope="read:credentials:dev",
        issued_at=datetime(2026, 6, 4, 20, 0, tzinfo=timezone.utc),
        ttl_hours=72,
        source_snapshot=snapshot,
    )


def run_case(name: str, current_raw: dict | None, snapshot: dict, expected: str) -> bool:
    def fake_get_json(url: str):
        return current_raw

    adapter = FIPSignSourceAdapter("https://fipsign.example.test", http_get_json=fake_get_json)
    gate = RederivationGate(adapter)
    event = gate.evaluate(make_grant(snapshot), datetime(2026, 6, 5, 12, 0, tzinfo=timezone.utc))
    passed = event.decision == expected
    marker = "PASS" if passed else "FAIL"
    print(f"{name:<28} expected={expected:<20} got={event.decision:<20} {marker}")
    return passed


def main() -> int:
    unchanged_raw = {
        "id": "cert-001",
        "subject": "agent:worker-1",
        "issuer": "fipsign-ca",
        "scope": "read:credentials:dev",
        "status": {"revoked": False, "expired": False},
        "meta": {"role": "dev-reader"},
        "signature": "mock-signature",
    }
    changed_raw = {
        **unchanged_raw,
        "scope": "read:logs:dev",
        "meta": {"role": "restricted"},
    }
    snapshot = normalize_pqcert(unchanged_raw)

    checks = [
        run_case("unchanged certificate", unchanged_raw, snapshot, "ALLOW"),
        run_case("changed certificate", changed_raw, snapshot, "REFUSED_STALE"),
        run_case("unreachable certificate", None, snapshot, "REFUSED_UNREACHABLE"),
    ]
    print(f"agent_writable=false: {FIPSignSourceAdapter('https://fipsign.example.test').agent_writable is False}")
    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
