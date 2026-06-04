#!/usr/bin/env python3
"""Inspect query action-type heuristics on scenario packets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from run_memory_store_eval import ROOT, query_action_types, tokenize


DEFAULT_SCENARIOS = [
    ROOT / "external_scenarios" / "fresh_governs_clutter_v0_1_source.json",
    ROOT / "external_scenarios" / "claim15_governance_stress_v0_1.json",
]
DEFAULT_RESULTS_JSON = ROOT / "results" / "action_type_diagnostic_results.json"
DEFAULT_RESULTS_MD = ROOT / "results" / "action_type_diagnostic_results.md"

READ_ONLY_EXPECTED_ACTIONS = {"answer", "answer_context"}
RISKY_EXPECTED_ACTIONS = {"warn", "verify_first", "block"}


def load_scenarios(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))["scenarios"]


def expected_semantic_bucket(scenario: dict[str, Any]) -> str:
    if scenario["expected_action"] in READ_ONLY_EXPECTED_ACTIONS:
        return "read"
    if scenario["expected_action"] in RISKY_EXPECTED_ACTIONS:
        return "non_read_or_guarded"
    return "other"


def issue_label(scenario: dict[str, Any], inferred: set[str]) -> str:
    expected_bucket = expected_semantic_bucket(scenario)
    if expected_bucket == "read" and inferred != {"read"}:
        return "read_query_not_classified_read_only"
    if expected_bucket == "non_read_or_guarded" and inferred == {"read"}:
        return "guarded_query_classified_read_only"
    return ""


def evaluate(paths: list[Path]) -> dict[str, Any]:
    rows = []
    for path in paths:
        for scenario in load_scenarios(path):
            inferred = query_action_types(scenario["query"])
            rows.append(
                {
                    "packet": str(path.relative_to(ROOT)),
                    "scenario_id": scenario["id"],
                    "query": scenario["query"],
                    "tokens": tokenize(scenario["query"]),
                    "expected_action": scenario["expected_action"],
                    "expected_semantic_bucket": expected_semantic_bucket(scenario),
                    "inferred_action_types": sorted(inferred),
                    "issue": issue_label(scenario, inferred),
                }
            )
    return {
        "status": "Diagnostic for deterministic query_action_types heuristic. Internal only.",
        "rows": rows,
        "issue_count": sum(1 for row in rows if row["issue"]),
    }


def render_markdown(output: dict[str, Any]) -> str:
    lines = [
        "# Action-Type Diagnostic Results",
        "",
        output["status"],
        "",
        f"Issue count: `{output['issue_count']}`",
        "",
        "| Packet | Scenario | Expected action | Expected bucket | Inferred action types | Issue | Query |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in output["rows"]:
        lines.append(
            f"| {row['packet']} | {row['scenario_id']} | {row['expected_action']} | "
            f"{row['expected_semantic_bucket']} | {', '.join(row['inferred_action_types'])} | "
            f"{row['issue']} | {row['query']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect query action type inference.")
    parser.add_argument("--scenarios", action="append", type=Path)
    parser.add_argument("--results-json", type=Path, default=DEFAULT_RESULTS_JSON)
    parser.add_argument("--results-md", type=Path, default=DEFAULT_RESULTS_MD)
    args = parser.parse_args()

    paths = args.scenarios or DEFAULT_SCENARIOS
    normalized_paths = [path if path.is_absolute() else ROOT / path for path in paths]
    results_json = args.results_json if args.results_json.is_absolute() else ROOT / args.results_json
    results_md = args.results_md if args.results_md.is_absolute() else ROOT / args.results_md

    output = evaluate(normalized_paths)
    results_json.parent.mkdir(parents=True, exist_ok=True)
    results_md.parent.mkdir(parents=True, exist_ok=True)
    results_json.write_text(json.dumps(output, indent=2), encoding="utf-8")
    results_md.write_text(render_markdown(output), encoding="utf-8")
    print(json.dumps(output, indent=2))
    print(f"Wrote {results_md}")
    print(f"Wrote {results_json}")


if __name__ == "__main__":
    main()
