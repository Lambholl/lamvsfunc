"""Shared helpers for case_*.py.

prepare(case_id, files, trim_seconds=None) resolves the fixture root,
recreates tests/.tmp/{case_id}/ empty, copies the requested fixtures
into it (truncating video files to trim_seconds via ffmpeg stream copy
when set), exports CASE_TMP / CASE_ROOT / CASE_ID into os.environ for
any child process the case might spawn, and returns the tmp path.

A missing fixture raises FileNotFoundError so the caller fails cleanly.
"""
from __future__ import annotations
import os
import re
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TMP_ROOT = REPO / "tests" / ".tmp"
FIXTURE_DEFAULT = REPO / "tests" / "fixtures"
PATH_CONFIG = FIXTURE_DEFAULT / ".path-config"

VIDEO_EXTS = {".mkv", ".m2ts", ".mp4", ".ts"}


def fixture_root() -> Path:
    if PATH_CONFIG.exists():
        for line in PATH_CONFIG.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                return Path(s)
    return FIXTURE_DEFAULT


M2TS_PACKET_SIZE = 192  # BD m2ts uses 188-byte TS packet + 4-byte timecode prefix


def _trim_video(src: Path, dst: Path, seconds: float) -> None:
    """Truncate a video fixture to roughly `seconds` of content.

    BD m2ts uses byte-level slicing because ffmpeg's mpegts muxer drops
    the BD-specific PMT codec_tags during stream copy — that makes eac3to
    misidentify PCM audio streams as "MPEG2 unknown" and refuse to
    extract audio. Slicing the raw container preserves the PMT exactly.

    Other containers (mkv/mp4/ts) use ffmpeg stream copy with explicit
    video+audio mapping to drop any PG/menu streams that might confuse
    downstream tools.
    """
    if src.suffix.lower() == ".m2ts":
        _trim_m2ts_bytes(src, dst, seconds)
        return
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(src),
            "-t", str(seconds),
            "-c", "copy",
            "-map", "0:v:0", "-map", "0:a",
            str(dst),
        ],
        check=True,
    )


_FFMPEG_DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)")


def _probe_duration(src: Path) -> float:
    """Return media duration in seconds, parsed from ffmpeg's stderr banner."""
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(src)],
        capture_output=True, text=True,
    )
    match = _FFMPEG_DURATION_RE.search(proc.stderr)
    if not match:
        raise RuntimeError(f"could not parse duration of {src}: {proc.stderr[:200]}")
    h, m, s = match.groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def _trim_m2ts_bytes(src: Path, dst: Path, seconds: float) -> None:
    """Truncate an m2ts to ~seconds by copying the first N 192-byte packets.

    Scales packet count by file size / source duration. The PMT/PAT live
    near the start of the file so truncating from the tail keeps the
    container parseable; eac3to / lsmas read it as a short BD m2ts.
    """
    total_dur = _probe_duration(src)
    file_size = src.stat().st_size
    target_bytes = int(file_size * seconds / total_dur)
    target_packets = max(1, target_bytes // M2TS_PACKET_SIZE)
    chunk_bytes = target_packets * M2TS_PACKET_SIZE
    with open(src, "rb") as f_in, open(dst, "wb") as f_out:
        remaining = chunk_bytes
        while remaining > 0:
            buf = f_in.read(min(remaining, 1 << 20))
            if not buf:
                break
            f_out.write(buf)
            remaining -= len(buf)


def prepare(case_id: str, files: list[str], trim_seconds: float | None = None) -> Path:
    """Set up the per-case tmp dir and copy fixtures.

    Args:
        case_id: Used as the .tmp/ subdirectory name.
        files: Fixture filenames or directory names under the fixture root.
        trim_seconds: If set, video fixtures (mkv/m2ts/mp4/ts) are truncated
            to this many seconds via ffmpeg stream copy. Non-video files
            and directories are copied verbatim.

    Returns the path to tests/.tmp/{case_id}/.
    Side effect: sets CASE_TMP, CASE_ROOT, CASE_ID in os.environ.
    """
    tmp = TMP_ROOT / case_id
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    root = fixture_root()
    for name in files:
        src = root / name
        if not src.exists():
            raise FileNotFoundError(f"missing fixture: {src}")
        dst = tmp / name
        if src.is_dir():
            shutil.copytree(src, dst)
        elif trim_seconds and src.suffix.lower() in VIDEO_EXTS:
            _trim_video(src, dst, trim_seconds)
        else:
            shutil.copy2(src, dst)
    os.environ["CASE_ID"] = case_id
    os.environ["CASE_ROOT"] = str(root)
    os.environ["CASE_TMP"] = str(tmp)
    return tmp
