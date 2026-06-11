"""
Run CLAIM-24 through RederivationGate using a live FIPSign CA SourceAdapter.

This script expects a scenario file whose grants contain source_snapshot values
already normalized with fipsign_source_adapter.normalize_pqcert, or at minimum
source_snapshot.cert_id values that identify live CA certificates.

It writes result artifacts only after a real external read is attempted.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import evaluator
from fipsign_source_adapter import FIPSignSourceAdapter
from rederivation_gate import RederivationGate


DEFAULT_OPERATION_TIME = datetime(2026, 6, 5, 12, 0, tzinfo=timezone.utc)
RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"


def parse_time(value: str | None) -> datetime:
    if not value:
        return DEFAULT_OPERATION_TIME
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def write_results(results: list, base_url: str, operation_time: datetime, label: str) -> tuple[Path, Path]:
    RESULTS_DIR.mkdir(exist_ok=True)
    safe_label = label.lower().replace(" ", "_")
    json_path = RESULTS_DIR / f"claim24_fipsign_{safe_label}_results.json"
    md_path = RESULTS_DIR / f"claim24_fipsign_{safe_label}_results.md"

    payload = {
        "claim": "CLAIM-24",
        "evidence_tier": "real-external-source candidate",
        "source_adapter": "FIPSignSourceAdapter",
        "base_url": base_url,
        "operation_time": operation_time.isoformat(),
        "results": results,
    }
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    all_pass = all(row["passed"] for row in results)
    lines = [
        "# CLAIM-24 FIPSign Live SourceAdapter Results",
        "",
        f"- Evidence tier: real-external-source candidate",
        f"- Source adapter: `FIPSignSourceAdapter`",
        f"- Base URL: `{base_url}`",
        f"- Operation time: `{operation_time.isoformat()}`",
        f"- All scenarios passed: `{all_pass}`",
        "",
        "| ID | Expected | Got | Pass | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in results:
        lines.append(
            f"| {row['scenario_id']} | {row['expected']} | {row['got']} | {row['passed']} | {row['notes']} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CLAIM-24 against a live FIPSign CA source.")
    parser.add_argument("--base-url", required=True, help="FIPSign CA base URL, without endpoint path.")
    parser.add_argument("--scenarios", help="Optional CLAIM-24 scenario file with live FIPSign cert IDs/snapshots.")
    parser.add_argument("--operation-time", help="ISO timestamp for deterministic TTL evaluation.")
    parser.add_argument("--label", default="live", help="Output artifact label.")
    args = parser.parse_args()

    operation_time = parse_time(args.operation_time)
    if args.scenarios:
        evaluator.SCENARIOS_PATH = Path(args.scenarios)

    adapter = FIPSignSourceAdapter(args.base_url)
    gate = RederivationGate(adapter)
    results = evaluator.run(gate, "RederivationGate + FIPSignSourceAdapter", operation_time)
    json_path, md_path = write_results(results, args.base_url, operation_time, args.label)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0 if all(row["passed"] for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
