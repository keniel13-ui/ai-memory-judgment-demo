#!/usr/bin/env python3
"""
Sanitized public retrieval-strategy demo.

This compares six deterministic retrieval strategies over six structured
memory files:
  1. TF-IDF over memory content only.
  2. TF-IDF over content plus metadata fields.
  3. TF-IDF over metadata, content, and retrieval_terms.
  4. BM25 over memory content only.
  5. BM25 over content plus metadata fields.
  6. BM25 over metadata, content, and retrieval_terms.

It does not test LLM generation, embeddings, or reranking. It isolates how
retrieval method and retrieval text construction change policy-decision outcomes.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SCENARIOS_PATH = ROOT / "scenarios" / "retrieval_scenarios.json"
RESULTS_MD = ROOT / "results" / "retrieval_eval_results.md"
RESULTS_JSON = ROOT / "results" / "retrieval_eval_results.json"

ACTION_RANK = {
    "archive_only": 0,
    "answer_context": 1,
    "answer": 2,
    "warn": 3,
    "verify_first": 4,
    "block": 5,
}

RISKY_EXPECTED = {"warn", "verify_first", "block"}
PERMISSIVE_ACTIONS = {"answer", "answer_context"}
TEXT_STRATEGIES = ["content_only", "metadata_content", "keyword_expanded"]
RETRIEVAL_STRATEGIES = [
    ("tfidf_content_only", "tfidf", "content_only"),
    ("tfidf_metadata_content", "tfidf", "metadata_content"),
    ("tfidf_keyword_expanded", "tfidf", "keyword_expanded"),
    ("bm25_content_only", "bm25", "content_only"),
    ("bm25_metadata_content", "bm25", "metadata_content"),
    ("bm25_keyword_expanded", "bm25", "keyword_expanded"),
]


@dataclass
class StrategyDecision:
    strategy: str
    scenario_id: str
    expected_action: str
    correct_memory_id: str
    retrieved_id: str
    retrieved_score: float
    retrieval_correct: bool
    action: str
    rationale: str
    action_correct: bool
    end_to_end_correct: bool
    benign_retrieval_miss: bool
    false_certainty_error: bool
    downgrade_miss: bool
    overblocking_error: bool


def extract_json_blocks(text: str) -> list[dict[str, Any]]:
    blocks = re.findall(r"```json\n(.*?)\n```", text, flags=re.DOTALL)
    items: list[dict[str, Any]] = []
    for block in blocks:
        loaded = json.loads(block)
        if isinstance(loaded, list):
            items.extend(loaded)
        else:
            items.append(loaded)
    return items


def load_all_memories() -> dict[str, dict[str, Any]]:
    memories: dict[str, dict[str, Any]] = {}
    for path in sorted(ROOT.glob("0*_*.md")):
        for item in extract_json_blocks(path.read_text(encoding="utf-8")):
            item["_file"] = path.name
            memories[item["id"]] = item
    return memories


def load_scenarios() -> list[dict[str, Any]]:
    return json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))


def tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-z0-9]+\b", text.lower())


def text_for_memory(mem_id: str, mem: dict[str, Any], strategy: str) -> str:
    if strategy == "content_only":
        return mem.get("content", "")

    metadata_parts = [
        mem_id.replace("_", " "),
        mem.get("memory_type", ""),
        mem.get("status", ""),
        mem.get("priority", ""),
        mem.get("epistemic_status", ""),
        mem.get("source", ""),
        mem.get("_file", ""),
        mem.get("content", ""),
    ]

    if strategy == "metadata_content":
        return " ".join(str(p) for p in metadata_parts if p)

    if strategy == "keyword_expanded":
        terms = mem.get("retrieval_terms", [])
        return " ".join(str(p) for p in [*metadata_parts, *terms] if p)

    raise ValueError(f"unknown strategy: {strategy}")


def build_tfidf_index(
    memories: dict[str, dict[str, Any]],
    strategy: str,
) -> tuple[dict[str, dict[str, float]], dict[str, float]]:
    documents = {
        mem_id: tokenize(text_for_memory(mem_id, mem, strategy))
        for mem_id, mem in memories.items()
    }

    n_docs = len(documents)
    df: Counter[str] = Counter()
    for tokens in documents.values():
        for token in set(tokens):
            df[token] += 1

    idf = {
        token: math.log((n_docs + 1) / (count + 1)) + 1.0
        for token, count in df.items()
    }

    vectors: dict[str, dict[str, float]] = {}
    for mem_id, tokens in documents.items():
        tf = Counter(tokens)
        total = len(tokens) or 1
        vectors[mem_id] = {
            token: (count / total) * idf[token]
            for token, count in tf.items()
        }

    return vectors, idf


def build_token_index(
    memories: dict[str, dict[str, Any]],
    strategy: str,
) -> dict[str, list[str]]:
    return {
        mem_id: tokenize(text_for_memory(mem_id, mem, strategy))
        for mem_id, mem in memories.items()
    }


def vectorize_query(query: str, idf: dict[str, float]) -> dict[str, float]:
    tokens = tokenize(query)
    tf = Counter(tokens)
    total = len(tokens) or 1
    return {
        token: (count / total) * idf.get(token, 1.0)
        for token, count in tf.items()
    }


def cosine_similarity(v1: dict[str, float], v2: dict[str, float]) -> float:
    keys = set(v1) & set(v2)
    dot = sum(v1[key] * v2[key] for key in keys)
    mag1 = math.sqrt(sum(value * value for value in v1.values()))
    mag2 = math.sqrt(sum(value * value for value in v2.values()))
    if mag1 == 0.0 or mag2 == 0.0:
        return 0.0
    return dot / (mag1 * mag2)


def retrieve_top1(
    query: str,
    vectors: dict[str, dict[str, float]],
    idf: dict[str, float],
) -> tuple[str, float]:
    query_vec = vectorize_query(query, idf)
    scores = {
        mem_id: cosine_similarity(query_vec, vector)
        for mem_id, vector in vectors.items()
    }
    top_id = max(scores, key=scores.get)
    return top_id, scores[top_id]


def retrieve_top1_bm25(
    query: str,
    documents: dict[str, list[str]],
    k1: float = 1.5,
    b: float = 0.75,
) -> tuple[str, float]:
    query_terms = tokenize(query)
    n_docs = len(documents)
    avgdl = sum(len(tokens) for tokens in documents.values()) / max(n_docs, 1)

    df: Counter[str] = Counter()
    for tokens in documents.values():
        for token in set(tokens):
            df[token] += 1

    scores: dict[str, float] = {}
    for mem_id, tokens in documents.items():
        tf = Counter(tokens)
        doc_len = len(tokens)
        score = 0.0
        for term in query_terms:
            if tf[term] == 0:
                continue
            idf = math.log(1.0 + (n_docs - df[term] + 0.5) / (df[term] + 0.5))
            denom = tf[term] + k1 * (1.0 - b + b * doc_len / max(avgdl, 1.0))
            score += idf * (tf[term] * (k1 + 1.0)) / denom
        scores[mem_id] = score

    top_id = max(scores, key=scores.get)
    return top_id, scores[top_id]


def layered_action(memory: dict[str, Any]) -> tuple[str, str]:
    if memory.get("status") in {"superseded", "archived"}:
        return "archive_only", f"{memory['id']} is {memory.get('status')}"

    if memory.get("memory_type") == "correction" and memory.get("status") == "active":
        hint = memory.get("allowed_action_hint")
        if hint in {"block", "warn"}:
            return hint, f"active correction uses {hint}"
        return "block", "active correction blocks repeating known failure"

    if memory.get("verification_required"):
        return "verify_first", "verification_required gate"

    if memory.get("epistemic_status") in {"unresolved", "contested"}:
        return "warn", f"{memory.get('epistemic_status')} gate"

    if int(memory.get("contradiction_count", 0)) >= 2:
        return "verify_first", "contradiction_count gate"

    hint = memory.get("allowed_action_hint", "answer")
    return hint, f"settled memory hint: {hint}"


def score_decision(
    strategy: str,
    scenario: dict[str, Any],
    retrieved_id: str,
    retrieved_score: float,
    action: str,
    rationale: str,
) -> StrategyDecision:
    expected_action = scenario["expected_action"]
    correct_memory_id = scenario["correct_memory_id"]
    retrieval_correct = retrieved_id == correct_memory_id
    action_correct = action == expected_action
    benign_retrieval_miss = not retrieval_correct and action_correct
    false_certainty_error = (
        expected_action in RISKY_EXPECTED and action in PERMISSIVE_ACTIONS
    )
    downgrade_miss = (
        not retrieval_correct
        and not false_certainty_error
        and ACTION_RANK[action] < ACTION_RANK[expected_action]
    )
    overblocking_error = (
        ACTION_RANK[action] > ACTION_RANK[expected_action]
        and not false_certainty_error
    )

    return StrategyDecision(
        strategy=strategy,
        scenario_id=scenario["id"],
        expected_action=expected_action,
        correct_memory_id=correct_memory_id,
        retrieved_id=retrieved_id,
        retrieved_score=round(retrieved_score, 6),
        retrieval_correct=retrieval_correct,
        action=action,
        rationale=rationale,
        action_correct=action_correct,
        end_to_end_correct=retrieval_correct and action_correct,
        benign_retrieval_miss=benign_retrieval_miss,
        false_certainty_error=false_certainty_error,
        downgrade_miss=downgrade_miss,
        overblocking_error=overblocking_error,
    )


def summarize(decisions: list[StrategyDecision]) -> dict[str, Any]:
    total = len(decisions)
    return {
        "total": total,
        "retrieval_correct": sum(d.retrieval_correct for d in decisions),
        "action_correct": sum(d.action_correct for d in decisions),
        "end_to_end_correct": sum(d.end_to_end_correct for d in decisions),
        "benign_retrieval_misses": sum(d.benign_retrieval_miss for d in decisions),
        "downgrade_misses": sum(d.downgrade_miss for d in decisions),
        "false_certainty_errors": sum(d.false_certainty_error for d in decisions),
        "overblocking_errors": sum(d.overblocking_error for d in decisions),
    }


def main() -> None:
    memories = load_all_memories()
    scenarios = load_scenarios()
    rows: list[StrategyDecision] = []

    for strategy_name, retrieval_method, text_strategy in RETRIEVAL_STRATEGIES:
        if retrieval_method == "tfidf":
            vectors, idf = build_tfidf_index(memories, text_strategy)
        else:
            documents = build_token_index(memories, text_strategy)

        for scenario in scenarios:
            if retrieval_method == "tfidf":
                retrieved_id, retrieved_score = retrieve_top1(
                    scenario["query"],
                    vectors,
                    idf,
                )
            else:
                retrieved_id, retrieved_score = retrieve_top1_bm25(
                    scenario["query"],
                    documents,
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

    by_strategy = {
        strategy_name: summarize([row for row in rows if row.strategy == strategy_name])
        for strategy_name, _, _ in RETRIEVAL_STRATEGIES
    }

    output = {
        "claim": "Sanitized demo comparing deterministic retrieval text-construction strategies and action-class consequences.",
        "not_claimed": [
            "embedding retrieval performance",
            "LLM generation quality",
            "external validation",
            "generalization beyond this small scenario set",
        ],
        "strategies": by_strategy,
        "rows": [asdict(row) for row in rows],
    }
    RESULTS_JSON.write_text(json.dumps(output, indent=2), encoding="utf-8")

    md = [
        "# Retrieval Eval Results",
        "",
        "Status: sanitized deterministic retrieval-strategy demo. Not benchmark-grade.",
        "",
        f"Memory pool: {len(memories)} memories across 6 files.",
        "",
        "## Strategy Summary",
        "",
        "| Strategy | Retrieval | Action correct | End-to-end | Benign misses | Downgrade misses | FC errors | Overblocking |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for strategy, _, _ in RETRIEVAL_STRATEGIES:
        summary = by_strategy[strategy]
        total = summary["total"]
        md.append(
            f"| {strategy} | {summary['retrieval_correct']}/{total} | "
            f"{summary['action_correct']}/{total} | {summary['end_to_end_correct']}/{total} | "
            f"{summary['benign_retrieval_misses']} | {summary['downgrade_misses']} | "
            f"{summary['false_certainty_errors']} | {summary['overblocking_errors']} |"
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
            "## Strategy Definitions",
            "",
            "- `tfidf_content_only`: TF-IDF over only the memory `content` field.",
            "- `tfidf_metadata_content`: TF-IDF over content plus ID, memory type, status fields, source, and file.",
            "- `tfidf_keyword_expanded`: TF-IDF over metadata+content plus `retrieval_terms` semantic identifiers.",
            "- `bm25_content_only`: BM25 over only the memory `content` field.",
            "- `bm25_metadata_content`: BM25 over content plus ID, memory type, status fields, source, and file.",
            "- `bm25_keyword_expanded`: BM25 over metadata+content plus `retrieval_terms` semantic identifiers.",
            "",
            "## Limitations",
            "",
            "- Deterministic lexical retrieval only; no embeddings, hybrid retrieval, or reranking.",
            "- Scenario set is small and still designed by the framework author.",
            "- No free-form LLM generation is scored.",
            "- Retrieval and memory-object design are entangled.",
            "- External scenarios and stronger baselines are needed before stronger claims.",
            "",
        ]
    )
    RESULTS_MD.write_text("\n".join(md), encoding="utf-8")

    print(json.dumps(by_strategy, indent=2))
    print(f"Wrote {RESULTS_MD}")
    print(f"Wrote {RESULTS_JSON}")


if __name__ == "__main__":
    main()
