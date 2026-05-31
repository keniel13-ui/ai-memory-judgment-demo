#!/usr/bin/env python3
"""
Evaluate fresh-authored governs metadata.

The script has two jobs:

1. Write an authoring packet that hides target/distractor roles and asks an
   external author to add jurisdiction metadata.
2. Apply the authored governs annotations back onto the v2.2 memory stores and
   compare ordinary BM25, role filtering, and scope-aware role filtering.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any

from run_memory_store_eval import ROOT, score_row, summarize


SOURCE_SCENARIOS = ROOT / "external_scenarios" / "fresh_claude_v0_4_v2_2_external_stores.json"
DEFAULT_PACKET = ROOT / "external_scenarios" / "fresh_governs_authoring_packet_v0_1.json"
DEFAULT_GOVERNS = ROOT / "external_scenarios" / "fresh_governs_annotations_v0_1.json"
RESULTS_JSON = ROOT / "results" / "fresh_governs_eval_results.json"
RESULTS_MD = ROOT / "results" / "fresh_governs_eval_results.md"
STRATEGIES = [
    "bm25_metadata_text",
    "role_filter_bm25_metadata_text",
    "scope_role_filter_bm25_metadata_text",
    "scope_precedence_role_filter_bm25_metadata_text",
]


def load_source(source_path: Path = SOURCE_SCENARIOS) -> dict[str, Any]:
    return json.loads(source_path.read_text(encoding="utf-8"))


def write_authoring_packet(source_path: Path, path: Path) -> None:
    payload = load_source(source_path)
    packet = {
        "schema_version": "governs_authoring_v0_1",
        "source_scenario_file": str(source_path.relative_to(ROOT)) if source_path.is_relative_to(ROOT) else str(source_path),
        "instructions": (
            "Add governs metadata for memories that should have jurisdiction over "
            "some class of user request. Do not use role/answer-key information."
        ),
        "governs_shape": {
            "any_terms": ["at least one of these query terms should appear"],
            "all_terms": ["all of these query terms must appear"],
            "excluded_terms": ["if any of these terms appear, scope does not match"],
            "action_types": ["optional: read, write, execute"],
        },
        "scenarios": [],
    }
    for scenario in payload["scenarios"]:
        packet["scenarios"].append(
            {
                "scenario_id": scenario["id"],
                "query": scenario["query"],
                "category": scenario.get("category", ""),
                "memories": [
                    {
                        "memory_index": index,
                        "memory_type": memory.get("memory_type"),
                        "status": memory.get("status"),
                        "priority": memory.get("priority"),
                        "epistemic_status": memory.get("epistemic_status"),
                        "verification_required": memory.get("verification_required"),
                        "allowed_action_hint": memory.get("allowed_action_hint"),
                        "retrieval_terms": memory.get("retrieval_terms", []),
                        "text": memory.get("text", ""),
                    }
                    for index, memory in enumerate(scenario["memory_store"], start=1)
                ],
            }
        )
    path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    print(f"Wrote {path}")


def load_annotations(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "annotations" in data:
        annotations = data["annotations"]
    elif isinstance(data, list):
        annotations = data
    else:
        raise ValueError("Governs file must be a list or an object with an 'annotations' list")
    if not isinstance(annotations, list):
        raise ValueError("'annotations' must be a list")
    return annotations


def normalize_terms(values: Any) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list):
        raise ValueError("governs terms must be lists")
    normalized = []
    for value in values:
        term = str(value).strip().lower()
        if term:
            normalized.append(term)
    return normalized


def normalize_governs(governs: dict[str, Any]) -> dict[str, list[str]]:
    return {
        "any_terms": normalize_terms(governs.get("any_terms")),
        "all_terms": normalize_terms(governs.get("all_terms")),
        "excluded_terms": normalize_terms(governs.get("excluded_terms")),
        "action_types": normalize_terms(governs.get("action_types")),
    }


def apply_annotations(payload: dict[str, Any], annotations: list[dict[str, Any]]) -> dict[str, Any]:
    scenario_by_id = {scenario["id"]: scenario for scenario in payload["scenarios"]}
    applied = 0
    for annotation in annotations:
        scenario_id = annotation.get("scenario_id")
        if scenario_id not in scenario_by_id:
            raise ValueError(f"Unknown scenario_id: {scenario_id}")
        memory_index = int(annotation.get("memory_index", 0))
        memories = scenario_by_id[scenario_id]["memory_store"]
        if memory_index < 1 or memory_index > len(memories):
            raise ValueError(f"Invalid memory_index {memory_index} for {scenario_id}")
        governs = annotation.get("governs") or {}
        if not governs:
            continue
        memories[memory_index - 1]["governs"] = normalize_governs(governs)
        applied += 1
    payload["governs_annotations_applied"] = applied
    return payload


def evaluate(payload: dict[str, Any], source_path: Path, governs_path: Path) -> dict[str, Any]:
    decisions = []
    for scenario in payload["scenarios"]:
        for strategy in STRATEGIES:
            decision = score_row(strategy, scenario)
            decisions.append(asdict(decision))

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in decisions:
        grouped[row["strategy"]].append(row)
    summary = {
        strategy: summarize_rows(rows)
        for strategy, rows in grouped.items()
    }
    return {
        "source_scenario_file": str(source_path.relative_to(ROOT)) if source_path.is_relative_to(ROOT) else str(source_path),
        "governs_file": str(governs_path.relative_to(ROOT)) if governs_path.is_relative_to(ROOT) else str(governs_path),
        "governs_annotations_applied": payload.get("governs_annotations_applied", 0),
        "strategies": STRATEGIES,
        "summary": summary,
        "rows": decisions,
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, int]:
    from run_memory_store_eval import MemoryStoreDecision

    decisions = [
        MemoryStoreDecision(
            **{
                key: value
                for key, value in row.items()
                if key in MemoryStoreDecision.__dataclass_fields__
            }
        )
        for row in rows
    ]
    return summarize(decisions)


def render_markdown(output: dict[str, Any]) -> str:
    lines = [
        "# Fresh Governs Eval Results",
        "",
        "Status: evaluation of externally/fresh-authored jurisdiction metadata. Not benchmark-grade.",
        "",
        f"Governs annotations applied: `{output['governs_annotations_applied']}`",
        "",
        "## Strategy Summary",
        "",
        "| Strategy | Target selected | Action correct | Trap failures | FC errors | Downgrade misses | Overblocking |",
        "|---|---:|---:|---:|---:|---:|---:|",
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
            f"{summary['overblocking_errors']} |"
        )

    lines.extend(
        [
            "",
            "## Scenario Rows",
            "",
            "| Strategy | Scenario | Expected | Selected role | Action | Act ok | Trap fail | FC | Downgrade | OB |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in output["rows"]:
        lines.append(
            f"| {row['strategy']} | {row['scenario_id']} | {row['expected_action']} | "
            f"{row['selected_role']} | {row['action']} | "
            f"{'ok' if row['action_correct'] else 'miss'} | "
            f"{'yes' if row['trap_failure'] else 'no'} | "
            f"{'yes' if row['false_certainty_error'] else 'no'} | "
            f"{'yes' if row['downgrade_miss'] else 'no'} | "
            f"{'yes' if row['overblocking_error'] else 'no'} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate fresh-authored governs metadata.")
    parser.add_argument("--write-packet", action="store_true", help="Write the authoring packet and exit.")
    parser.add_argument("--source-scenarios", type=Path, default=SOURCE_SCENARIOS)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--governs", type=Path, default=DEFAULT_GOVERNS)
    parser.add_argument("--results-json", type=Path, default=RESULTS_JSON)
    parser.add_argument("--results-md", type=Path, default=RESULTS_MD)
    args = parser.parse_args()

    source_path = args.source_scenarios if args.source_scenarios.is_absolute() else ROOT / args.source_scenarios
    packet_path = args.packet if args.packet.is_absolute() else ROOT / args.packet
    governs_path = args.governs if args.governs.is_absolute() else ROOT / args.governs
    results_json = args.results_json if args.results_json.is_absolute() else ROOT / args.results_json
    results_md = args.results_md if args.results_md.is_absolute() else ROOT / args.results_md

    if args.write_packet:
        write_authoring_packet(source_path, packet_path)
        return

    if not governs_path.exists():
        raise SystemExit(
            f"No governs annotation file found at {governs_path}. "
            f"Run with --write-packet first, then have a fresh author fill annotations."
        )

    payload = load_source(source_path)
    annotations = load_annotations(governs_path)
    scoped_payload = apply_annotations(payload, annotations)
    output = evaluate(scoped_payload, source_path, governs_path)
    results_json.parent.mkdir(parents=True, exist_ok=True)
    results_md.parent.mkdir(parents=True, exist_ok=True)
    results_json.write_text(json.dumps(output, indent=2), encoding="utf-8")
    results_md.write_text(render_markdown(output), encoding="utf-8")
    print(json.dumps(output["summary"], indent=2))
    print(f"Wrote {results_md}")
    print(f"Wrote {results_json}")


if __name__ == "__main__":
    main()
