"""down8d sanity: a 16-bit synthetic clip must dither to 8-bit while
preserving frame count, dimensions, fps and field order. The output
should be visually close to the input (we just check it produces a
sane clip).
"""
from __future__ import annotations
import sys


def _check(name, ok, detail=""):
    if ok:
        print(f"check {name}: PASS")
        return 0
    print(f"check {name}: FAIL {detail}")
    return 1


def main() -> int:
    import vapoursynth as vs
    import lamvsfunc as L
    sys.path.insert(0, "tests/scripts")
    from synth_blankclip import constant_clip, two_color_clip

    fails = 0

    src = constant_clip(width=320, height=180, length=24, bits=16)
    out = L.down8d(src)

    fails += _check("output is a VideoNode", isinstance(out, vs.VideoNode))
    fails += _check("frame count preserved", out.num_frames == src.num_frames,
                    f"src={src.num_frames}, out={out.num_frames}")
    fails += _check("width preserved", out.width == src.width)
    fails += _check("height preserved", out.height == src.height)
    fails += _check("fps preserved",
                    out.fps_num == src.fps_num and out.fps_den == src.fps_den)
    fails += _check("output is 8 bits",
                    out.format.bits_per_sample == 8,
                    f"got {out.format.bits_per_sample}")

    # Two-color clip just to make sure down8d handles non-constant input
    # without crashing.
    src2 = two_color_clip(width=320, height=180, length=12, bits=16)
    out2 = L.down8d(src2)
    fails += _check("two-color clip processed", out2.num_frames == 12)
    fails += _check("two-color clip is 8 bits", out2.format.bits_per_sample == 8)

    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
