#!/usr/bin/env python3
"""
Query-aligned top-k aggregation experiment.

This refines the blunt conservative aggregation rule:

Old rule:
  choose the most protective action among top-k retrieved memories.

New rule:
  only elevate to block if a top-k memory is block-class AND query-aligned
  by structured metadata, retrieval terms, memory ID terms, or correction
  target terms.

The goal is to preserve the s02 fix while reducing overblocking.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from run_retrieval_eval import (
    ACTION_RANK,
    ROOT,
    TEXT_STRATEGIES,
    layered_action,
    load_all_memories,
    load_scenarios,
    score_decision,
    summarize,
    tokenize,
)
from run_topk_inspection import ranked_bm25, ranked_tfidf


TOP_K = 3
RESULTS_MD = ROOT / "results" / "aligned_topk_aggregation_results.md"
RESULTS_JSON = ROOT / "results" / "aligned_topk_aggregation_results.json"
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "do",
    "does",
    "for",
    "from",
    "has",
    "have",
    "if",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "our",
    "should",
    "that",
    "the",
    "their",
    "this",
    "to",
    "we",
    "what",
    "when",
    "which",
    "with",
}


def meaningful_tokens(text: str) -> set[str]:
    return {token for token in tokenize(text) if token not in STOPWORDS}


def alignment_terms(memory_id: str, memory: dict[str, Any]) -> set[str]:
    terms = meaningful_tokens(memory_id.replace("_", " "))
    for key in [
        "memory_type",
        "status",
        "priority",
        "epistemic_status",
        "decision_risk",
        "source",
        "_file",
        "correction_target",
    ]:
        value = memory.get(key)
        if value:
            terms.update(meaningful_tokens(str(value).replace("_", " ")))
    for term in memory.get("retrieval_terms", []):
        terms.update(meaningful_tokens(str(term).replace("_", " ")))
    return terms


def is_query_aligned(query: str, memory_id: str, memory: dict[str, Any]) -> bool:
    query_terms = meaningful_tokens(query)
    terms = alignment_terms(memory_id, memory)
    return bool(query_terms & terms)


def aggregate_action(
    query: str,
    top_ids: list[str],
    memories: dict[str, dict[str, Any]],
) -> tuple[str, str]:
    actions = []
    for memory_id in top_ids:
        action, rationale = layered_action(memories[memory_id])
        aligned = is_query_aligned(query, memory_id, memories[memory_id])
        actions.append((action, memory_id, rationale, aligned))

    aligned_blocks = [
        item for item in actions
        if item[0] == "block" and item[3]
    ]
    if aligned_blocks:
        action, memory_id, rationale, _ = aligned_blocks[0]
        joined = "; ".join(
            f"{mem_id}:{act}:aligned={aligned}"
            for act, mem_id, _, aligned in actions
        )
        return action, f"aligned block via {memory_id}; candidates {joined}; selected: {rationale}"

    top_action, top_memory_id, top_rationale, _ = actions[0]
    joined = "; ".join(
        f"{mem_id}:{act}:aligned={aligned}"
        for act, mem_id, _, aligned in actions
    )
    return top_action, f"top-1 action retained via {top_memory_id}; candidates {joined}; selected: {top_rationale}"


def strategy_rankings(query: str) -> dict[str, list[tuple[str, float]]]:
    rankings = {}
    for text_strategy in TEXT_STRATEGIES:
        rankings[f"tfidf_{text_strategy}"] = ranked_tfidf(query, text_strategy)
        rankings[f"bm25_{text_strategy}"] = ranked_bm25(query, text_strategy)
    return rankings


def main() -> None:
    memories = load_all_memories()
    scenarios = load_scenarios()
    rows = []
    topk_recall = {f"tfidf_{s}": 0 for s in TEXT_STRATEGIES}
    topk_recall.update({f"bm25_{s}": 0 for s in TEXT_STRATEGIES})

    for scenario in scenarios:
        rankings = strategy_rankings(scenario["query"])
        for strategy, ranking in rankings.items():
            top_ids = [memory_id for memory_id, _ in ranking[:TOP_K]]
            top1_id, top1_score = ranking[0]
            if scenario["correct_memory_id"] in top_ids:
                topk_recall[strategy] += 1

            action, rationale = aggregate_action(
                scenario["query"],
                top_ids,
                memories,
            )
            rows.append(
                score_decision(
                    strategy=f"{strategy}_top{TOP_K}_aligned",
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
        base_strategy = strategy.replace(f"_top{TOP_K}_aligned", "")
        summary = summarize([row for row in rows if row.strategy == strategy])
        summary[f"top_{TOP_K}_recall"] = topk_recall[base_strategy]
        by_strategy[strategy] = summary

    output = {
        "claim": "Query-aligned top-k aggregation over deterministic lexical retrieval strategies.",
        "top_k": TOP_K,
        "aggregation_rule": "only elevate to block when a top-k block memory is query-aligned; otherwise retain top-1 action",
        "strategies": by_strategy,
        "rows": [asdict(row) for row in rows],
    }
    RESULTS_JSON.write_text(json.dumps(output, indent=2), encoding="utf-8")

    md = [
        "# Query-Aligned Top-K Aggregation Results",
        "",
        "Status: deterministic lexical top-k aggregation with query-aligned block elevation. Not benchmark-grade.",
        "",
        f"Top-k: `{TOP_K}`",
        "",
        "Rule:",
        "",
        "> Only elevate to `block` when a top-k `block` memory is query-aligned; otherwise retain the top-1 action.",
        "",
        "Alignment uses structured metadata, retrieval terms, memory ID terms, and correction-target terms after stopword filtering. It does not use full memory body text.",
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
            "- If downgrade misses drop without overblocking rising, query alignment improved the aggregation rule.",
            "- If downgrade misses remain, alignment was too strict or the strict memory was not present in top-k.",
            "",
        ]
    )
    RESULTS_MD.write_text("\n".join(md), encoding="utf-8")

    print(json.dumps(by_strategy, indent=2))
    print(f"Wrote {RESULTS_MD}")
    print(f"Wrote {RESULTS_JSON}")


if __name__ == "__main__":
    main()
