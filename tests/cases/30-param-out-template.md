# 30 param-out-template

## Purpose

`out_name_templates={'HEVC': '...'}` should rename the final mkv. The
template uses `{0}` for the source basename and `.mkv` is appended if
missing.

## Prerequisites

- Tools on PATH: `eac3to`, `mkvmerge`, `x265`.
- Fixture: `sample.m2ts`.

## Setup

Automatic. The script calls `case_lib.prepare("30", ["sample.m2ts"])`.

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_30.py
```

## Verify

- Exit code: `0`.
- Renamed output exists at `tests\.tmp\30\[Test] sample [HEVC].mkv`.
- The legacy name `tests\.tmp\30\sample.hevc.mkv` does NOT exist.
  ```powershell
  Test-Path "tests\.tmp\30\[Test] sample [HEVC].mkv"   # True
  Test-Path "tests\.tmp\30\sample.hevc.mkv"            # False
  ```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force "tests\.tmp\30" }
```
