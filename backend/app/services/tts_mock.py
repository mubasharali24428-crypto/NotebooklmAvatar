def generate_mock_tts(script: str, emotion: str) -> str:
    """Mock TTS generator. In a real system, this calls ElevenLabs/OpenAI TTS."""
    # For now, return a placeholder path or URL
    return f"https://mock-audio-service.com/tts?emotion={emotion}&length={len(script)}"
