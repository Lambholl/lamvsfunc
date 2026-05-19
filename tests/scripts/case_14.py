"""Case 14: BD + x264 CHS (burned subtitle, MP4Box mux with chapter)."""
import os
from vsenv import *
import lamvsfunc as lamvs

TMP = os.environ['CASE_TMP']
SOURCE = os.path.join(TMP, 'sample.m2ts')

@lamvs.encodeProcess(
    sourceType='BD',
    encodeTypes=['CHS'],
    chapter=True,
    rpc=True,
    log_file=os.path.join(TMP, 'run.log'),
    param_x264='"{0}" --demuxer y4m --preset veryfast --crf 23 -o "{1}.mp4" -',
)
def encode(source=''):
    src = core.lsmas.LWLibavSource(source).fmtc.bitdepth(bits=16)
    return src

encode(SOURCE)
