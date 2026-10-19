"""Regression tests for scripts/append_eval_log.py.

Failure modes covered:
- verify crashed with a JSONDecodeError traceback on a truncated or hand-edited
  line instead of reporting chain_ok=False;
- append silently chained a new event onto a log that no longer verified, which
  buries the break under a fresh, valid-looking tail.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _helpers import ROOT, load_module

eval_log = load_module("scripts/append_eval_log.py", "append_eval_log")
SCRIPT = ROOT / "scripts" / "append_eval_log.py"


def append_args(log: Path, result: Path) -> argparse.Namespace:
    return argparse.Namespace(
        log=str(log),
        result=str(result),
        scenario=[],
        evaluator=[],
        file=[],
        claim="CLAIM-TEST",
        label="unit",
        evidence_level="internal",
        summary="",
    )


class EvalLogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.log = self.dir / "log.jsonl"
        self.result = self.dir / "result.json"
        self.result.write_text('{"ok": true}\n', encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_committed_log_verifies(self) -> None:
        ok, messages = eval_log.verify_log(ROOT / "results" / "evaluation_log.jsonl")
        self.assertTrue(ok, messages)

    def test_append_then_verify_chains_from_genesis(self) -> None:
        first = eval_log.append_event(append_args(self.log, self.result))
        second = eval_log.append_event(append_args(self.log, self.result))
        self.assertEqual(first["previous_event_hash"], "GENESIS")
        self.assertEqual(second["previous_event_hash"], first["event_hash"])
        ok, messages = eval_log.verify_log(self.log)
        self.assertTrue(ok, messages)
        self.assertIn("events_checked=2", messages)

    def test_edited_event_is_detected(self) -> None:
        eval_log.append_event(append_args(self.log, self.result))
        event = json.loads(self.log.read_text(encoding="utf-8"))
        event["summary"] = "rewritten after the fact"
        self.log.write_text(json.dumps(event) + "\n", encoding="utf-8")
        ok, messages = eval_log.verify_log(self.log)
        self.assertFalse(ok)
        self.assertTrue(any("hash mismatch" in m for m in messages), messages)

    def test_malformed_line_reports_instead_of_crashing(self) -> None:
        eval_log.append_event(append_args(self.log, self.result))
        with self.log.open("a", encoding="utf-8") as handle:
            handle.write('{"truncated": \n')
        ok, messages = eval_log.verify_log(self.log)
        self.assertFalse(ok)
        self.assertTrue(any("not valid JSON" in m for m in messages), messages)

    def test_missing_event_hash_is_reported(self) -> None:
        eval_log.append_event(append_args(self.log, self.result))
        event = json.loads(self.log.read_text(encoding="utf-8"))
        del event["event_hash"]
        self.log.write_text(json.dumps(event) + "\n", encoding="utf-8")
        ok, messages = eval_log.verify_log(self.log)
        self.assertFalse(ok)
        self.assertTrue(any("missing event_hash" in m for m in messages), messages)

    def test_append_refuses_broken_chain(self) -> None:
        eval_log.append_event(append_args(self.log, self.result))
        event = json.loads(self.log.read_text(encoding="utf-8"))
        event["claim_id"] = "CLAIM-EDITED"
        self.log.write_text(json.dumps(event) + "\n", encoding="utf-8")
        before = self.log.read_bytes()
        with self.assertRaises(eval_log.BrokenChainError):
            eval_log.append_event(append_args(self.log, self.result))
        self.assertEqual(self.log.read_bytes(), before, "log must not change when append is refused")

    def test_cli_append_on_broken_log_exits_nonzero(self) -> None:
        self.log.write_text("not json\n", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "append", "--claim", "C", "--label", "L",
             "--result", str(self.result), "--log", str(self.log)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("refusing to append", proc.stderr)

    def test_check_files_reports_changed_artifact(self) -> None:
        eval_log.append_event(append_args(self.log, self.result))
        self.assertEqual(eval_log.file_drift(self.log), [])
        self.result.write_text('{"ok": false}\n', encoding="utf-8")
        drift = eval_log.file_drift(self.log)
        self.assertEqual(len(drift), 1)
        self.assertTrue(drift[0].startswith("file_changed"), drift)


if __name__ == "__main__":
    unittest.main()
