"""Verdict-level checks for the stdout-only gate evaluators (CLAIM-24 to CLAIM-27).

CLAIM-25 and CLAIM-26 recorded their full runs as text under results/. The
Notes column is truncated differently by the current code, so a byte comparison
is not meaningful. Instead every recorded (id, expected, got, pass) row must
appear unchanged in the current run, and the summary lines must match in order.
The current CLAIM-25 code prints one extra row (10, A2-overlap) that postdates
the recorded run; extra rows are allowed, changed or missing ones are not.
"""

from __future__ import annotations

import re
import subprocess
import sys
import unittest

from _helpers import ROOT

ROW = re.compile(r"^(\d+)\s+(?:\S+\s+)?([A-Z_]+)\s+([A-Z_]+)\s+(PASS|FAIL)\b")
SUMMARY = re.compile(r"^(All passed: (?:True|False)|Result: \d+/\d+ passed)$")


def verdicts(text: str) -> tuple[list[tuple[str, ...]], list[str]]:
    """Return (rows, summary lines). Row ids repeat across sections, so keep order."""
    rows: list[tuple[str, ...]] = []
    summaries: list[str] = []
    for line in text.splitlines():
        line = line.rstrip()
        row = ROW.match(line)
        if row:
            rows.append(row.groups())
        elif SUMMARY.match(line):
            summaries.append(line)
    return rows, summaries


def is_subsequence(needle: list, haystack: list) -> bool:
    it = iter(haystack)
    return all(item in it for item in needle)


def run(claim_dir: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT / claim_dir,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


class ClaimVerdictTests(unittest.TestCase):
    def assert_matches_recorded(self, claim_dir: str, script: str, recorded: str) -> None:
        proc = run(claim_dir, script, "full")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        recorded_rows, recorded_summaries = verdicts((ROOT / "results" / recorded).read_text(encoding="utf-8"))
        current_rows, current_summaries = verdicts(proc.stdout)
        self.assertGreater(len(recorded_rows), 5, "recorded run parsed to almost nothing")
        self.assertTrue(
            is_subsequence(recorded_rows, current_rows),
            f"recorded verdict rows changed or disappeared:\nrecorded={recorded_rows}\ncurrent={current_rows}",
        )
        self.assertEqual(current_summaries, recorded_summaries)

    def test_claim25_full_run_matches_recorded_verdicts(self) -> None:
        self.assert_matches_recorded("claim_25", "evaluator.py", "claim25_full_run_2026-06-06.txt")

    def test_claim26_full_run_matches_recorded_verdicts(self) -> None:
        self.assert_matches_recorded("claim_26", "evaluator.py", "claim26_full_run_2026-06-06.txt")

    def test_claim27_scope_soundness_outcome(self) -> None:
        proc = run("claim_27", "scope_soundness_evaluator.py")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("OUTCOME A: Boundary real and demonstrated.", proc.stdout)

    def test_claim24_timestamp_baseline_still_blocks_divergence_cell(self) -> None:
        # The timestamp-only baseline is expected to miss some scenarios; the
        # load-bearing line is that the divergence cell is not ALLOWed.
        proc = run("claim_24", "evaluator.py", "timestamp")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Divergence cell (scenario 3) result: BLOCK", proc.stdout)
        self.assertNotIn("ARCHITECTURE FAILED", proc.stdout)


if __name__ == "__main__":
    unittest.main()
