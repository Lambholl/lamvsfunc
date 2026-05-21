# 34 param-delfiles-clip

## Purpose

`delFiles=True` combined with `clip_frames` must clean every per-segment
intermediate (cut flac, mute mp4) plus the main flac, while keeping the
final muxed `.seg{i}.hevc.mkv` segment outputs.

Pairs with case 33 (`delFiles=False`, non-clip path, intermediates
kept) to cover both axes of the delFiles cleanup path. Specifically
guards the clip-mode cleanup path that relies on the end-of-function
global pass over `file2del` rather than a per-segment delete block.

## Prerequisites

- Tools on PATH: `eac3to`, `mkvmerge`, `x265`, `ffmpeg`.
- Fixture: `sample.m2ts` with **>= 1200 frames** (three segments:
  [0,600), [600,1200), [1200, end)).

## Setup

Automatic. The script calls `case_lib.prepare("34", ["sample.m2ts"])`.

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_34.py
```

## Verify

- Exit code: `0`.
- Per-segment intermediates removed:

  ```powershell
  foreach ($i in 0,1,2) {
      Test-Path "tests\.tmp\34\sample.seg$i.flac"        # False
      Test-Path "tests\.tmp\34\sample.seg$i.mute.mp4"    # False
  }
  ```
- Main flac removed:

  ```powershell
  Test-Path "tests\.tmp\34\sample.flac"                  # False
  ```
- Final segment outputs kept:

  ```powershell
  foreach ($i in 0,1,2) {
      Test-Path "tests\.tmp\34\sample.seg$i.hevc.mkv"    # True
  }
  ```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force "tests\.tmp\34" }
```
