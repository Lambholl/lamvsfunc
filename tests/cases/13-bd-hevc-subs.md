# 13 bd-hevc-subs

## Purpose

BD + HEVC mkv with two muxed subtitle tracks (CHS + CHT) plus subsetted
fonts attached. Exercises subsetFonts and the multi-track mkvmerge
path.

## Prerequisites

- Tools on PATH: `eac3to`, `mkvmerge`, `x265`, `AssFontSubset.Console.exe`.
- Fixtures: `sample.m2ts`, `sample.sc.ass`, `sample.tc.ass`, `sample.txt`, `fonts/`.

## Setup

```powershell
. tests\scripts\setup_case.ps1 -CaseId 13 `
    -Files @("sample.m2ts", "sample.sc.ass", "sample.tc.ass", "sample.txt", "fonts")
```

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_13.py
```

## Verify

- Exit code: `0`.
- Output `$env:CASE_TMP\sample.hevc.mkv` exists.
- mkvmerge identify: 4 tracks (HEVC + FLAC + sub-CHS + sub-CHT), at
  least one attachment, chapters present.
  ```powershell
  python tests\scripts\verify_mkv.py "$env:CASE_TMP\sample.hevc.mkv" `
      tracks.length tracks[2].type tracks[2].properties.language `
      tracks[3].type attachments.length chapters.length
  # tracks.length: 4
  # tracks[2].type: subtitles
  # tracks[2].properties.language: chi
  # tracks[3].type: subtitles
  # attachments.length: >= 1
  # chapters.length: 1
  ```
- Log shows subsetting ran:
  ```powershell
  python tests\scripts\verify_log.py "$env:CASE_TMP\run.log" `
      --must "Subsetting fonts" `
      --must "Fonts subsetting complete" `
      --must "RP Checker complete for HEVC" `
      --must-not "broken frame found"
  ```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force "$env:CASE_TMP" }
```
