# Agent protocol

This document tells an AI coding agent (or a careful human) how to
execute the cases in this suite consistently.

## Globals

- Repo root: the directory containing `lamvsfunc.py`.
- Working dir for artifacts: `tests/.tmp/{case-id}/`. Always start a
  case by recreating this directory empty.
- Fixture root resolution:
  1. If `tests/fixtures/.path-config` exists, its first non-blank,
     non-`#` line is taken as the absolute root.
  2. Otherwise, use `tests/fixtures/`.
- Python interpreter: assume the local VapourSynth portable Python.
  In this repo's primary dev environment that is
  `F:\Encode tools\VS-Portable-R65\python.exe`. The path is
  configurable; cases that invoke Python directly reference the
  variable `$LAMVS_PY` if you want to override.
- `import lamvsfunc` must work. The portable Python already has
  `Lib/site-packages/lamvsfunc.pth` pointing at this repo, so no
  `PYTHONPATH` is needed.

## Required preflight

Before running any case, do this once and cache the result:

1. **Resolve fixture root.** Print the absolute path so the report can
   include it.
2. **Probe fixtures.** For each file listed in `fixtures.md` under
   "Required", record present / missing.
3. **Probe tools.** For each tool in `fixtures.md` under "External
   tools", run `<tool> -version` (or the equivalent) and record the
   first line of output.
4. **Probe lamvsfunc import.** Run
   `python -c "import lamvsfunc; print(lamvsfunc.__file__)"`. Record
   the resolved path.

If any required fixture or tool referenced by the case you are about
to run is missing, mark the case `SKIP: missing <thing>` and continue
to the next case. Do not invent substitutes.

## Per-case loop

For each `cases/*.md` file you are running:

1. Read the case end-to-end before doing anything.
2. **Setup**: clean `tests/.tmp/{case-id}/`, copy or symlink fixtures
   into it as the case directs. Never edit `tests/fixtures/`.
3. **Execute**: run exactly what the `Execute` section specifies.
   Capture exit code, stdout, stderr. Stream output to
   `tests/.tmp/{case-id}/run.log`.
4. **Verify**: walk through each bullet in the `Verify` section. A
   single failed bullet fails the whole case. Record which bullet
   failed and the observed value.
5. **Cleanup**: if the case passed, delete `tests/.tmp/{case-id}/`.
   On failure, leave it so the operator can inspect.
6. Append one status line to the agent's running report:
   ```
   {case-id}: PASS
   {case-id}: FAIL ({bullet}: expected X, got Y)
   {case-id}: SKIP (missing eac3to)
   ```

## Reporting

When all requested cases finish, emit a summary block:

```
Summary
- 17 PASS, 2 FAIL, 3 SKIP
- Failures:
  - 13-bd-hevc-subs (track count: expected 4, got 3)
  - 32-param-torrent (mktorrent not found)
- Skips:
  - 14-bd-x264 (missing fixture: sample.sc.ass)
```

## Rules

- Never modify `lamvsfunc.py` to make a test pass. If a case fails on
  what looks like a real bug, report it; do not silently fix.
- Never delete `tests/fixtures/`. Treat it as read-only.
- Never push, commit, or open PRs from a test run unless the operator
  asks. Reports are textual.
- Test runs may produce hundreds of MB in `tests/.tmp/`. If a case
  passes, clean its tmp dir. If a case fails, the operator will clean
  when ready.
- If a case takes more than ten minutes wall-clock, treat that as a
  failure unless the case explicitly says it is long-running.
