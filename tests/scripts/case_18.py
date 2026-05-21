"""Case 18: Web + x264 CHS (burned subtitle, MP4Box mux with chapter).

First case to exercise the non-HEVC encode branch on a Web source.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from case_lib import prepare

TMP = prepare("18", ["sample.mkv", "sample.sc.ass", "sample.txt"], trim_seconds=15)
SOURCE = str(TMP / "sample.mkv")

from vsenv import *
import lamvsfunc as lamvs

@lamvs.encodeProcess(
    sourceType='Web',
    encodeTypes=['CHS'],
    chapter=True,
    rpc=True,
    log_file=str(TMP / 'run.log'),
    param_x264='"{0}" --demuxer y4m --preset veryfast --crf 23 -o "{1}.mp4" -',
)
def encode(source=''):
    src = core.lsmas.LWLibavSource(source).fmtc.bitdepth(bits=16)
    return src

encode(SOURCE)
