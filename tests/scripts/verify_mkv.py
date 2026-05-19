"""Inspect a Matroska or MP4 container with mkvmerge --identify (JSON).

Usage:
    python tests\\scripts\\verify_mkv.py <file> [<query> ...]

Without queries, prints the full JSON identification.
Queries are dotted paths into the JSON tree, with bracket indices:
    tracks.length
    tracks[0].codec
    tracks[0].properties.pixel_dimensions
    container.properties.duration
    attachments.length
    chapters[0].num_entries

Each query prints one line:
    <query>: <value>
or
    <query>: ERROR <message>

Exit code: 0 on success, 1 if mkvmerge fails or any query errors.
"""
from __future__ import annotations
import json
import re
import subprocess
import sys


def query(obj, path: str):
    """Walk a dotted path with optional [N] indices into the JSON tree."""
    cur = obj
    for raw in path.split('.'):
        m = re.match(r'^([^\[\]]+)(?:\[(\d+)\])?$', raw)
        if not m:
            raise ValueError(f"bad query segment {raw!r}")
        key, idx = m.group(1), m.group(2)
        if key == 'length':
            if not isinstance(cur, list):
                raise ValueError(f"length on non-list at {raw!r}")
            return len(cur)
        if isinstance(cur, dict):
            if key not in cur:
                raise KeyError(key)
            cur = cur[key]
        else:
            raise ValueError(f"non-dict at segment {raw!r}")
        if idx is not None:
            i = int(idx)
            if not isinstance(cur, list) or i >= len(cur):
                raise IndexError(i)
            cur = cur[i]
    return cur


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1
    path = argv[1]
    queries = argv[2:]
    try:
        out = subprocess.run(
            ['mkvmerge', '--identification-format', 'json', '--identify', path],
            capture_output=True, text=True, check=True,
        )
    except FileNotFoundError:
        print("ERROR mkvmerge not on PATH", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        print(f"ERROR mkvmerge exit {e.returncode}: {e.stderr.strip()}", file=sys.stderr)
        return 1
    data = json.loads(out.stdout)
    if not queries:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0
    bad = False
    for q in queries:
        try:
            v = query(data, q)
            print(f"{q}: {v}")
        except Exception as e:
            bad = True
            print(f"{q}: ERROR {e}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
