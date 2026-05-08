# AvatarLM (NotebooklmAvatar)

Production-oriented scaffold for an emotionally aware, avatar-based learning platform.

## Folder structure

```text
NotebooklmAvatar/
├── api/
│   └── openapi.yaml
├── frontend/
│   ├── app/
│   │   └── page.tsx
│   ├── components/
│   │   ├── AvatarStage.tsx
│   │   ├── EmotionPanel.tsx
│   │   └── ModeSwitcher.tsx
│   └── mockup/
│       └── index.html
├── src/
│   └── avatarlm/
│       ├── __init__.py
│       ├── example_flows.py
│       ├── pipeline.py
│       ├── schemas.py
│       └── engines/
│           ├── __init__.py
│           ├── emotion_engine.py
│           ├── quiz_engine.py
│           ├── scene_engine.py
│           └── voice_engine.py
└── tests/
    └── test_avatarlm.py
```

## Key modules

- **Emotion Engine**: Structured/extensible mapping of emotion → voice, appearance, animation.
- **Scene Engine**: Mandatory scene presets (beach, podcast studio, cliff, jungle, lake, office).
- **Pipeline**: Input parsing, script/dialogue generation, emotion transform, output package.
- **Quiz Engine**: MCQ, short answer, true/false generation + invigilator supervisor configuration.
- **Backend API**: FastAPI app with production-style contracts and mode endpoints.
- **Frontend scaffolding**: Next.js-style components for stage, emotion panel, mode switching.

## Example flows included

- Heartbroken explainer
- Podcast discussion (multi-avatar)
- Quiz supervisor session

## Running tests

```bash
cd /home/runner/work/NotebooklmAvatar/NotebooklmAvatar
python -m unittest discover -s tests -v
```

## Backend-first run

```bash
cd /home/runner/work/NotebooklmAvatar/NotebooklmAvatar
pip install -r requirements.txt
PYTHONPATH=src uvicorn avatarlm.backend.app:app --host 0.0.0.0 --port 8000
```

Available APIs:
- `GET /api/v1/health`
- `POST /api/v1/explainer`
- `POST /api/v1/podcast`
- `POST /api/v1/infographic`
- `POST /api/v1/quiz`
