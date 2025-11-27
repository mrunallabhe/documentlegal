## Backend Service

FastAPI-based orchestration tier handling evidence ingestion, processing, reasoning, and reporting.

### Local Setup
1. `python -m venv .venv && .venv\\Scripts\\activate`
2. `pip install -r requirements.txt`
3. `uvicorn app.main:app --reload`

### Folder Structure
```
backend/
  app/
    api/        # REST endpoints
    services/   # domain logic for each pipeline stage
    models/     # Pydantic schemas shared across routes
    config.py   # environment + path settings
```

### Notes
- Processing functions are scaffolds; replace stubs with actual model inference calls.
- All steps emit structured logs to ease debugging and audit trail construction.

