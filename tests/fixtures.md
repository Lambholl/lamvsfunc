# Fixtures

Everything in this list lives under the fixture root, which is
`tests/fixtures/` unless overridden by `tests/fixtures/.path-config`.

`tests/fixtures/` and `.path-config` are gitignored. Do not commit the
binary assets.

## Required

### Video sources

| File | Requirements |
|---|---|
| `sample.m2ts` | BD-style m2ts; 1080p24 (24000/1001); AVC + PCM stereo; frame count ≥ 2000 (~83 s); eac3to must accept it |
| `sample.mkv` | Web-style mkv; h264 + AAC; any length ≥ 10 s |

Quick derivation from an existing m2ts:
```powershell
ffmpeg -i source.m2ts -c:v copy -c:a aac -b:a 192k `
       -map 0:v:0 -map 0:a:0 tests\fixtures\sample.mkv
```

### Subtitles

| File | Requirements |
|---|---|
| `sample.sc.ass` | 5-10 Dialogue lines; references 1-2 fonts that exist in `fonts/` |
| `sample.tc.ass` | Same shape as sc, traditional Chinese text; references the same fonts so subsetFonts produces a single consistent set |

### Chapter

| File | Requirements |
|---|---|
| `sample.txt` | OGM chapter format, at least 2 entries within the m2ts duration |

OGM example:
```
CHAPTER01=00:00:00.000
CHAPTER01NAME=Intro
CHAPTER02=00:00:30.000
CHAPTER02NAME=Mid
```

### Fonts

| Path | Requirements |
|---|---|
| `fonts/*.ttf` or `fonts/*.otf` | All fonts referenced by `sample.sc.ass` and `sample.tc.ass` |

## Optional

| File | When used |
|---|---|
| `sample.jpsc.ass` / `sample.jptc.ass` | Only if you want to exercise the JPSC / JPTC encodeType paths; no current case requires them |
| `.path-config` | Single line with an absolute path. Overrides the fixture root, useful if you store the binary assets outside the repo |

## External tools (on PATH)

| Tool | Cases that need it |
|---|---|
| `ffmpeg` | Almost every non-pure-unit case |
| `mkvmerge` | Every case that produces a Matroska output (and the verify helpers) |
| `eac3to` | All BD-source cases |
| `qaac64` | All 264 (CHS / CHT / JPSC / JPTC) cases |
| `x264` | Same as qaac64 |
| `MP4Box` | Same as qaac64 |
| `x265` | All HEVC cases |
| `AssFontSubset.Console.exe` | HEVC + subtitles_info cases |
| `mktorrent` | Torrent case only |

When a tool is missing the corresponding case is skipped, not failed.

## Preflight check

Run the helper to print the current state of fixtures and tools:

```powershell
python tests\scripts\preflight.py
```

It prints one line per item, marking each `present` / `missing`. The
agent uses this output before any case run.
