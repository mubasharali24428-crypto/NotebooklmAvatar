#!/usr/bin/env python3
"""List a Twitch channel's most-viewed clips for the last seven days."""

import argparse
import json
import re
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("channel", help="Twitch channel login, e.g. xqc")
    parser.add_argument("--limit", type=int, default=10, help="number of clips (default: 10)")
    args = parser.parse_args()
    channel = args.channel.removeprefix("@").lower()
    if not re.fullmatch(r"[a-z0-9_]{1,25}", channel):
        parser.error("provide a Twitch channel login")
    if args.limit < 1:
        parser.error("--limit must be at least 1")

    url = f"https://www.twitch.tv/{channel}/clips?filter=clips&range=7d"
    command = [
        sys.executable, "-m", "yt_dlp", "--ignore-config",
        "--compat-options", "no-certifi", "--socket-timeout", "20",
        "--flat-playlist", "--playlist-items", f":{args.limit}",
        "--dump-single-json", "--", url,
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8",
                                errors="replace")
        listing = json.loads(result.stdout)
    except subprocess.CalledProcessError as error:
        parser.exit(1, f"Could not list Twitch clips.\n{error.stderr.strip()}\n")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Could not read the yt-dlp listing: {error}\n")

    clips = [clip for clip in (listing.get("entries") or []) if clip and clip.get("url")]
    clips.sort(key=lambda clip: clip.get("view_count") or 0, reverse=True)
    if not clips:
        print(f"No public clips returned for {channel} in the last seven days.")
        return

    for clip in clips:
        title = " ".join((clip.get("title") or "Untitled").split())
        views = clip.get("view_count")
        duration = clip.get("duration")
        view_label = f"{views:,} views" if views is not None else "views unavailable"
        time_label = f"{duration:g}s" if duration is not None else "duration unavailable"
        print(f"{title} | {view_label} | {time_label}\n  {clip['url']}")


if __name__ == "__main__":
    main()
