"""
CLAIM-28 evaluator.

Runs frozen scenarios against:
  - AuthorityOnlyGate
  - KeywordRiskGate
  - BehavioralNormGate

Usage:
  python3 evaluator.py
  python3 evaluator.py --json
"""

import argparse
import json
from pathlib import Path

from authority_only_gate import AuthorityOnlyGate
from behavioral_norm_gate import BehavioralNormGate
from gate_interface import parse_role_profile, parse_scenario
from keyword_risk_gate import KeywordRiskGate


ROOT = Path(__file__).parent
ROLE_PROFILE_PATH = ROOT / "role_profile.json"
SCENARIOS_PATH = ROOT / "scenarios.json"
RESULTS_JSON_PATH = ROOT / "results.json"
RESULTS_MD_PATH = ROOT / "results.md"


def load_role_profile():
    with open(ROLE_PROFILE_PATH) as f:
        return parse_role_profile(json.load(f))


def load_scenarios():
    with open(SCENARIOS_PATH) as f:
        raw = json.load(f)

    lock = raw.get("scenario_lock", {})
    if not lock.get("locked_before_gate_implementation"):
        raise RuntimeError("Scenario packet is not marked locked before gate implementation.")

    return [parse_scenario(s) for s in raw["scenarios"]]


def run_gate(gate, scenarios, role_profile):
    rows = []
    for scenario in scenarios:
        result = gate.evaluate(scenario, role_profile)
        expected = scenario.expected[gate.label]
        passed = result.decision == expected
        rows.append({
            "scenario_id": scenario.scenario_id,
            "label": scenario.label,
            "class": scenario.scenario_class,
            "gate": gate.label,
            "expected": expected,
            "decision": result.decision,
            "passed": passed,
            "memory_id": scenario.memory.memory_id,
            "principal": scenario.memory.principal,
            "action_tuple": {
                "action_type": scenario.action_tuple.action_type,
                "target_resource": scenario.action_tuple.target_resource,
                "recipient": scenario.action_tuple.recipient,
            },
            "prior_gate_failures": scenario.prior_gate_status.failed_fields(),
            "violated_norm_fields": result.violated_norm_fields,
            "exception_grant_id": result.exception_grant_id,
            "notes": result.notes,
        })
    return rows


def summarize(rows):
    summary = {}
    for row in rows:
        gate = row["gate"]
        summary.setdefault(gate, {"passed": 0, "total": 0})
        summary[gate]["total"] += 1
        if row["passed"]:
            summary[gate]["passed"] += 1
    return summary


def print_table(rows):
    print("=" * 92)
    print("CLAIM-28 Behavioral Norm Evaluation")
    print("=" * 92)
    print(f"{'Gate':<23} {'ID':<3} {'Label':<30} {'Expected':<38} {'Got':<38} {'Pass'}")
    print(f"{'-'*23} {'-'*3} {'-'*30} {'-'*38} {'-'*38} {'-'*4}")
    for row in rows:
        marker = "PASS" if row["passed"] else "FAIL"
        print(
            f"{row['gate']:<23} {row['scenario_id']:<3} {row['label']:<30} "
            f"{row['expected']:<38} {row['decision']:<38} {marker}"
        )

    print()
    for gate, data in summarize(rows).items():
        print(f"{gate}: {data['passed']}/{data['total']} expected decisions matched")

    failures = [row for row in rows if not row["passed"]]
    if failures:
        print("\nFailures:")
        for row in failures:
            print(
                f"- {row['gate']} scenario {row['scenario_id']} ({row['label']}): "
                f"expected {row['expected']}, got {row['decision']} — {row['notes']}"
            )


def write_results(rows, summary):
    payload = {
        "claim": "CLAIM-28",
        "role_profile": ROLE_PROFILE_PATH.name,
        "scenarios": SCENARIOS_PATH.name,
        "summary": summary,
        "rows": rows,
    }
    RESULTS_JSON_PATH.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# CLAIM-28 Results",
        "",
        "Status: internal V0 packet. Not external or benchmark-grade.",
        "",
        "## Summary",
        "",
        "| Gate | Expected decisions matched |",
        "|---|---:|",
    ]
    for gate, data in summary.items():
        lines.append(f"| {gate} | {data['passed']}/{data['total']} |")

    lines.extend([
        "",
        "## Row Results",
        "",
        "| Gate | Scenario | Class | Expected | Got | Pass | Notes |",
        "|---|---|---|---|---|---:|---|",
    ])
    for row in rows:
        marker = "yes" if row["passed"] else "no"
        notes = row["notes"].replace("|", "/")
        lines.append(
            f"| {row['gate']} | {row['label']} | {row['class']} | "
            f"{row['expected']} | {row['decision']} | {marker} | {notes} |"
        )

    RESULTS_MD_PATH.write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Print JSON payload after running.")
    args = parser.parse_args()

    role_profile = load_role_profile()
    scenarios = load_scenarios()
    gates = [
        AuthorityOnlyGate(),
        KeywordRiskGate(),
        BehavioralNormGate(),
    ]

    rows = []
    for gate in gates:
        rows.extend(run_gate(gate, scenarios, role_profile))

    summary = summarize(rows)
    write_results(rows, summary)
    print_table(rows)

    if args.json:
        print(json.dumps({
            "summary": summary,
            "rows": rows,
        }, indent=2))


if __name__ == "__main__":
    main()
