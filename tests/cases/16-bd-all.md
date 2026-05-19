# 16 bd-all

## Purpose

Full BD release flow: HEVC mkv with two muxed subtitle tracks + font
attachments, plus two x264 mp4s (CHS and CHT) with burned subs. Three
encoders run concurrently through `dual_out.multiple_outputs` with
mixed bit depths (HEVC 10-bit, x264 8-bit).

## Prerequisites

- Tools on PATH: `eac3to`, `qaac64`, `ffmpeg`, `x264`, `x265`,
  `MP4Box`, `mkvmerge`, `AssFontSubset.Console.exe`.
- Fixtures: `sample.m2ts`, `sample.sc.ass`, `sample.tc.ass`,
  `sample.txt`, `fonts/`.

## Setup

Automatic. The script calls
`case_lib.prepare("16", ["sample.m2ts", "sample.sc.ass", "sample.tc.ass", "sample.txt", "fonts"])`.

## Execute

This is the longest case; expect a few minutes.

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_16.py
```

## Verify

- Exit code: `0`.
- All three outputs exist:
  - `tests\.tmp\16\sample.hevc.mkv`
  - `tests\.tmp\16\sample.sc.mp4`
  - `tests\.tmp\16\sample.tc.mp4`
- HEVC mkv: 4 tracks + attachments + chapters.
  ```powershell
  python tests\scripts\verify_mkv.py "tests\.tmp\16\sample.hevc.mkv" `
      tracks.length attachments.length chapters.length
  # tracks.length: 4
  # attachments.length: >= 1
  # chapters.length: 1
  ```
- Both mp4s have 2 tracks + chapter.
  ```powershell
  python tests\scripts\verify_mkv.py "tests\.tmp\16\sample.sc.mp4" tracks.length chapters.length
  python tests\scripts\verify_mkv.py "tests\.tmp\16\sample.tc.mp4" tracks.length chapters.length
  ```
- Log shows all three rpc summaries:
  ```powershell
  python tests\scripts\verify_log.py "tests\.tmp\16\run.log" `
      --must "RP Checker complete for HEVC" `
      --must "RP Checker complete for CHS" `
      --must "RP Checker complete for CHT" `
      --must-not "broken frame found"
  ```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force "tests\.tmp\16" }
```
