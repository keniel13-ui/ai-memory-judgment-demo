"""Shared helpers for the stdlib unittest suite (run: python3 -m unittest discover -s tests)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def load_module(relative_path: str, name: str) -> ModuleType:
    """Import a repo script by path without putting the repo root on sys.path."""
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, path
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
