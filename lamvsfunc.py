import vapoursynth as vs
from vapoursynth import core
import dual_out, subprocess, os, gc, sys

'''
Functions:
down8d
encodeProcess
'''


# Down8 with dmode8 (Copied from ksks and x_x.)
def down8d(clip):
    amp1=clip.fmtc.bitdepth(bits=8,dmode=9,ampo=1.5)
    amp2=clip.fmtc.bitdepth(bits=8,dmode=9,ampo=2)
    dmask=core.std.Expr(clip.std.ShufflePlanes(0,vs.GRAY).resize.Point(format=vs.GRAY8,dither_type='none'),'x 100 > 0 255 ?')
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
def encodeProcess(sourceType='Web', ext='', encodeTypes=['CHS','CHT','HEVC'], subrender='libass', chapter=None, delFiles=False, rpc=True, qaac_path = 'qaac64.exe', ffmpeg_path = 'ffmpeg', x264_path='x264.exe', x265_path='x265.exe', mp4box_path='MP4Box.exe', mkvmerge_path='mkvmerge.exe', eac3to_path='eac3to.exe', 
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
                            '--language', '0:jpn', '--default-track', '0:yes', source[:-len(extSource)]+extAudio], 
                            source[:-len(extSource)]+'.hevc.mkv', '']
                    if chapter:
                        encodeParams[i][2] += ['--chapter-language', 'en', '--chapters', source[:-len(extSource)]+'.txt']
                    file2del.append(source[:-len(extSource)]+'.mute.mp4')
                else:
                    verName = {'CHS':'sc', 'CHT':'tc', 'JPSC':'jpsc', 'JPTC': 'jptc'}[encodeTypes[i]]
                    if not os.path.isfile(source[:-len(extSource)]+f'.{verName}.ass'):
                        raise TypeError('Your subtitle files are not ready yet!\nMiss '+source[:-len(extSource)]+f'.{verName}.ass')
                    encodeParams[i] = [sub(last2, source[:-len(extSource)]+f'.{verName}.ass'), 
                            param_x264.format(x264_path, source[:-len(extSource)]+f'.mute.{verName}'), 
                            [mp4box_path, '-add', source[:-len(extSource)]+f'.mute.{verName}.mp4', '-add', source[:-len(extSource)]+'.m4a', '-new', source[:-len(extSource)]+f'.{verName}.mp4'], source[:-len(extSource)]+f'.{verName}.mp4', source[:-len(extSource)]+f'.{verName}.ass']
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
            if delFiles:
                for i in file2del:
                    os.remove(i)
            if rpc:
                for i in range(len(encodes)):
                    rpChecker(source, encodeParams[i][3], subtitle=encodeParams[i][4], subrender=sub, message=encodeTypes[i], output=encodeParams[i][3]+'.rpc.txt')
            del encodes; del last; del last2
            gc.collect()
        return wrapper
    return decorator


# RPChecker (Modified from lazybee)
def rpChecker(source, ripped, subtitle='', message="rip", output='rpc.txt', subrender=core.assrender.TextSub):
    if type(source)==str:
        src = core.lsmas.LWLibavSource(source)[:100]
    elif type(source)==vs.VideoNode:
        src = source
    else:
        raise TypeError()
    rip = core.lsmas.LWLibavSource(ripped,cache=0)
    if subtitle:
        src = subrender(src, subtitle)
    assert rip.format.color_family in [vs.YUV, vs.GRAY], "only support YUV or Gray input"

    def force8bit(clip):
        if clip.format.bits_per_sample == 8:
            return clip
        return clip.resize.Spline64(format=clip.format.replace(bits_per_sample=8).id, dither_type='none')
    src = force8bit(src)
    rip = force8bit(rip)
    
    if src.width != rip.width or src.height != rip.height:
        src = src.resize.Bicubic(rip.width, rip.height)
        
    src_planes = [ src.std.ShufflePlanes(i, vs.GRAY) for i in range(3) ]
    rip_planes = [ rip.std.ShufflePlanes(i, vs.GRAY) for i in range(3) ]
    cmp_planes = [ core.complane.PSNR(a, b) for (a, b) in zip(rip_planes, src_planes) ]
    
    broken_frame = False
    total_frames = len(src)
    print(f"\nRP Checker is analyzing {message}:")
    for i in range(total_frames):
        PSNR_Y = cmp_planes[0].get_frame(i).props.PlanePSNR
        PSNR_U = cmp_planes[1].get_frame(i).props.PlanePSNR
        PSNR_V = cmp_planes[2].get_frame(i).props.PlanePSNR
        
        if (i % 100 == 0):
            output_blank = " " * 50
            sys.stdout.write(f"\r{output_blank}")
            sys.stdout.write(f"\rProcessing frame {i}/{total_frames}: Y-{round(PSNR_Y)} U-{round(PSNR_U)} V-{round(PSNR_V)}")
    
        if (PSNR_Y < 30) | (PSNR_U < 40) | (PSNR_V < 40):
            with open(output, 'a') as f:
                if not broken_frame:
                    broken_frame = True
                    print(f"RPC results for {message}", file=f)
                print(f"Possible broken frame {i}: Y-{PSNR_Y} U-{PSNR_U} V-{PSNR_V}", file=f)
    
    if broken_frame:
        print(f"\n\033[;31mRP Checker complete for {message}, broken frame found, please check output file!!!\033[0m")
    else:
        print(f"\n\033[;32mRP Checker complete for {message}, no broken frame found\033[0m")
