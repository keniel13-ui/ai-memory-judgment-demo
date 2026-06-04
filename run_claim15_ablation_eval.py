#!/usr/bin/env python3
"""Run CLAIM-15 governance-adjusted retrieval ablations."""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Any

from run_fresh_governs_eval import apply_annotations, load_annotations
from run_memory_store_eval import ROOT, score_row, summarize


DEFAULT_RESULTS_JSON = ROOT / "results" / "claim15_ablation_results.json"
DEFAULT_RESULTS_MD = ROOT / "results" / "claim15_ablation_results.md"

STRATEGIES = [
    "bm25_metadata_text",
    "scope_precedence_role_filter_bm25_metadata_text",
    "governance_adjusted_bm25_metadata_text",
    "governance_no_scope_bm25_metadata_text",
    "governance_no_governs_bm25_metadata_text",
    "governance_scope_weak_bm25_metadata_text",
    "authority_signal_fallback_bm25_metadata_text",
    "governs_trust_gated_bm25_metadata_text",
    "directional_action_governance_bm25_metadata_text",
]

DEFAULT_EVALS = [
    {
        "name": "fresh_governs_v0_1",
        "source": ROOT / "external_scenarios" / "fresh_claude_v0_4_v2_2_external_stores.json",
        "annotations": ROOT / "external_scenarios" / "fresh_governs_annotations_v0_1.json",
    },
    {
        "name": "fresh_governs_v0_2",
        "source": ROOT / "external_scenarios" / "fresh_claude_v0_4_v2_2_external_stores.json",
        "annotations": ROOT / "external_scenarios" / "fresh_governs_annotations_v0_2.json",
    },
    {
        "name": "fresh_governs_v0_3",
        "source": ROOT / "external_scenarios" / "fresh_claude_v0_4_v2_2_external_stores.json",
        "annotations": ROOT / "external_scenarios" / "fresh_governs_annotations_v0_3.json",
    },
    {
        "name": "clutter_action_types_v0_1",
        "source": ROOT / "external_scenarios" / "fresh_governs_clutter_v0_1_source.json",
        "annotations": ROOT / "external_scenarios" / "fresh_governs_clutter_action_types_annotations_v0_1.json",
    },
    {
        "name": "clutter_action_types_v0_2",
        "source": ROOT / "external_scenarios" / "fresh_governs_clutter_v0_1_source.json",
        "annotations": ROOT / "external_scenarios" / "fresh_governs_clutter_action_types_annotations_v0_2.json",
    },
    {
        "name": "claim15_stress_v0_1",
        "source": ROOT / "external_scenarios" / "claim15_governance_stress_v0_1.json",
        "annotations": None,
    },
    {
        "name": "claim15b_heldout_v0_1",
        "source": ROOT / "external_scenarios" / "claim15b_heldout_v0_1.json",
        "annotations": None,
    },
    {
        "name": "claim16_action_type_mismatch_v0_1",
        "source": ROOT / "external_scenarios" / "claim16_action_type_mismatch_v0_1.json",
        "annotations": None,
    },
]


def load_payload(source_path: Path, annotation_path: Path | None) -> dict[str, Any]:
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    if annotation_path is None:
        return payload
    annotations = load_annotations(annotation_path)
    return apply_annotations(payload, annotations)


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, int]:
    from run_memory_store_eval import MemoryStoreDecision

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


def evaluate(evals: list[dict[str, Any]]) -> dict[str, Any]:
    return evaluate_parallel(evals)


def evaluate_one(task: tuple[int, str, str, dict[str, Any]]) -> tuple[int, dict[str, Any]]:
    index, eval_name, strategy, scenario = task
    row = asdict(score_row(strategy, scenario))
    row["eval_name"] = eval_name
    return index, row


def evaluate_parallel(evals: list[dict[str, Any]], workers: int | None = None) -> dict[str, Any]:
    tasks: list[tuple[int, str, str, dict[str, Any]]] = []
    index = 0
    for eval_config in evals:
        source_path = eval_config["source"]
        if not source_path.exists():
            continue

        payload = load_payload(source_path, eval_config.get("annotations"))
        for scenario in payload["scenarios"]:
            for strategy in STRATEGIES:
                tasks.append((index, eval_config["name"], strategy, scenario))
                index += 1

    output_rows = []
    max_workers = workers or min(32, (os.cpu_count() or 1) + 4)
    if max_workers <= 1 or len(tasks) <= 1:
        output_rows = [evaluate_one(task)[1] for task in tasks]
    else:
        completed: list[tuple[int, dict[str, Any]]] = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(evaluate_one, task) for task in tasks]
            for future in as_completed(futures):
                completed.append(future.result())
        output_rows = [row for _, row in sorted(completed, key=lambda item: item[0])]

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in output_rows:
        grouped[f"{row['eval_name']}::{row['strategy']}"].append(row)

    summary = {}
    for key, rows in grouped.items():
        eval_name, strategy = key.split("::", 1)
        summary.setdefault(eval_name, {})[strategy] = summarize_rows(rows)

    return {
        "status": "CLAIM-15 governance-adjusted retrieval ablation results. Internal diagnostic, not benchmark-grade.",
        "strategies": STRATEGIES,
        "summary": summary,
        "rows": output_rows,
    }


def render_markdown(output: dict[str, Any]) -> str:
    lines = [
        "# CLAIM-15 Ablation Results",
        "",
        output["status"],
        "",
    ]
    for eval_name, by_strategy in output["summary"].items():
        lines.extend(
            [
                f"## {eval_name}",
                "",
                "| Strategy | Target selected | Action correct | Trap failures | FC errors | Downgrade misses | Overblocking |",
                "|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for strategy in STRATEGIES:
            if strategy not in by_strategy:
                continue
            summary = by_strategy[strategy]
            total = summary["total"]
            lines.append(
                f"| {strategy} | {summary['target_selected']}/{total} | "
                f"{summary['action_correct']}/{total} | "
                f"{summary['trap_failures']} | "
                f"{summary['false_certainty_errors']} | "
                f"{summary['downgrade_misses']} | "
                f"{summary['overblocking_errors']} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Scenario Rows",
            "",
            "| Eval | Strategy | Scenario | Expected | Selected | Role | Action | Act ok | Trap fail | OB |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in output["rows"]:
        lines.append(
            f"| {row['eval_name']} | {row['strategy']} | {row['scenario_id']} | "
            f"{row['expected_action']} | {row['selected_memory_id']} | {row['selected_role']} | "
            f"{row['action']} | {'ok' if row['action_correct'] else 'miss'} | "
            f"{'yes' if row['trap_failure'] else 'no'} | "
            f"{'yes' if row['overblocking_error'] else 'no'} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CLAIM-15 ablation evals.")
    parser.add_argument("--results-json", type=Path, default=DEFAULT_RESULTS_JSON)
    parser.add_argument("--results-md", type=Path, default=DEFAULT_RESULTS_MD)
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Parallel worker count. Use 1 for sequential execution.",
    )
    args = parser.parse_args()

    results_json = args.results_json if args.results_json.is_absolute() else ROOT / args.results_json
    results_md = args.results_md if args.results_md.is_absolute() else ROOT / args.results_md
    output = evaluate_parallel(DEFAULT_EVALS, workers=args.workers)
    results_json.parent.mkdir(parents=True, exist_ok=True)
    results_md.parent.mkdir(parents=True, exist_ok=True)
    results_json.write_text(json.dumps(output, indent=2), encoding="utf-8")
    results_md.write_text(render_markdown(output), encoding="utf-8")
    print(json.dumps(output["summary"], indent=2))
    print(f"Wrote {results_md}")
    print(f"Wrote {results_json}")


if __name__ == "__main__":
    main()
