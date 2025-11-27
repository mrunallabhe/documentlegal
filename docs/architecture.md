## Architecture Overview

1. **Upload Gateway** – React/Next.js client hits FastAPI `/evidence/upload`, storing encrypted artifacts in `storage/uploads`.
2. **Processing Queue** – `/evidence/process` schedules background pipeline (Celery/RQ in production; synchronous background task in this scaffold).
3. **Pipeline Steps**
   - Validation (`IngestionService`)
   - Classification (`ClassificationService`)
   - Content extraction (`ExtractionService`)
   - Normalization (`NormalizationService`)
   - Timeline creation (`TimelineService`)
   - Reasoning + missing evidence (`ReasoningService`)
   - Report persistence (`ReportingService`)
4. **Reporting** – `/reports/{case_id}` returns JSON summary; `/reports/{case_id}/download` exposes PDF path placeholder.

### Data Flow
```
Upload → Storage → Pipeline → Timeline/Reasoning → Reports/Dashboard
```

### Deployment Considerations
- Use S3/Azure Blob for evidence at rest, PostgreSQL for metadata, Neo4j for entity graphs.
- GPU-backed workers handle heavy ML tasks; CPU instances manage API + reporting.
- Observability via Prometheus, Loki/ELK, and audit log dashboards.

