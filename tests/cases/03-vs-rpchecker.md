# 03 vs-rpchecker

## Purpose

`rpChecker` should report zero broken frames when src and rip are
identical, and produce a `.rpc.txt` listing broken frames when they
diverge.

## Prerequisites

- VapourSynth importable, plus the `complane` plugin (for `PSNR`).
- `ffmpeg` on PATH.
- `lsmas` plugin loaded (it is in the portable build).

## Setup

```powershell
$tmp = "tests\.tmp\03"
if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
New-Item -ItemType Directory -Force $tmp | Out-Null
```

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_03_checks.py 2>&1 |
    Tee-Object -FilePath "tests\.tmp\03\run.log"
```

The script encodes two short lossless mp4 clips with `ffmpeg`'s libx264
inside `tests/.tmp/03/` and calls `rpChecker` against synthetic
references.

## Verify

- Exit code: `0`.
- Every `check` line ends in `PASS`.
- `tests/.tmp/03/rip_clean.mp4.rpc.txt` does *not* exist.
- `tests/.tmp/03/rip_bad.mp4.rpc.txt` exists and contains at least one
  `Possible broken frame` line.

Optional cross-check:
```powershell
python tests\scripts\verify_log.py "tests\.tmp\03\run.log" `
    --must "check identical clips: no rpc file: PASS" `
    --must "check mismatched clips: rpc file exists: PASS" `
    --must "check rpc file mentions broken frame: PASS" `
    --must-not "FAIL"
```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force tests\.tmp\03 }
```
