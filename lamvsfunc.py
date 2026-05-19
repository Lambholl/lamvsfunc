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


def getSources():
    """
    Get a list of file. 
    Drag files into cmd window and enter to add. Enter an empty line to end adding. 
    """
    result = []
    while True:
        inText = input('> ')
        if inText == '':
            return result
        else:
            result.append(inText.replace('\"', ''))


def down8d(clip):
    """Down8 with dmode8 (Copied from ksks and x_x.)"""
    amp1 = clip.fmtc.bitdepth(bits=8, dmode=9, ampo=1.5)
    amp2 = clip.fmtc.bitdepth(bits=8, dmode=9, ampo=2)
    dmask = core.std.Expr(
        clip.std.ShufflePlanes(0, vs.GRAY).resize.Point(format=vs.GRAY8, dither_type='none'),
        'x 100 > 0 255 ?'
    )
    res_d = core.std.MaskedMerge(amp1, amp2, dmask)
    return res_d


def getMimeType(ext: str) -> str:
    """Map font extensions to MKV attachment MIME types."""
    ext_map = {
        '.ttf': 'application/x-truetype-font',
        '.ttc': 'application/x-truetype-font',
        '.otf': 'application/vnd.ms-opentype',
        '.woff': 'font/woff',
        '.woff2': 'font/woff2',
    }
    return ext_map.get(ext.lower(), 'application/octet-stream')


def subsetFonts(sub_paths: list[str],
                fonts_dir: str,
                font_out_dir: str,
                assfontsubset_path: str = "AssFontSubset.Console.exe"):
    """Run AssFontSubset to process subtitle fonts."""
    print("Subsetting fonts...")

    if not os.path.exists(font_out_dir):
        os.makedirs(font_out_dir)

    cmd = [assfontsubset_path, *sub_paths, "--fonts", fonts_dir, "--output", font_out_dir]

    try:
        subprocess.run(cmd,
                       check=True,
                       capture_output=True,
                       text=True,
                       encoding='utf-8',
                       errors='replace')
        print(f"  -> Fonts subsetting complete. Saved to: {font_out_dir}")

    except subprocess.CalledProcessError as e:
        combined_output = f"{e.stdout or ''}\n{e.stderr or ''}"
        err_lines = [
            line for line in combined_output.splitlines() if "|ERR|" in line
        ]

        print(f"  -> Font subsetting failed. Exit code: {e.returncode}")
        for line in err_lines:
            print(f"     {line}")
        raise RuntimeError("Font subsetting failed. Aborting encode.")

    except FileNotFoundError:
        print(f"  -> Error: {assfontsubset_path} not found in PATH.")
        raise FileNotFoundError(f"{assfontsubset_path} not found in PATH.")


def encodeProcess(
    sourceType='Web',
    ext='',
    encodeTypes: None|list[str]=['CHS', 'CHT', 'HEVC'],
    subrender='libass',
    chapter=None,
    delFiles=True,
    rpc=True,
    fonts_dir: None|str=None,
    font_out_dir: None|str=None,
    subtitles_info=None,
    video_title="",
    assfontsubset_path="AssFontSubset.Console.exe",
    out_name_templates=None,
    qaac_path='qaac64.exe',
    ffmpeg_path='ffmpeg',
    x264_path='x264.exe',
    x265_path='x265.exe',
    mp4box_path='MP4Box.exe',
    mkvmerge_path='mkvmerge.exe',
    eac3to_path='eac3to.exe',
    mktorrent_path='mktorrent.exe',
    clip_frames: None|list[int]=None,
    create_torrent=False,
    trackers: None|list[int]=None,
    param_x264='"{0}" --demuxer y4m --preset veryslow --profile high --crf 18 --colorprim bt709 --transfer bt709 --colormatrix bt709 -o "{1}.mp4" -',
    param_x265='"{0}" --y4m -D 10 --preset slower --crf 18 -o "{1}.mp4" -'
):
    """
    Decorator while encoding
    
    Usage: 
        @lamvsfunc.encodeProcess(...)
        def encodeVideo(source='...'):

    Args:
        sourceType (str): 'BD' or 'Web'
        encodeTypes (list[str]): CHS, CHT, JPSC, JPTC, HEVC;
            subs exts: .sc  .tc  .jpsc .jptc  None
        delFiles (bool): whether to delete mute videos and audio file after encoding
        chapter (bool): Default False on Web and True on BD, accept txt files with the same filenames as source files
    """
    # 参数前置校验
    KNOWN_ENCODE_TYPES = {'CHS', 'CHT', 'JPSC', 'JPTC', 'HEVC'}
    KNOWN_SUB_TYPES = {'CHS', 'CHT', 'JPSC', 'JPTC'}
    if sourceType not in ('Web', 'BD'):
        raise ValueError(f"sourceType must be 'Web' or 'BD', got {sourceType!r}")
    if not encodeTypes:
        raise ValueError('encodeTypes cannot be empty')
    unknown = [t for t in encodeTypes if t not in KNOWN_ENCODE_TYPES]
    if unknown:
        raise ValueError(f'Unknown encodeTypes {unknown}; expected subset of {sorted(KNOWN_ENCODE_TYPES)}')
    if subtitles_info:
        for i, sub_cfg in enumerate(subtitles_info):
            if not isinstance(sub_cfg, dict):
                raise TypeError(f'subtitles_info[{i}] must be a dict, got {type(sub_cfg).__name__}')
            if sub_cfg.get('type') not in KNOWN_SUB_TYPES:
                raise ValueError(f"subtitles_info[{i}]['type']={sub_cfg.get('type')!r}; expected one of {sorted(KNOWN_SUB_TYPES)}")
    if clip_frames is not None:
        if not isinstance(clip_frames, list) or any(not isinstance(f, int) or f <= 0 for f in clip_frames):
            raise ValueError('clip_frames must be a list of positive ints')
        if any(clip_frames[i] >= clip_frames[i+1] for i in range(len(clip_frames)-1)):
            raise ValueError('clip_frames must be strictly increasing')

    # Source
    # Web means AAC and BD means FLAC
    extSource = {'Web': '.mkv', 'BD': '.m2ts'}[sourceType] if not ext else ext
    sub = {
        'libass': core.assrender.TextSub,
        'vsfiltermod': core.vsfm.TextSubMod
    }[subrender]
    chapter = {
        'Web': False,
        'BD': True
    }[sourceType] if chapter == None else chapter

    if clip_frames:
        if any(t != 'HEVC' for t in encodeTypes):
            raise ValueError("clip_frames mode only supports encodeTypes=['HEVC']; subtitle-burning types are disallowed because src subtitles can't be sliced losslessly here.")
        chapter = False
        create_torrent = False

    # 音频切割
    def cut_audio(src_audio, out_audio, start_sec, end_sec, is_lossless, ffmpeg_path, qaac_path):
        if is_lossless:
            cmd = [ffmpeg_path, '-y', '-i', src_audio, '-ss', str(start_sec), '-to', str(end_sec), '-vn', '-acodec', 'flac', out_audio]
            subprocess.run(cmd)
            return
        # m4a: ffmpeg writes a temp wav, qaac encodes to m4a
        tmp_wav = out_audio + '.tmp.wav'
        subprocess.run([ffmpeg_path, '-y', '-ss', str(start_sec), '-to', str(end_sec), '-i', src_audio, '-vn', '-f', 'wav', tmp_wav])
        subprocess.run([qaac_path, '-V', '127', tmp_wav, '-o', out_audio])
        os.remove(tmp_wav)

    # 参数生成
    def build_encode_params(
        encode_type, video_clip, audio_file, source, extSource, base_in_name, source_dir,
        out_name_templates, x264_path, x265_path, mp4box_path, mkvmerge_path, param_x264, param_x265,
        chapter, subtitles_info, font_out_dir, video_title, subrender, verName=None, is_clip=False, seg_idx=None
    ):
        params = {}
        if encode_type == 'HEVC':
            mute_video = f"{source[:-len(extSource)]}{f'.seg{seg_idx}' if is_clip else ''}.mute"
            if (out_name_templates) and (encode_type in out_name_templates):
                custom_name = out_name_templates[encode_type].format(base_in_name)
                if not custom_name.lower().endswith('.mkv'):
                    custom_name += '.mkv'
                if is_clip:
                    custom_name = custom_name[:-4] + f'.seg{seg_idx}.mkv'
                output_mkv = os.path.join(source_dir, custom_name)
            else:
                output_mkv = f"{source[:-len(extSource)]}{f'.seg{seg_idx}' if is_clip else ''}.hevc.mkv"
            mux_cmd = [mkvmerge_path, '--output', output_mkv]
            if video_title:
                mux_cmd.extend(['--title',  video_title.format(base_in_name)])
            mux_cmd.extend([
                '--language', '0:und', '--default-track', '0:yes',
                mute_video+'.mp4', '--language', '0:jpn', '--default-track',
                '0:yes', audio_file
            ])
            # 字幕和字体（仅非分段）
            if subtitles_info and not is_clip:
                for sub_cfg in subtitles_info:
                    sub_verName = {'CHS': 'sc', 'CHT': 'tc', 'JPSC': 'jpsc', 'JPTC': 'jptc'}[sub_cfg.get("type")]
                    sub_file_path = source[:-len(extSource)] + f'.{sub_verName}.ass'
                    mux_cmd.extend([
                        "--language",
                        f"0:{sub_cfg.get('language', 'chi')}",
                        "--track-name",
                        f"0:{sub_cfg.get('track_name', '')}",
                        "--default-track",
                        f"0:{'yes' if sub_cfg.get('is_default', False) else 'no'}",
                        sub_file_path
                    ])
                if font_out_dir and os.path.isdir(font_out_dir):
                    for filename in os.listdir(font_out_dir):
                        font_path = os.path.join(font_out_dir, filename)
                        if os.path.isfile(font_path):
                            _, ext_font = os.path.splitext(filename)
                            if ext_font.lower() in ['.ttf', '.ttc', '.otf', '.woff', '.woff2']:
                                mux_cmd.extend([
                                    "--attachment-mime-type",
                                    getMimeType(ext_font),
                                    "--attach-file", font_path
                                ])
            # 章节（仅非分段）
            if chapter and not is_clip:
                mux_cmd.extend([
                    '--chapter-language', 'en', '--chapters',
                    source[:-len(extSource)] + '.txt'
                ])
            params = {
                'encode_type': encode_type,
                'video': video_clip,
                'encode_cmd': param_x265.format(x265_path, mute_video),
                'mux_cmd': mux_cmd,
                'output': output_mkv,
                'subtitle': '',
                'mute_video': mute_video+'.mp4'
            }
        else:
            if not verName:
                raise ValueError('verName required for non-HEVC')
            if (out_name_templates) and (encode_type in out_name_templates):
                custom_name = out_name_templates[encode_type].format(base_in_name)
                if not custom_name.lower().endswith('.mp4'):
                    custom_name += '.mp4'
                if is_clip:
                    custom_name = custom_name[:-4] + f'.seg{seg_idx}.mp4'
                output_mp4 = os.path.join(source_dir, custom_name)
            else:
                output_mp4 = f"{source[:-len(extSource)]}{f'.seg{seg_idx}' if is_clip else ''}.{verName}.mp4"
            mute_mp4 = f"{source[:-len(extSource)]}{f'.seg{seg_idx}' if is_clip else ''}.mute.{verName}.mp4"
            mux_cmd = [mp4box_path, '-add', mute_mp4, '-add', audio_file, '-new', output_mp4]
            if chapter and not is_clip:
                mux_cmd = mux_cmd[:-2] + ['-chap', source[:-len(extSource)] + '.txt'] + mux_cmd[-2:]
            params = {
                'encode_type': encode_type,
                'video': video_clip,
                'encode_cmd': param_x264.format(x264_path, mute_mp4[:-4]),
                'mux_cmd': mux_cmd,
                'output': output_mp4,
                'subtitle': f"{source[:-len(extSource)]}.{verName}.ass",
                'mute_video': mute_mp4
            }
        return params

    def decorator(func):
        def wrapper(*args, **kw):
            source = args[0]
            if not source.endswith(extSource):
                raise FileNotFoundError(f'Source file extention doesn\'t match. It should have been {extSource}')
            if chapter:
                chapter_txt = source[:-len(extSource)] + '.txt'
                if not os.path.exists(chapter_txt):
                    raise FileNotFoundError(f'chapter=True but chapter file not found: {chapter_txt}')
            source_dir = os.path.dirname(source) or '.'
            base_in_name = os.path.basename(source)[:-len(extSource)]
            resolved_fonts_dir = fonts_dir if fonts_dir else os.path.join(source_dir, 'fonts')
            resolved_font_out_dir = font_out_dir if font_out_dir else source[:-len(extSource)] + '-font-output'
            if 'HEVC' in encodeTypes and subtitles_info:
                subtitle_paths = []
                for sub_cfg in subtitles_info:
                    verName = {'CHS': 'sc', 'CHT': 'tc', 'JPSC': 'jpsc', 'JPTC': 'jptc'}[sub_cfg.get("type")]
                    sp = source[:-len(extSource)] + f'.{verName}.ass'
                    if not os.path.exists(sp):
                        raise FileNotFoundError(f"Subtitle file missing: {sp}")
                    subtitle_paths.append(sp)
                subsetFonts(subtitle_paths, resolved_fonts_dir, resolved_font_out_dir, assfontsubset_path)
            file2del = []
            # 抽取音频
            if sourceType == 'Web':
                subprocess.run([ffmpeg_path, '-i', source, '-c:a', 'copy', '-vn', source[:-len(extSource)] + '.m4a'])
                if not os.path.exists(source[:-len(extSource)] + '.m4a'):
                    raise FileNotFoundError(f"Failed to create {source[:-len(extSource)]+'.m4a'}")
                file2del.append(source[:-len(extSource)] + '.m4a')
                src_audio_file = source[:-len(extSource)] + '.m4a'
            elif sourceType == 'BD':
                flac_path = source[:-len(extSource)] + '.flac'
                m4a_path = source[:-len(extSource)] + '.m4a'
                has_hevc = 'HEVC' in encodeTypes
                has_264 = any(t != 'HEVC' for t in encodeTypes)
                if has_hevc:
                    subprocess.run([eac3to_path, source, flac_path])
                    if not os.path.exists(flac_path):
                        raise FileNotFoundError(f"Failed to create {flac_path}")
                    file2del.append(flac_path)
                if has_264:
                    ffmpeg_proc = subprocess.Popen(
                        [ffmpeg_path, '-i', source, '-f', 'wav', '-vn', '-'],
                        stdout=subprocess.PIPE,
                    )
                    qaac_proc = subprocess.Popen(
                        [qaac_path, '-V', '127', '-', '-o', m4a_path],
                        stdin=ffmpeg_proc.stdout,
                    )
                    ffmpeg_proc.stdout.close()
                    qaac_proc.communicate()
                    ffmpeg_proc.wait()
                    if not os.path.exists(m4a_path):
                        raise FileNotFoundError(f"Failed to create {m4a_path}")
                    file2del.append(m4a_path)
                src_audio_file = flac_path if has_hevc else m4a_path
            last: vs.VideoNode = func(*args, **kw)
            last2 = down8d(last)
            encodeParamsList = []
            # 分段处理
            if clip_frames:
                length = last.num_frames
                pieces = []
                audios = []
                lastI = 0
                for i in clip_frames:
                    if i>length:
                        break
                    if lastI!=i:
                        pieces.append([lastI, i])
                        audios.append([lastI*last.fps_den/last.fps_num, i*last.fps_den/last.fps_num])
                    lastI = i
                if lastI < length:
                    pieces.append([lastI, length])
                    audios.append([lastI*last.fps_den/last.fps_num, length*last.fps_den/last.fps_num])
                # 对每个分段生成参数
                for seg_idx, ((start, end), (astart, aend)) in enumerate(zip(pieces, audios)):
                    for encode_type in encodeTypes:
                        is_lossless = (sourceType == 'BD' and encode_type == 'HEVC')
                        # 音频切割
                        seg_audio = f"{source[:-len(extSource)]}.seg{seg_idx}{'.flac' if is_lossless else '.m4a'}"
                        cut_audio(src_audio_file, seg_audio, astart, aend, is_lossless, ffmpeg_path, qaac_path)
                        file2del.append(seg_audio)
                        # 视频切片
                        if encode_type == 'HEVC':
                            video_clip = last[start:end].fmtc.bitdepth(bits=10, dmode=8, patsize=64)
                            params = build_encode_params(
                                encode_type, video_clip, seg_audio, source, extSource, base_in_name, source_dir,
                                out_name_templates, x264_path, x265_path, mp4box_path, mkvmerge_path, param_x264, param_x265,
                                False, subtitles_info, resolved_font_out_dir, video_title, subrender, None, True, seg_idx
                            )
                        else:
                            verName = {'CHS': 'sc', 'CHT': 'tc', 'JPSC': 'jpsc', 'JPTC': 'jptc'}[encode_type]
                            # 先sub再切片
                            video_clip = sub(last2, source[:-len(extSource)] + f'.{verName}.ass')[start:end]
                            params = build_encode_params(
                                encode_type, video_clip, seg_audio, source, extSource, base_in_name, source_dir,
                                out_name_templates, x264_path, x265_path, mp4box_path, mkvmerge_path, param_x264, param_x265,
                                False, subtitles_info, resolved_font_out_dir, video_title, subrender, verName, True, seg_idx
                            )
                        params['frame_range'] = (start, end)
                        params['seg_idx'] = seg_idx
                        encodeParamsList.append(params)
            else:
                # 整体处理
                for encode_type in encodeTypes:
                    if encode_type == 'HEVC':
                        video_clip = last.fmtc.bitdepth(bits=10, dmode=8, patsize=64)
                        params = build_encode_params(
                            encode_type, video_clip, src_audio_file, source, extSource, base_in_name, source_dir,
                            out_name_templates, x264_path, x265_path, mp4box_path, mkvmerge_path, param_x264, param_x265,
                            chapter, subtitles_info, resolved_font_out_dir, video_title, subrender
                        )
                    else:
                        verName = {'CHS': 'sc', 'CHT': 'tc', 'JPSC': 'jpsc', 'JPTC': 'jptc'}[encode_type]
                        if not os.path.isfile(source[:-len(extSource)] + f'.{verName}.ass'):
                            raise FileNotFoundError('Your subtitle files are not ready yet!\nMissing ' + source[:-len(extSource)] + f'.{verName}.ass')
                        video_clip = sub(last2, source[:-len(extSource)] + f'.{verName}.ass')
                        params = build_encode_params(
                            encode_type, video_clip, src_audio_file, source, extSource, base_in_name, source_dir,
                            out_name_templates, x264_path, x265_path, mp4box_path, mkvmerge_path, param_x264, param_x265,
                            chapter, subtitles_info, resolved_font_out_dir, video_title, subrender, verName
                        )
                    encodeParamsList.append(params)
            # 编码与封装
            encodes = []
            for params in encodeParamsList:
                encodes.append(subprocess.Popen(params['encode_cmd'], stdin=subprocess.PIPE, shell=True))
            dual_out.multiple_outputs([params['video'] for params in encodeParamsList], [p.stdin for p in encodes])
            for p in encodes:
                p.communicate()
            for i, p in enumerate(encodes):
                if p.returncode != 0:
                    raise RuntimeError(f"Encoder {i} ({encodeParamsList[i]['encode_type']}) exited with code {p.returncode}")
            for params in encodeParamsList:
                subprocess.run(params['mux_cmd'])
                if not os.path.exists(params['output']):
                    raise FileNotFoundError(f"Failed to create {params['output']}")
                file2del.append(params['mute_video'])
            # 收尾
            if delFiles:
                for f in file2del:
                    if os.path.exists(f):
                        os.remove(f)
            if rpc:
                for params in encodeParamsList:
                    src_arg = source
                    if params.get('frame_range'):
                        s, e = params['frame_range']
                        src_arg = core.lsmas.LWLibavSource(source)[s:e]
                    msg = params['encode_type']
                    if params.get('seg_idx') is not None:
                        msg = f"{msg} seg{params['seg_idx']}"
                    rpChecker(src_arg, params['output'], subtitle=params['subtitle'], subrender=sub, message=msg, output=params['output'] + '.rpc.txt')
            if create_torrent:
                for params in encodeParamsList:
                    makeTorrent(mktorrent_path, params['output'], trackers)
            del encodes
            del last
            del last2
            gc.collect()
        return wrapper
    return decorator


def rpChecker(source,
              ripped,
              subtitle='',
              message="rip",
              output='rpc.txt',
              subrender=core.assrender.TextSub):
    '''RPChecker (Modified from lazybee)'''
    if type(source) == str:
        src = core.lsmas.LWLibavSource(source)
    elif type(source) == vs.VideoNode:
        src = source
    else:
        raise TypeError()
    rip = core.lsmas.LWLibavSource(ripped, cache=0)
    if subtitle:
        src = subrender(src, subtitle)
    assert rip.format.color_family in [vs.YUV, vs.GRAY], "only support YUV or Gray input"

    def force8bit(clip):
        if clip.format.bits_per_sample == 8:
            return clip
        return clip.resize.Spline64(
            format=clip.format.replace(bits_per_sample=8).id,
            dither_type='none')

    src = force8bit(src)
    rip = force8bit(rip)

    if src.width != rip.width or src.height != rip.height:
        rip = rip.resize.Bicubic(src.width, src.height)

    src_planes = [src.std.ShufflePlanes(i, vs.GRAY) for i in range(3)]
    rip_planes = [rip.std.ShufflePlanes(i, vs.GRAY) for i in range(3)]
    cmp_planes = [
        core.complane.PSNR(a, b) for (a, b) in zip(rip_planes, src_planes)
    ]

    broken_frame = False
    total_frames = len(src)
    print(f"\nRP Checker is analyzing {message}:")
    out_file = None
    try:
        for i in range(total_frames):
            PSNR_Y = cmp_planes[0].get_frame(i).props.PlanePSNR
            PSNR_U = cmp_planes[1].get_frame(i).props.PlanePSNR
            PSNR_V = cmp_planes[2].get_frame(i).props.PlanePSNR

            if (i % 100 == 0):
                output_blank = " " * 50
                sys.stdout.write(f"\r{output_blank}")
                sys.stdout.write(
                    f"\rProcessing frame {i}/{total_frames}: Y-{round(PSNR_Y)} U-{round(PSNR_U)} V-{round(PSNR_V)}"
                )

            if (PSNR_Y < 30) | (PSNR_U < 40) | (PSNR_V < 40):
                if not broken_frame:
                    broken_frame = True
                    out_file = open(output, 'a')
                    print(f"RPC results for {message}", file=out_file)
                print(
                    f"Possible broken frame {i}: Y-{PSNR_Y} U-{PSNR_U} V-{PSNR_V}",
                    file=out_file)
    finally:
        if out_file is not None:
            out_file.close()

    if broken_frame:
        print(
            f"\n\033[;31mRP Checker complete for {message}, broken frame found, please check output file!!!\033[0m"
        )
    else:
        print(
            f"\n\033[;32mRP Checker complete for {message}, no broken frame found\033[0m"
        )


def makeTorrent(mktorrent_path,
                video_file,
                trackers_list=None,
                is_private=False):
    """Generate a .torrent file using mktorrent, calculating piece size dynamically."""
    print(
        f"\n[Workflow] Creating torrent for {os.path.basename(video_file)}...")
    if not os.path.exists(video_file):
        print(f"  -> Error: Video file not found ({video_file})")
        return

    file_size = os.path.getsize(video_file)
    if file_size <= 512 * 1024**2:  # <= 512 MiB, use 512 KiB
        piece_size = "19"
    elif file_size <= 1024 * 1024**2:  # <= 1 GiB, use 1 MiB
        piece_size = "20"
    elif file_size <= 2048 * 1024**2:  # <= 2 GiB, use 2 MiB
        piece_size = "21"
    elif file_size <= 4096 * 1024**2:  # <= 4 GiB, use 4 MiB
        piece_size = "22"
    elif file_size <= 8192 * 1024**2:  # <= 8 GiB, use 8 MiB
        piece_size = "23"
    else:  # > 8 GiB, use 16 MiB
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
        print(
            "  -> Warning: No trackers provided. Creating trackerless torrent."
        )

    cmd.append(video_basename)

    try:
        subprocess.run(cmd,
                       check=True,
                       stdout=subprocess.DEVNULL,
                       cwd=working_dir)
        print(f"  -> Success. Torrent saved to: {output_torrent_full}")
    except subprocess.CalledProcessError as e:
        print(f"  -> Torrent creation failed. Exit code: {e.returncode}")
    except FileNotFoundError:
        print("  -> Error: mktorrent not found in PATH.")
