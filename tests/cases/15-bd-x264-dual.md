# 15 bd-x264-dual

## Purpose

Two parallel x264 encodes off the same VS source via
`dual_out.multiple_outputs`. Validates that the dual-output plumbing
works for two different burned-subtitle clips.

## Prerequisites

- Tools on PATH: `eac3to`, `qaac64`, `ffmpeg`, `x264`, `MP4Box`.
- Fixtures: `sample.m2ts`, `sample.sc.ass`, `sample.tc.ass`, `sample.txt`.

## Setup

```powershell
. tests\scripts\setup_case.ps1 -CaseId 15 `
    -Files @("sample.m2ts", "sample.sc.ass", "sample.tc.ass", "sample.txt")
```

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_15.py
```

## Verify

- Exit code: `0`.
- Both `$env:CASE_TMP\sample.sc.mp4` and `$env:CASE_TMP\sample.tc.mp4`
  exist.
- Identify both:
  ```powershell
  python tests\scripts\verify_mkv.py "$env:CASE_TMP\sample.sc.mp4" tracks.length chapters.length
  python tests\scripts\verify_mkv.py "$env:CASE_TMP\sample.tc.mp4" tracks.length chapters.length
  ```
- Log contains rpc lines for both CHS and CHT:
  ```powershell
  python tests\scripts\verify_log.py "$env:CASE_TMP\run.log" `
      --must "RP Checker complete for CHS" `
      --must "RP Checker complete for CHT" `
      --must-not "broken frame found"
  ```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force "$env:CASE_TMP" }
```
