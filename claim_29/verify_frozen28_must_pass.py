"""
CLAIM-29 frozen CLAIM-28 verification.

This script imports the CLAIM-28 BehavioralNormGate unchanged and runs it against
the CLAIM-29 role profile plus the frozen scenario packets. It is intentionally
adapter-shaped: scenario rows stay in the CLAIM-29 packet format, while this script
normalizes only the input fields needed by the frozen CLAIM-28 parser.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CLAIM_28_DIR = ROOT / "claim_28"
CLAIM_29_DIR = ROOT / "claim_29"

sys.path.insert(0, str(CLAIM_28_DIR))

from behavioral_norm_gate import BehavioralNormGate  # noqa: E402
from gate_interface import (  # noqa: E402
    ALLOW,
    CHALLENGE_ANOMALOUS_AUTHORIZED_MEMORY,
    REFUSE_EXISTING_GATE,
    parse_role_profile,
    parse_scenario,
)


EXPECTED_FROZEN28 = {
    1: ALLOW,
    2: ALLOW,
    3: REFUSE_EXISTING_GATE,
    4: CHALLENGE_ANOMALOUS_AUTHORIZED_MEMORY,
    5: ALLOW,
    6: ALLOW,
    7: ALLOW,
    8: ALLOW,
    9: ALLOW,
    10: ALLOW,
    11: ALLOW,
    12: ALLOW,
}

MUST_PASS_ROWS = {5, 6, 7, 8, 9}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_exception_grant(raw: dict[str, Any]) -> dict[str, Any]:
    grant = raw.get("exception_grant")
    if not grant or "exception_id" in grant:
        return raw

    scope = grant["scope"]
    normalized = {
        **raw,
        "exception_grant": {
            "exception_id": grant["grant_id"],
            "granted_by": grant["issuer"],
            "allowed_action_type": scope["action_type"],
            "allowed_target_resource": scope["target_resource"],
            "allowed_recipient": scope["recipient"],
            "verification_rule_satisfied": grant.get(
                "verification_rule_satisfied", ""
            ),
        },
    }
    return normalized


def parse_claim29_scenario(raw: dict[str, Any]):
    normalized = normalize_exception_grant(raw)
    return parse_scenario({**normalized, "expected": {}})


def load_scenarios() -> list[dict[str, Any]]:
    control_rows = load_json(CLAIM_29_DIR / "scenarios_control_rows_1_4_11_12.json")
    fresh_rows = load_json(CLAIM_29_DIR / "scenarios_fresh_rows_5_10.json")
    rows = control_rows + fresh_rows
    return sorted(rows, key=lambda row: row["id"])


def main() -> int:
    role_profile = parse_role_profile(load_json(CLAIM_29_DIR / "role_profile.json"))
    gate = BehavioralNormGate()
    failures: list[str] = []
    report: list[dict[str, Any]] = []

    for raw in load_scenarios():
        scenario = parse_claim29_scenario(raw)
        result = gate.evaluate(scenario, role_profile)
        expected = EXPECTED_FROZEN28[scenario.scenario_id]
        passed = result.decision == expected

        if not passed:
            failures.append(
                f"row {scenario.scenario_id}: expected {expected}, got {result.decision}"
            )

        report.append(
            {
                "id": scenario.scenario_id,
                "label": scenario.label,
                "class": scenario.scenario_class,
                "frozen28_decision": result.decision,
                "expected": expected,
                "passed": passed,
                "must_pass_escape_row": scenario.scenario_id in MUST_PASS_ROWS,
                "notes": result.notes,
                "violated_norm_fields": result.violated_norm_fields,
                "exception_grant_id": result.exception_grant_id,
            }
        )

    print(json.dumps(report, indent=2, sort_keys=True))

    must_pass_failures = [
        entry
        for entry in report
        if entry["must_pass_escape_row"] and entry["frozen28_decision"] != ALLOW
    ]
    if must_pass_failures:
        failures.append("one or more rows 5-9 failed the frozen CLAIM-28 must-pass")

    if failures:
        print("\nFROZEN28 VERIFICATION FAILED", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("\nFROZEN28 VERIFICATION PASSED", file=sys.stderr)
    print("Rows 5-9 all pass the frozen CLAIM-28 gate.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
