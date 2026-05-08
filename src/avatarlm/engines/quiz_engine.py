"""Quiz generation and supervisor mode scaffolding."""

from __future__ import annotations

from typing import Dict, List


def extract_key_concepts(topic_text: str) -> List[str]:
    parts = [p.strip() for p in topic_text.replace("\n", " ").split(".")]
    return [p for p in parts if p][:3]


def generate_quiz(topic_text: str) -> Dict[str, List[Dict[str, str]]]:
    concepts = extract_key_concepts(topic_text)
    mcqs = []
    short_answers = []
    true_false = []
    for idx, concept in enumerate(concepts, start=1):
        mcqs.append(
            {
                "id": f"mcq-{idx}",
                "question": f"Which statement best represents: {concept}?",
                "options": "A) Core idea B) Opposite idea C) Unrelated idea D) Unsure",
                "answer": "A",
            }
        )
        short_answers.append(
            {
                "id": f"sa-{idx}",
                "question": f"Explain this concept in one sentence: {concept}",
            }
        )
        true_false.append(
            {
                "id": f"tf-{idx}",
                "question": f"'{concept}' is a key concept in this topic.",
                "answer": "True",
            }
        )
    return {"mcq": mcqs, "short_answer": short_answers, "true_false": true_false}


def build_supervisor_mode(duration_seconds: int = 300) -> Dict[str, object]:
    return {
        "behavior": ["walk_across_screen", "maintain_eye_contact", "subtle_presence"],
        "timer_seconds": duration_seconds,
        "ethical_guardrails": ["no_shaming_language", "encouraging_neutral_feedback"],
    }

