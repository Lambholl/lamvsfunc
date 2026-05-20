# 00 unit-pure

## Purpose

Exercise the pure-Python helpers in `lamvsfunc.py` that have no
VapourSynth or external-tool dependency: `getMimeType`,
`_normalize_for_log`, `_LogStream`, `_Tee`.

If this case fails, the suite has a regression in the most basic
plumbing and later cases will likely produce confusing failures.

## Prerequisites

- `lamvsfunc` importable from the portable Python (the `.pth` install
  is documented in [`AGENT.md`](../AGENT.md)).
- No fixtures.
- No external tools.

## Setup

Automatic. The script calls `case_lib.prepare("00", [])` which
recreates `tests/.tmp/00/` empty. No fixtures needed.

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_00_checks.py 2>&1 |
    Tee-Object -FilePath "tests\.tmp\00\run.log"
```

## Verify

- Exit code: `0`.
- Every line of `tests\.tmp\00\run.log` matches `^check .+: PASS$`.
- No line contains `FAIL`.

You can also re-confirm with:
```powershell
python tests\scripts\verify_log.py "tests\.tmp\00\run.log" `
    --must "check mime ttf: PASS" `
    --must "check normalize ansi strip: PASS" `
    --must "check logstream strips and converts: PASS" `
    --must "check tee writes to all: PASS" `
    --must-not "FAIL"
```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force tests\.tmp\00 }
```
