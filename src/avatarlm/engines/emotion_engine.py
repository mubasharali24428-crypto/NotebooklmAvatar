"""Emotion engine with strict, extensible mappings."""

from __future__ import annotations

from typing import Dict

from avatarlm.schemas import (
    AnimationProfile,
    AppearanceProfile,
    EmotionPreset,
    VoiceProfile,
)


EMOTION_PRESETS: Dict[str, EmotionPreset] = {
    "heartbroken": EmotionPreset(
        emotion="heartbroken",
        voice=VoiceProfile(
            pitch="low",
            speed="slow",
            pauses="long",
            tone="soft_unstable",
            ssml_style="sad",
        ),
        appearance=AppearanceProfile(
            facial_expression="tired_eyes_low_gaze",
            body_posture="slouched",
            clothing="suit_without_tie_open_buttons",
            props=["bouquet_of_flowers"],
            facial_hair="light_stubble",
        ),
        animation=AnimationProfile(
            movement="minimal",
            head_tilt="down",
            blink_rate="low",
            micro_animations=["subtle_sigh_pause", "shoulder_drop"],
        ),
        word_choice="gentle_reflective",
        speech_rhythm="slow_fragile",
    ),
    "confident": EmotionPreset(
        emotion="confident",
        voice=VoiceProfile(
            pitch="medium",
            speed="medium",
            pauses="balanced",
            tone="steady_assured",
            ssml_style="news",
        ),
        appearance=AppearanceProfile(
            facial_expression="direct_eye_contact_slight_smile",
            body_posture="upright_open_shoulders",
            clothing="smart_formal",
            props=["laser_pointer"],
            facial_hair="trimmed",
        ),
        animation=AnimationProfile(
            movement="purposeful",
            head_tilt="neutral",
            blink_rate="normal",
            micro_animations=["pointing", "open_palm_gesture"],
        ),
        word_choice="clear_precise",
        speech_rhythm="measured",
    ),
}


def get_emotion_preset(emotion: str) -> EmotionPreset:
    """Return a strict emotion preset with graceful fallback."""
    return EMOTION_PRESETS.get(emotion.lower(), EMOTION_PRESETS["confident"])

