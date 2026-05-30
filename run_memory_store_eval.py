#!/usr/bin/env python3
"""
Scenario-local memory-store evaluator.

This keeps the fresh-Claude v0.4 adversarial mini-benchmark separate from
the original shared-pool retrieval evaluator. Each scenario carries its own
target/distractor memories, so the test asks:

Given this local adversarial memory set, does retrieval select a memory that
is safe to act on, or a tempting distractor?
"""

from __future__ import annotations

import json
import math
import os
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from run_retrieval_eval import ACTION_RANK, ROOT, layered_action, tokenize


DEFAULT_SCENARIOS_PATH = ROOT / "external_scenarios" / "fresh_claude_v0_4_v2_top5.json"
DEFAULT_RESULTS_JSON = ROOT / "results" / "memory_store_eval_results.json"
DEFAULT_RESULTS_MD = ROOT / "results" / "memory_store_eval_results.md"

RISKY_EXPECTED = {"warn", "verify_first", "block"}
PERMISSIVE_ACTIONS = {"answer", "answer_context"}
LEXICAL_STRATEGIES = ["tfidf_text", "tfidf_metadata_text", "bm25_text", "bm25_metadata_text"]
EMBEDDING_STRATEGIES = ["nomic_embed_text", "nomic_embed_metadata_text"]

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text:latest")


@dataclass
class MemoryStoreDecision:
    strategy: str
    scenario_id: str
    expected_action: str
    selected_memory_id: str
    selected_role: str
    selected_trap: str
    selected_score: float
    action: str
    action_correct: bool
    target_selected: bool
    trap_failure: bool
    false_certainty_error: bool
    downgrade_miss: bool
    overblocking_error: bool
    dangerous_overcaution: bool
    soft_overcaution: bool
    failure_cost: str
    discriminating_signal: str
    rationale: str


def memory_text(memory: dict[str, Any], strategy: str) -> str:
    base = memory.get("text", "")
    if strategy.endswith("_text") and "metadata" not in strategy:
        return base

    parts = [
        memory.get("id", ""),
        memory.get("role", ""),
        memory.get("distractor_trap", ""),
        memory.get("memory_type", ""),
        memory.get("status", ""),
        memory.get("priority", ""),
        memory.get("epistemic_status", ""),
        memory.get("allowed_action_hint", ""),
        str(memory.get("recency_rank", "")),
        *memory.get("retrieval_terms", []),
        base,
    ]
    return " ".join(str(part) for part in parts if part)


def normalize_memory_store(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    normalized = []
    role_counts: Counter[str] = Counter()
    for index, memory in enumerate(scenario["memory_store"], start=1):
        item = dict(memory)
        role = str(item.get("role", f"memory_{index}"))
        role_counts[role] += 1
        if "id" not in item:
            suffix = role if role_counts[role] == 1 else f"{role}_{role_counts[role]}"
            item["id"] = f"{scenario['id']}::{suffix}"
        normalized.append(item)
    return normalized


def tfidf_scores(query: str, memories: list[dict[str, Any]], strategy: str) -> dict[str, float]:
    docs = {memory["id"]: tokenize(memory_text(memory, strategy)) for memory in memories}
    n_docs = len(docs)
    df: Counter[str] = Counter()
    for tokens in docs.values():
        for token in set(tokens):
            df[token] += 1

    idf = {
        token: math.log((n_docs + 1) / (count + 1)) + 1.0
        for token, count in df.items()
    }
    query_tokens = tokenize(query)
    query_tf = Counter(query_tokens)
    query_total = len(query_tokens) or 1
    query_vector = {
        token: (count / query_total) * idf.get(token, 1.0)
        for token, count in query_tf.items()
    }

    scores: dict[str, float] = {}
    for memory_id, tokens in docs.items():
        tf = Counter(tokens)
        total = len(tokens) or 1
        vector = {
            token: (count / total) * idf[token]
            for token, count in tf.items()
        }
        dot = sum(query_vector.get(token, 0.0) * vector.get(token, 0.0) for token in query_vector)
        q_norm = math.sqrt(sum(value * value for value in query_vector.values())) or 1.0
        d_norm = math.sqrt(sum(value * value for value in vector.values())) or 1.0
        scores[memory_id] = dot / (q_norm * d_norm)
    return scores


def bm25_scores(
    query: str,
    memories: list[dict[str, Any]],
    strategy: str,
    k1: float = 1.5,
    b: float = 0.75,
) -> dict[str, float]:
    docs = {memory["id"]: tokenize(memory_text(memory, strategy)) for memory in memories}
    n_docs = len(docs)
    avgdl = sum(len(tokens) for tokens in docs.values()) / max(n_docs, 1)
    df: Counter[str] = Counter()
    for tokens in docs.values():
        for token in set(tokens):
            df[token] += 1

    scores: dict[str, float] = {}
    for memory_id, tokens in docs.items():
        tf = Counter(tokens)
        doc_len = len(tokens)
        score = 0.0
        for term in tokenize(query):
            if tf[term] == 0:
                continue
            idf = math.log(1.0 + (n_docs - df[term] + 0.5) / (df[term] + 0.5))
            denom = tf[term] + k1 * (1.0 - b + b * doc_len / max(avgdl, 1.0))
            score += idf * (tf[term] * (k1 + 1.0)) / denom
        scores[memory_id] = score
    return scores


def ollama_available() -> bool:
    try:
        with urllib.request.urlopen(f"{OLLAMA_BASE_URL.rstrip('/')}/api/tags", timeout=5):
            return True
    except Exception:
        return False


def embed_texts(texts: list[str]) -> list[list[float]]:
    payload = json.dumps({"model": OLLAMA_EMBED_MODEL, "input": texts}).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_BASE_URL.rstrip('/')}/api/embed",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read())
    embeddings = data.get("embeddings")
    if not isinstance(embeddings, list) or len(embeddings) != len(texts):
        raise RuntimeError(f"Unexpected Ollama embedding response: {data}")
    return embeddings


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(x * x for x in v1))
    mag2 = math.sqrt(sum(x * x for x in v2))
    if mag1 == 0.0 or mag2 == 0.0:
        return 0.0
    return dot / (mag1 * mag2)


def embedding_scores(query: str, memories: list[dict[str, Any]], strategy: str) -> dict[str, float]:
    all_texts = [query] + [memory_text(m, strategy) for m in memories]
    all_embeddings = embed_texts(all_texts)
    query_emb = all_embeddings[0]
    return {
        memory["id"]: cosine_similarity(query_emb, emb)
        for memory, emb in zip(memories, all_embeddings[1:])
    }


def retrieve(query: str, memories: list[dict[str, Any]], strategy: str) -> tuple[dict[str, Any], float]:
    if strategy.startswith("tfidf"):
        scores = tfidf_scores(query, memories, strategy)
    elif strategy.startswith("bm25"):
        scores = bm25_scores(query, memories, strategy)
    else:
        scores = embedding_scores(query, memories, strategy)
    memory_by_id = {memory["id"]: memory for memory in memories}
    selected_id = max(scores, key=scores.get)
    return memory_by_id[selected_id], scores[selected_id]


def score_row(strategy: str, scenario: dict[str, Any]) -> MemoryStoreDecision:
    memory_store = normalize_memory_store(scenario)
    selected, score = retrieve(scenario["query"], memory_store, strategy)
    action, rationale = layered_action(selected)
    expected = scenario["expected_action"]
    action_correct = action == expected
    target_selected = selected.get("role") == "target"
    trap_failure = selected.get("distractor_trap") == "should_not_fire"
    false_certainty_error = expected in RISKY_EXPECTED and action in PERMISSIVE_ACTIONS
    downgrade_miss = (
        ACTION_RANK[action] < ACTION_RANK[expected]
        and not false_certainty_error
        and not action_correct
    )
    overblocking_error = (
        ACTION_RANK[action] > ACTION_RANK[expected]
        and not false_certainty_error
    )
    dangerous_overcaution = bool(scenario.get("over_caution_is_the_failure")) and overblocking_error
    soft_overcaution = overblocking_error and not dangerous_overcaution

    return MemoryStoreDecision(
        strategy=strategy,
        scenario_id=scenario["id"],
        expected_action=expected,
        selected_memory_id=selected["id"],
        selected_role=selected.get("role", ""),
        selected_trap=selected.get("distractor_trap", ""),
        selected_score=round(score, 6),
        action=action,
        action_correct=action_correct,
        target_selected=target_selected,
        trap_failure=trap_failure,
        false_certainty_error=false_certainty_error,
        downgrade_miss=downgrade_miss,
        overblocking_error=overblocking_error,
        dangerous_overcaution=dangerous_overcaution,
        soft_overcaution=soft_overcaution,
        failure_cost=scenario.get("failure_cost", ""),
        discriminating_signal=scenario.get("discriminating_signal", ""),
        rationale=rationale,
    )


def summarize(rows: list[MemoryStoreDecision]) -> dict[str, int]:
    return {
        "total": len(rows),
        "target_selected": sum(row.target_selected for row in rows),
        "action_correct": sum(row.action_correct for row in rows),
        "trap_failures": sum(row.trap_failure for row in rows),
        "false_certainty_errors": sum(row.false_certainty_error for row in rows),
        "downgrade_misses": sum(row.downgrade_miss for row in rows),
        "overblocking_errors": sum(row.overblocking_error for row in rows),
        "dangerous_overcaution": sum(row.dangerous_overcaution for row in rows),
        "soft_overcaution": sum(row.soft_overcaution for row in rows),
    }


def output_paths(scenarios_path: Path) -> tuple[Path, Path]:
    if scenarios_path == DEFAULT_SCENARIOS_PATH:
        return DEFAULT_RESULTS_JSON, DEFAULT_RESULTS_MD
    stem = scenarios_path.stem
    return (
        ROOT / "results" / f"{stem}_results.json",
        ROOT / "results" / f"{stem}_results.md",
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run scenario-local memory-store eval.")
    parser.add_argument(
        "--scenarios",
        type=Path,
        default=DEFAULT_SCENARIOS_PATH,
        help="Path to scenario-local memory-store JSON.",
    )
    args = parser.parse_args()

    scenarios_path = args.scenarios
    if not scenarios_path.is_absolute():
        scenarios_path = ROOT / scenarios_path
    results_json, results_md = output_paths(scenarios_path)

    strategies = list(LEXICAL_STRATEGIES)
    if ollama_available():
        strategies += EMBEDDING_STRATEGIES
        print(f"Ollama available — including embedding strategies with {OLLAMA_EMBED_MODEL}")
    else:
        print("Ollama not reachable — skipping embedding strategies.")

    payload = json.loads(scenarios_path.read_text(encoding="utf-8"))
    scenarios = payload["scenarios"]
    rows = [
        score_row(strategy, scenario)
        for strategy in strategies
        for scenario in scenarios
    ]
    by_strategy = {
        strategy: summarize([row for row in rows if row.strategy == strategy])
        for strategy in strategies
    }
    output = {
        "scenario_file": str(scenarios_path.relative_to(ROOT)),
        "status": "fresh-Claude top-5 scenario-local memory-store mini-benchmark",
        "authorship": payload.get("authorship"),
        "strategies": by_strategy,
        "rows": [asdict(row) for row in rows],
    }
    results_json.write_text(json.dumps(output, indent=2), encoding="utf-8")

    md = [
        "# Memory Store Eval Results",
        "",
        "Status: fresh-Claude top-5 scenario-local memory-store mini-benchmark. Not benchmark-grade.",
        "",
        "Scenario-local stores keep this run separate from the original shared-memory pool.",
        "",
        "## Strategy Summary",
        "",
        "| Strategy | Target selected | Action correct | Trap failures | FC errors | Downgrade misses | Overblocking | Dangerous overcaution | Soft overcaution |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for strategy in strategies:
        summary = by_strategy[strategy]
        total = summary["total"]
        md.append(
            f"| {strategy} | {summary['target_selected']}/{total} | "
            f"{summary['action_correct']}/{total} | "
            f"{summary['trap_failures']} | "
            f"{summary['false_certainty_errors']} | "
            f"{summary['downgrade_misses']} | "
            f"{summary['overblocking_errors']} | "
            f"{summary['dangerous_overcaution']} | "
            f"{summary['soft_overcaution']} |"
        )

    md.extend(
        [
            "",
            "## Scenario Rows",
            "",
            "| Strategy | Scenario | Expected | Selected | Role | Trap | Action | Act ok | Trap fail | FC | Downgrade | OB |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        md.append(
            f"| {row.strategy} | {row.scenario_id} | {row.expected_action} | "
            f"{row.selected_memory_id} | {row.selected_role} | {row.selected_trap} | "
            f"{row.action} | {'ok' if row.action_correct else 'miss'} | "
            f"{'yes' if row.trap_failure else 'no'} | "
            f"{'yes' if row.false_certainty_error else 'no'} | "
            f"{'yes' if row.downgrade_miss else 'no'} | "
            f"{'yes' if row.overblocking_error else 'no'} |"
        )

    results_md.write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(by_strategy, indent=2))
    print(f"Wrote {results_md}")
    print(f"Wrote {results_json}")


if __name__ == "__main__":
    main()
