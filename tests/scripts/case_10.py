"""Case 10: Web + HEVC full file."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from case_lib import prepare

TMP = prepare("10", ["sample.mkv"], trim_seconds=10)
SOURCE = str(TMP / "sample.mkv")

from vsenv import *
import lamvsfunc as lamvs

@lamvs.encodeProcess(
    sourceType='Web',
    encodeTypes=['HEVC'],
    rpc=True,
    log_file=str(TMP / 'run.log'),
    param_x265='"{0}" --y4m -D 10 --preset veryfast --crf 23 -o "{1}.mp4" -',
)
def encode(source=''):
    src = core.lsmas.LWLibavSource(source).fmtc.bitdepth(bits=16)
    return src

encode(SOURCE)
