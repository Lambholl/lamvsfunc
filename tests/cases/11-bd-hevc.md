# 11 bd-hevc

## Purpose

Smallest BD-source path: eac3to extracts FLAC, x265 encodes, mkvmerge
muxes. No chapter, no subs. Verifies the BD-only audio extraction
optimization (qaac should not run when only HEVC is requested).

## Prerequisites

- Tools on PATH: `eac3to`, `mkvmerge`, `x265`, `ffmpeg` (for the rpc lsmas read).
- Fixture: `sample.m2ts`.

## Setup

```powershell
. tests\scripts\setup_case.ps1 -CaseId 11 -Files @("sample.m2ts")
```

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_11.py
```

## Verify

- Exit code: `0`.
- Output `$env:CASE_TMP\sample.hevc.mkv` exists.
- mkvmerge identify: 2 tracks (HEVC + FLAC).
  ```powershell
  python tests\scripts\verify_mkv.py "$env:CASE_TMP\sample.hevc.mkv" `
      tracks.length tracks[0].codec tracks[1].codec
  # tracks.length: 2
  # tracks[0].codec: HEVC/H.265/MPEG-H
  # tracks[1].codec: FLAC
  ```
- Log file:
  ```powershell
  python tests\scripts\verify_log.py "$env:CASE_TMP\run.log" `
      --must "RP Checker complete for HEVC" `
      --must-not "qaac" `
      --must-not "broken frame found"
  ```
  The `qaac` must-not check confirms the HEVC-only optimization is in effect.

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force "$env:CASE_TMP" }
```
