#!/usr/bin/env python3
"""Scan repo files with .claude/security-patterns.json.

This is a lightweight local preflight inspired by Claude Code's security-guidance
pattern layer. It is intentionally deterministic: no model call, no network, no
claim interpretation. It only reports configured substring/regex matches.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATTERNS = ROOT / ".claude" / "security-patterns.json"


@dataclass
class Finding:
    file_path: Path
    rule_name: str
    reminder: str


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def load_patterns(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    patterns = payload.get("patterns", [])
    if not isinstance(patterns, list):
        raise ValueError(f"{path} must contain a top-level patterns list")
    return patterns


def path_matches(path: Path, include: list[str] | None, exclude: list[str] | None) -> bool:
    rel = repo_relative(path)
    include = include or ["**/*"]
    exclude = exclude or []
    return any(glob_match(rel, pattern) for pattern in include) and not any(
        glob_match(rel, pattern) for pattern in exclude
    )


def glob_match(rel: str, pattern: str) -> bool:
    """fnmatch with glob-style ``**/``: a leading ``**/`` also matches zero directories.

    Plain fnmatch needs at least one ``/`` for ``**/*.json``, so repo-root JSON
    files were silently excluded from every JSON rule.
    """
    if fnmatch.fnmatch(rel, pattern):
        return True
    return pattern.startswith("**/") and fnmatch.fnmatch(rel, pattern[3:])


def scan_file(path: Path, patterns: list[dict[str, Any]], text: str | None = None) -> list[Finding]:
    """Scan one file. When ``text`` is given it is scanned instead of the on-disk copy."""
    if text is None:
        if not path.exists() or not path.is_file():
            return []
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return []

    findings: list[Finding] = []
    for pattern in patterns:
        if not path_matches(path, pattern.get("paths"), pattern.get("exclude_paths")):
            continue

        matched = False
        for needle in pattern.get("substrings", []) or []:
            if needle in text:
                matched = True
                break

        regex = pattern.get("regex")
        if regex and re.search(regex, text, flags=re.IGNORECASE | re.MULTILINE):
            matched = True

        if matched:
            findings.append(
                Finding(
                    file_path=path,
                    rule_name=str(pattern.get("rule_name", "unnamed_rule")),
                    reminder=str(pattern.get("reminder", "")),
                )
            )
    return findings


def staged_files() -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", "replace").strip() or "git diff failed")
    names = result.stdout.decode("utf-8", "surrogateescape").split("\0")
    return [ROOT / name for name in names if name]


def staged_text(path: Path) -> str | None:
    """Return the staged (index) content of ``path``, or None if it is not UTF-8 text.

    The pre-commit hook must scan what will be committed. Reading the working
    tree instead lets a partially staged file pass (or fail) on content that is
    not part of the commit.
    """
    result = subprocess.run(
        ["git", "show", f":{repo_relative(path)}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", "replace").strip() or "git show failed")
    try:
        return result.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None


# Directories that never hold research artifacts. Walking them makes --all slow
# and can report findings from third-party JSON (virtualenvs, node_modules).
SKIP_DIRS = {".git", ".venv", "venv", "env", "node_modules", "__pycache__", ".ruff_cache", ".pytest_cache"}


def all_candidate_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        rel_parts = path.relative_to(ROOT).parts
        if any(part in SKIP_DIRS for part in rel_parts[:-1]):
            continue
        if path.is_file() and path.suffix in {".json", ".md"}:
            files.append(path)
    return sorted(set(files))


def render_findings(findings: list[Finding]) -> str:
    lines = ["Authority pattern findings:"]
    for finding in findings:
        lines.append(f"- {repo_relative(finding.file_path)} [{finding.rule_name}]")
        if finding.reminder:
            lines.append(f"  {finding.reminder}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan authority research files for configured risk patterns.")
    parser.add_argument("paths", nargs="*", type=Path, help="Optional files to scan.")
    parser.add_argument("--patterns", type=Path, default=DEFAULT_PATTERNS)
    parser.add_argument("--staged", action="store_true", help="Scan staged git files.")
    parser.add_argument("--all", action="store_true", help="Scan all repo markdown/json candidates.")
    parser.add_argument("--warn-only", action="store_true", help="Report findings but exit 0.")
    args = parser.parse_args()

    pattern_path = args.patterns if args.patterns.is_absolute() else ROOT / args.patterns
    patterns = load_patterns(pattern_path)

    if args.staged:
        files = staged_files()
    elif args.all:
        files = all_candidate_files()
    else:
        files = [path if path.is_absolute() else ROOT / path for path in args.paths]

    files = [path for path in files if path.suffix in {".json", ".md"}]
    findings: list[Finding] = []
    for path in files:
        if args.staged:
            text = staged_text(path)
            if text is None:
                continue
            findings.extend(scan_file(path, patterns, text=text))
        else:
            findings.extend(scan_file(path, patterns))

    if findings:
        print(render_findings(findings), file=sys.stderr)
        return 0 if args.warn_only else 1

    print(f"Authority pattern scan clean ({len(files)} files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
