import vapoursynth as vs
from vapoursynth import core
import dual_out, subprocess, os, gc, sys

'''
Functions:
getSources
down8d
encodeProcess
rpChecker
getMimeType
subsetFonts
'''

# Get a list of file
# Drag files into cmd window and enter to add. Enter an empty line to end adding. 
def getSources():
    result = []
    while True:
        inText = input('> ')
        if inText == '':
            return result
        else:
            result.append(inText.replace('\"',''))

# Down8 with dmode8 (Copied from ksks and x_x.)
def down8d(clip):
    amp1=clip.fmtc.bitdepth(bits=8,dmode=9,ampo=1.5)
    amp2=clip.fmtc.bitdepth(bits=8,dmode=9,ampo=2)
    dmask=core.std.Expr(clip.std.ShufflePlanes(0,vs.GRAY).resize.Point(format=vs.GRAY8,dither_type='none'),'x 100 > 0 255 ?')
    res_d=core.std.MaskedMerge(amp1,amp2,dmask)
    return res_d

def getMimeType(ext: str) -> str:
    """Map font extensions to MKV attachment MIME types."""
    ext_map = {
        '.ttf': 'application/x-truetype-font',
        '.ttc': 'application/x-truetype-font',
        '.otf': 'application/vnd.ms-opentype',
        '.woff': 'font/woff',
        '.woff2': 'font/woff2'
    }
    return ext_map.get(ext.lower(), 'application/octet-stream')

def subsetFonts(sub_paths, fonts_dir, font_out_dir, assfontsubset_path="AssFontSubset.Console.exe"):
    """Run AssFontSubset to process subtitle fonts."""
    print("Subsetting fonts...")
    
    if not os.path.exists(font_out_dir):
        os.makedirs(font_out_dir)

    cmd = [assfontsubset_path] + sub_paths + [
        "--fonts", fonts_dir,
        "--output", font_out_dir
    ]
    
    try:
        subprocess.run(
            cmd, check=True, input='\n', 
            capture_output=True, text=True, 
            encoding='utf-8', errors='ignore'
        )
        print(f"  -> Fonts subsetting complete. Saved to: {font_out_dir}")
        
    except subprocess.CalledProcessError as e:
        valid_exts = ('.ttf', '.ttc', '.otf', '.woff', '.woff2')
        files_generated = any(
            f.lower().endswith(valid_exts) for f in os.listdir(font_out_dir)
        ) if os.path.exists(font_out_dir) else False
        
        combined_output = f"{e.stdout or ''}\n{e.stderr or ''}"
        err_lines = [line for line in combined_output.splitlines() if "|ERR|" in line]
        
        if files_generated:
            print("  -> Fonts subsetting complete (bypassed exit prompt).")
            if err_lines:
                for err in err_lines:
                    print(f"     {err}")
        else:
            print(f"  -> Font subsetting failed. Exit code: {e.returncode}")
            for line in err_lines:
                print(f"     {line}")
            raise RuntimeError("Font subsetting failed. Aborting encode.")
            
    except FileNotFoundError:
        print(f"  -> Error: {assfontsubset_path} not found in PATH.")
        raise FileNotFoundError(f"{assfontsubset_path} not found in PATH.")

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
def encodeProcess(sourceType='Web', ext='', encodeTypes=['CHS','CHT','HEVC'], subrender='libass', chapter=None, delFiles=False, rpc=True, 
    fonts_dir=None, font_out_dir=None, subtitles_info=None, video_title="", assfontsubset_path="AssFontSubset.Console.exe", out_name_templates=None,
    qaac_path='qaac64.exe', ffmpeg_path='ffmpeg', x264_path='x264.exe', x265_path='x265.exe', mp4box_path='MP4Box.exe', mkvmerge_path='mkvmerge.exe', eac3to_path='eac3to.exe', 
    mktorrent_path='mktorrent.exe', create_torrent=False, trackers=None,
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
                raise FileNotFoundError('Source file extention doesn\'t match. It should have been '+extSource)
            
            source_dir = os.path.dirname(source) or '.'
            base_in_name = os.path.basename(source)[:-len(extSource)]
            resolved_fonts_dir = fonts_dir if fonts_dir else os.path.join(source_dir, 'fonts')
            resolved_font_out_dir = font_out_dir if font_out_dir else source[:-len(extSource)] + '-font-output'
            
            if 'HEVC' in encodeTypes and subtitles_info:
                subtitle_paths = []
                for sub_cfg in subtitles_info:
                    verName = {'CHS':'sc', 'CHT':'tc', 'JPSC':'jpsc', 'JPTC': 'jptc'}[sub_cfg.get("type")]
                    sp = source[:-len(extSource)] + f'.{verName}.ass'
                    if not os.path.exists(sp):
                        raise FileNotFoundError(f"Subtitle file missing: {sp}")
                    subtitle_paths.append(sp)
                subsetFonts(subtitle_paths, resolved_fonts_dir, resolved_font_out_dir, assfontsubset_path)
                
            file2del = []
            if sourceType == 'Web':
                subprocess.run([ffmpeg_path, '-i', source, '-c:a', 'copy', '-vn', source[:-len(extSource)]+'.m4a'], shell=True)
                if not os.path.exists(source[:-len(extSource)]+'.m4a'):
                    raise FileNotFoundError(f"Failed to create {source[:-len(extSource)]+'.m4a'}")
                file2del.append(source[:-len(extSource)]+'.m4a')
            elif sourceType == 'BD':
                subprocess.run([eac3to_path, source, source[:-len(extSource)]+'.flac'], shell=True)
                if not os.path.exists(source[:-len(extSource)]+'.flac'):
                    raise FileNotFoundError(f"Failed to create {source[:-len(extSource)]+'.flac'}")
                subprocess.run([ffmpeg_path, '-i', source, '-f', 'wav', '-vn', '-', '|', qaac_path, '-V', '127', '-', '-o', source[:-len(extSource)]+'.m4a'], shell=True)
                if not os.path.exists(source[:-len(extSource)]+'.m4a'):
                    raise FileNotFoundError(f"Failed to create {source[:-len(extSource)]+'.m4a'}")
                file2del.append(source[:-len(extSource)]+'.flac')
                file2del.append(source[:-len(extSource)]+'.m4a')
            
            last = func(*args, **kw)
            last2 = down8d(last)
            encodeParams = []
            
            for i in range(len(encodeTypes)):
                encode_type = encodeTypes[i]
                encodeParams.append([])
                if encode_type=='HEVC':
                    extAudio = {'Web':'.m4a', 'BD':'.flac'}[sourceType]
                    mute_video = source[:-len(extSource)]+'.mute.mp4'
                    if out_name_templates and encode_type in out_name_templates:
                        custom_name = out_name_templates[encode_type].format(base_in_name)
                        if not custom_name.lower().endswith('.mkv'):
                            custom_name += '.mkv'
                        output_mkv = os.path.join(source_dir, custom_name)
                    else:
                        output_mkv = source[:-len(extSource)]+'.hevc.mkv'
                    
                    mux_cmd = [mkvmerge_path, '--output', output_mkv]
                    if video_title and subtitles_info:
                        mux_cmd.extend(['--title', video_title.format(base_in_name)])
                        
                    mux_cmd.extend([
                        '--language', '0:und', '--default-track', '0:yes', mute_video,
                        '--language', '0:jpn', '--default-track', '0:yes', source[:-len(extSource)]+extAudio
                    ])

                    if subtitles_info:
                        for sub_cfg in subtitles_info:
                            sub_file_path = source[:-len(extSource)] + f'.{sub_cfg.get("type")}.ass'
                            mux_cmd.extend([
                                "--language", f"0:{sub_cfg.get('language', 'zho')}",
                                "--track-name", f"0:{sub_cfg.get('track_name', '')}",
                                "--default-track", f"0:{'yes' if sub_cfg.get('is_default', False) else 'no'}",
                                sub_file_path
                            ])
                        
                        if font_out_dir and os.path.isdir(font_out_dir):
                            for filename in os.listdir(font_out_dir):
                                font_path = os.path.join(font_out_dir, filename)
                                if os.path.isfile(font_path):
                                    _, ext_font = os.path.splitext(filename)
                                    if ext_font.lower() in ['.ttf', '.ttc', '.otf', '.woff', '.woff2']:
                                        mux_cmd.extend([
                                            "--attachment-mime-type", getMimeType(ext_font),
                                            "--attach-file", font_path
                                        ])
                    
                    if chapter:
                        mux_cmd.extend(['--chapter-language', 'en', '--chapters', source[:-len(extSource)]+'.txt'])

                    encodeParams[i] = [
                        last.fmtc.bitdepth(bits=10,dmode=8,patsize=64), 
                        param_x265.format(x265_path, source[:-len(extSource)]+'.mute'), 
                        mux_cmd, 
                        output_mkv,
                        '',
                    ]
                    file2del.append(mute_video)
                else:
                    verName = {'CHS':'sc', 'CHT':'tc', 'JPSC':'jpsc', 'JPTC': 'jptc'}[encodeTypes[i]]
                    if not os.path.isfile(source[:-len(extSource)]+f'.{verName}.ass'):
                        raise FileNotFoundError('Your subtitle files are not ready yet!\nMiss '+source[:-len(extSource)]+f'.{verName}.ass')
                    
                    if out_name_templates and encode_type in out_name_templates:
                        custom_name = out_name_templates[encode_type].format(base_in_name)
                        if not custom_name.lower().endswith('.mp4'):
                            custom_name += '.mp4'
                        output_mp4 = os.path.join(source_dir, custom_name)
                    else:
                        output_mp4 = source[:-len(extSource)]+f'.{verName}.mp4'
                    
                    encodeParams[i] = [
                        sub(last2, source[:-len(extSource)]+f'.{verName}.ass'), 
                        param_x264.format(x264_path, source[:-len(extSource)]+f'.mute.{verName}'), 
                        [mp4box_path, '-add', source[:-len(extSource)]+f'.mute.{verName}.mp4', '-add', source[:-len(extSource)]+'.m4a', '-new', output_mp4],
                        output_mp4, source[:-len(extSource)]+f'.{verName}.ass',
                    ]
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
                if not os.path.exists(i[3]):
                    raise FileNotFoundError(f"Failed to create {i[3]}")
            
            if delFiles:
                for i in file2del:
                    os.remove(i)
            if rpc:
                for i in range(len(encodes)):
                    rpChecker(source, encodeParams[i][3], subtitle=encodeParams[i][4], subrender=sub, message=encodeTypes[i], output=encodeParams[i][3]+'.rpc.txt')
            if create_torrent:
                for i in range(len(encodes)):
                    output_video = encodeParams[i][3]
                    makeTorrent(mktorrent_path, output_video, trackers)
            del encodes; del last; del last2
            gc.collect()
        return wrapper
    return decorator

# RPChecker (Modified from lazybee)
def rpChecker(source, ripped, subtitle='', message="rip", output='rpc.txt', subrender=core.assrender.TextSub):
    if type(source)==str:
        src = core.lsmas.LWLibavSource(source)
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

def makeTorrent(mktorrent_path, video_file, trackers_list=None, is_private=False):
    """Generate a .torrent file using mktorrent, calculating piece size dynamically."""
    print(f"\n[Workflow] Creating torrent for {os.path.basename(video_file)}...")
    if not os.path.exists(video_file):
        print(f"  -> Error: Video file not found ({video_file})")
        return
    
    file_size = os.path.getsize(video_file)
    if file_size <= 512 * 1024**2:       # <= 512 MiB, use 512 KiB
        piece_size = "19"
    elif file_size <= 1024 * 1024**2:    # <= 1 GiB, use 1 MiB
        piece_size = "20"
    elif file_size <= 2048 * 1024**2:    # <= 2 GiB, use 2 MiB
        piece_size = "21"
    elif file_size <= 4096 * 1024**2:    # <= 4 GiB, use 4 MiB
        piece_size = "22"
    elif file_size <= 8192 * 1024**2:    # <= 8 GiB, use 8 MiB
        piece_size = "23"
    else:                                # > 8 GiB, use 16 MiB
        piece_size = "24"
    
    working_dir = os.path.dirname(video_file) or '.'
    video_basename = os.path.basename(video_file)
    output_basename = video_basename + ".torrent"
    output_torrent_full = video_file + ".torrent"

    cmd = [mktorrent_path, "-o", output_basename, "-l", piece_size]
    
    if is_private:
        cmd.append("-p")
        
    if trackers_list and isinstance(trackers_list, list):
        cmd.extend(["-a", ",".join(trackers_list)])
    else:
        print("  -> Warning: No trackers provided. Creating trackerless torrent.")
        
    cmd.append(video_basename)

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, cwd=working_dir)
        print(f"  -> Success. Torrent saved to: {output_torrent_full}")
    except subprocess.CalledProcessError as e:
        print(f"  -> Torrent creation failed. Exit code: {e.returncode}")
    except FileNotFoundError:
        print("  -> Error: mktorrent not found in PATH.")