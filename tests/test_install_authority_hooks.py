"""Regression tests for scripts/install_authority_hooks.sh.

Failure modes covered:
- the installer wrote to $ROOT/.git/hooks, which fails in a linked worktree
  (.git is a file there) and ignores core.hooksPath;
- it silently overwrote any existing pre-commit hook.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from _helpers import ROOT

INSTALLER = ROOT / "scripts" / "install_authority_hooks.sh"
ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
       "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False, env=ENV)


@unittest.skipUnless(shutil.which("git") and shutil.which("sh"), "needs git and sh")
class InstallHookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        (self.repo / "scripts").mkdir(parents=True)
        shutil.copy2(INSTALLER, self.repo / "scripts" / "install_authority_hooks.sh")
        run(["git", "init", "-q"], self.repo)
        run(["git", "add", "."], self.repo)
        run(["git", "commit", "-q", "-m", "init"], self.repo)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def install(self, cwd: Path, *args: str) -> subprocess.CompletedProcess:
        return run(["sh", "scripts/install_authority_hooks.sh", *args], cwd)

    def test_installs_into_hooks_dir(self) -> None:
        proc = self.install(self.repo)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        hook = self.repo / ".git" / "hooks" / "pre-commit"
        self.assertTrue(os.access(hook, os.X_OK))
        self.assertIn("check_authority_patterns.py --staged", hook.read_text())
        # Re-running with an identical hook is a no-op success.
        self.assertEqual(self.install(self.repo).returncode, 0)

    def test_works_in_linked_worktree(self) -> None:
        worktree = Path(self.tmp.name) / "wt"
        self.assertEqual(run(["git", "worktree", "add", "-q", str(worktree)], self.repo).returncode, 0)
        proc = self.install(worktree)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((self.repo / ".git" / "hooks" / "pre-commit").exists())

    def test_does_not_clobber_existing_hook_without_force(self) -> None:
        hook = self.repo / ".git" / "hooks" / "pre-commit"
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text("#!/bin/sh\necho mine\n")
        proc = self.install(self.repo)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(hook.read_text(), "#!/bin/sh\necho mine\n")
        proc = self.install(self.repo, "--force")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual((hook.parent / "pre-commit.bak").read_text(), "#!/bin/sh\necho mine\n")


if __name__ == "__main__":
    unittest.main()
