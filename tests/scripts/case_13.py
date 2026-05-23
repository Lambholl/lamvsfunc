"""Case 13: BD + HEVC + multi-subtitle muxing + font subsetting."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from case_lib import prepare

TMP = prepare("13", ["sample.m2ts", "sample.sc.ass", "sample.tc.ass", "sample.txt", "fonts"], trim_seconds=15)
SOURCE = str(TMP / "sample.m2ts")

from vsenv import *
import lamvsfunc as lamvs

@lamvs.encodeProcess(
    sourceType='BD',
    encodeTypes=['HEVC'],
    chapter=True,
    rpc=True,
    subtitles_info=[
        {'type': 'CHS', 'language': 'chi', 'track_name': 'Simplified', 'is_default': True},
        {'type': 'CHT', 'language': 'chi', 'track_name': 'Traditional', 'is_default': False},
    ],
    fonts_dir=str(TMP / 'fonts'),
    font_out_dir=str(TMP / 'font-output'),
    log_file=str(TMP / 'run.log'),
    param_x265='"{0}" --y4m -D 10 --preset veryfast --crf 23 -o "{1}.mp4" -',
)
def encode(source=''):
    src = core.lsmas.LWLibavSource(source).fmtc.bitdepth(bits=16)
    return src

encode(SOURCE)
