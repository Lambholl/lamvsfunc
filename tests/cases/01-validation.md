# 01 validation

## Purpose

The parameter pre-checks in `encodeProcess` should reject invalid
input at decorator-construction time. This case covers everything that
does *not* need a source file or fixture (those are in cases 40-49).

## Prerequisites

- `lamvsfunc` importable.

## Setup

Automatic. `case_lib.prepare("01", [])` is called by the script itself.

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_01_checks.py 2>&1 |
    Tee-Object -FilePath "tests\.tmp\01\run.log"
```

## Verify

- Exit code: `0`.
- Each check line ends in `PASS`.
- No `FAIL` substring in the log.
- The error messages quoted in the `PASS` lines should mention the
  offending parameter (e.g. `clip_frames must be strictly increasing`).

Optional cross-check:
```powershell
python tests\scripts\verify_log.py "tests\.tmp\01\run.log" `
    --must "check bad sourceType: PASS" `
    --must "check clip+non-HEVC: PASS" `
    --must "check valid args accepted: PASS" `
    --must-not "FAIL"
```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force tests\.tmp\01 }
```
