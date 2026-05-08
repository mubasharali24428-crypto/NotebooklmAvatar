"""Backend service orchestration for AvatarLM modes."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List

from avatarlm.engines.quiz_engine import build_supervisor_mode, generate_quiz
from avatarlm.pipeline import build_dialogue, build_script, generate_structured_explanation
from avatarlm.engines.emotion_engine import get_emotion_preset
from avatarlm.engines.scene_engine import get_scene_preset
from avatarlm.engines.voice_engine import build_ssml_config


def _serialize(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    return value


class AvatarLMService:
    """Application service boundary for backend-first orchestration."""

    model_provider = "configurable_llm"
    pipeline_version = "1.0.0"

    def _metadata(self, mode: str) -> Dict[str, str]:
        return {
            "mode": mode,
            "model_provider": self.model_provider,
            "pipeline_version": self.pipeline_version,
        }

    def _render_payload(self, topic: str, emotion: str, scene: str, dialogue: List[Dict[str, str]] | None = None) -> Dict[str, Any]:
        explanation = generate_structured_explanation(topic)
        emotion_preset = get_emotion_preset(emotion)
        scene_preset = get_scene_preset(scene)
        render = {
            "script": build_script(explanation),
            "voice": build_ssml_config(emotion_preset),
            "animation_states": ["idle", "speaking", "walking", "reacting"],
            "scene": _serialize(scene_preset),
            "emotion": _serialize(emotion_preset),
            "dialogue": dialogue,
        }
        return {"explanation": explanation, "render": render}

    def explainer(self, topic: str, emotion: str, scene: str) -> Dict[str, Any]:
        payload = self._render_payload(topic=topic, emotion=emotion, scene=scene)
        return {
            "metadata": self._metadata("video_explainer"),
            "explanation": payload["explanation"],
            "render": payload["render"],
        }

    def podcast(self, topic: str, emotion: str, scene: str) -> Dict[str, Any]:
        dialogue = build_dialogue(topic, ["Ava", "Orion"])
        payload = self._render_payload(topic=topic, emotion=emotion, scene=scene, dialogue=dialogue)
        return {
            "metadata": self._metadata("podcast"),
            "explanation": payload["explanation"],
            "render": payload["render"],
        }

    def infographic(self, topic: str, emotion: str, scene: str) -> Dict[str, Any]:
        payload = self._render_payload(topic=topic, emotion=emotion, scene=scene)
        steps = payload["explanation"]["steps"]
        infographic = {
            "title": f"{topic} visual breakdown",
            "elements": [
                {"type": "highlight", "content": steps[0]},
                {"type": "pointing", "content": steps[1]},
                {"type": "step_breakdown", "content": steps[2]},
            ],
        }
        return {
            "metadata": self._metadata("infographic"),
            "infographic": infographic,
            "render": payload["render"],
        }

    def quiz(self, topic_text: str, duration_seconds: int) -> Dict[str, Any]:
        return {
            "metadata": self._metadata("quiz"),
            "quiz": generate_quiz(topic_text),
            "supervisor": build_supervisor_mode(duration_seconds=duration_seconds),
        }

