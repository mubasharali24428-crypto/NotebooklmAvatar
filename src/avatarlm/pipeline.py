"""AvatarLM pipeline orchestration."""

from __future__ import annotations

from typing import Dict, List

from avatarlm.engines.emotion_engine import get_emotion_preset
from avatarlm.engines.scene_engine import get_scene_preset
from avatarlm.engines.voice_engine import build_ssml_config


def generate_structured_explanation(topic: str) -> Dict[str, object]:
    return {
        "title": topic,
        "steps": [
            f"Define {topic}",
            f"Break down why {topic} matters",
            f"Apply {topic} in a practical example",
        ],
    }


def build_script(explanation: Dict[str, object]) -> str:
    steps: List[str] = explanation["steps"]  # type: ignore[assignment]
    return " ".join([f"{idx + 1}. {step}." for idx, step in enumerate(steps)])


def build_dialogue(topic: str, participants: List[str]) -> List[Dict[str, str]]:
    return [
        {"speaker": participants[0], "line": f"Let's unpack {topic} with intuition."},
        {"speaker": participants[1], "line": f"I'll challenge assumptions with concrete examples."},
    ]


def run_pipeline(topic: str, mode: str, emotion: str, scene: str) -> Dict[str, object]:
    explanation = generate_structured_explanation(topic)
    emotion_preset = get_emotion_preset(emotion)
    scene_preset = get_scene_preset(scene)
    payload: Dict[str, object] = {
        "input": {"topic": topic, "mode": mode},
        "explanation": explanation,
        "script": build_script(explanation),
        "emotion": emotion_preset,
        "scene": scene_preset,
        "voice": build_ssml_config(emotion_preset),
        "animation_states": ["idle", "speaking", "walking", "reacting"],
    }
    if mode == "podcast":
        payload["dialogue"] = build_dialogue(topic, ["Ava", "Orion"])
    return payload

