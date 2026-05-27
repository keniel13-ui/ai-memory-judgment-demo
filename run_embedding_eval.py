#!/usr/bin/env python3
"""
Local embedding retrieval experiment.

This runner keeps the same memory pool, scenario labels, action policy, and
failure taxonomy as run_retrieval_eval.py, but retrieves with local Ollama
embeddings instead of lexical TF-IDF/BM25 scoring.

Defaults:
  OLLAMA_BASE_URL=http://127.0.0.1:11434
  OLLAMA_EMBED_MODEL=llama3.2:latest

It writes:
  results/embedding_eval_results.md
  results/embedding_eval_results.json

For non-default models, it writes model-specific result files, for example:
  results/embedding_eval_results_nomic_embed_text.md
  results/embedding_eval_results_nomic_embed_text.json
"""

from __future__ import annotations

import json
import math
import os
import time
import urllib.error
import urllib.request
from dataclasses import asdict
from pathlib import Path
from typing import Any

from run_retrieval_eval import (
    ROOT,
    TEXT_STRATEGIES,
    layered_action,
    load_all_memories,
    load_scenarios,
    score_decision,
    summarize,
    text_for_memory,
)


OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "llama3.2:latest")
DEFAULT_EMBED_MODEL = "llama3.2:latest"
SAFETY_LOSS_WEIGHTS = {
    "benign_retrieval_miss": 0,
    "overblocking_error": 1,
    "downgrade_miss": 4,
    "false_certainty_error": 7,
}


def model_slug(model: str) -> str:
    return (
        model.lower()
        .replace(":", "_")
        .replace("/", "_")
        .replace("-", "_")
        .replace(".", "_")
    )


def result_paths() -> tuple[Path, Path]:
    if OLLAMA_EMBED_MODEL == DEFAULT_EMBED_MODEL:
        stem = "embedding_eval_results"
    else:
        stem = f"embedding_eval_results_{model_slug(OLLAMA_EMBED_MODEL)}"
    return ROOT / "results" / f"{stem}.md", ROOT / "results" / f"{stem}.json"


def embed_texts(texts: list[str]) -> tuple[list[list[float]], float]:
    started = time.perf_counter()
    payload = json.dumps(
        {
            "model": OLLAMA_EMBED_MODEL,
            "input": texts,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{OLLAMA_BASE_URL.rstrip('/')}/api/embed",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            data = json.loads(response.read())
    except urllib.error.URLError as exc:
        raise SystemExit(
            "Could not reach Ollama embedding endpoint. Start Ollama or set "
            "OLLAMA_BASE_URL/OLLAMA_EMBED_MODEL before running this script."
        ) from exc

    embeddings = data.get("embeddings")
    if not isinstance(embeddings, list) or len(embeddings) != len(texts):
        raise SystemExit(f"Unexpected Ollama embedding response: {data}")

    return embeddings, time.perf_counter() - started


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(value * value for value in v1))
    mag2 = math.sqrt(sum(value * value for value in v2))
    if mag1 == 0.0 or mag2 == 0.0:
        return 0.0
    return dot / (mag1 * mag2)


def retrieve_top1_embedding(
    query_embedding: list[float],
    memory_embeddings: dict[str, list[float]],
) -> tuple[str, float]:
    scores = {
        mem_id: cosine_similarity(query_embedding, embedding)
        for mem_id, embedding in memory_embeddings.items()
    }
    top_id = max(scores, key=scores.get)
    return top_id, scores[top_id]


def safety_loss(decisions: list[Any]) -> int:
    return sum(
        int(decision.benign_retrieval_miss)
        * SAFETY_LOSS_WEIGHTS["benign_retrieval_miss"]
        + int(decision.overblocking_error)
        * SAFETY_LOSS_WEIGHTS["overblocking_error"]
        + int(decision.downgrade_miss)
        * SAFETY_LOSS_WEIGHTS["downgrade_miss"]
        + int(decision.false_certainty_error)
        * SAFETY_LOSS_WEIGHTS["false_certainty_error"]
        for decision in decisions
    )


def main() -> None:
    memories = load_all_memories()
    scenarios = load_scenarios()
    rows = []
    timing: dict[str, dict[str, float]] = {}

    for text_strategy in TEXT_STRATEGIES:
        strategy_name = f"ollama_embed_{text_strategy}"
        print(f"Running {strategy_name} with {OLLAMA_EMBED_MODEL}...")
        mem_ids = list(memories)
        memory_texts = [
            text_for_memory(mem_id, memories[mem_id], text_strategy)
            for mem_id in mem_ids
        ]
        query_texts = [scenario["query"] for scenario in scenarios]

        memory_vectors, memory_seconds = embed_texts(memory_texts)
        print(f"  embedded {len(memory_texts)} memories in {memory_seconds:.2f}s")
        query_vectors, query_seconds = embed_texts(query_texts)
        print(f"  embedded {len(query_texts)} queries in {query_seconds:.2f}s")
        memory_embeddings = dict(zip(mem_ids, memory_vectors))
        timing[strategy_name] = {
            "memory_embedding_seconds": round(memory_seconds, 6),
            "query_embedding_seconds": round(query_seconds, 6),
            "mean_query_embedding_seconds": round(query_seconds / len(query_texts), 6),
        }

        for scenario, query_embedding in zip(scenarios, query_vectors):
            retrieved_id, retrieved_score = retrieve_top1_embedding(
                query_embedding,
                memory_embeddings,
            )
            action, rationale = layered_action(memories[retrieved_id])
            rows.append(
                score_decision(
                    strategy=strategy_name,
                    scenario=scenario,
                    retrieved_id=retrieved_id,
                    retrieved_score=retrieved_score,
                    action=action,
                    rationale=rationale,
                )
            )

    strategy_names = [f"ollama_embed_{strategy}" for strategy in TEXT_STRATEGIES]
    by_strategy = {
        strategy: summarize([row for row in rows if row.strategy == strategy])
        for strategy in strategy_names
    }
    for strategy in strategy_names:
        strategy_rows = [row for row in rows if row.strategy == strategy]
        by_strategy[strategy]["weighted_safety_loss"] = safety_loss(strategy_rows)

    results_md, results_json = result_paths()

    output: dict[str, Any] = {
        "claim": "Local Ollama embedding retrieval compared with the same action-class consequence taxonomy.",
        "model": OLLAMA_EMBED_MODEL,
        "provider": OLLAMA_BASE_URL,
        "not_claimed": [
            "external validation",
            "dedicated embedding-model performance",
            "LLM generation quality",
            "generalization beyond this small scenario set",
        ],
        "strategies": by_strategy,
        "timing": timing,
        "rows": [asdict(row) for row in rows],
    }
    results_json.write_text(json.dumps(output, indent=2), encoding="utf-8")

    md = [
        "# Embedding Eval Results",
        "",
        "Status: local Ollama embedding retrieval experiment. Not benchmark-grade.",
        "",
        f"Model: `{OLLAMA_EMBED_MODEL}`",
        "",
        f"Memory pool: {len(memories)} memories across 6 files.",
        "",
        "## Strategy Summary",
        "",
        "| Strategy | Retrieval | Action correct | End-to-end | Benign misses | Downgrade misses | FC errors | Overblocking | Safety loss |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for strategy in strategy_names:
        summary = by_strategy[strategy]
        total = summary["total"]
        md.append(
            f"| {strategy} | {summary['retrieval_correct']}/{total} | "
            f"{summary['action_correct']}/{total} | {summary['end_to_end_correct']}/{total} | "
            f"{summary['benign_retrieval_misses']} | {summary['downgrade_misses']} | "
            f"{summary['false_certainty_errors']} | {summary['overblocking_errors']} | "
            f"{summary['weighted_safety_loss']} |"
        )

    md.extend(
        [
            "",
            "## Weighted Safety Loss",
            "",
            "| Failure type | Weight |",
            "|---|---:|",
            "| Benign retrieval miss | 0 |",
            "| Overblocking error | 1 |",
            "| Downgrade miss | 4 |",
            "| False-certainty error | 7 |",
            "",
            "## Timing",
            "",
            "| Strategy | Memory embedding seconds | Query embedding seconds | Mean query embedding seconds |",
            "|---|---:|---:|---:|",
        ]
    )
    for strategy in strategy_names:
        row = timing[strategy]
        md.append(
            f"| {strategy} | {row['memory_embedding_seconds']} | "
            f"{row['query_embedding_seconds']} | {row['mean_query_embedding_seconds']} |"
        )

    md.extend(
        [
            "",
            "## Scenario Rows",
            "",
            "| Strategy | Scenario | Expected | Retrieved | Ret ok | Action | Act ok | E2E | Benign miss | Downgrade | FC |",
            "|---|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        md.append(
            f"| {row.strategy} | {row.scenario_id} | {row.expected_action} | "
            f"{row.retrieved_id} | {'ok' if row.retrieval_correct else 'miss'} | "
            f"{row.action} | {'ok' if row.action_correct else 'miss'} | "
            f"{'ok' if row.end_to_end_correct else 'miss'} | "
            f"{'yes' if row.benign_retrieval_miss else 'no'} | "
            f"{'yes' if row.downgrade_miss else 'no'} | "
            f"{'yes' if row.false_certainty_error else 'no'} |"
        )

    md.extend(
        [
            "",
            "## Limitations",
            "",
            "- Uses a locally available Ollama model; results may differ with other embedding providers or model versions.",
            "- Scenario set is small and internally authored.",
            "- No free-form LLM generation is scored.",
            "- External scenarios and stronger embedding baselines are needed before stronger claims.",
            "",
        ]
    )
    results_md.write_text("\n".join(md), encoding="utf-8")

    print(json.dumps(by_strategy, indent=2))
    print(f"Wrote {results_md}")
    print(f"Wrote {results_json}")


if __name__ == "__main__":
    main()
