# lamvsfunc test suite

Agent-driven functional test suite for [`lamvsfunc.py`](../lamvsfunc.py).
This suite is not pytest. Each case is a self-contained Markdown file
that an AI coding agent reads, executes, and reports on.

## What's here

| Path | Purpose |
|---|---|
| [`AGENT.md`](AGENT.md) | The protocol the agent follows: discovery, setup, run, verify, report. |
| [`fixtures.md`](fixtures.md) | Inventory of the binary assets a human must provide before running. |
| `cases/*.md` | One file per test case. Numbered by topic: 00-09 unit/helpers, 10-29 encodeProcess paths, 30-39 parameter variants, 40-49 error paths. |
| `scripts/` | Small shared helpers the cases call (mkv identification, log search, blank-clip synthesis). |
| `fixtures/` | Local-only directory the human populates. Gitignored. |
| `.tmp/` | Working directory the cases write into. Gitignored. |

## Why this shape

- The tests need VapourSynth, Windows-only command-line tools (eac3to,
  qaac, x264, x265, MP4Box, mkvmerge, AssFontSubset, mktorrent) and
  real video assets. None of that runs cleanly on a generic CI runner.
- An agent can read the case, check prerequisites, run the script,
  inspect mkvmerge output and log files, and write a pass/fail/skip
  back to the operator. That gives reproducible coverage without
  asking a human to babysit two dozen invocations.
- Markdown stays diff-able and human-readable; new cases are easy to
  add by copying an existing one.

## Running

Point an agent at this directory and tell it which cases to run, for
example:

> "Run cases 10-16 and report results."

The agent follows [`AGENT.md`](AGENT.md). Each case ends with a status
line so you can collect a summary at the end.

For a single case you can also follow the markdown by hand: every
`Execute` block is plain PowerShell or Python you can paste.

## Adding a case

1. Copy the file most similar in shape to your new test.
2. Pick the next free number in its bucket (10-29 for end-to-end
   pipelines, 30-39 for parameter variants, 40-49 for errors).
3. Keep the same five sections: Purpose, Prerequisites, Setup,
   Execute, Verify, Cleanup.
4. If you need a new helper, add it to `scripts/` and reference it
   from the case rather than inlining shell. Helpers should print one
   machine-parseable line so the agent can branch on it.
