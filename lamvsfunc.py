import vapoursynth as vs
from vapoursynth import core
import dual_out, subprocess, os, gc

'''
Functions:
down8d
encodeProcess
'''


# Down8 with dmode8(Originately writen by x_x.)
def down8d(clip):
    amp1=clip.fmtc.bitdepth(bits=8,dmode=8,ampo=1.5)
    amp2=clip.fmtc.bitdepth(bits=8,dmode=8,ampo=2)
    dmask=core.std.Expr(clip.std.ShufflePlanes(0,vs.GRAY).fmtc.bitdepth(bits=8),'x 100 > 0 255 ?')
    res_d=core.std.MaskedMerge(amp1,amp2,dmask)
    return res_d

# Decorator while encoding
'''
Usage: 
@lamvsfunc.encodeProcess(...)
encodeVideo(source='...')

sourceType: 'BD' or 'Web'
encodeTypes: CHS, CHT, JPSC, JPTC, HEVC
 subs exts: .sc  .tc  .jpsc .jptc  None
delFiles: whether to delete mute videos and audio file after encoding
chapter: Default False on Web and True on BD, accept txt files with the same filenames as source files
'''
def encodeProcess(sourceType='Web', ext='', encodeTypes=['CHS','CHT','HEVC'], subrender='libass', chapter=None, delFiles=False, qaac_path = 'qaac64.exe', ffmpeg_path = 'ffmpeg', x264_path='x264.exe', x265_path='x265.exe', mp4box_path='MP4Box.exe', mkvmerge_path='mkvmerge.exe', eac3to_path='eac3to.exe', 
    param_x264='"{0}" --demuxer y4m --preset veryslow --profile high --crf 18 --colorprim bt709 --transfer bt709 --colormatrix bt709 -o "{1}.mp4" -', 
    param_x265='"{0}" --y4m -D 10 --preset slower --crf 18 -o "{1}.mp4" -'):
    # Source
    # Web means AAC and BD means FLAC
    extSource = {'Web':'.mkv', 'BD':'.m2ts'}[sourceType] if not ext else ext
    sub = {'libass': core.assrender.TextSub, 'vsfiltermod': core.vsfm.TextSubMod}[subrender]
    chapter = {'Web': False, 'BD': True}[sourceType] if chapter==None else chapter
    def decorator(func):
        def wrapper(*args, **kw):
            source=args[0]
            if source[-len(extSource):] != extSource:
                raise TypeError('Source file extention doesn\'t match. It should have been '+extSource)
            file2del = []
            if sourceType == 'Web':
                subprocess.run([ffmpeg_path, '-i', source, '-c:a', 'copy', '-vn', source[:-len(extSource)]+'.m4a'], shell=True)
                file2del.append(source[:-len(extSource)]+'.m4a')
            elif sourceType == 'BD':
                subprocess.run([eac3to_path, source, source[:-len(extSource)]+'.flac'], shell=True)
                subprocess.run([ffmpeg_path, '-i', source, '-f', 'wav', '-vn', '-', '|', qaac_path, '-V', '127', '-', '-o', source[:-len(extSource)]+'.m4a'], shell=True)
                file2del.append(source[:-len(extSource)]+'.flac')
                file2del.append(source[:-len(extSource)]+'.m4a')
            last = func(*args, **kw)
            last2 = down8d(last)
            encodeParams = []
            for i in range(len(encodeTypes)):
                encodeParams.append([])
                if encodeTypes[i]=='HEVC':
                    extAudio = {'Web':'.m4a', 'BD':'.flac'}[sourceType]
                    encodeParams[i] = [last.fmtc.bitdepth(bits=10,dmode=8,patsize=64), 
                            param_x265.format(x265_path, source[:-len(extSource)]+'.mute'), 
                            [mkvmerge_path, '--output', source[:-len(extSource)]+'.hevc.mkv',
                            '--language', '0:und', '--default-track', '0:yes', source[:-len(extSource)]+'.mute.mp4',
                            '--language', '0:jpn', '--default-track', '0:yes', source[:-len(extSource)]+extAudio]]
                    if chapter:
                        encodeParams[i][2] += ['--chapter-language', 'en', '--chapters', source[:-len(extSource)]+'.txt']
                    file2del.append(source[:-len(extSource)]+'.mute.mp4')
                else:
                    verName = {'CHS':'sc', 'CHT':'tc', 'JPSC':'jpsc', 'JPTC': 'jptc'}[encodeTypes[i]]
                    if not os.path.isfile(source[:-len(extSource)]+f'.{verName}.ass'):
                        raise TypeError('Your subtitle files are not ready yet!\nMiss '+source[:-len(extSource)]+f'.{verName}.ass')
                    encodeParams[i] = [sub(last2, source[:-len(extSource)]+f'.{verName}.ass'), 
                            param_x264.format(x264_path, source[:-len(extSource)]+f'.mute.{verName}'), 
                            [mp4box_path, '-add', source[:-len(extSource)]+f'.mute.{verName}.mp4', '-add', source[:-len(extSource)]+'.m4a', '-new', source[:-len(extSource)]+f'.{verName}.mp4']]
                    if chapter:
                        encodeParams[i][2] = encodeParams[i][2][:-2] + ['-chap', source[:-len(extSource)]+'.txt'] + encodeParams[i][2][-2:]
                    file2del.append(source[:-len(extSource)]+f'.mute.{verName}.mp4')
            encodes = []
            for i in encodeParams:
                encodes.append(subprocess.Popen(i[1] , stdin=subprocess.PIPE, shell=True))
            
            dual_out.multiple_outputs([i[0] for i in encodeParams], [i.stdin for i in encodes])
            
            for i in range(len(encodes)):
                encodes[i].communicate()
            for i in range(len(encodes)):
                encodes[i].wait()
            for i in encodeParams:
                    subprocess.run(i[2], shell=True)
            del encodes; del last; del last2
            if delFiles:
                for i in file2del:
                    os.remove(i)
            gc.collect()
        return wrapper
    return decorator

