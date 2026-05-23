# 24 web-clip-hevc

## Purpose

Web + HEVC with clip_frames produces multiple segment outputs plus
per-segment rpc reports. Web counterpart of case 20.

**Unique coverage**: this is the only case in the suite that exercises
the AAC (lossy) branch of `_cut_audio` — the per-segment ffmpeg-decode
→ qaac-encode pipe in `_ffmpeg_to_qaac`. BD clip cuts flac via ffmpeg
directly, so that pipeline is otherwise untested.
Note that per-segment AAC re-encode adds ~21 ms of priming/padding per
seam, so reassembling segments is not bit-exact — the test only checks
that segments are produced and rpc passes per segment.

## Prerequisites

- Tools on PATH: `ffmpeg`, `qaac64`, `mkvmerge`, `x265`.
- Fixture: `sample.mkv` with at least ~240 frames (~10 s @ 24fps) so
  the cut at [80, 160] produces three segments.

## Setup

Automatic. The script calls `case_lib.prepare("24", ["sample.mkv"], trim_seconds=15)`.

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_24.py
```

## Verify

- Exit code: `0`.
- Three segment outputs exist (HEVC clip names are zero-padded):
  - `tests\.tmp\24\sample.seg00.hevc.mkv`
  - `tests\.tmp\24\sample.seg01.hevc.mkv`
  - `tests\.tmp\24\sample.seg02.hevc.mkv`
- Each is 2 tracks (HEVC + AAC), no attachments, no chapters.
  ```powershell
  foreach ($i in '00','01','02') {
      python tests\scripts\verify_mkv.py "tests\.tmp\24\sample.seg$i.hevc.mkv" `
          tracks.length tracks[1].codec attachments.length chapters.length
  }
  # for each segment:
  # tracks.length: 2
  # tracks[1].codec: AAC
  # attachments.length: 0
  # chapters.length: 0
  ```
- Log confirms qaac ran (the cut_audio AAC branch was taken) and
  contains rpc for all three segments:
  ```powershell
  python tests\scripts\verify_log.py "tests\.tmp\24\run.log" `
      --must "qaac" `
      --must "RP Checker complete for HEVC seg0" `
      --must "RP Checker complete for HEVC seg1" `
      --must "RP Checker complete for HEVC seg2" `
      --must-not "broken frame found"
  ```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force "tests\.tmp\24" }
```
