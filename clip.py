#!/usr/bin/env python3
"""Turn a Twitch or YouTube excerpt into a vertical Vice City Codex Short."""

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path
from urllib.parse import urlsplit


WIDTH = 1080
HEIGHT = 1920
FPS = 30
# Leave room for AAC packet and video frame rounding in the final MP4.
MAX_RENDER_SECONDS = 59.9
DEFAULT_TEMPLATE = """{lead}

Streamer: {streamer}
Source: {url}

#GTA6 #GTAVI #ViceCityCodex #TheGTA6Codex #Shorts
"""
LOGO_POSITIONS = {
    "top-left": "48:48",
    "top-right": "W-w-48:48",
    "bottom-left": "48:H-h-48",
    "bottom-right": "W-w-48:H-h-48",
}


def timestamp(value):
    match = re.fullmatch(r"([0-9]{2,}):([0-5][0-9]):([0-5][0-9])(?:\.([0-9]{1,3}))?", value)
    if not match:
        raise argparse.ArgumentTypeError("use HH:MM:SS or HH:MM:SS.mmm")
    hours, minutes, seconds, millis = match.groups()
    return (int(hours) * 3600 + int(minutes) * 60 + int(seconds)) * 1000 + int(
        (millis or "").ljust(3, "0")
    )


def facecam_box(value):
    if not re.fullmatch(r"\s*\d+\s*(?:,\s*\d+\s*){3}", value):
        raise argparse.ArgumentTypeError("use x,y,w,h in source pixels")
    x, y, width, height = map(int, value.split(","))
    if min(width, height) < 2:
        raise argparse.ArgumentTypeError("facecam width and height must be at least 2 pixels")
    return x, y, width, height


def source_url(value):
    try:
        url = urlsplit(value)
        host = url.hostname or ""
    except ValueError as error:
        raise argparse.ArgumentTypeError("invalid URL") from error
    domains = ("youtube.com", "youtu.be", "twitch.tv")
    if url.scheme not in ("http", "https") or not any(
        host == domain or host.endswith(f".{domain}") for domain in domains
    ):
        raise argparse.ArgumentTypeError("use a Twitch or YouTube URL")
    if url.username or url.password or url.path.rstrip("/") == "/playlist":
        raise argparse.ArgumentTypeError("use a direct video, VOD, or clip URL")
    return value


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, type=source_url)
    parser.add_argument("--start", required=True, metavar="HH:MM:SS")
    parser.add_argument("--end", required=True, metavar="HH:MM:SS")
    parser.add_argument("--crop-zoom", nargs="?", const=1.25, default=1.0, type=float, metavar="FACTOR",
                        help="center zoom from 1 to 3 (1.25 when passed without a factor)")
    parser.add_argument("--facecam", type=facecam_box, metavar="X,Y,W,H",
                        help="crop a camera panel from the source and place it above the gameplay")
    parser.add_argument("--logo", type=Path, metavar="PNG", help="streamer logo for the entire clip")
    parser.add_argument("--pos", default="top-right", choices=LOGO_POSITIONS, help="logo position")
    parser.add_argument("--hook", default="", help="headline for the first two seconds")
    parser.add_argument("--preview", action="store_true", help="save source and layout PNGs without transcription")
    parser.add_argument("--captions", type=Path, metavar="SRT", help="use edited captions in clip-relative time")
    parser.add_argument("--save-captions", action="store_true", help="also save editable SRT captions")
    parser.add_argument("--template", type=Path, help="UTF-8 template for the suggested post text")
    parser.add_argument("-o", "--output", type=Path, default=Path("short.mp4"), help="output MP4 path")
    args = parser.parse_args()
    try:
        args.duration_ms = timestamp(args.end) - timestamp(args.start)
    except argparse.ArgumentTypeError as error:
        parser.error(str(error))
    if not math.ceil(1000 / FPS) <= args.duration_ms <= 60_000:
        parser.error("select a range between 34 ms and 60 seconds")
    if not 1 <= args.crop_zoom <= 3:
        parser.error("--crop-zoom must be between 1 and 3")
    if args.logo and (args.logo.suffix.lower() != ".png" or not args.logo.is_file()):
        parser.error("--logo must point to an existing PNG")
    if args.preview and (args.captions or args.save_captions or args.template):
        parser.error("--preview produces PNGs and cannot be combined with caption or template options")
    if args.output.suffix.lower() != ".mp4":
        parser.error("--output must end with .mp4")
    args.output = args.output.absolute()
    if args.logo:
        args.logo = args.logo.resolve()
    return args


def run(command, *, cwd=None):
    result = subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if result.returncode:
        name = "yt-dlp" if command[:3] == [sys.executable, "-m", "yt_dlp"] else command[0]
        raise RuntimeError(f"{name} failed.\n{result.stderr.strip()}")
    return result.stdout


def download(args, directory):
    end = args.end
    if args.preview and args.duration_ms > 1000:
        end = format_timestamp(timestamp(args.start) + 1000, ".")
    command = [
        sys.executable, "-m", "yt_dlp", "--ignore-config", "--compat-options", "no-certifi",
        "--socket-timeout", "20", "--no-playlist", "--playlist-items", "1", "--no-progress",
        "--no-simulate", "--match-filters", "!is_live & !is_upcoming",
        "--download-sections", f"*{args.start}-{end}",
        "--force-keyframes-at-cuts", "-S", "res:1080", "--merge-output-format", "mkv",
        "-P", str(directory), "-o", "source.%(ext)s",
        "--print", "after_move:%(.{filepath,title,channel,uploader})j",
    ]
    if shutil.which("node"):
        command += ["--js-runtimes", "node"]
    result = run([*command, "--", args.url]).splitlines()
    if not result:
        raise RuntimeError(
            "No section was downloaded. Use a published clip, a completed VOD, or a public video "
            "and check that --start is within the source."
        )
    if len(result) != 1:
        raise RuntimeError("Expected one section. Use a direct video, VOD, or clip URL.")
    metadata = json.loads(result[0])
    return Path(metadata["filepath"]), metadata


def probe(path):
    return json.loads(run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)
    ]))


def source_geometry(video):
    width, height = video["width"], video["height"]
    try:
        numerator, denominator = map(int, video.get("sample_aspect_ratio", "1:1").split(":"))
        ratio = numerator / denominator if numerator > 0 and denominator > 0 else 1
    except ValueError:
        ratio = 1
    rotation = next((item["rotation"] for item in video.get("side_data_list", []) if "rotation" in item), 0)
    if round(rotation) % 180 == 90:
        return height, width, 1 / ratio
    return width, height, ratio


def even(value):
    return max(2, round(value / 2) * 2)


def fit(aspect, width, height):
    return even(min(width, height * aspect)), even(min(height, width / aspect))


def transcribe(source, directory, duration):
    import numpy as np
    from faster_whisper import WhisperModel

    wav = directory / "speech.wav"
    run([
        "ffmpeg", "-v", "error", "-nostdin", "-i", str(source), "-map", "0:a:0",
        "-af", "aresample=async=1:first_pts=0", "-t", f"{duration:.3f}",
        "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(wav),
    ])
    # FFmpeg already decoded and resampled the audio to Whisper's input format.
    with wave.open(str(wav), "rb") as audio:
        samples = np.frombuffer(audio.readframes(audio.getnframes()), dtype="<i2").astype(np.float32)
    samples *= 1 / 32768
    model = WhisperModel("base", device="cpu", compute_type="int8", cpu_threads=min(os.cpu_count() or 1, 4))
    segments, _ = model.transcribe(samples, word_timestamps=True, vad_filter=True)
    return [
        (word.start, word.end, word.word.strip())
        for segment in segments for word in (segment.words or [])
        if word.word.strip() and word.start < duration
    ]


def caption_groups(words, duration):
    phrase = []
    phrases = []
    for word in words:
        if phrase and (
            word[0] - phrase[-1][1] > 0.65
            or (len(phrase) >= 2 and phrase[-1][2].endswith((".", "!", "?", "。", "！", "？")))
        ):
            phrases.append(phrase)
            phrase = []
        phrase.append(word)
    if phrase:
        phrases.append(phrase)

    groups = []
    for phrase in phrases:
        offset = 0
        while offset < len(phrase):
            remaining = len(phrase) - offset
            size = 3 if remaining == 5 else min(remaining, 4)
            chunk = phrase[offset:offset + size]
            groups.append((chunk[0][0], chunk[-1][1], " ".join(word[2] for word in chunk)))
            offset += size

    for index, (start, end, text) in enumerate(groups):
        next_start = groups[index + 1][0] if index + 1 < len(groups) else duration
        end = min(duration, next_start, max(end, start + 0.35))
        if round(end * 100) > round(start * 100):
            yield start, end, text


def ass_time(seconds):
    minutes, remainder = divmod(max(0, round(seconds * 100)), 6000)
    hours, minutes = divmod(minutes, 60)
    seconds, centiseconds = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"


def format_timestamp(milliseconds, separator):
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}{separator}{milliseconds:03d}"


def read_srt(path):
    contents = path.read_text(encoding="utf-8-sig").strip()
    cues = []
    for index, block in enumerate(re.split(r"\n[ \t]*\n+", contents), start=1):
        if not block.strip():
            continue
        lines = block.strip().splitlines()
        if lines[0].isdigit():
            lines.pop(0)
        try:
            start_text, end_text = lines[0].split("-->")
            start = timestamp(start_text.strip().replace(",", ".")) / 1000
            end = timestamp(end_text.strip().replace(",", ".")) / 1000
        except (argparse.ArgumentTypeError, IndexError, ValueError) as error:
            raise ValueError(f"Invalid SRT timing in cue {index} of {path}.") from error
        text = " ".join(" ".join(lines[1:]).split())
        if not text or start >= end:
            raise ValueError(f"SRT cue {index} needs text and a positive duration.")
        if cues and start < cues[-1][1]:
            raise ValueError(f"SRT cue {index} overlaps or precedes the previous cue.")
        cues.append((start, end, text))
    return cues


def write_srt(path, cues):
    blocks = []
    for index, (start, end, text) in enumerate(cues, start=1):
        time_start = format_timestamp(round(start * 1000), ",")
        time_end = format_timestamp(round(end * 1000), ",")
        blocks.append(f"{index}\n{time_start} --> {time_end}\n{text}\n")
    path.write_text("\n".join(blocks), encoding="utf-8")


def ass_text(text):
    # Keep arbitrary input from becoming an ASS override or a forced line break.
    return " ".join(text.split()).translate(str.maketrans({"\\": "＼", "{": "｛", "}": "｝"}))


def write_overlays(path, hook, captions, duration):
    events = []
    if hook.strip():
        events.append(f"Dialogue: 1,0:00:00.00,{ass_time(min(2, duration))},Hook,{ass_text(hook)}")
    events.extend(
        f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Caption,{ass_text(text)}"
        for start, end, text in captions
    )
    if not events:
        return False
    path.write_text(
        f"""[Script Info]
ScriptType: v4.00+
PlayResX: {WIDTH}
PlayResY: {HEIGHT}
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Arial,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,8,0,8,96,96,205,1
Style: Caption,Arial,72,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,6,0,2,90,90,415,1

[Events]
Format: Layer, Start, End, Style, Text
""" + "\n".join(events) + "\n",
        encoding="utf-8",
    )
    return True


def video_filters(args, geometry, overlays):
    width, height, sar = geometry
    aspect = width * sar / height
    background_w = even(max(WIDTH / 4, HEIGHT / 4 * aspect))
    background_h = even(max(HEIGHT / 4, WIDTH / 4 / aspect))
    game_w, game_h = fit(aspect, WIDTH, 1080 if args.facecam else HEIGHT)
    zoom_w = max(2, round(width / args.crop_zoom))
    zoom_h = max(2, round(height / args.crop_zoom))
    sources = "[bgsrc][gamesrc]" + ("[camsrc]" if args.facecam else "")
    filters = [
        f"[0:v:0]fps={FPS},split={3 if args.facecam else 2}{sources}",
        f"[bgsrc]scale={background_w}:{background_h},crop={WIDTH // 4}:{HEIGHT // 4},"
        f"gblur=sigma=10,scale={WIDTH}:{HEIGHT},setsar=1[bg]",
        f"[gamesrc]crop={zoom_w}:{zoom_h}:exact=1,scale={game_w}:{game_h},setsar=1[game]",
    ]
    if args.facecam:
        x, y, cam_w, cam_h = args.facecam
        panel_w, panel_h = fit(cam_w * sar / cam_h, 640, 360)
        gap = 24
        panel_y = (HEIGHT - panel_h - gap - game_h) // 2
        game_y = panel_y + panel_h + gap
        filters.extend([
            f"[camsrc]crop={cam_w}:{cam_h}:{x}:{y}:exact=1,scale={panel_w}:{panel_h},setsar=1[cam]",
            f"[bg][cam]overlay=(W-w)/2:{panel_y}[stack]",
        ])
        background = "[stack]"
    else:
        game_y = (HEIGHT - game_h) // 2
        background = "[bg]"

    filters.append(f"{background}[game]overlay=(W-w)/2:{game_y}[layout]")
    current = "[layout]"
    if overlays:
        filters.append(f"{current}ass=overlays.ass[words]")
        current = "[words]"
    if args.logo:
        filters.extend([
            "[1:v:0]format=rgba,scale=200:128:force_original_aspect_ratio=decrease,setsar=1[logo]",
            f"{current}[logo]overlay={LOGO_POSITIONS[args.pos]}:eof_action=repeat:repeatlast=1[branded]",
        ])
        current = "[branded]"
    filters.append(f"{current}format=yuv420p[out]")
    return ";".join(filters)


def video_inputs(args, source):
    command = [
        "ffmpeg", "-v", "error", "-nostdin", "-filter_complex_threads", "2", "-i", str(source),
    ]
    if args.logo:
        command += ["-i", str(args.logo)]
    return command


def render_preview(args, source, directory, geometry):
    raw = directory / "source.png"
    preview = directory / "preview.png"
    png_options = ["-frames:v", "1", "-threads:v", "1", "-c:v", "png", "-f", "image2", "-update", "1"]
    run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(source), "-map", "0:v:0", *png_options, str(raw)])
    overlays = write_overlays(directory / "overlays.ass", args.hook, [], 1)
    run([
        *video_inputs(args, source), "-filter_complex", video_filters(args, geometry, overlays),
        "-map", "[out]", *png_options, str(preview),
    ], cwd=directory)
    return raw, preview


def render(args, source, directory, geometry, duration, has_audio, overlays):
    video = directory / "render.mp4"
    command = video_inputs(args, source)
    if not has_audio:
        command += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    audio_stream = "0:a:0" if has_audio else f"{2 if args.logo else 1}:a:0"
    run([
        *command, "-filter_complex", video_filters(args, geometry, overlays),
        "-map", "[out]", "-map", audio_stream, "-af", "aresample=async=1:first_pts=0,apad",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-threads:v", "4",
        "-c:a", "aac", "-b:a", "160k", "-ac", "2", "-movflags", "+faststart",
        "-map_metadata", "-1", "-t", f"{duration:.3f}", "-shortest", str(video),
    ], cwd=directory)
    return video


def publish_outputs(pairs):
    # The staging directory is on the destination filesystem. Each link
    # publishes a completed file and fails if another run claimed that name.
    published = []
    try:
        for source, destination in pairs:
            os.link(source, destination)
            published.append(destination)
    except (OSError, KeyboardInterrupt):
        for path in reversed(published):
            path.unlink(missing_ok=True)
        raise
    for path in published:
        print(path)


def format_post(template, args, metadata):
    title = metadata.get("title") or "Vice City Codex"
    streamer = metadata.get("channel") or metadata.get("uploader") or "Unknown"
    hook = args.hook.strip()
    try:
        return template.format(lead=hook or title, hook=hook, title=title, streamer=streamer, url=args.url)
    except (ValueError, KeyError, AttributeError, IndexError) as error:
        raise ValueError(
            f"Invalid post template: {error}. Use {{lead}}, {{hook}}, {{title}}, {{streamer}}, or {{url}}."
        ) from error


def verify_video(path):
    info = probe(path)
    video = next((stream for stream in info["streams"] if stream["codec_type"] == "video"), {})
    if (video.get("width"), video.get("height"), video.get("codec_name")) != (WIDTH, HEIGHT, "h264"):
        raise RuntimeError("The rendered file must contain 1080×1920 H.264 video.")
    if not any(stream["codec_type"] == "audio" and stream.get("codec_name") == "aac" for stream in info["streams"]):
        raise RuntimeError("The rendered file must contain AAC audio.")
    if not 0 < float(info["format"]["duration"]) < 60:
        raise RuntimeError("The rendered file must be shorter than 60 seconds.")


def create_short(args):
    for program in ("ffmpeg", "ffprobe"):
        if not shutil.which(program):
            raise RuntimeError(f"Install FFmpeg and put {program} on PATH.")
    if args.preview:
        destinations = [args.output.with_name(f"{args.output.stem}-{kind}.png") for kind in ("source", "preview")]
    else:
        destinations = [args.output, args.output.with_suffix(".txt")]
        if args.save_captions:
            destinations.append(args.output.with_suffix(".srt"))
    for path in destinations:
        if path.exists() or path.is_symlink():
            raise RuntimeError(f"Choose a new output name. {path} already exists.")

    if args.logo:
        with args.logo.open("rb") as logo:
            if logo.read(8) != b"\x89PNG\r\n\x1a\n":
                raise ValueError("--logo must be a PNG file.")
    template = args.template.read_text(encoding="utf-8-sig") if args.template else DEFAULT_TEMPLATE
    if args.template:
        format_post(template, args, {})
    edited_captions = read_srt(args.captions) if args.captions else None
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".vcc-", dir=args.output.parent) as temp:
        directory = Path(temp)
        print("Downloading first second for preview…" if args.preview else "Downloading selected section…",
              file=sys.stderr, flush=True)
        source, metadata = download(args, directory)
        info = probe(source)
        video = next((stream for stream in info["streams"] if stream["codec_type"] == "video"), None)
        if video is None:
            raise RuntimeError("The downloaded section has no video.")
        has_audio = any(stream["codec_type"] == "audio" for stream in info["streams"])
        geometry = source_geometry(video)
        if args.facecam:
            x, y, width, height = args.facecam
            if x + width > geometry[0] or y + height > geometry[1]:
                raise RuntimeError(f"Facecam box extends outside the {geometry[0]}x{geometry[1]} source.")
        if args.preview:
            print(f"Source frame is {geometry[0]}×{geometry[1]}.", file=sys.stderr)
            publish_outputs(zip(render_preview(args, source, directory, geometry), destinations))
            return

        requested = min(args.duration_ms / 1000, MAX_RENDER_SECONDS)
        measured = float(info["format"].get("duration", requested))
        if not math.isfinite(measured) or measured <= 0:
            raise RuntimeError("The selected range has no measurable duration.")
        duration = min(requested, measured)
        if requested - duration > 1 / FPS:
            print(f"Source section ended early at {duration:.3f} seconds.", file=sys.stderr)

        if edited_captions is not None:
            caption_events = []
            for start, end, text in edited_captions:
                end = min(end, duration)
                if round(end * 100) > round(start * 100):
                    caption_events.append((start, end, text))
        elif has_audio:
            print("Transcribing with faster-whisper base (CPU)…", file=sys.stderr, flush=True)
            words = transcribe(source, directory, duration)
            caption_events = list(caption_groups(words, duration))
        else:
            caption_events = []
        print(f"Rendering 1080x1920 with {len(caption_events)} caption groups…", file=sys.stderr, flush=True)
        overlays = write_overlays(directory / "overlays.ass", args.hook, caption_events, duration)
        rendered = render(args, source, directory, geometry, duration, has_audio, overlays)
        verify_video(rendered)
        text = format_post(template, args, metadata)
        draft = directory / "post.txt"
        draft.write_text(text.rstrip() + "\n", encoding="utf-8")
        outputs = [rendered, draft]
        if args.save_captions:
            subtitles = directory / "captions.srt"
            write_srt(subtitles, caption_events)
            outputs.append(subtitles)
        publish_outputs(zip(outputs, destinations))


def main():
    args = parse_args()
    try:
        create_short(args)
    except KeyboardInterrupt:
        raise SystemExit(130) from None
    except (RuntimeError, OSError, ImportError, ValueError, KeyError) as error:
        raise SystemExit(f"Could not create Short.\n{error}") from None


if __name__ == "__main__":
    main()
