"""Regression tests for scripts/check_authority_patterns.py.

Failure modes covered:
- --staged scanned the working-tree copy, so a partially staged file was judged
  on content that is not part of the commit;
- --all walked .git and virtualenv/node_modules trees.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _helpers import ROOT, load_module

checker = load_module("scripts/check_authority_patterns.py", "check_authority_patterns")

RISKY = '{"governs": {"any_terms": []}}\n'
CLEAN = '{"governs": {"any_terms": ["vpn"]}}\n'


def git(cwd: Path, *args: str) -> None:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@example.invalid",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@example.invalid",
    }
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, env=env)


class PatternScanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.patterns = checker.load_patterns(ROOT / ".claude" / "security-patterns.json")

    def test_empty_any_terms_rule_fires_on_text(self) -> None:
        target = checker.ROOT / "external_scenarios" / "x.json"
        names = [f.rule_name for f in checker.scan_file(target, self.patterns, text=RISKY)]
        self.assertIn("governs_empty_any_terms", names)
        self.assertEqual(checker.scan_file(target, self.patterns, text=CLEAN), [])

    def test_double_star_matches_repo_root_files(self) -> None:
        # "**/*.json" must cover a JSON file at the repo root, as in glob semantics.
        self.assertTrue(checker.path_matches(checker.ROOT / "packet.json", ["**/*.json"], []))
        self.assertTrue(checker.path_matches(checker.ROOT / "a" / "b.json", ["**/*.json"], []))
        self.assertFalse(checker.path_matches(checker.ROOT / "packet.md", ["**/*.json"], []))

    def test_all_skips_vendor_dirs(self) -> None:
        for path in checker.all_candidate_files():
            rel = path.relative_to(checker.ROOT).parts
            self.assertFalse(set(rel[:-1]) & checker.SKIP_DIRS, path)


class StagedScanTests(unittest.TestCase):
    """Run the real script inside a throwaway git repo."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "scripts").mkdir()
        (self.repo / ".claude").mkdir()
        (self.repo / "scripts" / "check_authority_patterns.py").write_bytes(
            (ROOT / "scripts" / "check_authority_patterns.py").read_bytes()
        )
        (self.repo / ".claude" / "security-patterns.json").write_bytes(
            (ROOT / ".claude" / "security-patterns.json").read_bytes()
        )
        git(self.repo, "init", "-q")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_staged(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "scripts/check_authority_patterns.py", "--staged"],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_staged_scan_reads_index_not_worktree(self) -> None:
        packet = self.repo / "packet.json"
        packet.write_text(RISKY, encoding="utf-8")
        git(self.repo, "add", "packet.json")
        packet.write_text(CLEAN, encoding="utf-8")  # unstaged fix must not hide the staged risk
        proc = self.run_staged()
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("governs_empty_any_terms", proc.stderr)

    def test_staged_clean_content_passes_even_if_worktree_is_risky(self) -> None:
        packet = self.repo / "packet.json"
        packet.write_text(CLEAN, encoding="utf-8")
        git(self.repo, "add", "packet.json")
        packet.write_text(RISKY, encoding="utf-8")
        proc = self.run_staged()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("scan clean (1 files)", proc.stdout)

    def test_staged_path_with_space(self) -> None:
        packet = self.repo / "my packet.json"
        packet.write_text(json.dumps({"governs": {"any_terms": []}}), encoding="utf-8")
        git(self.repo, "add", "my packet.json")
        proc = self.run_staged()
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("my packet.json", proc.stderr)


if __name__ == "__main__":
    unittest.main()
