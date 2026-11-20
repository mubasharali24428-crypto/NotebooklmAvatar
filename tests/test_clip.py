import argparse
import contextlib
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import clip


class ClipTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name)

    def test_short_selections_include_one_minute(self):
        command = ["clip.py", "--url", "https://www.twitch.tv/videos/123", "--start", "00:12:30", "--end"]
        for end, milliseconds in [("00:13:00", 30_000), ("00:13:30", 60_000)]:
            with self.subTest(end=end), patch("sys.argv", [*command, end]):
                self.assertEqual(clip.parse_args().duration_ms, milliseconds)
        with patch("sys.argv", [*command, "00:13:30.001"]), contextlib.redirect_stderr(io.StringIO()) as stderr:
            with self.assertRaises(SystemExit) as error:
                clip.parse_args()
        self.assertEqual(error.exception.code, 2)
        self.assertIn("between 34 ms and 60 seconds", stderr.getvalue())

    def test_preview_requests_only_first_second(self):
        args = argparse.Namespace(
            preview=True, duration_ms=40_000, start="00:59:59.350", end="01:00:39.350",
            url="https://youtu.be/example",
        )
        download = json.dumps({"filepath": str(self.directory / "source.mp4")})
        with patch("clip.run", return_value=download) as run:
            clip.download(args, self.directory)
        command = run.call_args.args[0]
        self.assertEqual(command[command.index("--download-sections") + 1], "*00:59:59.350-01:00:00.350")
        self.assertEqual(command[command.index("--playlist-items") + 1], "1")

    def test_srt_round_trip_and_multiline_edit(self):
        subtitles = self.directory / "captions.srt"
        events = [(0.12, 1.075, "First caption"), (1.075, 2.5, "Second caption")]
        clip.write_srt(subtitles, events)
        self.assertEqual(clip.read_srt(subtitles), events)
        edited = "\ufeff" + subtitles.read_text().replace("First caption", "Edited\ncaption")
        subtitles.write_bytes(edited.replace("\n", "\r\n").encode("utf-8"))
        self.assertEqual(clip.read_srt(subtitles)[0], (0.12, 1.075, "Edited caption"))

    def test_overlapping_cues_identify_the_bad_cue(self):
        subtitles = self.directory / "bad.srt"
        clip.write_srt(subtitles, [(0, 2, "First caption"), (1, 3, "Second caption")])
        with self.assertRaisesRegex(ValueError, "cue 2 overlaps"):
            clip.read_srt(subtitles)

    def test_caption_grouping_respects_sentence_break_and_avoids_one_word_tail(self):
        words = "Hey there. This one has five words".split()
        events = [(index * 0.25, index * 0.25 + 0.24, word) for index, word in enumerate(words)]
        self.assertEqual([text for _, _, text in clip.caption_groups(events, 2)],
                         ["Hey there.", "This one has", "five words"])

    def test_output_collision_rolls_back_our_files(self):
        movie = self.directory / "render"
        draft = self.directory / "draft"
        movie.write_bytes(b"new movie")
        draft.write_bytes(b"new draft")
        output = self.directory / "short.mp4"
        sidecar = self.directory / "short.txt"
        sidecar.write_bytes(b"existing draft")

        with self.assertRaises(FileExistsError):
            clip.publish_outputs([(movie, output), (draft, sidecar)])

        self.assertFalse(output.exists())
        self.assertEqual(sidecar.read_bytes(), b"existing draft")

    def test_invalid_template_fails_before_downloading(self):
        template = self.directory / "bad.txt"
        template.write_text("{unknown}", encoding="utf-8")
        args = argparse.Namespace(
            output=self.directory / "short.mp4", preview=False, save_captions=False, captions=None,
            logo=None, template=template, hook="", url="https://youtu.be/example",
        )
        with patch("clip.shutil.which", return_value="/ffmpeg"), patch("clip.download") as download:
            with self.assertRaisesRegex(ValueError, "Invalid post template"):
                clip.create_short(args)
        download.assert_not_called()

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "requires FFmpeg")
    def test_preview_and_captioned_video_with_silent_source(self):
        source = self.directory / "fixture.mp4"
        subprocess.run([
            "ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=c=gray:s=320x180:r=30:d=0.5",
            "-c:v", "libx264", "-an", str(source),
        ], check=True)
        args = argparse.Namespace(
            output=self.directory / "short.mp4", preview=True, save_captions=False,
            captions=None, logo=None, template=None, hook="Vice City", url="https://youtu.be/example",
            facecam=(0, 0, 64, 48), crop_zoom=1.25, duration_ms=500,
        )
        with patch("clip.download", return_value=(source, {})), contextlib.redirect_stdout(io.StringIO()):
            clip.create_short(args)
            raw = clip.probe(self.directory / "short-source.png")["streams"][0]
            preview = clip.probe(self.directory / "short-preview.png")["streams"][0]
            self.assertEqual((raw["width"], raw["height"]), (320, 180))
            self.assertEqual((preview["width"], preview["height"]), (1080, 1920))
            self.assertFalse(args.output.exists())

            args.preview = False
            args.captions = self.directory / "edit.srt"
            args.save_captions = True
            clip.write_srt(args.captions, [(0, 0.2, "Edited caption"), (0.4, 0.7, "Tail caption")])
            clip.create_short(args)

        clip.verify_video(args.output)
        events = clip.read_srt(self.directory / "short.srt")
        self.assertEqual(events, [(0, 0.2, "Edited caption"), (0.4, 0.5, "Tail caption")])
        self.assertIn("#ViceCityCodex", (self.directory / "short.txt").read_text())
