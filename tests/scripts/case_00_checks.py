"""Pure-Python helper checks for lamvsfunc.

Run from anywhere:
    python tests\\scripts\\case_00_checks.py

Prints one `check NAME: PASS` or `check NAME: FAIL reason` per assertion.
Exit code 0 iff every check passes.
"""
from __future__ import annotations
import io
import sys


def _check(name, ok, detail=""):
    if ok:
        print(f"check {name}: PASS")
        return 0
    print(f"check {name}: FAIL {detail}")
    return 1


def main() -> int:
    import lamvsfunc as L
    fails = 0

    # getMimeType
    fails += _check("mime ttf", L.getMimeType(".ttf") == "application/x-truetype-font")
    fails += _check("mime ttc", L.getMimeType(".TTC") == "application/x-truetype-font")
    fails += _check("mime otf", L.getMimeType(".otf") == "application/vnd.ms-opentype")
    fails += _check("mime woff", L.getMimeType(".woff") == "font/woff")
    fails += _check("mime woff2", L.getMimeType(".woff2") == "font/woff2")
    fails += _check("mime unknown", L.getMimeType(".xyz") == "application/octet-stream")

    # _normalize_for_log
    fails += _check(
        "normalize ansi strip",
        L._normalize_for_log("\x1b[31mhi\x1b[0m") == "hi",
    )
    fails += _check(
        "normalize cr->lf",
        L._normalize_for_log("a\rb\rc") == "a\nb\nc",
    )
    fails += _check(
        "normalize crlf preserved",
        L._normalize_for_log("a\r\nb") == "a\r\nb",
    )

    # _LogStream
    sink = io.StringIO()
    ls = L._LogStream(sink)
    ls.write("\x1b[32mhello\x1b[0m\rworld")
    fails += _check(
        "logstream strips and converts",
        sink.getvalue() == "hello\nworld",
        f"got {sink.getvalue()!r}",
    )

    # _Tee
    a = io.StringIO()
    b = io.StringIO()
    tee = L._Tee(a, b)
    tee.write("xyz")
    fails += _check("tee writes to all", a.getvalue() == "xyz" and b.getvalue() == "xyz")
    tee_with_none = L._Tee(a, None, b)
    tee_with_none.write("!")
    fails += _check("tee skips None", a.getvalue() == "xyz!" and b.getvalue() == "xyz!")

    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
