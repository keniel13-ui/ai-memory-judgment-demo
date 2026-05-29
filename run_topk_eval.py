#!/usr/bin/env python3
"""
Top-k recall and conservative policy aggregation experiment.

Question: For the s02 downgrade miss, does the correct memory
(correction_no_overclaim_eval, block) appear in top-2, top-3, or top-5
results, even when it is not retrieved at top-1?

If yes: conservative policy aggregation (take the most restrictive action
across all top-k retrieved memories) would fix the downgrade miss without
requiring better retrieval accuracy.

Runs all 6 lexical strategies. Embedding strategies not included here
because they require the ollama server; nomic-embed results documented
separately.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SCENARIOS_PATH = ROOT / "scenarios" / "retrieval_scenarios.json"
RESULTS_DIR = ROOT / "results"
RESULTS_MD = RESULTS_DIR / "topk_eval_results.md"
RESULTS_JSON = RESULTS_DIR / "topk_eval_results.json"

K_VALUES = [1, 2, 3, 5]

ACTION_RANK = {
    "archive_only": 0,
    "answer_context": 1,
    "answer": 2,
    "warn": 3,
    "verify_first": 4,
    "block": 5,
}

RETRIEVAL_STRATEGIES = [
    ("tfidf_content_only", "tfidf", "content_only"),
    ("tfidf_metadata_content", "tfidf", "metadata_content"),
    ("tfidf_keyword_expanded", "tfidf", "keyword_expanded"),
    ("bm25_content_only", "bm25", "content_only"),
    ("bm25_metadata_content", "bm25", "metadata_content"),
    ("bm25_keyword_expanded", "bm25", "keyword_expanded"),
]


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
    mag1 = math.sqrt(sum(v * v for v in v1.values()))
    mag2 = math.sqrt(sum(v * v for v in v2.values()))
    if mag1 == 0.0 or mag2 == 0.0:
        return 0.0
    return dot / (mag1 * mag2)


def retrieve_topk_tfidf(
    query: str,
    vectors: dict[str, dict[str, float]],
    idf: dict[str, float],
    k: int,
) -> list[tuple[str, float]]:
    query_vec = vectorize_query(query, idf)
    scores = {
        mem_id: cosine_similarity(query_vec, vector)
        for mem_id, vector in vectors.items()
    }
    sorted_ids = sorted(scores, key=scores.get, reverse=True)
    return [(mid, scores[mid]) for mid in sorted_ids[:k]]


def retrieve_topk_bm25(
    query: str,
    documents: dict[str, list[str]],
    k: int,
    k1: float = 1.5,
    b: float = 0.75,
) -> list[tuple[str, float]]:
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
            idf_val = math.log(1.0 + (n_docs - df[term] + 0.5) / (df[term] + 0.5))
            denom = tf[term] + k1 * (1.0 - b + b * doc_len / max(avgdl, 1.0))
            score += idf_val * (tf[term] * (k1 + 1.0)) / denom
        scores[mem_id] = score

    sorted_ids = sorted(scores, key=scores.get, reverse=True)
    return [(mid, scores[mid]) for mid in sorted_ids[:k]]


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


def conservative_action(
    top_k_ids: list[tuple[str, float]],
    memories: dict[str, dict[str, Any]],
) -> tuple[str, str]:
    """Take the most restrictive action across all top-k retrieved memories."""
    best_action = "answer"
    best_rank = ACTION_RANK["answer"]
    sources = []
    for mem_id, _ in top_k_ids:
        action, rationale = layered_action(memories[mem_id])
        rank = ACTION_RANK.get(action, 0)
        sources.append(f"{mem_id}→{action}")
        if rank > best_rank:
            best_rank = rank
            best_action = action
    return best_action, f"conservative aggregation: {', '.join(sources)}"


def main() -> None:
    memories = load_all_memories()
    scenarios = load_scenarios()

    # --- Top-k recall by strategy and k ---
    recall_results: dict[str, dict[str, Any]] = {}

    for strategy_name, retrieval_method, text_strategy in RETRIEVAL_STRATEGIES:
        if retrieval_method == "tfidf":
            vectors, idf = build_tfidf_index(memories, text_strategy)
        else:
            documents = build_token_index(memories, text_strategy)

        strategy_data: dict[str, Any] = {"scenarios": {}}

        for scenario in scenarios:
            sid = scenario["id"]
            correct_id = scenario["correct_memory_id"]
            expected_action = scenario["expected_action"]
            query = scenario["query"]

            max_k = max(K_VALUES)
            if retrieval_method == "tfidf":
                topk = retrieve_topk_tfidf(query, vectors, idf, max_k)
            else:
                topk = retrieve_topk_bm25(query, documents, max_k)

            ranked_ids = [mid for mid, _ in topk]
            recall_at_k = {k: correct_id in ranked_ids[:k] for k in K_VALUES}

            # Conservative aggregation at each k
            conservative_at_k: dict[int, dict[str, Any]] = {}
            for k in K_VALUES:
                c_action, c_rationale = conservative_action(topk[:k], memories)
                conservative_at_k[k] = {
                    "action": c_action,
                    "correct": c_action == expected_action,
                    "rationale": c_rationale,
                }

            strategy_data["scenarios"][sid] = {
                "query": query,
                "expected_action": expected_action,
                "correct_memory_id": correct_id,
                "top5_ranked": [
                    {"rank": i + 1, "id": mid, "score": round(score, 6)}
                    for i, (mid, score) in enumerate(topk)
                ],
                "recall_at_k": recall_at_k,
                "conservative_at_k": {str(k): v for k, v in conservative_at_k.items()},
            }

        recall_results[strategy_name] = strategy_data

    # --- Write JSON ---
    output = {
        "experiment": "top-k recall and conservative policy aggregation",
        "question": (
            "For the s02 downgrade miss, does the correct memory appear in top-k, "
            "and does conservative aggregation fix the downgrade miss?"
        ),
        "k_values_tested": K_VALUES,
        "strategies": recall_results,
    }
    RESULTS_JSON.write_text(json.dumps(output, indent=2), encoding="utf-8")

    # --- Write Markdown ---
    md = [
        "# Top-k Recall and Conservative Policy Aggregation Results",
        "",
        "**Experiment question:** For the s02 downgrade miss, does `correction_no_overclaim_eval`",
        "(the `block`-level correction) appear in top-2, top-3, or top-5 results?",
        "If yes: does conservative policy aggregation (take the most restrictive action",
        "across all top-k retrieved memories) fix the downgrade miss?",
        "",
        f"Memory pool: {len(memories)} memories. Scenarios: {len(scenarios)}.",
        "",
        "---",
        "",
        "## s02 Deep Dive",
        "",
        "s02 is the only case where top-1 retrieval misses the correct memory across all",
        "6 lexical strategies. All strategies retrieve `correction_strawman_baseline` (warn)",
        "instead of `correction_no_overclaim_eval` (block).",
        "",
        "| Strategy | Rank 1 | Rank 2 | Rank 3 | Rank 4 | Rank 5 | In top-3? | In top-5? |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for strategy_name, _, _ in RETRIEVAL_STRATEGIES:
        s02_data = recall_results[strategy_name]["scenarios"].get("s02_overclaim_eval_results")
        if not s02_data:
            continue
        top5 = s02_data["top5_ranked"]
        ranked_ids = [r["id"] for r in top5]
        correct_id = s02_data["correct_memory_id"]
        # Truncate IDs for display
        short = [rid.replace("correction_", "corr_").replace("_eval", "") for rid in ranked_ids]
        in_top3 = correct_id in ranked_ids[:3]
        in_top5 = correct_id in ranked_ids[:5]
        padded = (short + ["—"] * 5)[:5]
        md.append(
            f"| {strategy_name} | {padded[0]} | {padded[1]} | {padded[2]} | {padded[3]} | {padded[4]} "
            f"| {'**yes**' if in_top3 else 'no'} | {'**yes**' if in_top5 else 'no'} |"
        )

    md.extend([
        "",
        "## Conservative Policy Aggregation — s02 Action at Each k",
        "",
        "If we take the most restrictive action across top-k retrieved memories,",
        "does the output change from `warn` to `block` for s02?",
        "",
        "| Strategy | top-1 | top-2 | top-3 | top-5 |",
        "|---|---|---|---|---|",
    ])

    for strategy_name, _, _ in RETRIEVAL_STRATEGIES:
        s02_data = recall_results[strategy_name]["scenarios"].get("s02_overclaim_eval_results")
        if not s02_data:
            continue
        c = s02_data["conservative_at_k"]
        actions = [c[str(k)]["action"] for k in K_VALUES]
        correct_marks = ["**block**" if a == "block" else a for a in actions]
        md.append(f"| {strategy_name} | {' | '.join(correct_marks)} |")

    md.extend([
        "",
        "---",
        "",
        "## Recall@k Summary (All Scenarios)",
        "",
        "How many scenarios have the correct memory in top-k? (out of 10)",
        "",
        "| Strategy | Recall@1 | Recall@2 | Recall@3 | Recall@5 |",
        "|---|---|---|---|---|",
    ])

    for strategy_name, _, _ in RETRIEVAL_STRATEGIES:
        strategy_data = recall_results[strategy_name]
        recall_counts = {k: 0 for k in K_VALUES}
        for sid, sdata in strategy_data["scenarios"].items():
            for k in K_VALUES:
                if sdata["recall_at_k"][k]:
                    recall_counts[k] += 1
        total = len(scenarios)
        row = " | ".join(f"{recall_counts[k]}/{total}" for k in K_VALUES)
        md.append(f"| {strategy_name} | {row} |")

    md.extend([
        "",
        "---",
        "",
        "## Conservative Aggregation — Action Accuracy at Each k",
        "",
        "Using conservative (most restrictive) policy across top-k, how many scenarios",
        "produce the correct action?",
        "",
        "| Strategy | @k=1 | @k=2 | @k=3 | @k=5 |",
        "|---|---|---|---|---|",
    ])

    for strategy_name, _, _ in RETRIEVAL_STRATEGIES:
        strategy_data = recall_results[strategy_name]
        action_counts = {k: 0 for k in K_VALUES}
        for sid, sdata in strategy_data["scenarios"].items():
            for k in K_VALUES:
                if sdata["conservative_at_k"][str(k)]["correct"]:
                    action_counts[k] += 1
        total = len(scenarios)
        row = " | ".join(f"{action_counts[k]}/{total}" for k in K_VALUES)
        md.append(f"| {strategy_name} | {row} |")

    md.extend([
        "",
        "---",
        "",
        "## Interpretation",
        "",
        "- If `correction_no_overclaim_eval` appears in top-k for s02: the failure is a **ranking problem**, not a coverage problem.",
        "  Conservative aggregation can fix the downgrade miss architecturally.",
        "- If it does not appear even in top-5: the failure is a **coverage problem**.",
        "  Lexical retrieval cannot surface the correct memory at any rank.",
        "  Only semantic retrieval (embedding-based) can solve it.",
        "",
        "## Limitations",
        "",
        "- Conservative aggregation increases overblocking risk: taking the most restrictive",
        "  action across top-k will sometimes over-restrict on scenarios where top-1 was already correct.",
        "- The overblocking tradeoff must be measured, not assumed acceptable.",
        "- This experiment is lexical-only. Embedding top-k results are not included here.",
        "",
    ])

    RESULTS_MD.write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(
        {s: {
            "s02_recall": recall_results[s]["scenarios"].get("s02_overclaim_eval_results", {}).get("recall_at_k"),
            "s02_conservative_k3": recall_results[s]["scenarios"].get("s02_overclaim_eval_results", {}).get("conservative_at_k", {}).get("3"),
        } for s, _, _ in RETRIEVAL_STRATEGIES},
        indent=2
    ))
    print(f"\nWrote {RESULTS_MD}")
    print(f"Wrote {RESULTS_JSON}")


if __name__ == "__main__":
    main()
