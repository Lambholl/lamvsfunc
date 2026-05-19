"""Case 16: BD + HEVC + CHS + CHT (three parallel encodes).
HEVC muxes subtitles + fonts; the 264 outputs burn subtitles in.
"""
import os
from vsenv import *
import lamvsfunc as lamvs

TMP = os.environ['CASE_TMP']
SOURCE = os.path.join(TMP, 'sample.m2ts')

@lamvs.encodeProcess(
    sourceType='BD',
    encodeTypes=['HEVC', 'CHS', 'CHT'],
    chapter=True,
    rpc=True,
    subtitles_info=[
        {'type': 'CHS', 'language': 'chi', 'track_name': 'Simplified', 'is_default': True},
        {'type': 'CHT', 'language': 'chi', 'track_name': 'Traditional', 'is_default': False},
    ],
    fonts_dir=os.path.join(TMP, 'fonts'),
    font_out_dir=os.path.join(TMP, 'font-output'),
    log_file=os.path.join(TMP, 'run.log'),
    param_x264='"{0}" --demuxer y4m --preset veryfast --crf 23 -o "{1}.mp4" -',
    param_x265='"{0}" --y4m -D 10 --preset veryfast --crf 23 -o "{1}.mp4" -',
)
def encode(source=''):
    src = core.lsmas.LWLibavSource(source).fmtc.bitdepth(bits=16)
    return src

encode(SOURCE)
