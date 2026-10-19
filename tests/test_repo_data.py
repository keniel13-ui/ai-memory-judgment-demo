"""Structural checks on the research data that every evaluator depends on."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from _helpers import ROOT, load_module

retrieval = load_module("run_retrieval_eval.py", "run_retrieval_eval")


def tracked(pattern: str) -> list[Path]:
    proc = subprocess.run(["git", "ls-files", "-z", pattern], cwd=ROOT, capture_output=True, check=False)
    if proc.returncode != 0:
        return sorted(ROOT.rglob(pattern.replace("**/", "")))
    return [ROOT / name for name in proc.stdout.decode("utf-8").split("\0") if name]


class RepoDataTests(unittest.TestCase):
    def test_every_json_file_parses(self) -> None:
        files = tracked("*.json")
        self.assertGreater(len(files), 50)
        for path in files:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                json.loads(path.read_text(encoding="utf-8"))

    def test_evaluation_log_chain_verifies(self) -> None:
        proc = subprocess.run(
            [sys.executable, "scripts/append_eval_log.py", "verify"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("chain_ok=True", proc.stdout)

    def test_evaluation_log_paths_exist(self) -> None:
        for line in (ROOT / "results" / "evaluation_log.jsonl").read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            records = [event["result"]] + [
                r for key in ("scenario_files", "evaluator_files", "extra_files") for r in event.get(key, [])
            ]
            for record in records:
                with self.subTest(claim=event["claim_id"], path=record["path"]):
                    self.assertTrue((ROOT / record["path"]).exists())

    def test_memory_layers_load(self) -> None:
        memories = retrieval.load_all_memories()
        # README "Method Snapshot": 21 memory objects across 6 files.
        self.assertEqual(len(memories), 21)
        self.assertEqual(len({m["_file"] for m in memories.values()}), 6)

    def test_retrieval_scenarios_reference_real_memories(self) -> None:
        memories = retrieval.load_all_memories()
        scenarios = retrieval.load_scenarios()
        ids = [s["id"] for s in scenarios]
        self.assertEqual(len(ids), len(set(ids)), "duplicate scenario ids")
        for scenario in scenarios:
            with self.subTest(scenario=scenario["id"]):
                self.assertIn(scenario["correct_memory_id"], memories)
                self.assertIn(scenario["expected_action"], retrieval.ACTION_RANK)


if __name__ == "__main__":
    unittest.main()
