# Lambholl's VapourSynth Functions

## Requirements:
* `dual_out.py` by YomikoR and RyougiKukoc. You can download [here](https://github.com/lpsub-114514/Encode-Tools/blob/main/dual_out.py)
  
## Functions:
* `encodeProcess` (decorator)
* `down8d` copied from ksks and x_x
* `getSources`
* `rpChecker` Modified from lazybee
* Producing...

#### getSources
Get a list of file. Drag files into cmd window and enter to add. Enter an empty line to end adding.  
得到一个文件名列表，将需要压制的片源文件依次拖拽进窗口回车，一行对应一个文件，输入空行以结束  

#### encodeProcess
Args: `sourceType='Web', ext='', encodeTypes=['CHS','CHT','HEVC'], subrender='libass', chapter=None, delFiles=False, rpc=True, `  
`qaac_path = 'qaac64.exe', ffmpeg_path = 'ffmpeg', x264_path='x264.exe', x265_path='x265.exe', mp4box_path='MP4Box.exe', mkvmerge_path='mkvmerge.exe', eac3to_path='eac3to.exe', param_x264='"{0}" --demuxer y4m --preset veryslow --profile high --crf 18 --colorprim bt709 --transfer bt709 --colormatrix bt709 -o "{1}.mp4" -', param_x265='"{0}" --y4m -D 10 --preset slower --crf 18 -o "{1}.mp4" -'`  
  
e.g. 
```python
import vapoursynth as vs
core=vs.core
import lamvsfunc as lamvs
import zvs

@lamvs.encodeProcess(encodeTypes=['JPSC','JPTC','HEVC'], delFiles=True, rpc=True)
def encodeVideo(source=''):
    src=core.lsmas.LWLibavSource(source).fmtc.bitdepth(bits=16,dmode=1)
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
  
#### rpChecker
Args: `source, ripped, subtitle='', message="rip", output='rpc.txt', subrender=core.assrender.TextSub`
