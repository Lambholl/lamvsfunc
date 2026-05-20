"""Case 15: BD + x264 CHS + CHT (two parallel encodes via dual_out)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from case_lib import prepare

TMP = prepare("15", ["sample.m2ts", "sample.sc.ass", "sample.tc.ass", "sample.txt"])
SOURCE = str(TMP / "sample.m2ts")

from vsenv import *
import lamvsfunc as lamvs

@lamvs.encodeProcess(
    sourceType='BD',
    encodeTypes=['CHS', 'CHT'],
    chapter=True,
    rpc=True,
    log_file=str(TMP / 'run.log'),
    param_x264='"{0}" --demuxer y4m --preset veryfast --crf 23 -o "{1}.mp4" -',
)
def encode(source=''):
    src = core.lsmas.LWLibavSource(source).fmtc.bitdepth(bits=16)
    return src

encode(SOURCE)
