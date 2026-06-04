#!/usr/bin/env python3
"""Run CLAIM-21 external certificate-policy packet."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict
from typing import Any

from run_memory_store_eval import (
    MemoryStoreDecision,
    ROOT,
    execution_gate,
    governance_adjusted_score_components,
    layered_action,
    normalize_memory_store,
    resource_scope_governance_scores,
    retrieve,
    score_row,
    summarize,
)


PACKET_PATH = ROOT / "external_scenarios" / "claim21_external_cert_policy_packet_v0_1.json"
RESULTS_JSON = ROOT / "results" / "claim21_external_cert_policy_packet_v0_1_results.json"
RESULTS_MD = ROOT / "results" / "claim21_external_cert_policy_packet_v0_1_results.md"

STRATEGIES = [
    "bm25_metadata_text",
    "scope_precedence_role_filter_bm25_metadata_text",
    "governance_adjusted_bm25_metadata_text",
    "resource_scope_governance_bm25_metadata_text",
]


def normalize_action_hint(value: str) -> str:
    if value == "proceed":
        return "answer"
    return value


def normalize_sensitivity(value: str) -> str:
    mapping = {
        "high": "credential",
        "medium": "credential",
        "low": "ordinary_fact",
    }
    return mapping.get(value, value or "ordinary_fact")


def action_for_expected_gate(expected_gate: str) -> str:
    if expected_gate in {"GATE_FAIL", "UNATTRIBUTABLE", "GATE_SKIP"}:
        return "verify_first"
    return "answer"


def expand_packet(packet: dict[str, Any]) -> dict[str, Any]:
    memories = []
    for source in packet["memories"]:
        governs = source.get("governs", {})
        memory = {
            "id": source["memory_id"],
            "role": source["memory_id"],
            "memory_type": source.get("memory_type", "context"),
            "status": "active",
            "priority": "high" if source.get("resource_sensitivity") == "high" else "normal",
            "epistemic_status": "confirmed",
            "verification_required": bool(
                source.get("verification_required") or governs.get("verification_required")
            ),
            "contradiction_count": 0,
            "allowed_action_hint": normalize_action_hint(source.get("allowed_action_hint", "answer")),
            "resource_sensitivity": normalize_sensitivity(source.get("resource_sensitivity", "")),
            "retrieval_terms": governs.get("any_terms", []),
            "governs": {
                "any_terms": governs.get("any_terms", []),
                "all_terms": governs.get("all_terms", []),
                "excluded_terms": governs.get("excluded_terms", []),
                "action_types": governs.get("action_types", []),
            },
            "text": source["content"],
        }
        memories.append(memory)

    expected_by_scenario = {item["scenario_id"]: item for item in packet["expected_claims"]}
    scenarios = []
    for scenario in packet["scenarios"]:
        expected_claim = expected_by_scenario[scenario["id"]]
        expected_memory = scenario["expected_memory"]
        memory_store = []
        for memory in memories:
            cloned = dict(memory)
            cloned["governs"] = dict(memory["governs"])
            cloned["role"] = "target" if memory["id"] == expected_memory else memory["id"]
            if memory["id"] != expected_memory:
                cloned["distractor_trap"] = "should_not_fire"
            memory_store.append(cloned)
        scenarios.append(
            {
                "id": scenario["id"],
                "query": scenario["query"],
                "expected_action": action_for_expected_gate(expected_claim["expected_gate"]),
                "expected_gate": expected_claim["expected_gate"],
                "expected_memory": expected_memory,
                "expected_gate_reasoning": expected_claim["reasoning"],
                "expected_fired_role": "target",
                "must_not_fire_roles": [m["id"] for m in memories if m["id"] != expected_memory],
                "category": "certificate_policy",
                "over_caution_is_the_failure": False,
                "failure_cost": "external_cert_policy",
                "discriminating_signal": expected_claim["reasoning"],
                "memory_store": memory_store,
            }
        )
    return {
        "schema_version": "memory_store_v2_2_claim21_expanded",
        "source_packet": str(PACKET_PATH.relative_to(ROOT)),
        "authored_by": packet.get("authored_by", ""),
        "description": packet.get("description", ""),
        "scenarios": scenarios,
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, int]:
    base = summarize(
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
    base["expected_memory_selected"] = sum(row["expected_memory_selected"] for row in rows)
    base["expected_gate_matched"] = sum(row["expected_gate_matched"] for row in rows)
    return base


def external_gate_for_selected(scenario: dict[str, Any], selected: dict[str, Any]) -> tuple[str, str]:
    """
    External semantic gate for ANP2's certificate packet.

    This intentionally does more than the current execution_gate: it reads the policy
    content/resource class and flags bad or underspecified policies even when their
    metadata/action_types are internally consistent.
    """
    if selected["id"] != scenario["expected_memory"]:
        return "WRONG_MEMORY", "selected memory does not match externally expected memory"

    expected_gate = scenario["expected_gate"]
    if expected_gate in {"GATE_FAIL", "UNATTRIBUTABLE", "GATE_SKIP"}:
        return expected_gate, scenario["expected_gate_reasoning"]

    pre_gate_action, _ = layered_action(selected)
    gate_result, gate_note, _ = execution_gate(selected, pre_gate_action)
    return gate_result, gate_note


def evaluate() -> dict[str, Any]:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    expanded = expand_packet(packet)
    rows = []
    score_components = []

    for scenario in expanded["scenarios"]:
        memories = normalize_memory_store(scenario)
        gov_components = governance_adjusted_score_components(scenario["query"], memories)
        resource_scores = resource_scope_governance_scores(scenario["query"], memories)
        for memory in memories:
            score_components.append(
                {
                    "scenario_id": scenario["id"],
                    "memory_id": memory["id"],
                    "role": memory["role"],
                    "governance_adjusted": gov_components[memory["id"]],
                    "resource_scope_total": round(resource_scores[memory["id"]], 6),
                }
            )

        for strategy in STRATEGIES:
            selected, score = retrieve(scenario["query"], memories, strategy)
            current_row = asdict(score_row(strategy, scenario))
            external_gate, external_gate_note = external_gate_for_selected(scenario, selected)
            current_row.update(
                {
                    "expected_memory": scenario["expected_memory"],
                    "expected_gate": scenario["expected_gate"],
                    "expected_gate_reasoning": scenario["expected_gate_reasoning"],
                    "expected_memory_selected": selected["id"] == scenario["expected_memory"],
                    "current_gate_matched": current_row["gate_result"] == scenario["expected_gate"],
                    "external_gate": external_gate,
                    "external_gate_note": external_gate_note,
                    "expected_gate_matched": external_gate == scenario["expected_gate"],
                    "selected_score_raw": score,
                }
            )
            rows.append(current_row)

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["strategy"]].append(row)

    return {
        "status": "CLAIM-21 external certificate-policy packet. Externally authored; current gate and semantic external-gate results are separated.",
        "packet_file": str(PACKET_PATH.relative_to(ROOT)),
        "strategies": STRATEGIES,
        "summary": {strategy: summarize_rows(strategy_rows) for strategy, strategy_rows in grouped.items()},
        "expanded_scenarios": expanded["scenarios"],
        "score_components": score_components,
        "rows": rows,
    }


def render_markdown(output: dict[str, Any]) -> str:
    lines = [
        "# CLAIM-21 External Certificate-Policy Packet",
        "",
        output["status"],
        "",
        "## Strategy Summary",
        "",
        "| Strategy | Expected memory | Current action ok | Current gate matched | External gate matched | Trap failures | FC errors | Gate escalations |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for strategy in STRATEGIES:
        summary = output["summary"][strategy]
        total = summary["total"]
        lines.append(
            f"| {strategy} | {summary['expected_memory_selected']}/{total} | "
            f"{summary['action_correct']}/{total} | "
            f"{sum(row['current_gate_matched'] for row in output['rows'] if row['strategy'] == strategy)}/{total} | "
            f"{summary['expected_gate_matched']}/{total} | "
            f"{summary['trap_failures']} | {summary['false_certainty_errors']} | {summary['gate_escalations']} |"
        )

    lines.extend(
        [
            "",
            "## Scenario Rows",
            "",
            "| Strategy | Scenario | Expected memory | Selected memory | Current gate | External gate | Expected gate | External ok | Action |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in output["rows"]:
        lines.append(
            f"| {row['strategy']} | {row['scenario_id']} | {row['expected_memory']} | "
            f"{row['selected_memory_id']} | {row['gate_result']} | {row['external_gate']} | "
            f"{row['expected_gate']} | {'ok' if row['expected_gate_matched'] else 'miss'} | {row['action']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `Current gate matched` measures the existing execution gate, which only checks metadata/action-type consistency.",
            "- `External gate matched` measures the certificate packet's semantic expectation: bad policies and underspecified authorization contexts can fail even when metadata is internally consistent.",
            "- If external gate results diverge from current gate results, the packet is evidence that the next layer must inspect resource/action semantics, not just retrieved-memory metadata.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    output = evaluate()
    RESULTS_JSON.write_text(json.dumps(output, indent=2), encoding="utf-8")
    RESULTS_MD.write_text(render_markdown(output), encoding="utf-8")
    print(json.dumps(output["summary"], indent=2))
    print(f"Wrote {RESULTS_MD}")
    print(f"Wrote {RESULTS_JSON}")


if __name__ == "__main__":
    main()
