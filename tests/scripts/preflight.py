"""Print fixture and tool availability.

Run from the repo root:
    python tests\\scripts\\preflight.py

Output lines are stable for the agent to parse:
    fixture sample.m2ts: present F:\\...\\sample.m2ts (503162880 bytes)
    fixture sample.mkv: missing
    tool ffmpeg: present F:\\Encode tools\\ffmpeg.exe
    tool eac3to: missing
"""
from __future__ import annotations
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURES = REPO_ROOT / "tests" / "fixtures"
PATH_CONFIG = DEFAULT_FIXTURES / ".path-config"

REQUIRED_FIXTURES = [
    "sample.m2ts",
    "sample.mkv",
    "sample.sc.ass",
    "sample.tc.ass",
    "sample.txt",
]

REQUIRED_FIXTURE_DIRS = [
    "fonts",
]

TOOLS = [
    "ffmpeg",
    "mkvmerge",
    "eac3to",
    "qaac64",
    "x264",
    "x265",
    "MP4Box",
    "AssFontSubset.Console",
    "mktorrent",
]


def fixture_root() -> Path:
    if PATH_CONFIG.exists():
        for line in PATH_CONFIG.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                return Path(line)
    return DEFAULT_FIXTURES


def main() -> int:
    root = fixture_root()
    print(f"fixture-root: {root}")

    for name in REQUIRED_FIXTURES:
        path = root / name
        if path.exists():
            print(f"fixture {name}: present {path} ({path.stat().st_size} bytes)")
        else:
            print(f"fixture {name}: missing")

    for d in REQUIRED_FIXTURE_DIRS:
        path = root / d
        if path.is_dir():
            files = sorted(p.name for p in path.iterdir() if p.is_file())
            print(f"fixture {d}/: present {path} ({len(files)} files)")
        else:
            print(f"fixture {d}/: missing")

    for tool in TOOLS:
        found = shutil.which(tool) or shutil.which(tool + ".exe")
        if found:
            print(f"tool {tool}: present {found}")
        else:
            print(f"tool {tool}: missing")

    return 0


if __name__ == "__main__":
    sys.exit(main())
