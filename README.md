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
