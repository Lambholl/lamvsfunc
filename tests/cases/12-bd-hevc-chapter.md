# 12 bd-hevc-chapter

## Purpose

BD + HEVC with chapter muxed in. Verifies the OGM chapter file is
attached to the output mkv.

## Prerequisites

- Tools on PATH: `eac3to`, `mkvmerge`, `x265`.
- Fixtures: `sample.m2ts`, `sample.txt`.

## Setup

Automatic. The script calls
`case_lib.prepare("12", ["sample.m2ts", "sample.txt"])`.

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_12.py
```

## Verify

- Exit code: `0`.
- Output `tests\.tmp\12\sample.hevc.mkv` exists.
- mkvmerge identify shows chapters:
  ```powershell
  python tests\scripts\verify_mkv.py "tests\.tmp\12\sample.hevc.mkv" `
      tracks.length chapters.length chapters[0].num_entries
  # tracks.length: 2
  # chapters.length: 1
  # chapters[0].num_entries: >= 2
  ```
- Log:
  ```powershell
  python tests\scripts\verify_log.py "tests\.tmp\12\run.log" `
      --must "RP Checker complete for HEVC" `
      --must-not "broken frame found"
  ```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force "tests\.tmp\12" }
```
