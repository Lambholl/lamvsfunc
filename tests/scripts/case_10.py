"""Case 10: Web + HEVC full file.

CASE_TMP must point at a directory containing sample.mkv (set by
setup_case.ps1 before launching this script).
"""
import os
from vsenv import *
import lamvsfunc as lamvs

TMP = os.environ['CASE_TMP']
SOURCE = os.path.join(TMP, 'sample.mkv')

@lamvs.encodeProcess(
    sourceType='Web',
    encodeTypes=['HEVC'],
    rpc=True,
    log_file=os.path.join(TMP, 'run.log'),
    param_x265='"{0}" --y4m -D 10 --preset veryfast --crf 23 -o "{1}.mp4" -',
)
def encode(source=''):
    src = core.lsmas.LWLibavSource(source).fmtc.bitdepth(bits=16)
    return src

encode(SOURCE)
