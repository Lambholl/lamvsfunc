# 17 web-hevc-subs

## Purpose

Web + HEVC mkv with two muxed subtitle tracks (CHS + CHT) plus
subsetted fonts attached and a chapter file. Web counterpart of case
13. Exercises subsetFonts and the multi-track mkvmerge path on top of
the Web audio extraction (ffmpeg `-c:a copy` into m4a, no qaac).

## Prerequisites

- Tools on PATH: `ffmpeg`, `mkvmerge`, `x265`, `AssFontSubset.Console.exe`.
- Fixtures: `sample.mkv`, `sample.sc.ass`, `sample.tc.ass`, `sample.txt`, `fonts/`.

## Setup

Automatic. The script calls
`case_lib.prepare("17", ["sample.mkv", "sample.sc.ass", "sample.tc.ass", "sample.txt", "fonts"])`.

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_17.py
```

## Verify

- Exit code: `0`.
- Output `tests\.tmp\17\sample.hevc.mkv` exists.
- mkvmerge identify: 4 tracks (HEVC + AAC + sub-CHS + sub-CHT), at
  least one attachment, chapters present.
  ```powershell
  python tests\scripts\verify_mkv.py "tests\.tmp\17\sample.hevc.mkv" `
      tracks.length tracks[1].codec tracks[2].type `
      tracks[2].properties.language tracks[3].type `
      attachments.length chapters.length
  # tracks.length: 4
  # tracks[1].codec: AAC
  # tracks[2].type: subtitles
  # tracks[2].properties.language: chi
  # tracks[3].type: subtitles
  # attachments.length: >= 1
  # chapters.length: 1
  ```
- Log shows subsetting ran and confirms qaac never ran (Web HEVC-only
  reuses the ffmpeg-copy m4a):
  ```powershell
  python tests\scripts\verify_log.py "tests\.tmp\17\run.log" `
      --must "Subsetting fonts" `
      --must "Fonts subsetting complete" `
      --must "RP Checker complete for HEVC" `
      --must-not "qaac" `
      --must-not "broken frame found"
  ```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force "tests\.tmp\17" }
```
