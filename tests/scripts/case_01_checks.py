"""Parameter validation checks for encodeProcess.

Only the validation that runs at decorator-construction time is
exercised here (no fixture or source file required). Wrapper-time
validation that depends on the source path is covered by the 40s error
cases.

Prints `check NAME: PASS` / `check NAME: FAIL ...` per assertion. Exit
code 0 iff every check passes.
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from case_lib import prepare
prepare("01", [])


def _check_raises(name, exc_type, fn):
    try:
        fn()
    except exc_type as e:
        print(f"check {name}: PASS ({exc_type.__name__}: {e})")
        return 0
    except BaseException as e:
        print(f"check {name}: FAIL wrong exception {type(e).__name__}: {e}")
        return 1
    print(f"check {name}: FAIL no exception raised")
    return 1


def main() -> int:
    import lamvsfunc as L
    fails = 0
    EP = L.encodeProcess

    fails += _check_raises("bad sourceType", ValueError,
                           lambda: EP(sourceType='XX'))
    fails += _check_raises("empty encodeTypes", ValueError,
                           lambda: EP(encodeTypes=[]))
    fails += _check_raises("unknown encodeType", ValueError,
                           lambda: EP(encodeTypes=['ZZZ']))
    fails += _check_raises("mixed known/unknown encodeType", ValueError,
                           lambda: EP(encodeTypes=['HEVC', 'WAT']))

    fails += _check_raises("subtitles_info non-dict", TypeError,
                           lambda: EP(subtitles_info=["not-a-dict"]))
    fails += _check_raises("subtitles_info bad type", ValueError,
                           lambda: EP(subtitles_info=[{"type": "BAD"}]))
    fails += _check_raises("subtitles_info missing type", ValueError,
                           lambda: EP(subtitles_info=[{}]))

    fails += _check_raises("clip_frames non-list", ValueError,
                           lambda: EP(clip_frames="not a list"))
    fails += _check_raises("clip_frames negative", ValueError,
                           lambda: EP(clip_frames=[-1, 100]))
    fails += _check_raises("clip_frames zero", ValueError,
                           lambda: EP(clip_frames=[0, 100]))
    fails += _check_raises("clip_frames duplicate", ValueError,
                           lambda: EP(clip_frames=[100, 100]))
    fails += _check_raises("clip_frames decreasing", ValueError,
                           lambda: EP(clip_frames=[200, 100]))

    fails += _check_raises("clip+non-HEVC", ValueError,
                           lambda: EP(clip_frames=[100, 200], encodeTypes=['CHS']))

    # Accept good values silently (must NOT raise).
    try:
        EP(sourceType='BD', encodeTypes=['HEVC'], clip_frames=[100, 200, 300])
        print("check valid args accepted: PASS")
    except Exception as e:
        fails += 1
        print(f"check valid args accepted: FAIL {e!r}")

    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
