from fastapi import APIRouter
from app.models.emotion import GenerateRequest, GenerateResponse, EmotionConfig, VoiceConfig, AppearanceConfig, AnimationConfig
from app.services.llm_mock import generate_script
from app.services.tts_mock import generate_mock_tts

router = APIRouter()

# Simple mock database of emotions based on spec
EMOTION_DATABASE = {
    "heartbroken": EmotionConfig(
        emotion="heartbroken",
        voice=VoiceConfig(pitch="low", speed="slow", pauses="long"),
        appearance=AppearanceConfig(
            facial_hair="light_stubble",
            clothing="loose_formal",
            accessories=["flowers"]
        ),
        animation=AnimationConfig(
            movement="minimal",
            head_tilt="down",
            blink_rate="low",
            color_overlay="#1a202c" # Darkish tone
        )
    ),
    "excited": EmotionConfig(
        emotion="excited",
        voice=VoiceConfig(pitch="high", speed="fast", pauses="short"),
        appearance=AppearanceConfig(
            facial_hair="clean",
            clothing="bright_casual",
            accessories=["glasses"]
        ),
        animation=AnimationConfig(
            movement="energetic",
            head_tilt="up",
            blink_rate="fast",
            color_overlay="#f6e05e" # Yellow/bright tone
        )
    ),
    "neutral": EmotionConfig(
        emotion="neutral",
        voice=VoiceConfig(pitch="medium", speed="medium", pauses="medium"),
        appearance=AppearanceConfig(
            facial_hair="clean",
            clothing="smart_casual",
            accessories=[]
        ),
        animation=AnimationConfig(
            movement="moderate",
            head_tilt="straight",
            blink_rate="normal",
            color_overlay="#ffffff"
        )
    )
}

@router.post("/generate", response_model=GenerateResponse)
async def generate_avatar_content(request: GenerateRequest):
    topic = request.topic
    emotion_key = request.emotion.lower()

    emotion_mapping = EMOTION_DATABASE.get(emotion_key, EMOTION_DATABASE["neutral"])

    script = generate_script(topic, emotion_key)
    audio_url = generate_mock_tts(script, emotion_key)

    return GenerateResponse(
        script=script,
        emotion_mapping=emotion_mapping,
        audio_url=audio_url
    )
