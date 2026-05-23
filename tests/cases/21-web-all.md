# 21 web-all

## Purpose

Full Web release flow: HEVC mkv with two muxed subtitle tracks + font
attachments, plus two x264 mp4s (CHS and CHT) with burned subs. Three
encoders run concurrently through `dual_out.multiple_outputs`. Web
counterpart of case 16; verifies that the single ffmpeg-copy m4a is
reused by all three encoders (qaac never runs).

## Prerequisites

- Tools on PATH: `ffmpeg`, `x264`, `x265`, `MP4Box`, `mkvmerge`,
  `AssFontSubset.Console.exe`.
- Fixtures: `sample.mkv`, `sample.sc.ass`, `sample.tc.ass`,
  `sample.txt`, `fonts/`.

## Setup

Automatic. The script calls
`case_lib.prepare("21", ["sample.mkv", "sample.sc.ass", "sample.tc.ass", "sample.txt", "fonts"])`.

## Execute

This is the longest Web case; expect a few minutes.

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_21.py
```

## Verify

- Exit code: `0`.
- All three outputs exist:
  - `tests\.tmp\21\sample.hevc.mkv`
  - `tests\.tmp\21\sample.sc.mp4`
  - `tests\.tmp\21\sample.tc.mp4`
- HEVC mkv: 4 tracks (HEVC + AAC + 2 subs) + attachments + chapters.
  ```powershell
  python tests\scripts\verify_mkv.py "tests\.tmp\21\sample.hevc.mkv" `
      tracks.length tracks[1].codec attachments.length chapters.length
  # tracks.length: 4
  # tracks[1].codec: AAC
  # attachments.length: >= 1
  # chapters.length: 1
  ```
- Both mp4s have 2 tracks + chapter.
  ```powershell
  python tests\scripts\verify_mkv.py "tests\.tmp\21\sample.sc.mp4" tracks.length chapters.length
  python tests\scripts\verify_mkv.py "tests\.tmp\21\sample.tc.mp4" tracks.length chapters.length
  ```
- Log shows all three rpc summaries and confirms qaac was not invoked
  (Web reuses ffmpeg-copy m4a for every encoder):
  ```powershell
  python tests\scripts\verify_log.py "tests\.tmp\21\run.log" `
      --must "RP Checker complete for HEVC" `
      --must "RP Checker complete for CHS" `
      --must "RP Checker complete for CHT" `
      --must-not "qaac" `
      --must-not "broken frame found"
  ```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force "tests\.tmp\21" }
```
