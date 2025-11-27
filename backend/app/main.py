from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import routes_evidence, routes_reports
from app.config import settings


app = FastAPI(
    title=settings.app_name,
    description="Backend orchestration tier for the AI Crime Evidence Organizer.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_evidence.router, prefix="/evidence", tags=["evidence"])
app.include_router(routes_reports.router, prefix="/reports", tags=["reports"])

# Serve frontend static files
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    return {
        "message": "AI Crime Evidence Organizer API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "frontend": "/static/index.html",
    }


@app.get("/health", tags=["meta"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/.well-known/appspecific/com.chrome.devtools.json")
async def chrome_devtools_config() -> JSONResponse:
    """
    Suppress Chrome DevTools 404 errors.
    Chrome DevTools automatically requests this file when open.
    Returns empty JSON to prevent 404 logs.
    """
    return JSONResponse(content={})

