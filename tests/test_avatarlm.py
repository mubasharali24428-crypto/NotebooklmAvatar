import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avatarlm.engines.emotion_engine import get_emotion_preset
from avatarlm.engines.quiz_engine import build_supervisor_mode, generate_quiz
from avatarlm.engines.scene_engine import SCENE_PRESETS, get_scene_preset
from avatarlm.example_flows import heartbroken_explainer_flow, podcast_discussion_flow, quiz_supervisor_flow


class AvatarLMTests(unittest.TestCase):
    def test_heartbroken_mapping_contains_required_signals(self):
        preset = get_emotion_preset("heartbroken")
        self.assertEqual(preset.voice.speed, "slow")
        self.assertIn("bouquet_of_flowers", preset.appearance.props)
        self.assertEqual(preset.animation.movement, "minimal")

    def test_all_mandatory_scenes_exist(self):
        for required in ["beach", "podcast_studio", "cliff", "jungle", "lake", "office"]:
            self.assertIn(required, SCENE_PRESETS)
        self.assertEqual(get_scene_preset("unknown").scene, "office")

    def test_quiz_generator_and_supervisor_mode(self):
        quiz = generate_quiz("Neural networks learn from examples. Backpropagation updates weights.")
        self.assertGreaterEqual(len(quiz["mcq"]), 1)
        supervisor = build_supervisor_mode(120)
        self.assertEqual(supervisor["timer_seconds"], 120)
        self.assertIn("maintain_eye_contact", supervisor["behavior"])

    def test_example_flows(self):
        explainer = heartbroken_explainer_flow("Entropy")
        self.assertEqual(explainer["input"]["mode"], "video_explainer")
        podcast = podcast_discussion_flow("Vector databases")
        self.assertIn("dialogue", podcast)
        quiz = quiz_supervisor_flow("Photosynthesis converts light into chemical energy.")
        self.assertEqual(quiz["mode"], "quiz")


if __name__ == "__main__":
    unittest.main()
