#!/usr/bin/env python3
"""
Top-k inspection for the s02 downgrade miss.

This script answers the current v0.3 question:

Does correction_no_overclaim_eval appear in top-k for s02 even when it is not
ranked first?

It inspects deterministic lexical strategies without network/model calls.
Embedding top-k can be added separately after this coverage check.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from run_retrieval_eval import (
    ROOT,
    TEXT_STRATEGIES,
    build_tfidf_index,
    build_token_index,
    cosine_similarity,
    load_all_memories,
    load_scenarios,
    retrieve_top1_bm25,
    vectorize_query,
)


RESULTS_MD = ROOT / "results" / "topk_inspection_results.md"
RESULTS_JSON = ROOT / "results" / "topk_inspection_results.json"
TARGET_SCENARIO_ID = "s02_overclaim_eval_results"
TARGET_MEMORY_ID = "correction_no_overclaim_eval"
TOP_K = 5


@dataclass
class TopKRow:
    strategy: str
    rank: int
    memory_id: str
    score: float
    is_target: bool


def ranked_tfidf(query: str, text_strategy: str) -> list[tuple[str, float]]:
    memories = load_all_memories()
    vectors, idf = build_tfidf_index(memories, text_strategy)
    query_vector = vectorize_query(query, idf)
    scores = {
        memory_id: cosine_similarity(query_vector, vector)
        for memory_id, vector in vectors.items()
    }
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def ranked_bm25(query: str, text_strategy: str) -> list[tuple[str, float]]:
    # Use the same BM25 implementation as run_retrieval_eval.py, then compute all
    # scores by temporarily removing the max-only wrapper logic here.
    import math
    from collections import Counter
    from run_retrieval_eval import tokenize

    memories = load_all_memories()
    documents = build_token_index(memories, text_strategy)
    query_terms = tokenize(query)
    n_docs = len(documents)
    avgdl = sum(len(tokens) for tokens in documents.values()) / max(n_docs, 1)
    k1 = 1.5
    b = 0.75

    df: Counter[str] = Counter()
    for tokens in documents.values():
        for token in set(tokens):
            df[token] += 1

    scores: dict[str, float] = {}
    for memory_id, tokens in documents.items():
        tf = Counter(tokens)
        doc_len = len(tokens)
        score = 0.0
        for term in query_terms:
            if tf[term] == 0:
                continue
            idf = math.log(1.0 + (n_docs - df[term] + 0.5) / (df[term] + 0.5))
            denom = tf[term] + k1 * (1.0 - b + b * doc_len / max(avgdl, 1.0))
            score += idf * (tf[term] * (k1 + 1.0)) / denom
        scores[memory_id] = score

    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def target_scenario() -> dict:
    for scenario in load_scenarios():
        if scenario["id"] == TARGET_SCENARIO_ID:
            return scenario
    raise SystemExit(f"Missing scenario: {TARGET_SCENARIO_ID}")


def main() -> None:
    scenario = target_scenario()
    query = scenario["query"]
    rows: list[TopKRow] = []
    summaries = []

    strategy_rankings: dict[str, list[tuple[str, float]]] = {}
    for text_strategy in TEXT_STRATEGIES:
        strategy_rankings[f"tfidf_{text_strategy}"] = ranked_tfidf(query, text_strategy)
        strategy_rankings[f"bm25_{text_strategy}"] = ranked_bm25(query, text_strategy)

    for strategy, ranking in strategy_rankings.items():
        target_rank = None
        for rank, (memory_id, score) in enumerate(ranking, start=1):
            if rank <= TOP_K:
                rows.append(
                    TopKRow(
                        strategy=strategy,
                        rank=rank,
                        memory_id=memory_id,
                        score=round(score, 6),
                        is_target=memory_id == TARGET_MEMORY_ID,
                    )
                )
            if memory_id == TARGET_MEMORY_ID:
                target_rank = rank

        summaries.append(
            {
                "strategy": strategy,
                "target_rank": target_rank,
                "target_in_top_3": target_rank is not None and target_rank <= 3,
                "target_in_top_5": target_rank is not None and target_rank <= 5,
                "top_1": ranking[0][0],
            }
        )

    output = {
        "scenario_id": TARGET_SCENARIO_ID,
        "target_memory_id": TARGET_MEMORY_ID,
        "question": "Does the stricter correction appear in top-k for s02?",
        "summaries": summaries,
        "rows": [asdict(row) for row in rows],
    }
    RESULTS_JSON.write_text(json.dumps(output, indent=2), encoding="utf-8")

    md = [
        "# Top-K Inspection Results",
        "",
        "Status: deterministic lexical top-k inspection for the s02 downgrade miss.",
        "",
        f"Scenario: `{TARGET_SCENARIO_ID}`",
        f"Target memory: `{TARGET_MEMORY_ID}`",
        "",
        "## Summary",
        "",
        "| Strategy | Top-1 | Target rank | In top-3 | In top-5 |",
        "|---|---|---:|---|---|",
    ]
    for summary in summaries:
        md.append(
            f"| {summary['strategy']} | {summary['top_1']} | "
            f"{summary['target_rank']} | "
            f"{'yes' if summary['target_in_top_3'] else 'no'} | "
            f"{'yes' if summary['target_in_top_5'] else 'no'} |"
        )

    md.extend(
        [
            "",
            "## Top-5 Rows",
            "",
            "| Strategy | Rank | Memory | Score | Target |",
            "|---|---:|---|---:|---|",
        ]
    )
    for row in rows:
        md.append(
            f"| {row.strategy} | {row.rank} | {row.memory_id} | "
            f"{row.score} | {'yes' if row.is_target else 'no'} |"
        )

    md.extend(
        [
            "",
            "## Interpretation Rule",
            "",
            "- If the target appears in top-k, conservative aggregation can be tested.",
            "- If the target does not appear in top-k, the miss is a retrieval coverage failure for that strategy.",
            "",
        ]
    )
    RESULTS_MD.write_text("\n".join(md), encoding="utf-8")

    print(json.dumps(output["summaries"], indent=2))
    print(f"Wrote {RESULTS_MD}")
    print(f"Wrote {RESULTS_JSON}")


if __name__ == "__main__":
    main()

