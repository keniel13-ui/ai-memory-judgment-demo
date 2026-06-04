#!/usr/bin/env python3
"""Run CLAIM-17 resource-sensitivity diagnostics."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any

from run_memory_store_eval import (
    MemoryStoreDecision,
    ROOT,
    normalize_memory_store,
    resource_sensitivity,
    scope_matches_query,
    score_row,
    summarize,
    tokenize,
)


SCENARIOS_PATH = ROOT / "external_scenarios" / "claim17_resource_sensitivity_v0_1.json"
DEFAULT_RESULTS_JSON = ROOT / "results" / "claim17_resource_sensitivity_v0_1_results.json"
DEFAULT_RESULTS_MD = ROOT / "results" / "claim17_resource_sensitivity_v0_1_results.md"

STRATEGIES = [
    "bm25_metadata_text",
    "scope_precedence_role_filter_bm25_metadata_text",
    "governance_adjusted_bm25_metadata_text",
    "directional_action_governance_bm25_metadata_text",
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


def scope_overlap_audit(payload: dict[str, Any]) -> list[dict[str, Any]]:
    audits = []
    for scenario in payload["scenarios"]:
        query_tokens = set(tokenize(scenario["query"]))
        for memory in normalize_memory_store(scenario):
            governs = memory.get("governs")
            if not isinstance(governs, dict):
                continue
            any_terms = {str(term).lower() for term in governs.get("any_terms", [])}
            all_terms = {str(term).lower() for term in governs.get("all_terms", [])}
            audits.append(
                {
                    "scenario_id": scenario["id"],
                    "memory_id": memory["id"],
                    "role": memory.get("role", ""),
                    "resource_sensitivity": resource_sensitivity(memory),
                    "query_tokens": sorted(query_tokens),
                    "governs_any_terms": sorted(any_terms),
                    "governs_all_terms": sorted(all_terms),
                    "token_overlap": sorted(query_tokens & (any_terms | all_terms)),
                    "scope_matches_query": scope_matches_query(memory, scenario["query"]),
                }
            )
    return audits


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
        "status": "CLAIM-17 resource-sensitivity diagnostic. Internal, pre-registered, not benchmark-grade.",
        "scenario_file": str(SCENARIOS_PATH.relative_to(ROOT)),
        "strategies": STRATEGIES,
        "summary": {strategy: summarize_rows(rows) for strategy, rows in grouped.items()},
        "scope_overlap_audit": scope_overlap_audit(payload),
        "rows": output_rows,
    }


def render_markdown(output: dict[str, Any]) -> str:
    lines = [
        "# CLAIM-17 Resource Sensitivity Results",
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
            "## Scope Overlap Audit",
            "",
            "| Scenario | Role | Sensitivity | Scope match | Overlap | Any terms |",
            "|---|---|---|---|---|---|",
        ]
    )
    for audit in output["scope_overlap_audit"]:
        lines.append(
            f"| {audit['scenario_id']} | {audit['role']} | {audit['resource_sensitivity']} | "
            f"{'yes' if audit['scope_matches_query'] else 'no'} | "
            f"{', '.join(audit['token_overlap']) or '-'} | "
            f"{', '.join(audit['governs_any_terms']) or '-'} |"
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
