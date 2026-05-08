def generate_script(topic: str, emotion: str) -> str:
    """Mock LLM call to generate an explainer script based on topic and emotion."""
    if emotion.lower() == "heartbroken":
        return f"Hey... *sigh* today I guess we should talk about {topic}. It's... it's just so hard to even think about it right now."
    elif emotion.lower() == "excited":
        return f"Wow! I can't wait to dive into {topic}! This is literally the most amazing thing ever!"
    else:
        return f"Let's discuss {topic}. Here is a clear, step-by-step breakdown of the concepts involved."
