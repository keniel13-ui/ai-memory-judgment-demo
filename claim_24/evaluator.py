"""
CLAIM-24 evaluator.
Runs all 7 pre-registered scenarios through a gate and produces a result table.
Pass either TimestampOnlyGate or RederivationGate.
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from gate_interface import Gate, Grant, AuthorityEvent


SCENARIOS_PATH = Path(__file__).parent / "scenarios.json"


def load_scenarios() -> list:
    with open(SCENARIOS_PATH) as f:
        data = json.load(f)
    return data["scenarios"]


def parse_grant(raw: Optional[dict]) -> Optional[Grant]:
    if raw is None:
        return None
    return Grant(
        grant_id=raw["grant_id"],
        recipient=raw["recipient"],
        scope=raw["scope"],
        issued_at=datetime.fromisoformat(raw["issued_at"].replace("Z", "+00:00")),
        ttl_hours=raw["ttl_hours"],
        source_snapshot=raw["source_snapshot"]
    )


def run(gate: Gate, label: str, operation_time: Optional[datetime] = None) -> list:
    scenarios = load_scenarios()
    now = operation_time or datetime.now(timezone.utc)
    results = []

    print(f"\n{'='*60}")
    print(f"CLAIM-24 Evaluation — {label}")
    print(f"Run time: {now.isoformat()}")
    print(f"{'='*60}\n")
    print(f"{'ID':<4} {'Expected':<22} {'Got':<22} {'Pass':<6} Notes")
    print(f"{'-'*4} {'-'*22} {'-'*22} {'-'*6} {'-'*30}")

    all_pass = True
    divergence_cell_result = None

    for s in scenarios:
        grant = parse_grant(s.get("grant"))
        event: AuthorityEvent = gate.evaluate(grant, now)

        expected = s["expected"]
        got = event.decision
        passed = got == expected

        if s["id"] == 3:
            divergence_cell_result = got

        if not passed:
            all_pass = False

        marker = "PASS" if passed else "FAIL"
        divergence = " ← DIVERGENCE CELL" if s["id"] == 3 else ""
        print(f"{s['id']:<4} {expected:<22} {got:<22} {marker:<6} {event.notes}{divergence}")

        results.append({
            "scenario_id": s["id"],
            "description": s["description"],
            "expected": expected,
            "got": got,
            "passed": passed,
            "condition_delta": event.condition_delta,
            "ttl_remaining_hours": event.ttl_remaining_hours,
            "notes": event.notes
        })

    print(f"\n{'='*60}")
    print(f"All scenarios passed: {all_pass}")
    print(f"Divergence cell (scenario 3) result: {divergence_cell_result}")
    if divergence_cell_result == "ALLOW":
        print("*** ARCHITECTURE FAILED — divergence cell returned ALLOW ***")
    print(f"{'='*60}\n")

    return results


if __name__ == "__main__":
    gate_type = sys.argv[1] if len(sys.argv) > 1 else "timestamp"

    if gate_type == "timestamp":
        from timestamp_only_gate import TimestampOnlyGate
        gate = TimestampOnlyGate()
        label = "TimestampOnlyGate (baseline)"
    elif gate_type == "rederivation":
        # When Ken's Local Brain source is available:
        # from your_source_adapter import LocalBrainAdapter
        # source = LocalBrainAdapter(...)
        # gate = RederivationGate(source)
        print("RederivationGate requires an external source adapter.")
        print("Implement SourceAdapter for Ken W Alger's Local Brain, then pass it here.")
        sys.exit(1)
    else:
        print(f"Unknown gate type: {gate_type}. Use 'timestamp' or 'rederivation'.")
        sys.exit(1)

    run(gate, label)
