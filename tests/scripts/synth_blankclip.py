"""Synthesize a deterministic VapourSynth clip for unit-style tests of
down8d and rpChecker. Importable; not meant to be run directly.

The clips returned have predictable PSNR characteristics so a case can
assert on them.
"""
from __future__ import annotations
import vapoursynth as vs
from vapoursynth import core


def constant_clip(width: int = 320, height: int = 180, length: int = 24,
                  color: tuple[int, int, int] = (180, 128, 128),
                  bits: int = 16) -> vs.VideoNode:
    """A constant-color YUV clip in the requested bit depth.

    Used as both src and rip in rpChecker tests where we expect identical
    frames (PSNR -> inf -> reported as 0 by the PSNR plugin, treated as
    no-broken-frame upstream)."""
    base = core.std.BlankClip(
        width=width, height=height, length=length,
        format=vs.YUV420P8, color=color,
        fpsnum=24000, fpsden=1001,
    )
    if bits == 8:
        return base
    return base.fmtc.bitdepth(bits=bits)


def two_color_clip(width: int = 320, height: int = 180, length: int = 24,
                   colors=((180, 128, 128), (60, 128, 128)),
                   switch_at: int | None = None,
                   bits: int = 16) -> vs.VideoNode:
    """A clip that switches color partway through. Useful for forcing
    PSNR mismatches when paired with a constant-color reference.
    switch_at defaults to length//2 so callers can just pass length."""
    if switch_at is None:
        switch_at = length // 2
    if switch_at < 1 or switch_at >= length:
        raise ValueError(f"switch_at={switch_at} invalid for length={length}")
    a = constant_clip(width, height, switch_at, colors[0], bits)
    b = constant_clip(width, height, length - switch_at, colors[1], bits)
    return a + b
