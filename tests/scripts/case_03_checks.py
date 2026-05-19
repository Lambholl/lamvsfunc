"""rpChecker behavior on synthetic clips.

Identical src and rip should produce zero broken-frame reports and no
.rpc.txt file. A mismatched rip should produce a .rpc.txt file with
at least one "Possible broken frame" line.

Requires the `complane` VS plugin and ffmpeg on PATH (libx264).
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from case_lib import prepare

TMP = prepare("03", [])


def _check(name, ok, detail=""):
    if ok:
        print(f"check {name}: PASS")
        return 0
    print(f"check {name}: FAIL {detail}")
    return 1


def _encode_to_mp4(clip, path):
    import subprocess
    cmd = ["ffmpeg", "-y", "-f", "yuv4mpegpipe", "-i", "-",
           "-c:v", "libx264", "-preset", "ultrafast", "-qp", "0",
           "-pix_fmt", "yuv420p", path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    clip.output(proc.stdin, y4m=True)
    proc.stdin.close()
    proc.wait()


def main() -> int:
    import vapoursynth as vs
    from vapoursynth import core
    import lamvsfunc as L
    from synth_blankclip import constant_clip, two_color_clip

    fails = 0

    src8 = constant_clip(width=320, height=180, length=24, bits=8)
    rip_path = TMP / "rip_clean.mp4"
    _encode_to_mp4(src8, str(rip_path))

    out_rpc = TMP / "rip_clean.mp4.rpc.txt"
    if out_rpc.exists():
        out_rpc.unlink()
    L.rpChecker(src8, str(rip_path), output=str(out_rpc), message="clean")
    print()
    fails += _check("identical clips: no rpc file", not out_rpc.exists(),
                    f"unexpected file: {out_rpc}")

    src_two = two_color_clip(width=320, height=180, length=24, bits=8)
    rip_bad = TMP / "rip_bad.mp4"
    _encode_to_mp4(src_two, str(rip_bad))
    out_rpc2 = TMP / "rip_bad.mp4.rpc.txt"
    if out_rpc2.exists():
        out_rpc2.unlink()
    L.rpChecker(src8, str(rip_bad), output=str(out_rpc2), message="bad")
    print()
    fails += _check("mismatched clips: rpc file exists", out_rpc2.exists())
    if out_rpc2.exists():
        body = out_rpc2.read_text(encoding="utf-8")
        fails += _check("rpc file mentions broken frame",
                        "Possible broken frame" in body,
                        f"body: {body!r}")

    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
