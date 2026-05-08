"""Request and response contracts for backend APIs."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ExplainerRequest(BaseModel):
    topic: str = Field(min_length=3)
    emotion: str = Field(default="confident", min_length=2)
    scene: str = Field(default="office", min_length=2)


class PodcastRequest(BaseModel):
    topic: str = Field(min_length=3)
    scene: str = Field(default="podcast_studio", min_length=2)
    emotion: str = Field(default="confident", min_length=2)


class InfographicRequest(BaseModel):
    topic: str = Field(min_length=3)
    emotion: str = Field(default="confident", min_length=2)
    scene: str = Field(default="office", min_length=2)


class QuizRequest(BaseModel):
    topic_text: str = Field(alias="topicText", min_length=3)
    duration_seconds: int = Field(default=600, ge=60, le=7200, alias="durationSeconds")

    class Config:
        populate_by_name = True


class ProcessingMetadata(BaseModel):
    mode: str
    model_provider: str
    pipeline_version: str


class RenderPackage(BaseModel):
    script: str
    voice: Dict[str, str]
    animation_states: List[str]
    scene: Dict[str, str]
    emotion: Dict[str, object]
    dialogue: Optional[List[Dict[str, str]]] = None


class ExplainerResponse(BaseModel):
    metadata: ProcessingMetadata
    render: RenderPackage
    explanation: Dict[str, object]


class InfographicResponse(BaseModel):
    metadata: ProcessingMetadata
    infographic: Dict[str, object]
    render: RenderPackage


class QuizResponse(BaseModel):
    metadata: ProcessingMetadata
    quiz: Dict[str, object]
    supervisor: Dict[str, object]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

