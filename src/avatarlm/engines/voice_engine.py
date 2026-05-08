"""Voice synthesis request mapping for emotion-aware TTS."""

from __future__ import annotations

from typing import Dict

from avatarlm.schemas import EmotionPreset


def build_ssml_config(emotion_preset: EmotionPreset) -> Dict[str, str]:
    """Map emotion profile to TTS/SSML-friendly parameters."""
    return {
        "pitch": emotion_preset.voice.pitch,
        "rate": emotion_preset.voice.speed,
        "pauses": emotion_preset.voice.pauses,
        "tone": emotion_preset.voice.tone,
        "style": emotion_preset.voice.ssml_style,
    }

