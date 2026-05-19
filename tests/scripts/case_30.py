"""Case 30: out_name_templates renames the HEVC output."""
import os
from vsenv import *
import lamvsfunc as lamvs

TMP = os.environ['CASE_TMP']
SOURCE = os.path.join(TMP, 'sample.m2ts')

@lamvs.encodeProcess(
    sourceType='BD',
    encodeTypes=['HEVC'],
    chapter=False,
    rpc=False,
    log_file=os.path.join(TMP, 'run.log'),
    out_name_templates={'HEVC': '[Test] {0} [HEVC]'},
    param_x265='"{0}" --y4m -D 10 --preset veryfast --crf 23 -o "{1}.mp4" -',
)
def encode(source=''):
    src = core.lsmas.LWLibavSource(source).fmtc.bitdepth(bits=16)
    return src

encode(SOURCE)
