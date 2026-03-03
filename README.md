# GEO System (MVP)

A practical GEO (Generative Engine Optimization) system to help brands become preferred answers in LLM outputs.

## What it does
- Build an intent graph from prompts
- Dedupe and cluster prompts by bucket
- Store and manage GEO assets (entity/faq/comparison/use-case)
- Run model visibility scans (mention/citation/recommendation)
- Support a real OpenAI-compatible scan adapter
- Generate weekly KPI reports with bucket breakdown

## Architecture
- `src/geo_system/intent_engine.py`
- `src/geo_system/content_engine.py`
- `src/geo_system/model_testing_engine.py`
- `src/geo_system/feedback_orchestrator.py`
- `src/geo_system/reporting.py`

## Quick start
```bash
cd geo-system
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

geo init --project tripo3d --domain tripo3d.ai --brand tripo3d
geo prompts generate --seed "3d,ai 3d,text to 3d,image to 3d" --count 100
geo adapter set --base-url https://lonr.zeabur.app/v1 --api-key YOUR_KEY --model gpt-5.3-codex
geo scan run --models openai:live,claude,gemini
geo report weekly
```

## Notes
This MVP stores data locally in JSON files for simplicity.
