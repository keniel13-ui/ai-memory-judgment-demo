#!/usr/bin/env python3
"""Bounded CLI for the frozen FIPSign Mandate Cell 7 run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mandate_cell7 import (
    DEFAULT_KEY_ENV,
    MandateCell7Error,
    capture,
    evaluate,
    load_key_from_env,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="phase", required=True)

    capture_parser = subparsers.add_parser("capture")
    capture_parser.add_argument("--bound-id", required=True)
    capture_parser.add_argument("--run-root", type=Path, required=True)
    capture_parser.add_argument("--run-id")
    capture_parser.add_argument("--api-key-env", default=DEFAULT_KEY_ENV)

    evaluate_parser = subparsers.add_parser("evaluate")
    evaluate_parser.add_argument("--run-dir", type=Path, required=True)
    evaluate_parser.add_argument("--baseline-sha256", required=True)
    evaluate_parser.add_argument("--capture-receipt-sha256", required=True)
    evaluate_parser.add_argument("--api-key-env", default=DEFAULT_KEY_ENV)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.phase == "capture":
            result = capture(
                bound_id=args.bound_id,
                run_root=args.run_root,
                run_id=args.run_id,
                api_key=load_key_from_env(args.api_key_env),
            )
        else:
            # The environment is not read until evaluate() has verified every carry
            # artifact and the four-hour/source-expiry window.
            result = evaluate(
                run_dir=args.run_dir,
                expected_baseline_sha256=args.baseline_sha256,
                expected_capture_receipt_sha256=args.capture_receipt_sha256,
                key_loader=lambda: load_key_from_env(args.api_key_env),
            )
    except MandateCell7Error as exc:
        print(json.dumps({"status": "REFUSED", "code": exc.code}), file=sys.stderr)
        return 2

    print(json.dumps(result.public_dict(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
