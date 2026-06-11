#!/usr/bin/env python3
"""
Append-only evaluation log for Self-Correcting Systems research runs.

The log is intentionally simple JSONL:
- each event includes hashes of the result artifact and optional input/code files
- each event includes the previous event hash
- each event hash is computed over the canonical event body

This does not change any evaluator outcome. It records completed runs in a
tamper-evident chain that can be independently verified later.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG = ROOT / "results" / "evaluation_log.jsonl"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def file_record(path: Path) -> dict:
    resolved = path.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return {
        "path": rel_path(resolved),
        "sha256": sha256_file(resolved),
        "bytes": resolved.stat().st_size,
    }


def load_events(log_path: Path) -> list[dict]:
    if not log_path.exists():
        return []
    events = []
    for line_number, line in enumerate(log_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        event = json.loads(line)
        event["_line_number"] = line_number
        events.append(event)
    return events


def compute_event_hash(event_body: dict) -> str:
    return sha256_bytes(canonical_json(event_body))


def strip_runtime_keys(event: dict) -> dict:
    return {key: value for key, value in event.items() if key not in {"event_hash", "_line_number"}}


def previous_hash(log_path: Path) -> str:
    events = load_events(log_path)
    if not events:
        return "GENESIS"
    last = events[-1]
    return last["event_hash"]


def append_event(args: argparse.Namespace) -> dict:
    log_path = Path(args.log).resolve()
    result_file = Path(args.result).resolve()
    scenario_files = [Path(item).resolve() for item in args.scenario or []]
    evaluator_files = [Path(item).resolve() for item in args.evaluator or []]
    extra_files = [Path(item).resolve() for item in args.file or []]

    event_body = {
        "schema": "self-correcting-systems.eval-log.v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "claim_id": args.claim,
        "run_label": args.label,
        "evidence_level": args.evidence_level,
        "summary": args.summary,
        "previous_event_hash": previous_hash(log_path),
        "result": file_record(result_file),
        "scenario_files": [file_record(path) for path in scenario_files],
        "evaluator_files": [file_record(path) for path in evaluator_files],
        "extra_files": [file_record(path) for path in extra_files],
    }
    event_hash = compute_event_hash(event_body)
    event = {**event_body, "event_hash": event_hash}

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n")
    return event


def verify_log(log_path: Path) -> tuple[bool, list[str]]:
    events = load_events(log_path)
    messages = []
    previous = "GENESIS"
    ok = True

    for index, event in enumerate(events, start=1):
        event_body = strip_runtime_keys(event)
        expected_hash = compute_event_hash(event_body)
        if event.get("event_hash") != expected_hash:
            ok = False
            messages.append(f"line {event.get('_line_number', index)} hash mismatch")
        if event_body.get("previous_event_hash") != previous:
            ok = False
            messages.append(f"line {event.get('_line_number', index)} previous hash mismatch")
        previous = event.get("event_hash")

    messages.append(f"events_checked={len(events)}")
    return ok, messages


def main() -> int:
    parser = argparse.ArgumentParser(description="Append or verify the evaluation log.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    append_parser = subparsers.add_parser("append", help="Append one completed evaluation event.")
    append_parser.add_argument("--claim", required=True, help="Claim id, e.g. CLAIM-29.")
    append_parser.add_argument("--label", required=True, help="Short run label.")
    append_parser.add_argument("--result", required=True, help="Result artifact to hash.")
    append_parser.add_argument("--scenario", action="append", help="Scenario/input file to hash. Repeatable.")
    append_parser.add_argument("--evaluator", action="append", help="Evaluator/code file to hash. Repeatable.")
    append_parser.add_argument("--file", action="append", help="Additional file to hash. Repeatable.")
    append_parser.add_argument("--summary", default="", help="Human-readable summary.")
    append_parser.add_argument("--evidence-level", default="internal", help="Evidence level label.")
    append_parser.add_argument("--log", default=str(DEFAULT_LOG), help="JSONL log path.")

    verify_parser = subparsers.add_parser("verify", help="Verify event hashes and previous-hash chain.")
    verify_parser.add_argument("--log", default=str(DEFAULT_LOG), help="JSONL log path.")

    args = parser.parse_args()
    if args.command == "append":
        event = append_event(args)
        print(f"appended_event_hash={event['event_hash']}")
        print(f"log={Path(args.log).resolve()}")
        return 0

    ok, messages = verify_log(Path(args.log).resolve())
    for message in messages:
        print(message)
    print(f"chain_ok={ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
