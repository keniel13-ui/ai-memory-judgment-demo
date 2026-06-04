#!/usr/bin/env python3
"""Decompose governance-adjusted scores for selected CLAIM-15 stress cases."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from run_memory_store_eval import (
    ROOT,
    governance_adjusted_score_components,
    normalize_memory_store,
)


DEFAULT_SCENARIOS = ROOT / "external_scenarios" / "claim15_governance_stress_v0_1.json"
DEFAULT_RESULTS_JSON = ROOT / "results" / "claim15_score_decomposition.json"
DEFAULT_RESULTS_MD = ROOT / "results" / "claim15_score_decomposition.md"
DEFAULT_SCENARIO_IDS = [
    "claim15_missing_target_governs_v0_1",
    "claim15_target_governs_mismatch_v0_1",
]


def load_scenarios(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))["scenarios"]


def decompose(scenarios: list[dict[str, Any]], scenario_ids: list[str]) -> dict[str, Any]:
    output = {
        "status": "CLAIM-15 governance-adjusted score decomposition for targeted stress failures.",
        "scenarios": [],
    }
    selected_ids = set(scenario_ids)
    for scenario in scenarios:
        if scenario["id"] not in selected_ids:
            continue

        memories = normalize_memory_store(scenario)
        components = governance_adjusted_score_components(scenario["query"], memories)
        ranked = sorted(
            memories,
            key=lambda memory: components[memory["id"]]["total"],
            reverse=True,
        )
        expected_role = scenario.get("expected_fired_role", "target")
        target = next((memory for memory in ranked if memory.get("role") == expected_role), None)
        winner = ranked[0]
        row = {
            "scenario_id": scenario["id"],
            "query": scenario["query"],
            "expected_action": scenario["expected_action"],
            "winner_id": winner["id"],
            "winner_role": winner.get("role", ""),
            "winner_components": components[winner["id"]],
            "target_id": target["id"] if target else "",
            "target_role": target.get("role", "") if target else "",
            "target_components": components[target["id"]] if target else {},
            "ranked": [
                {
                    "memory_id": memory["id"],
                    "role": memory.get("role", ""),
                    "trap": memory.get("distractor_trap", ""),
                    "components": components[memory["id"]],
                }
                for memory in ranked
            ],
        }
        if target:
            row["winner_minus_target"] = {
                key: round(
                    components[winner["id"]][key] - components[target["id"]][key],
                    6,
                )
                for key in components[winner["id"]]
            }
        output["scenarios"].append(row)
    return output


def render_markdown(output: dict[str, Any]) -> str:
    lines = [
        "# CLAIM-15 Score Decomposition",
        "",
        output["status"],
        "",
    ]
    component_names = [
        "relevance",
        "authority",
        "scope",
        "specificity",
        "action_type",
        "status",
        "conflict_penalty",
        "total",
    ]
    for scenario in output["scenarios"]:
        lines.extend(
            [
                f"## {scenario['scenario_id']}",
                "",
                f"Expected action: `{scenario['expected_action']}`",
                "",
                f"Winner: `{scenario['winner_id']}` ({scenario['winner_role']})",
                "",
                f"Target: `{scenario['target_id']}` ({scenario['target_role']})",
                "",
                "### Winner Minus Target",
                "",
                "| Component | Delta |",
                "|---|---:|",
            ]
        )
        for component in component_names:
            lines.append(f"| {component} | {scenario['winner_minus_target'].get(component, 0.0)} |")

        lines.extend(
            [
                "",
                "### Ranked Components",
                "",
                "| Rank | Memory | Role | Trap | Relevance | Authority | Scope | Specificity | Action type | Status | Conflict penalty | Total |",
                "|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for rank, memory in enumerate(scenario["ranked"], start=1):
            components = memory["components"]
            lines.append(
                f"| {rank} | {memory['memory_id']} | {memory['role']} | {memory['trap']} | "
                f"{components['relevance']} | {components['authority']} | {components['scope']} | "
                f"{components['specificity']} | {components['action_type']} | {components['status']} | "
                f"{components['conflict_penalty']} | {components['total']} |"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Decompose CLAIM-15 governance-adjusted scores.")
    parser.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS)
    parser.add_argument("--scenario-id", action="append", dest="scenario_ids")
    parser.add_argument("--results-json", type=Path, default=DEFAULT_RESULTS_JSON)
    parser.add_argument("--results-md", type=Path, default=DEFAULT_RESULTS_MD)
    args = parser.parse_args()

    scenarios_path = args.scenarios if args.scenarios.is_absolute() else ROOT / args.scenarios
    results_json = args.results_json if args.results_json.is_absolute() else ROOT / args.results_json
    results_md = args.results_md if args.results_md.is_absolute() else ROOT / args.results_md
    scenario_ids = args.scenario_ids or DEFAULT_SCENARIO_IDS

    output = decompose(load_scenarios(scenarios_path), scenario_ids)
    results_json.parent.mkdir(parents=True, exist_ok=True)
    results_md.parent.mkdir(parents=True, exist_ok=True)
    results_json.write_text(json.dumps(output, indent=2), encoding="utf-8")
    results_md.write_text(render_markdown(output), encoding="utf-8")
    print(json.dumps(output, indent=2))
    print(f"Wrote {results_md}")
    print(f"Wrote {results_json}")


if __name__ == "__main__":
    main()
