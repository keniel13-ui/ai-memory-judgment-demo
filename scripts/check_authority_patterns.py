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
    return any(fnmatch.fnmatch(rel, pattern) for pattern in include) and not any(
        fnmatch.fnmatch(rel, pattern) for pattern in exclude
    )


def scan_file(path: Path, patterns: list[dict[str, Any]]) -> list[Finding]:
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
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff failed")
    return [ROOT / line for line in result.stdout.splitlines() if line.strip()]


def all_candidate_files() -> list[Path]:
    roots = [ROOT / "external_scenarios", ROOT / "results", ROOT]
    files: list[Path] = []
    for base in roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
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
        findings.extend(scan_file(path, patterns))

    if findings:
        print(render_findings(findings), file=sys.stderr)
        return 0 if args.warn_only else 1

    print(f"Authority pattern scan clean ({len(files)} files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
