"""Error-path checks that need a source file.

Exercises validation that fires inside the wrapper (i.e. after the
decorator is applied, when encode() is actually invoked). The 01 case
covers validation that fires at decorator-construction time.

Run:
    python tests\\scripts\\case_40_checks.py
"""
from __future__ import annotations
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
from case_lib import prepare

TMP = prepare("40", ["sample.m2ts"])


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
    src = str(TMP / "sample.m2ts")
    import lamvsfunc as L
    from vsenv import core  # noqa: F401  (load VS plugins)

    fails = 0

    @L.encodeProcess(sourceType='BD', encodeTypes=['HEVC'])
    def enc_bd(source=''):
        return core.lsmas.LWLibavSource(source).fmtc.bitdepth(bits=16)

    # ext mismatch: BD wrapper called with a .mkv path.
    fake_mkv = src + ".tmp.mkv"
    open(fake_mkv, "wb").close()
    fails += _check_raises("ext mismatch (BD given .mkv)", FileNotFoundError,
                           lambda: enc_bd(fake_mkv))
    os.remove(fake_mkv)

    # chapter=True but no chapter txt.
    work = tempfile.mkdtemp(prefix="case40-", dir=str(TMP))
    try:
        local_src = os.path.join(work, "x.m2ts")
        shutil.copy(src, local_src)

        @L.encodeProcess(sourceType='BD', encodeTypes=['HEVC'], chapter=True)
        def enc_with_chap(source=''):
            return core.lsmas.LWLibavSource(source).fmtc.bitdepth(bits=16)

        fails += _check_raises("missing chapter txt", FileNotFoundError,
                               lambda: enc_with_chap(local_src))

        # missing subtitle for 264 encodeType.
        @L.encodeProcess(sourceType='BD', encodeTypes=['CHS'], chapter=False)
        def enc_chs(source=''):
            return core.lsmas.LWLibavSource(source).fmtc.bitdepth(bits=16)

        fails += _check_raises("missing CHS subtitle", FileNotFoundError,
                               lambda: enc_chs(local_src))

        # missing subtitle for HEVC subtitles_info path.
        @L.encodeProcess(sourceType='BD', encodeTypes=['HEVC'], chapter=False,
                         subtitles_info=[{"type": "CHS"}])
        def enc_hevc_subs(source=''):
            return core.lsmas.LWLibavSource(source).fmtc.bitdepth(bits=16)

        fails += _check_raises("missing HEVC sub for subtitles_info", FileNotFoundError,
                               lambda: enc_hevc_subs(local_src))
    finally:
        shutil.rmtree(work, ignore_errors=True)

    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
