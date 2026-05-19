"""Case 20: BD + HEVC + clip_frames + rpc."""
import os
from vsenv import *
import lamvsfunc as lamvs

TMP = os.environ['CASE_TMP']
SOURCE = os.path.join(TMP, 'sample.m2ts')

@lamvs.encodeProcess(
    sourceType='BD',
    encodeTypes=['HEVC'],
    clip_frames=[600, 1200],
    rpc=True,
    log_file=os.path.join(TMP, 'run.log'),
    param_x265='"{0}" --y4m -D 10 --preset veryfast --crf 23 -o "{1}.mp4" -',
)
def encode(source=''):
    src = core.lsmas.LWLibavSource(source).fmtc.bitdepth(bits=16)
    return src

encode(SOURCE)
