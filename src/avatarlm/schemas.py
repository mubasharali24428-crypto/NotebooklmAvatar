"""Core schemas for AvatarLM."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class VoiceProfile:
    pitch: str
    speed: str
    pauses: str
    tone: str
    ssml_style: str


@dataclass(frozen=True)
class AppearanceProfile:
    facial_expression: str
    body_posture: str
    clothing: str
    props: List[str]
    facial_hair: str = "clean"


@dataclass(frozen=True)
class AnimationProfile:
    movement: str
    head_tilt: str
    blink_rate: str
    micro_animations: List[str]


@dataclass(frozen=True)
class EmotionPreset:
    emotion: str
    voice: VoiceProfile
    appearance: AppearanceProfile
    animation: AnimationProfile
    word_choice: str
    speech_rhythm: str


@dataclass(frozen=True)
class ScenePreset:
    scene: str
    lighting: str
    sound: str
    camera: str
    avatar_spacing: str


@dataclass(frozen=True)
class AvatarLayers:
    appearance_layer: Dict[str, str] = field(default_factory=dict)
    emotion_layer: Dict[str, str] = field(default_factory=dict)
    context_layer: Dict[str, str] = field(default_factory=dict)

