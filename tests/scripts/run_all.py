"""Run every case in sequence and print a PASS/FAIL/SKIP table.

Each case_*.py is self-contained: it calls case_lib.prepare() to set
up tests/.tmp/{id}/ and copy its own fixtures, then runs the encode.
This runner just invokes each script, captures its exit code, and
checks the listed artifacts.

Usage:
    python tests\\scripts\\run_all.py             # run every case
    python tests\\scripts\\run_all.py 11 13 20    # only the listed ids
    python tests\\scripts\\run_all.py --keep      # do not delete passing tmp dirs
"""
from __future__ import annotations
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PY = r"F:\Encode tools\VS-Portable-R65\python.exe"
TMP_ROOT = REPO / "tests" / ".tmp"

CASES = [
    {"id": "00", "script": "case_00_checks.py"},
    {"id": "01", "script": "case_01_checks.py"},
    {"id": "02", "script": "case_02_checks.py"},
    {"id": "03", "script": "case_03_checks.py"},
    {"id": "10", "script": "case_10.py", "artifacts": ["sample.hevc.mkv"]},
    {"id": "11", "script": "case_11.py", "artifacts": ["sample.hevc.mkv"]},
    {"id": "12", "script": "case_12.py", "artifacts": ["sample.hevc.mkv"]},
    {"id": "13", "script": "case_13.py", "artifacts": ["sample.hevc.mkv"]},
    {"id": "14", "script": "case_14.py", "artifacts": ["sample.sc.mp4"]},
    {"id": "15", "script": "case_15.py", "artifacts": ["sample.sc.mp4", "sample.tc.mp4"]},
    {"id": "16", "script": "case_16.py",
     "artifacts": ["sample.hevc.mkv", "sample.sc.mp4", "sample.tc.mp4"]},
    {"id": "17", "script": "case_17.py", "artifacts": ["sample.hevc.mkv"]},
    {"id": "18", "script": "case_18.py", "artifacts": ["sample.sc.mp4"]},
    {"id": "20", "script": "case_20.py",
     "artifacts": ["sample.seg00.hevc.mkv", "sample.seg01.hevc.mkv", "sample.seg02.hevc.mkv"]},
    {"id": "21", "script": "case_21.py",
     "artifacts": ["sample.hevc.mkv", "sample.sc.mp4", "sample.tc.mp4"]},
    {"id": "24", "script": "case_24.py",
     "artifacts": ["sample.seg00.hevc.mkv", "sample.seg01.hevc.mkv", "sample.seg02.hevc.mkv"]},
    {"id": "30", "script": "case_30.py", "artifacts": ["[Test] sample [HEVC].mkv"]},
    {"id": "31", "script": "case_31.py", "artifacts": ["sample.hevc.mkv", "case31.log"]},
    {"id": "33", "script": "case_33.py",
     "artifacts": ["sample.hevc.mkv", "sample.flac", "sample.mute.mp4"]},
    {"id": "34", "script": "case_34.py",
     "artifacts": ["sample.seg00.hevc.mkv", "sample.seg01.hevc.mkv", "sample.seg02.hevc.mkv"]},
    {"id": "40", "script": "case_40_checks.py"},
]


def run_case(case: dict, keep: bool) -> tuple[str, str, int]:
    cid = case["id"]
    script = "tests/scripts/" + case["script"]
    print(f"\n=== Case {cid} ===", flush=True)
    started = time.time()
    rc = subprocess.run([PY, script], cwd=str(REPO)).returncode
    elapsed = int(time.time() - started)
    if rc != 0:
        return "FAIL", f"exit {rc}", elapsed
    tmp = TMP_ROOT / cid
    missing = [a for a in case.get("artifacts", []) if not (tmp / a).exists()]
    if missing:
        return "FAIL", f"missing artifact: {', '.join(missing)}", elapsed
    if not keep and tmp.exists():
        shutil.rmtree(tmp, ignore_errors=True)
    return "PASS", "", elapsed


def main(argv: list[str]) -> int:
    keep = False
    only: list[str] = []
    for a in argv[1:]:
        if a == "--keep":
            keep = True
        else:
            only.append(a)
    print(f"repo: {REPO}")
    print(f"tmp:  {TMP_ROOT}")
    results = []
    for case in CASES:
        if only and case["id"] not in only:
            continue
        status, detail, secs = run_case(case, keep)
        results.append((case["id"], status, detail, secs))

    print("\n=== Summary ===")
    print(f"{'Id':<4} {'Status':<6} {'Time':>5}  Detail")
    for cid, status, detail, secs in results:
        print(f"{cid:<4} {status:<6} {secs:>4}s  {detail}")
    p = sum(1 for r in results if r[1] == "PASS")
    f = sum(1 for r in results if r[1] == "FAIL")
    s = sum(1 for r in results if r[1] == "SKIP")
    print(f"Totals: {p} PASS, {f} FAIL, {s} SKIP")
    return 1 if f else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
