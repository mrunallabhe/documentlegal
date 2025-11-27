from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, UploadFile, HTTPException

from app.config import settings
from app.models.schemas import (
    EvidenceIngestResponse,
    EvidenceProcessingRequest,
    EvidenceProcessingResponse,
)
from app.services.pipeline import EvidencePipeline


router = APIRouter()
pipeline = EvidencePipeline()


@router.post("/upload", response_model=EvidenceIngestResponse)
async def upload_evidence(file: UploadFile = File(...)) -> EvidenceIngestResponse:
    case_id = uuid4().hex
    target_path = settings.upload_dir / f"{case_id}_{file.filename}"
    content = await file.read()
    target_path.write_bytes(content)
    return EvidenceIngestResponse(
        case_id=case_id,
        filename=file.filename,
        stored_path=str(target_path),
        message="Evidence stored. Trigger processing via /evidence/process.",
    )


@router.post("/process", response_model=EvidenceProcessingResponse)
async def process_evidence(
    payload: EvidenceProcessingRequest, tasks: BackgroundTasks
) -> EvidenceProcessingResponse:
    """
    Process evidence in background.
    Note: First-time processing may take 2-5 minutes due to model downloads.
    The report will be available at /reports/{case_id} when ready.
    """
    artifact_path = Path(payload.artifact_path)
    if not artifact_path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found on server.")

    def _run_pipeline() -> None:
        """Background task to run the pipeline."""
        try:
            # Create status file to indicate processing has started
            from app.config import settings
            status_path = settings.reports_dir / f"{payload.case_id}.status"
            status_path.write_text("processing", encoding="utf-8")
            
            print(f"[Background Task] Starting pipeline for case {payload.case_id}")
            pipeline.execute(case_id=payload.case_id, artifact_path=artifact_path)
            print(f"[Background Task] Pipeline completed for case {payload.case_id}")
            
            # Remove status file when done (report file will exist)
            if status_path.exists():
                status_path.unlink()
        except Exception as e:
            print(f"[Background Task] ERROR in pipeline for case {payload.case_id}: {e}")
            import traceback
            traceback.print_exc()
            # Mark as failed
            from app.config import settings
            status_path = settings.reports_dir / f"{payload.case_id}.status"
            status_path.write_text("failed", encoding="utf-8")

    tasks.add_task(_run_pipeline)
    return EvidenceProcessingResponse(
        case_id=payload.case_id,
        artifact_path=str(artifact_path),
        status="queued",
        message="Processing started in background. This may take 2-5 minutes on first run (models downloading). Poll /reports/{case_id} to check status.",
    )
