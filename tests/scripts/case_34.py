"""Case 34: delFiles=True with clip_frames removes per-segment intermediates."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from case_lib import prepare

TMP = prepare("34", ["sample.m2ts"], trim_seconds=15)
SOURCE = str(TMP / "sample.m2ts")

from vsenv import *
import lamvsfunc as lamvs

@lamvs.encodeProcess(
    sourceType='BD',
    encodeTypes=['HEVC'],
    clip_frames=[80, 160],
    delFiles=True,
    rpc=False,
    log_file=str(TMP / 'run.log'),
    param_x265='"{0}" --y4m -D 10 --preset veryfast --crf 23 -o "{1}.mp4" -',
)
def encode(source=''):
    src = core.lsmas.LWLibavSource(source).fmtc.bitdepth(bits=16)
    return src

encode(SOURCE)

# Inline cleanup assertions: clip mode + delFiles=True must remove every
# per-segment intermediate plus the main flac, while keeping each segment's
# final muxed output.
for i in range(3):
    assert not (TMP / f"sample.seg{i:02d}.flac").exists(), f"sample.seg{i:02d}.flac should be removed"
    assert not (TMP / f"sample.seg{i:02d}.mute.mp4").exists(), f"sample.seg{i:02d}.mute.mp4 should be removed"
    assert (TMP / f"sample.seg{i:02d}.hevc.mkv").exists(), f"sample.seg{i:02d}.hevc.mkv should remain"
assert not (TMP / "sample.flac").exists(), "sample.flac (main) should be removed"
