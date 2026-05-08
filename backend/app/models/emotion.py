from pydantic import BaseModel
from typing import List, Optional

class VoiceConfig(BaseModel):
    pitch: str
    speed: str
    pauses: str

class AppearanceConfig(BaseModel):
    facial_hair: Optional[str] = None
    clothing: str
    accessories: List[str] = []

class AnimationConfig(BaseModel):
    movement: str
    head_tilt: str
    blink_rate: str
    color_overlay: Optional[str] = None

class EmotionConfig(BaseModel):
    emotion: str
    voice: VoiceConfig
    appearance: AppearanceConfig
    animation: AnimationConfig

class GenerateRequest(BaseModel):
    topic: str
    emotion: str

class GenerateResponse(BaseModel):
    script: str
    emotion_mapping: EmotionConfig
    audio_url: str
