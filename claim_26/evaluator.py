"""
CLAIM-26 evaluator.
Runs 7 scenarios through all 4 gates and produces a comparison table.

Usage:
  python3 evaluator.py                  # PairedAuthorityActionGate on all 7 scenarios
  python3 evaluator.py baselines        # 3 baseline gates on all 7 scenarios
  python3 evaluator.py full             # all 4 gates, full comparison table
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from gate_interface import AuthorityRecord, ActionRecord, AuditContext
from decision_only_gate import DecisionOnlyGate
from mutable_pointer_gate import MutablePointerAuditGate
from separate_write_gate import SeparateWriteGate
from paired_authority_action_gate import PairedAuthorityActionGate


SCENARIOS_PATH = Path(__file__).parent / "scenarios.json"


def load_scenarios():
    with open(SCENARIOS_PATH) as f:
        return json.load(f)


def parse_authority(raw: Optional[dict]) -> Optional[AuthorityRecord]:
    if raw is None:
        return None
    return AuthorityRecord(
        authority_event_id=raw["authority_event_id"],
        grant_id=raw["grant_id"],
        decision=raw["decision"],
        decision_timestamp=datetime.fromisoformat(raw["decision_timestamp"].replace("Z", "+00:00")),
        snapshot_hash=raw.get("snapshot_hash"),
        source_sequence=raw.get("source_sequence"),
        policy_version=raw.get("policy_version"),
        run_id=raw["run_id"],
        is_immutable=raw["is_immutable"],
        written_at=datetime.fromisoformat(raw["written_at"].replace("Z", "+00:00")),
        source_uri=raw.get("source_uri"),
    )


def parse_action(raw: dict) -> ActionRecord:
    return ActionRecord(
        action_id=raw["action_id"],
        authority_event_id=raw.get("authority_event_id"),
        action_type=raw["action_type"],
        run_id=raw["run_id"],
        snapshot_hash=raw.get("snapshot_hash"),
        written_at=datetime.fromisoformat(raw["written_at"].replace("Z", "+00:00")),
    )


def parse_context(raw: dict) -> AuditContext:
    return AuditContext(
        active_snapshot_hash=raw.get("active_snapshot_hash"),
    )


def run_gate(gate, gate_label: str, scenarios: list) -> list:
    print(f"\n{'='*72}")
    print(f"Gate: {gate_label}")
    print(f"{'='*72}")
    print(f"{'ID':<4} {'Label':<14} {'Expected':<26} {'Got':<26} {'Pass'}")
    print(f"{'-'*4} {'-'*14} {'-'*26} {'-'*26} {'-'*4}")

    all_pass = True
    results = []

    for s in scenarios:
        authority = parse_authority(s.get("authority_record"))
        action = parse_action(s["action_record"])
        context = parse_context(s["audit_context"])

        result = gate.evaluate(authority, action, context)

        expected = s["expected"]
        got = result.decision
        passed = got == expected

        if not passed:
            all_pass = False

        marker = "PASS" if passed else "FAIL"
        print(f"{s['id']:<4} {s['label']:<14} {expected:<26} {got:<26} {marker}")

        results.append({
            "id": s["id"],
            "label": s["label"],
            "expected": expected,
            "got": got,
            "passed": passed,
            "notes": result.notes,
        })

    pass_count = sum(1 for r in results if r["passed"])
    print(f"\nResult: {pass_count}/{len(results)} passed")
    if not all_pass:
        for r in results:
            if not r["passed"]:
                print(f"  FAIL id={r['id']} ({r['label']}): expected {r['expected']}, got {r['got']}")
                print(f"       notes: {r['notes']}")

    return results


def comparison_table(all_results: dict):
    gates = list(all_results.keys())
    scenario_ids = [r["id"] for r in all_results[gates[0]]]
    labels = {r["id"]: r["label"] for r in all_results[gates[0]]}

    print(f"\n{'='*72}")
    print("Comparison table")
    print(f"{'='*72}")

    gate_short = {
        "DecisionOnlyGate": "Decision",
        "MutablePointerAuditGate": "MutPtr",
        "SeparateWriteGate": "SepWrite",
        "PairedAuthorityActionGate": "Paired",
    }

    header = f"{'ID':<4} {'Label':<14} {'Expected':<26}"
    for g in gates:
        header += f" {gate_short.get(g, g):<10}"
    print(header)
    print("-" * (4 + 14 + 26 + len(gates) * 11))

    for sid in scenario_ids:
        label = labels[sid]
        expected = all_results[gates[0]][[r for r in all_results[gates[0]] if r["id"] == sid][0]["id"] - 1]["expected"]
        row = f"{sid:<4} {label:<14} {expected:<26}"
        for g in gates:
            r = next(r for r in all_results[g] if r["id"] == sid)
            marker = "PASS" if r["passed"] else "FAIL"
            row += f" {marker:<10}"
        print(row)

    print()
    for g in gates:
        results = all_results[g]
        passes = sum(1 for r in results if r["passed"])
        print(f"  {gate_short.get(g, g):<12} {passes}/{len(results)}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "closing"
    data = load_scenarios()
    scenarios = data["scenarios"]

    closing = PairedAuthorityActionGate()
    baseline1 = DecisionOnlyGate()
    baseline2 = MutablePointerAuditGate()
    baseline3 = SeparateWriteGate()

    if mode == "closing":
        run_gate(closing, "PairedAuthorityActionGate", scenarios)

    elif mode == "baselines":
        run_gate(baseline1, "DecisionOnlyGate", scenarios)
        run_gate(baseline2, "MutablePointerAuditGate", scenarios)
        run_gate(baseline3, "SeparateWriteGate", scenarios)

    elif mode == "full":
        all_results = {}
        for gate, label in [
            (closing,   "PairedAuthorityActionGate"),
            (baseline1, "DecisionOnlyGate"),
            (baseline2, "MutablePointerAuditGate"),
            (baseline3, "SeparateWriteGate"),
        ]:
            all_results[label] = run_gate(gate, label, scenarios)
        comparison_table(all_results)

    else:
        print(f"Unknown mode: {mode}. Use 'closing', 'baselines', or 'full'.")
        sys.exit(1)
