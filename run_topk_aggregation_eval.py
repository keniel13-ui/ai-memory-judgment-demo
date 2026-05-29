#!/usr/bin/env python3
"""
Conservative top-k aggregation experiment.

This tests whether the stricter memory appearing in top-k can recover the
correct action class when top-1 retrieves a weaker memory.

Aggregation rule:
  choose the most protective action among top-k retrieved memories.

This is intentionally simple and likely too conservative. The purpose is to
measure whether top-k aggregation fixes downgrade misses and how much
overblocking it introduces.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any

from run_retrieval_eval import (
    ACTION_RANK,
    ROOT,
    TEXT_STRATEGIES,
    StrategyDecision,
    layered_action,
    load_all_memories,
    load_scenarios,
    score_decision,
    summarize,
)
from run_topk_inspection import ranked_bm25, ranked_tfidf


TOP_K = 3
RESULTS_MD = ROOT / "results" / "topk_aggregation_results.md"
RESULTS_JSON = ROOT / "results" / "topk_aggregation_results.json"


def aggregate_action(memory_ids: list[str], memories: dict[str, dict[str, Any]]) -> tuple[str, str]:
    actions = []
    for memory_id in memory_ids:
        action, rationale = layered_action(memories[memory_id])
        actions.append((action, memory_id, rationale))

    action, memory_id, rationale = max(
        actions,
        key=lambda item: ACTION_RANK[item[0]],
    )
    joined = "; ".join(f"{mem_id}:{act}" for act, mem_id, _ in actions)
    return action, f"top-{TOP_K} conservative max via {memory_id}; candidates {joined}; selected: {rationale}"


def strategy_rankings(query: str) -> dict[str, list[tuple[str, float]]]:
    rankings = {}
    for text_strategy in TEXT_STRATEGIES:
        rankings[f"tfidf_{text_strategy}"] = ranked_tfidf(query, text_strategy)
        rankings[f"bm25_{text_strategy}"] = ranked_bm25(query, text_strategy)
    return rankings


def main() -> None:
    memories = load_all_memories()
    scenarios = load_scenarios()
    rows: list[StrategyDecision] = []
    topk_recall: defaultdict[str, int] = defaultdict(int)
    strategy_counts: defaultdict[str, int] = defaultdict(int)

    for scenario in scenarios:
        rankings = strategy_rankings(scenario["query"])
        for strategy, ranking in rankings.items():
            strategy_counts[strategy] += 1
            top_ids = [memory_id for memory_id, _ in ranking[:TOP_K]]
            top1_id, top1_score = ranking[0]
            if scenario["correct_memory_id"] in top_ids:
                topk_recall[strategy] += 1

            action, rationale = aggregate_action(top_ids, memories)
            rows.append(
                score_decision(
                    strategy=f"{strategy}_top{TOP_K}_conservative",
                    scenario=scenario,
                    retrieved_id=top1_id,
                    retrieved_score=top1_score,
                    action=action,
                    rationale=rationale,
                )
            )

    strategy_names = sorted({row.strategy for row in rows})
    by_strategy = {}
    for strategy in strategy_names:
        base_strategy = strategy.replace(f"_top{TOP_K}_conservative", "")
        summary = summarize([row for row in rows if row.strategy == strategy])
        summary[f"top_{TOP_K}_recall"] = topk_recall[base_strategy]
        by_strategy[strategy] = summary

    output = {
        "claim": "Top-k conservative aggregation over deterministic lexical retrieval strategies.",
        "top_k": TOP_K,
        "aggregation_rule": "choose the most protective action among top-k retrieved memories",
        "strategies": by_strategy,
        "rows": [asdict(row) for row in rows],
    }
    RESULTS_JSON.write_text(json.dumps(output, indent=2), encoding="utf-8")

    md = [
        "# Top-K Aggregation Results",
        "",
        "Status: deterministic lexical top-k conservative aggregation. Not benchmark-grade.",
        "",
        f"Top-k: `{TOP_K}`",
        "",
        "Rule:",
        "",
        "> Choose the most protective action among the top-k retrieved memories.",
        "",
        "## Strategy Summary",
        "",
        f"| Strategy | Top-{TOP_K} recall | Top-1 retrieval | Action correct | End-to-end | Benign misses | Downgrade misses | FC errors | Overblocking |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for strategy in strategy_names:
        summary = by_strategy[strategy]
        total = summary["total"]
        md.append(
            f"| {strategy} | {summary[f'top_{TOP_K}_recall']}/{total} | "
            f"{summary['retrieval_correct']}/{total} | "
            f"{summary['action_correct']}/{total} | "
            f"{summary['end_to_end_correct']}/{total} | "
            f"{summary['benign_retrieval_misses']} | "
            f"{summary['downgrade_misses']} | "
            f"{summary['false_certainty_errors']} | "
            f"{summary['overblocking_errors']} |"
        )

    md.extend(
        [
            "",
            "## Scenario Rows",
            "",
            "| Strategy | Scenario | Expected | Top-1 | Action | Act ok | Benign miss | Downgrade | FC | Overblocking |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        md.append(
            f"| {row.strategy} | {row.scenario_id} | {row.expected_action} | "
            f"{row.retrieved_id} | {row.action} | "
            f"{'ok' if row.action_correct else 'miss'} | "
            f"{'yes' if row.benign_retrieval_miss else 'no'} | "
            f"{'yes' if row.downgrade_miss else 'no'} | "
            f"{'yes' if row.false_certainty_error else 'no'} | "
            f"{'yes' if row.overblocking_error else 'no'} |"
        )

    md.extend(
        [
            "",
            "## Interpretation",
            "",
            "- If downgrade misses drop but overblocking rises, the rule is protective but too blunt.",
            "- If downgrade misses remain, top-k did not surface the stricter memory or aggregation failed to select it.",
            "",
        ]
    )
    RESULTS_MD.write_text("\n".join(md), encoding="utf-8")

    print(json.dumps(by_strategy, indent=2))
    print(f"Wrote {RESULTS_MD}")
    print(f"Wrote {RESULTS_JSON}")


if __name__ == "__main__":
    main()

