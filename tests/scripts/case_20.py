"""Case 20: BD + HEVC + clip_frames + rpc."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from case_lib import prepare

TMP = prepare("20", ["sample.m2ts"])
SOURCE = str(TMP / "sample.m2ts")

from vsenv import *
import lamvsfunc as lamvs

@lamvs.encodeProcess(
    sourceType='BD',
    encodeTypes=['HEVC'],
    clip_frames=[600, 1200],
    rpc=True,
    log_file=str(TMP / 'run.log'),
    param_x265='"{0}" --y4m -D 10 --preset veryfast --crf 23 -o "{1}.265" -',
)
def encode(source=''):
    src = core.lsmas.LWLibavSource(source).fmtc.bitdepth(bits=16)
    return src

encode(SOURCE)
