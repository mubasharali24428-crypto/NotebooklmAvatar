# Vice City Codex Shorts

A local Python command-line tool for turning Twitch clips, Twitch VODs, and YouTube videos into 1080×1920 Shorts for Vice City Codex (@TheGTA6Codex). It uses yt-dlp, FFmpeg, and faster-whisper on CPU. There are no paid services or API keys.

## Install

Use Python 3.10+ and an FFmpeg build with `ffprobe`, `libx264`, and `libass`. Install FFmpeg with `sudo apt install ffmpeg` on Debian/Ubuntu or `brew install ffmpeg` on macOS. On Windows, put the FFmpeg and ffprobe executables on PATH.

Run from the directory containing the scripts:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
ffmpeg -version
ffprobe -version
```

In Windows PowerShell, use `py -m venv .venv` and `.\.venv\Scripts\Activate.ps1` before the pip command.

The first transcription downloads the free multilingual Whisper `base` model (about 145 MB). Later runs use the local cache. YouTube extraction may require a JavaScript runtime for yt-dlp. A supported Deno installation works through yt-dlp's defaults, and the script also enables Node.js when it is on PATH. See the [yt-dlp YouTube support notes](https://github.com/yt-dlp/yt-dlp/wiki/EJS).

## Find Twitch moments

```bash
python find_moments.py xqc
python find_moments.py xqc --limit 5
```

Twitch supplies the seven-day ranking. The script prints title, views, duration, and URL using yt-dlp's flat playlist metadata.

## Make a Short

```bash
python clip.py \
  --url 'https://www.twitch.tv/xqc/clip/VivaciousCallousYogurtDxCat-tcAghtrsbnP82HX2' \
  --start 00:00:03 --end 00:00:13 \
  --hook 'xQc reacts to GTA VI' \
  --output shorts/gta-vi-reaction.mp4
```

For a VOD, substitute its URL and the timestamps in the original video. For a Twitch clip, start and end are relative to the clip itself. Use a recorded video or a published clip. Select a span from 34 milliseconds up to and including 60 seconds. For example, with `--start 00:12:30`, use `--end 00:13:00` for 30 seconds or `--end 00:13:30` for one minute. A one-minute selection exports at approximately 59.9 seconds to keep the MP4 under 60 seconds. yt-dlp requests only the specified section. The host can serve the surrounding keyframes or streaming segments needed for that cut.

Add the campaign logo and an optional facecam panel:

```bash
python clip.py \
  --url 'https://www.twitch.tv/xqc/clip/VivaciousCallousYogurtDxCat-tcAghtrsbnP82HX2' \
  --start 00:00:03 --end 00:00:13 \
  --crop-zoom 1.25 --facecam 0,0,396,312 \
  --logo ./streamer-logo.png --pos top-right \
  --hook 'xQc reacts to GTA VI' \
  --output shorts/gta-vi-campaign.mp4
```

Supply the streamer's campaign PNG at `./streamer-logo.png`. It stays in the chosen corner from the first frame through the last. `--pos` defaults to `top-right` and also accepts `top-left`, `bottom-left`, and `bottom-right`. The facecam box uses top-left `x,y` and width/height in pixels of the downloaded source rendition, with source formats sorted toward 1080p. The example box matches this Twitch clip at 1920×1080. The camera panel appears above the gameplay. `--crop-zoom` without a value uses 1.25×, and an explicit factor can range from 1 to 3.

The render uses blurred fill behind centered gameplay. The optional hook appears in the opening two seconds. Whisper burns bold outlined captions in the lower third, grouped into two to four words where possible, with single words preserved when isolated by a pause. Each run writes an H.264/AAC MP4 and a matching `.txt` file. The default names are `short.mp4` and `short.txt`. If the source ends before the requested end time, the tool reports the shorter section and renders the available footage.

## Preview the framing

```bash
python clip.py \
  --url 'https://www.twitch.tv/xqc/clip/VivaciousCallousYogurtDxCat-tcAghtrsbnP82HX2' \
  --start 00:00:03 --end 00:00:13 \
  --preview --crop-zoom --facecam 0,0,396,312 \
  --hook 'xQc reacts to GTA VI' --output shorts/gta-vi-reaction.mp4
```

This downloads up to one second and writes `shorts/gta-vi-reaction-source.png` at the original pixel dimensions and `shorts/gta-vi-reaction-preview.png` at 1080×1920. Use the source PNG to measure the facecam crop and the vertical PNG to check the hook, zoom, and any supplied logo. The first-frame preview skips transcription. Run the same command without `--preview` to make the full Short.

## Review and correct captions

```bash
python clip.py \
  --url 'https://www.twitch.tv/xqc/clip/VivaciousCallousYogurtDxCat-tcAghtrsbnP82HX2' \
  --start 00:00:03 --end 00:00:13 \
  --save-captions --output shorts/review.mp4
```

Edit `shorts/review.srt` in a text editor. Keep the timestamps relative to the start of the Short, use plain text, and keep cues in chronological order without overlaps. Use the same URL, range, and layout flags for the final render. Passing `--captions` burns the edited SRT and skips Whisper.

```bash
python clip.py \
  --url 'https://www.twitch.tv/xqc/clip/VivaciousCallousYogurtDxCat-tcAghtrsbnP82HX2' \
  --start 00:00:03 --end 00:00:13 \
  --captions shorts/review.srt --output shorts/final.mp4
```

## Customize the post text

Create a UTF-8 file and pass `--template ./caption-template.txt`. Available fields are `{lead}` (hook or title), `{hook}`, `{title}`, `{streamer}`, and `{url}`. Use double braces for literal braces.

```bash
cat > caption-template.txt <<'TEMPLATE'
{lead}

Stream by {streamer}
{url}

#GTA6 #ViceCityCodex #GamingShorts
TEMPLATE

python clip.py \
  --url 'https://www.twitch.tv/xqc/clip/VivaciousCallousYogurtDxCat-tcAghtrsbnP82HX2' \
  --start 00:00:03 --end 00:00:13 \
  --template ./caption-template.txt --output shorts/gta-vi-custom.mp4
```

Use a fresh output basename for each full render. The output filesystem needs hard-link support, such as NTFS, APFS, or ext4. The tool stages completed files next to the requested path and uses hard links to guard against concurrent overwrites.

## Verification

Run the local regression suite without network access:

```bash
python -m unittest discover -s tests -v
```

The campaign example was tested on the public xQc clip using a temporary PNG labeled TEST and `--save-captions`. yt-dlp extracted the 10-second section, CPU Whisper produced seven caption groups, and ffprobe reported 1080×1920 H.264 video and AAC audio at 10.000 seconds. The hook was present through frame 59 and gone at frame 60. The test logo was present on all 300 frames.

The edited SRT was then burned into a second render with the Whisper model cache unavailable. A completed Twitch VOD was also tested at `00:12:30`–`00:12:35` and produced a 5.000-second Short.

```bash
ffprobe -v error -show_entries stream=codec_name,width,height,nb_frames:format=duration \
  -of json shorts/gta-vi-campaign.mp4
```
