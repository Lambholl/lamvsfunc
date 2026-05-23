# 20 clip-bd-hevc

## Purpose

BD + HEVC with clip_frames produces multiple segment outputs plus
per-segment rpc reports. Validates the slicing code, per-segment audio
cut, and the seg-aware rpChecker call.

## Prerequisites

- Tools on PATH: `eac3to`, `mkvmerge`, `x265`, `ffmpeg`.
- Fixture: `sample.m2ts`. The case trims to 15 s before running, so any
  m2ts that already meets `fixtures.md` requirements works. The cut at
  `[80, 160]` produces three segments: `[0,80)`, `[80,160)`, `[160, end]`.

## Setup

Automatic. The script calls
`case_lib.prepare("20", ["sample.m2ts"], trim_seconds=15)`.

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_20.py
```

## Verify

- Exit code: `0`.
- Three segment outputs exist (HEVC clip names are zero-padded width 2):
  - `tests\.tmp\20\sample.seg00.hevc.mkv`
  - `tests\.tmp\20\sample.seg01.hevc.mkv`
  - `tests\.tmp\20\sample.seg02.hevc.mkv`
- Each is 2 tracks (HEVC + FLAC), no attachments, no chapters.
  ```powershell
  foreach ($i in '00','01','02') {
      python tests\scripts\verify_mkv.py "tests\.tmp\20\sample.seg$i.hevc.mkv" `
          tracks.length attachments.length chapters.length
  }
  # for each segment:
  # tracks.length: 2
  # attachments.length: 0
  # chapters.length: 0
  ```
- Log contains rpc for all three segments:
  ```powershell
  python tests\scripts\verify_log.py "tests\.tmp\20\run.log" `
      --must "RP Checker complete for HEVC seg0" `
      --must "RP Checker complete for HEVC seg1" `
      --must "RP Checker complete for HEVC seg2" `
      --must-not "broken frame found"
  ```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force "tests\.tmp\20" }
```
