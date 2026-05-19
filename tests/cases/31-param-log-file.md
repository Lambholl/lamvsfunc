# 31 param-log-file

## Purpose

Validate the `log_file` parameter: the file should exist after the run
and contain output from at least eac3to, x265, mkvmerge and rpChecker.

## Prerequisites

- Tools on PATH: `eac3to`, `mkvmerge`, `x265`, `ffmpeg`.
- Fixture: `sample.m2ts`.

## Setup

```powershell
. tests\scripts\setup_case.ps1 -CaseId 31 -Files @("sample.m2ts")
```

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_31.py
```

## Verify

- Exit code: `0`.
- `$env:CASE_TMP\case31.log` exists and is non-trivial (> 5 KB).
- The log captures output from each tool the run touched:
  ```powershell
  python tests\scripts\verify_log.py "$env:CASE_TMP\case31.log" `
      --must "eac3to processing took" `
      --must "x265 [info]:" `
      --must "mkvmerge" `
      --must "RP Checker complete for HEVC"
  ```
- No raw ANSI escape codes (ESC=0x1B) survive in the log:
  ```powershell
  $bytes = [System.IO.File]::ReadAllBytes("$env:CASE_TMP\case31.log")
  $hasEsc = $bytes -contains 0x1B
  # $hasEsc should be False.
  ```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force "$env:CASE_TMP" }
```
