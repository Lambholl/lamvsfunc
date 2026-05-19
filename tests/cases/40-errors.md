# 40 errors

## Purpose

Wrapper-time validation: the decorator was built fine but the user
called `encode()` with a source whose neighbors are missing or have
the wrong extension. Each scenario should raise a specific exception
before any encoder is launched.

This case covers:
- ext mismatch (BD wrapper given a `.mkv`)
- `chapter=True` without `<source>.txt`
- 264 encodeType without `<source>.<verName>.ass`
- HEVC `subtitles_info` without `<source>.<verName>.ass`

## Prerequisites

- `lamvsfunc` importable.
- Fixture: `sample.m2ts` (any valid m2ts; only the filename and
  enough of the stream for `LWLibavSource` to instantiate is used).

## Setup

Automatic. The script calls `case_lib.prepare("40", ["sample.m2ts"])`.

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_40_checks.py 2>&1 |
    Tee-Object -FilePath "tests\.tmp\40\run.log"
```

## Verify

- Exit code: `0`.
- Each check line ends in `PASS`. The error messages should mention
  what is missing (chapter file, subtitle file, extension).

Optional cross-check:
```powershell
python tests\scripts\verify_log.py "tests\.tmp\40\run.log" `
    --must "check ext mismatch (BD given .mkv): PASS" `
    --must "check missing chapter txt: PASS" `
    --must "check missing CHS subtitle: PASS" `
    --must "check missing HEVC sub for subtitles_info: PASS" `
    --must-not "FAIL"
```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force "tests\.tmp\40" }
```
