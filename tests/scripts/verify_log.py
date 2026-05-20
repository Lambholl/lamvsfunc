"""Check that a log file contains expected substrings (and optionally lacks others).

Usage:
    python tests\\scripts\\verify_log.py <log_file> --must <substring> [--must <substring>] ...
                                                       [--must-not <substring> ...]

Prints one line per pattern:
    must "RP Checker complete for HEVC, no broken frame found": present
    must "xyz": MISSING
    must-not "Traceback": absent
    must-not "abc": PRESENT

Exit code: 0 if every must-have is present and every must-not is absent; 1 otherwise.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('log_file')
    ap.add_argument('--must', action='append', default=[])
    ap.add_argument('--must-not', action='append', default=[])
    args = ap.parse_args(argv[1:])
    text = Path(args.log_file).read_text(encoding='utf-8', errors='replace')
    bad = False
    for s in args.must:
        if s in text:
            print(f'must "{s}": present')
        else:
            bad = True
            print(f'must "{s}": MISSING')
    for s in getattr(args, 'must_not'):
        if s in text:
            bad = True
            print(f'must-not "{s}": PRESENT')
        else:
            print(f'must-not "{s}": absent')
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
