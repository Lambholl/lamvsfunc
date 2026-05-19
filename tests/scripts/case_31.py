"""Case 31: log_file captures both Python and subprocess output."""
import os
from vsenv import *
import lamvsfunc as lamvs

TMP = os.environ['CASE_TMP']
SOURCE = os.path.join(TMP, 'sample.m2ts')
LOG = os.path.join(TMP, 'case31.log')

@lamvs.encodeProcess(
    sourceType='BD',
    encodeTypes=['HEVC'],
    chapter=False,
    rpc=True,
    log_file=LOG,
    param_x265='"{0}" --y4m -D 10 --preset veryfast --crf 23 -o "{1}.mp4" -',
)
def encode(source=''):
    src = core.lsmas.LWLibavSource(source).fmtc.bitdepth(bits=16)
    return src

encode(SOURCE)
