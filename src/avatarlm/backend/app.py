"""FastAPI application entrypoint for AvatarLM backend."""

from __future__ import annotations

from fastapi import FastAPI

from avatarlm.backend.api_models import (
    ExplainerRequest,
    ExplainerResponse,
    HealthResponse,
    InfographicRequest,
    InfographicResponse,
    PodcastRequest,
    QuizRequest,
    QuizResponse,
)
from avatarlm.backend.service import AvatarLMService


def create_app() -> FastAPI:
    service = AvatarLMService()
    app = FastAPI(
        title="AvatarLM Backend",
        version="1.0.0",
        description="Backend-first API for emotion-aware avatar learning flows.",
    )

    @app.get("/api/v1/health", response_model=HealthResponse, tags=["system"])
    def health() -> HealthResponse:
        return HealthResponse(status="ok", service="avatarlm-backend", version=app.version)

    @app.post("/api/v1/explainer", response_model=ExplainerResponse, tags=["learning"])
    def explainer(request: ExplainerRequest) -> ExplainerResponse:
        payload = service.explainer(topic=request.topic, emotion=request.emotion, scene=request.scene)
        return ExplainerResponse(**payload)

    @app.post("/api/v1/podcast", response_model=ExplainerResponse, tags=["learning"])
    def podcast(request: PodcastRequest) -> ExplainerResponse:
        payload = service.podcast(topic=request.topic, emotion=request.emotion, scene=request.scene)
        return ExplainerResponse(**payload)

    @app.post("/api/v1/infographic", response_model=InfographicResponse, tags=["learning"])
    def infographic(request: InfographicRequest) -> InfographicResponse:
        payload = service.infographic(topic=request.topic, emotion=request.emotion, scene=request.scene)
        return InfographicResponse(**payload)

    @app.post("/api/v1/quiz", response_model=QuizResponse, tags=["learning"])
    def quiz(request: QuizRequest) -> QuizResponse:
        payload = service.quiz(topic_text=request.topic_text, duration_seconds=request.duration_seconds)
        return QuizResponse(**payload)

    return app


app = create_app()

