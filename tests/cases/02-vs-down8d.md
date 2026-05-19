# 02 vs-down8d

## Purpose

`down8d` is the 16-bit-to-8-bit dither used as the input to x264 and
as the basis for rpChecker comparisons. Verify it returns a valid VS
clip with the expected shape, frame count and bit depth from a
synthetic source.

## Prerequisites

- VapourSynth importable from the portable Python.
- `fmtc` plugin loaded (it is in the standard portable build).

## Setup

```powershell
$tmp = "tests\.tmp\02"
if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
New-Item -ItemType Directory -Force $tmp | Out-Null
```

## Execute

```powershell
& "F:\Encode tools\VS-Portable-R65\python.exe" tests\scripts\case_02_checks.py 2>&1 |
    Tee-Object -FilePath "tests\.tmp\02\run.log"
```

## Verify

- Exit code: `0`.
- Each check line ends in `PASS`.
- The "output is 8 bits" check confirms the dither happened.
- The "frame count preserved" check confirms `down8d` did not silently
  re-time the clip.

Optional cross-check:
```powershell
python tests\scripts\verify_log.py "tests\.tmp\02\run.log" `
    --must "check output is 8 bits: PASS" `
    --must "check frame count preserved: PASS" `
    --must-not "FAIL"
```

## Cleanup

```powershell
if ($LASTEXITCODE -eq 0) { Remove-Item -Recurse -Force tests\.tmp\02 }
```
