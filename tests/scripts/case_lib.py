"""Shared helpers for case_*.py.

prepare(case_id, files) resolves the fixture root, recreates
tests/.tmp/{case_id}/ empty, copies the requested fixtures into it,
exports CASE_TMP / CASE_ROOT / CASE_ID into os.environ for any child
process the case might spawn, and returns the tmp path.

A missing fixture raises FileNotFoundError so the caller fails cleanly.
"""
from __future__ import annotations
import os
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TMP_ROOT = REPO / "tests" / ".tmp"
FIXTURE_DEFAULT = REPO / "tests" / "fixtures"
PATH_CONFIG = FIXTURE_DEFAULT / ".path-config"


def fixture_root() -> Path:
    if PATH_CONFIG.exists():
        for line in PATH_CONFIG.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                return Path(s)
    return FIXTURE_DEFAULT


def prepare(case_id: str, files: list[str]) -> Path:
    """Set up the per-case tmp dir and copy fixtures.

    Returns the path to tests/.tmp/{case_id}/.
    Side effect: sets CASE_TMP, CASE_ROOT, CASE_ID in os.environ.
    """
    tmp = TMP_ROOT / case_id
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    root = fixture_root()
    for name in files:
        src = root / name
        if not src.exists():
            raise FileNotFoundError(f"missing fixture: {src}")
        dst = tmp / name
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
    os.environ["CASE_ID"] = case_id
    os.environ["CASE_ROOT"] = str(root)
    os.environ["CASE_TMP"] = str(tmp)
    return tmp
