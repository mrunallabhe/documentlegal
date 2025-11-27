from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class EvidenceIngestResponse(BaseModel):
    case_id: str
    filename: str
    stored_path: str
    message: str


class EvidenceProcessingRequest(BaseModel):
    case_id: str = Field(..., description="Case identifier returned by upload API.")
    artifact_path: str = Field(..., description="Server path of previously uploaded file.")


class EvidenceProcessingResponse(BaseModel):
    case_id: str
    artifact_path: str
    status: Literal["queued", "running", "completed", "failed"]
    message: str


class ReportSummary(BaseModel):
    case_id: str
    generated_at: datetime
    timeline_events: int
    inconsistencies: int
    missing_evidence: list[str]
    report_path: str
    preview: dict[str, Any]

