# Lambholl's VapourSynth Functions

## Functions:
* `encodeProcess` (decorator)
* `down8d` copied from ksks
* Producing...

#### encodeProcess
Args: `(sourceType='Web', ext='', encodeTypes=['CHS','CHT','HEVC'], subrender='libass', chapter=None, delFiles=False, qaac_path = 'qaac64.exe', ffmpeg_path = 'ffmpeg', x264_path='x264.exe', x265_path='x265.exe', mp4box_path='MP4Box.exe', mkvmerge_path='mkvmerge.exe', eac3to_path='eac3to.exe', param_x264='"{0}" --demuxer y4m --preset veryslow --profile high --crf 18 --colorprim bt709 --transfer bt709 --colormatrix bt709 -o "{1}.mp4" -', param_x265='"{0}" --y4m -D 10 --preset slower --crf 18 -o "{1}.mp4" -')`  

e.g. 
```python
@lamvsfunc.encodeProcess(encodeTypes=['JPSC','JPTC','HEVC'], delFiles=True
def encodeVideo(source=''):
    src=core.lsmas.LWLibavSource(source,cache=0).fmtc.bitdepth(bits=16,dmode=1)
    last=src
    last=src
    last=zvs.zmdg(last,thsad=120,thscd1=250,truemotion=True,refinemotion=True,lf=0.2,cs=True)
    last=zvs.bm3d(last,sigma=[2,1,1],sigma2=[0.8,0.5,0.5],radius=1,preset='np',vt=1,mode='cuda_rtc')
    # more produces
    return last

if __name__ == '__main__':
    videos = getSources()
    for i in videos:
        encodeVideo(i)
```
