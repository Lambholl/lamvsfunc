# 20 clip-bd-hevc

## Purpose

BD + HEVC with clip_frames produces multiple segment outputs plus
per-segment rpc reports. Validates the slicing code, per-segment audio
cut, and the seg-aware rpChecker call.

## Prerequisites

- Tools on PATH: `eac3to`, `mkvmerge`, `x265`, `ffmpeg`.
- Fixture: `sample.m2ts` with **≥ 1200 frames** (so the cut produces
  at least three segments: [0,600), [600,1200), [1200, end)).

## Setup

```powershell
. tests\scripts\setup_case.ps1 -CaseId 20 -Files @("sample.m2ts")
```

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_20.py
```

## Verify

- Exit code: `0`.
- Three segment outputs exist:
  - `$env:CASE_TMP\sample.seg0.hevc.mkv`
  - `$env:CASE_TMP\sample.seg1.hevc.mkv`
  - `$env:CASE_TMP\sample.seg2.hevc.mkv`
- Each is 2 tracks (HEVC + FLAC), no attachments, no chapters.
  ```powershell
  foreach ($i in 0,1,2) {
      python tests\scripts\verify_mkv.py "$env:CASE_TMP\sample.seg$i.hevc.mkv" `
          tracks.length attachments.length chapters.length
  }
  # for each segment:
  # tracks.length: 2
  # attachments.length: 0
  # chapters.length: 0
  ```
- Log contains rpc for all three segments:
  ```powershell
  python tests\scripts\verify_log.py "$env:CASE_TMP\run.log" `
      --must "RP Checker complete for HEVC seg0" `
      --must "RP Checker complete for HEVC seg1" `
      --must "RP Checker complete for HEVC seg2" `
      --must-not "broken frame found"
  ```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force "$env:CASE_TMP" }
```
