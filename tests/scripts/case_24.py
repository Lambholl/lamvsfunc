"""Case 24: Web + HEVC + clip_frames.

The only case that exercises cut_audio's AAC (lossy) branch:
per-segment ffmpeg-decode -> qaac-encode pipe. BD clip cuts flac via
ffmpeg directly, which never touches that code path.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from case_lib import prepare

TMP = prepare("24", ["sample.mkv"], trim_seconds=15)
SOURCE = str(TMP / "sample.mkv")

from vsenv import *
import lamvsfunc as lamvs

@lamvs.encodeProcess(
    sourceType='Web',
    encodeTypes=['HEVC'],
    clip_frames=[80, 160],
    rpc=True,
    log_file=str(TMP / 'run.log'),
    param_x265='"{0}" --y4m -D 10 --preset veryfast --crf 23 -o "{1}.mp4" -',
)
def encode(source=''):
    src = core.lsmas.LWLibavSource(source).fmtc.bitdepth(bits=16)
    return src

encode(SOURCE)
