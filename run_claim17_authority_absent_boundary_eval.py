#!/usr/bin/env python3
"""Run CLAIM-17 authority-absent sensitive-memory boundary diagnostics."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict
from typing import Any

from run_memory_store_eval import (
    MemoryStoreDecision,
    ROOT,
    governance_adjusted_score_components,
    normalize_memory_store,
    resource_scope_governance_scores,
    resource_sensitivity_weight,
    scope_matches_query,
    score_row,
    summarize,
)


SCENARIOS_PATH = ROOT / "external_scenarios" / "claim17_authority_absent_boundary_v0_1.json"
DEFAULT_RESULTS_JSON = ROOT / "results" / "claim17_authority_absent_boundary_v0_1_results.json"
DEFAULT_RESULTS_MD = ROOT / "results" / "claim17_authority_absent_boundary_v0_1_results.md"

STRATEGIES = [
    "bm25_metadata_text",
    "scope_precedence_role_filter_bm25_metadata_text",
    "governance_adjusted_bm25_metadata_text",
    "resource_sensitivity_only_bm25_metadata_text",
    "resource_scope_governance_bm25_metadata_text",
]


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, int]:
    return summarize(
        [
            MemoryStoreDecision(
                **{
                    key: value
                    for key, value in row.items()
                    if key in MemoryStoreDecision.__dataclass_fields__
                }
            )
            for row in rows
        ]
    )


def score_components(payload: dict[str, Any]) -> list[dict[str, Any]]:
    output = []
    for scenario in payload["scenarios"]:
        memories = normalize_memory_store(scenario)
        governance_components = governance_adjusted_score_components(scenario["query"], memories)
        resource_scores = resource_scope_governance_scores(scenario["query"], memories)
        for memory in memories:
            resource_bonus = (
                resource_sensitivity_weight(memory)
                if memory.get("resource_sensitivity") and scope_matches_query(memory, scenario["query"])
                else 0.0
            )
            output.append(
                {
                    "scenario_id": scenario["id"],
                    "memory_id": memory["id"],
                    "role": memory.get("role", ""),
                    "resource_sensitivity": memory.get("resource_sensitivity", "ordinary_fact"),
                    "has_governs": isinstance(memory.get("governs"), dict),
                    "scope_matches_query": scope_matches_query(memory, scenario["query"]),
                    "resource_bonus": round(resource_bonus, 6),
                    "governance_adjusted": governance_components[memory["id"]],
                    "resource_scope_total": round(resource_scores[memory["id"]], 6),
                }
            )
    return output


def evaluate() -> dict[str, Any]:
    payload = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))
    output_rows = []
    for scenario in payload["scenarios"]:
        for strategy in STRATEGIES:
            output_rows.append(asdict(score_row(strategy, scenario)))

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in output_rows:
        grouped[row["strategy"]].append(row)

    return {
        "status": "CLAIM-17 authority-absent boundary diagnostic. Internal, not benchmark-grade.",
        "scenario_file": str(SCENARIOS_PATH.relative_to(ROOT)),
        "strategies": STRATEGIES,
        "summary": {strategy: summarize_rows(rows) for strategy, rows in grouped.items()},
        "score_components": score_components(payload),
        "rows": output_rows,
    }


def render_markdown(output: dict[str, Any]) -> str:
    lines = [
        "# CLAIM-17 Authority-Absent Boundary Results",
        "",
        output["status"],
        "",
        "## Strategy Summary",
        "",
        "| Strategy | Target selected | Action correct | Trap failures | FC errors | Downgrade misses | Overblocking | Dangerous overcaution |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for strategy in STRATEGIES:
        summary = output["summary"][strategy]
        total = summary["total"]
        lines.append(
            f"| {strategy} | {summary['target_selected']}/{total} | "
            f"{summary['action_correct']}/{total} | "
            f"{summary['trap_failures']} | "
            f"{summary['false_certainty_errors']} | "
            f"{summary['downgrade_misses']} | "
            f"{summary['overblocking_errors']} | "
            f"{summary['dangerous_overcaution']} |"
        )

    lines.extend(
        [
            "",
            "## Score Components",
            "",
            "| Scenario | Role | Sensitivity | Governs | Scope match | Resource bonus | Governance total | Resource-scope total | Authority | Relevance |",
            "|---|---|---|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for item in output["score_components"]:
        components = item["governance_adjusted"]
        lines.append(
            f"| {item['scenario_id']} | {item['role']} | {item['resource_sensitivity']} | "
            f"{'yes' if item['has_governs'] else 'no'} | "
            f"{'yes' if item['scope_matches_query'] else 'no'} | "
            f"{item['resource_bonus']} | {components['total']} | {item['resource_scope_total']} | "
            f"{components['authority']} | {components['relevance']} |"
        )

    lines.extend(
        [
            "",
            "## Scenario Rows",
            "",
            "| Strategy | Scenario | Expected | Selected | Role | Trap | Action | Act ok | Trap fail | OB |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in output["rows"]:
        lines.append(
            f"| {row['strategy']} | {row['scenario_id']} | {row['expected_action']} | "
            f"{row['selected_memory_id']} | {row['selected_role']} | {row['selected_trap']} | "
            f"{row['action']} | {'ok' if row['action_correct'] else 'miss'} | "
            f"{'yes' if row['trap_failure'] else 'no'} | "
            f"{'yes' if row['overblocking_error'] else 'no'} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    output = evaluate()
    DEFAULT_RESULTS_JSON.write_text(json.dumps(output, indent=2), encoding="utf-8")
    DEFAULT_RESULTS_MD.write_text(render_markdown(output), encoding="utf-8")
    print(json.dumps(output["summary"], indent=2))
    print(f"Wrote {DEFAULT_RESULTS_MD}")
    print(f"Wrote {DEFAULT_RESULTS_JSON}")


if __name__ == "__main__":
    main()
