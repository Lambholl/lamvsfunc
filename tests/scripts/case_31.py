"""Case 31: log_file captures both Python and subprocess output."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from case_lib import prepare

TMP = prepare("31", ["sample.m2ts"])
SOURCE = str(TMP / "sample.m2ts")
LOG = str(TMP / "case31.log")

from vsenv import *
import lamvsfunc as lamvs

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
