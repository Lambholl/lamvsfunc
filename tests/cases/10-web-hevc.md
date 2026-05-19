# 10 web-hevc

## Purpose

Smallest Web-source path: ffmpeg copies AAC into m4a, x265 encodes the
HEVC mkv, rpChecker validates. No subtitles, no chapter.

## Prerequisites

- Tools on PATH: `ffmpeg`, `mkvmerge`, `x265`.
- Fixture: `sample.mkv`.

## Setup

```powershell
. tests\scripts\setup_case.ps1 -CaseId 10 -Files @("sample.mkv")
```

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_10.py
```

## Verify

- Exit code: `0`.
- Output `$env:CASE_TMP\sample.hevc.mkv` exists.
- mkvmerge identify reports 2 tracks; track 0 codec is HEVC, track 1 is AAC.
  ```powershell
  python tests\scripts\verify_mkv.py "$env:CASE_TMP\sample.hevc.mkv" `
      tracks.length tracks[0].codec tracks[1].codec
  # tracks.length: 2
  # tracks[0].codec: HEVC/H.265/MPEG-H
  # tracks[1].codec: AAC
  ```
- Log file contains the rpc completion line:
  ```powershell
  python tests\scripts\verify_log.py "$env:CASE_TMP\run.log" `
      --must "RP Checker complete for HEVC" `
      --must-not "broken frame found"
  ```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force "$env:CASE_TMP" }
```
