#!/usr/bin/env python3
"""Run CLAIM-23 tool-call authorization gate evaluation."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_memory_store_eval import (
    ROOT,
    execution_gate,
    layered_action,
    normalize_memory_store,
    retrieve,
)
from run_split_architecture_eval import operation_context_gate


PACKET_PATH = ROOT / "external_scenarios" / "claim23_tool_call_authorization_v0_1.json"
RESULTS_JSON = ROOT / "results" / "claim23_tool_call_authorization_v0_1_results.json"
RESULTS_MD = ROOT / "results" / "claim23_tool_call_authorization_v0_1_results.md"

STRATEGY = "bm25_metadata_text"
RISKY_ACTIONS = {"warn", "verify_first", "block"}
PERMISSIVE_ACTIONS = {"answer", "answer_context"}


@dataclass
class GrantMatch:
    gate_result: str
    final_action: str
    grant_id: str
    reason: str


@dataclass
class Claim23Row:
    scenario_id: str
    query: str
    expected_action: str
    selected_memory_id: str
    selected_role: str
    target_selected: bool
    pre_gate_action: str
    self_description_action: str
    self_description_correct: bool
    query_context_action: str
    query_context_correct: bool
    tool_call_action: str
    tool_call_correct: bool
    tool_call_gate_result: str
    matching_grant_id: str
    grant_reason: str
    sd_false_certainty: bool
    qc_false_certainty: bool
    tc_false_certainty: bool
    parameter_bound_refusal: bool


def parse_time(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def exact_grant_matches(tool_call: dict[str, Any], grant: dict[str, Any]) -> bool:
    fields = ["agent_id", "action_type", "target_resource", "recipient", "scope"]
    return all(str(tool_call.get(field, "")) == str(grant.get(field, "")) for field in fields)


def tool_call_grant_gate(scenario: dict[str, Any], pre_gate_action: str) -> GrantMatch:
    tool_call = scenario["tool_call"]
    now = parse_time(scenario["now"])

    expired_exact: list[str] = []
    partial_reasons: list[str] = []

    for grant in scenario.get("external_grants", []):
        if exact_grant_matches(tool_call, grant):
            expires_at = parse_time(grant["expires_at"])
            if expires_at < now:
                expired_exact.append(grant["grant_id"])
                continue
            decision = grant.get("decision", "verify_first")
            if decision == "allow":
                return GrantMatch("GATE_PASS", pre_gate_action, grant["grant_id"], "exact active allow grant")
            if decision == "block":
                return GrantMatch("GATE_FAIL", "block", grant["grant_id"], "exact active block grant")
            return GrantMatch("GATE_FAIL", "verify_first", grant["grant_id"], "exact active grant requires verification")

        same_agent_action_resource = all(
            str(tool_call.get(field, "")) == str(grant.get(field, ""))
            for field in ["agent_id", "action_type", "target_resource"]
        )
        if same_agent_action_resource:
            mismatches = [
                field
                for field in ["recipient", "scope"]
                if str(tool_call.get(field, "")) != str(grant.get(field, ""))
            ]
            if mismatches:
                partial_reasons.append(f"{grant['grant_id']} mismatch on {','.join(mismatches)}")

    if expired_exact:
        return GrantMatch(
            "GATE_FAIL",
            "verify_first",
            "",
            f"exact grant expired: {','.join(expired_exact)}",
        )
    if partial_reasons:
        return GrantMatch(
            "GATE_FAIL",
            "verify_first",
            "",
            "; ".join(partial_reasons),
        )
    return GrantMatch("GATE_FAIL", "verify_first", "", "no exact active external grant")


def is_false_certainty(expected: str, action: str) -> bool:
    return expected in RISKY_ACTIONS and action in PERMISSIVE_ACTIONS


def evaluate_scenario(scenario: dict[str, Any]) -> Claim23Row:
    memories = normalize_memory_store(scenario)
    selected, _ = retrieve(scenario["query"], memories, STRATEGY)
    pre_gate_action, _ = layered_action(selected)

    _, _, sd_action = execution_gate(selected, pre_gate_action)
    _, _, qc_action, _ = operation_context_gate(scenario["query"], selected, pre_gate_action)
    tc = tool_call_grant_gate(scenario, pre_gate_action)

    expected = scenario["expected_action"]
    parameter_bound_refusal = (
        tc.final_action in RISKY_ACTIONS
        and tc.grant_id == ""
        and tc.reason != "no exact active external grant"
    )

    return Claim23Row(
        scenario_id=scenario["id"],
        query=scenario["query"],
        expected_action=expected,
        selected_memory_id=selected["id"],
        selected_role=selected.get("role", ""),
        target_selected=selected.get("role") == scenario.get("expected_fired_role", "target"),
        pre_gate_action=pre_gate_action,
        self_description_action=sd_action,
        self_description_correct=sd_action == expected,
        query_context_action=qc_action,
        query_context_correct=qc_action == expected,
        tool_call_action=tc.final_action,
        tool_call_correct=tc.final_action == expected,
        tool_call_gate_result=tc.gate_result,
        matching_grant_id=tc.grant_id,
        grant_reason=tc.reason,
        sd_false_certainty=is_false_certainty(expected, sd_action),
        qc_false_certainty=is_false_certainty(expected, qc_action),
        tc_false_certainty=is_false_certainty(expected, tc.final_action),
        parameter_bound_refusal=parameter_bound_refusal,
    )


def summarize(rows: list[Claim23Row]) -> dict[str, int]:
    total = len(rows)
    return {
        "total": total,
        "self_description_correct": sum(row.self_description_correct for row in rows),
        "query_context_correct": sum(row.query_context_correct for row in rows),
        "tool_call_correct": sum(row.tool_call_correct for row in rows),
        "self_description_false_certainty": sum(row.sd_false_certainty for row in rows),
        "query_context_false_certainty": sum(row.qc_false_certainty for row in rows),
        "tool_call_false_certainty": sum(row.tc_false_certainty for row in rows),
        "parameter_bound_refusals": sum(row.parameter_bound_refusal for row in rows),
        "target_selected": sum(row.target_selected for row in rows),
    }


def render_markdown(rows: list[Claim23Row], summary: dict[str, int]) -> str:
    lines = [
        "# CLAIM-23 Tool-Call Authorization Gate",
        "",
        "Status: internally authored packet. Tests concrete tool-call parameters against an external grant table.",
        "",
        "## Summary",
        "",
        "| Gate | Action correct | False-certainty errors |",
        "|---|---:|---:|",
        f"| Self-description gate | {summary['self_description_correct']}/{summary['total']} | {summary['self_description_false_certainty']} |",
        f"| Query-context gate (CLAIM-22) | {summary['query_context_correct']}/{summary['total']} | {summary['query_context_false_certainty']} |",
        f"| Tool-call grant gate | {summary['tool_call_correct']}/{summary['total']} | {summary['tool_call_false_certainty']} |",
        "",
        f"Parameter-bound refusals: {summary['parameter_bound_refusals']}",
        "",
        "## Scenario Rows",
        "",
        "| Scenario | Expected | SD action | Query action | Tool-call action | Grant | Tool-call reason |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row.scenario_id} | {row.expected_action} | "
            f"{row.self_description_action} {'ok' if row.self_description_correct else 'miss'} | "
            f"{row.query_context_action} {'ok' if row.query_context_correct else 'miss'} | "
            f"{row.tool_call_action} {'ok' if row.tool_call_correct else 'miss'} | "
            f"{row.matching_grant_id or '—'} | {row.grant_reason} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The self-description gate reads the selected memory and therefore misses cases where the selected memory says `answer`.",
            "- The query-context gate improves on self-description but can still miss vague-query cases because it infers risk from natural language.",
            "- The tool-call grant gate reads concrete operation parameters and external grants. It catches recipient, scope, and expiry mismatches.",
            "- This does not solve write-time authorization or production policy semantics. It only demonstrates the next gate shape on a small internal packet.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    rows = [evaluate_scenario(scenario) for scenario in packet["scenarios"]]
    summary = summarize(rows)
    output = {
        "claim": "CLAIM-23",
        "packet_file": str(PACKET_PATH.relative_to(ROOT)),
        "summary": summary,
        "rows": [asdict(row) for row in rows],
    }
    RESULTS_JSON.write_text(json.dumps(output, indent=2), encoding="utf-8")
    RESULTS_MD.write_text(render_markdown(rows, summary), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Wrote {RESULTS_MD}")
    print(f"Wrote {RESULTS_JSON}")


if __name__ == "__main__":
    main()
