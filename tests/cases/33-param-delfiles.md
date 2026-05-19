# 33 param-delfiles

## Purpose

`delFiles=False` should keep the intermediates (flac, mute.mp4) around
after the encode. The default behavior (`delFiles=True`, covered by
cases 10-16) deletes them.

## Prerequisites

- Tools on PATH: `eac3to`, `mkvmerge`, `x265`.
- Fixture: `sample.m2ts`.

## Setup

Automatic. The script calls `case_lib.prepare("33", ["sample.m2ts"])`.

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_33.py
```

## Verify

- Exit code: `0`.
- Intermediates remain in `tests\.tmp\33`:
  - `sample.flac` (eac3to output)
  - `sample.mute.mp4` (x265 output before mux)
- Final output also remains:
  - `sample.hevc.mkv`

```powershell
Test-Path "tests\.tmp\33\sample.flac"        # True
Test-Path "tests\.tmp\33\sample.mute.mp4"    # True
Test-Path "tests\.tmp\33\sample.hevc.mkv"    # True
```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force "tests\.tmp\33" }
```
