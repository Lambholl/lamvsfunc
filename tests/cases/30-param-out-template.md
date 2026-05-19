# 30 param-out-template

## Purpose

`out_name_templates={'HEVC': '...'}` should rename the final mkv. The
template uses `{0}` for the source basename and `.mkv` is appended if
missing.

## Prerequisites

- Tools on PATH: `eac3to`, `mkvmerge`, `x265`.
- Fixture: `sample.m2ts`.

## Setup

```powershell
. tests\scripts\setup_case.ps1 -CaseId 30 -Files @("sample.m2ts")
```

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_30.py
```

## Verify

- Exit code: `0`.
- Renamed output exists at `$env:CASE_TMP\[Test] sample [HEVC].mkv`.
- The legacy name `$env:CASE_TMP\sample.hevc.mkv` does NOT exist.
  ```powershell
  Test-Path "$env:CASE_TMP\[Test] sample [HEVC].mkv"   # True
  Test-Path "$env:CASE_TMP\sample.hevc.mkv"            # False
  ```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force "$env:CASE_TMP" }
```
