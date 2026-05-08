"""Example product flows required by the AvatarLM spec."""

from __future__ import annotations

from typing import Dict

from avatarlm.engines.quiz_engine import build_supervisor_mode, generate_quiz
from avatarlm.pipeline import run_pipeline


def heartbroken_explainer_flow(topic: str) -> Dict[str, object]:
    return run_pipeline(topic=topic, mode="video_explainer", emotion="heartbroken", scene="cliff")


def podcast_discussion_flow(topic: str) -> Dict[str, object]:
    return run_pipeline(topic=topic, mode="podcast", emotion="confident", scene="podcast_studio")


def quiz_supervisor_flow(topic_text: str) -> Dict[str, object]:
    return {
        "mode": "quiz",
        "quiz": generate_quiz(topic_text),
        "supervisor": build_supervisor_mode(duration_seconds=600),
    }

