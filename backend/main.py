from pathlib import Path
import sys
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from freelanceflow.demo import DEMO_BRIEF
from freelanceflow.exports import csv_bytes
from freelanceflow.ollama_client import GenerationError
from freelanceflow.schemas import REQUIRED_KEYS

from .config import settings
from .models import (
    BriefRequest,
    GenerationResponse,
    HealthResponse,
    HistoryRecord,
    PricingRequest,
    SaveHistoryRequest,
)
from .services import BackendService

app = FastAPI(title="FreelanceFlow AI API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)


def get_service() -> BackendService:
    return BackendService(settings)


@app.exception_handler(ValueError)
async def value_error_handler(_, exc: ValueError) -> Response:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.get("/api/health", response_model=HealthResponse)
def health(service: BackendService = Depends(get_service)) -> dict[str, Any]:
    result = service.health()
    result["configured_model"] = settings.model
    result["fallback_model"] = settings.fallback_model
    return result


@app.get("/api/models")
def models(service: BackendService = Depends(get_service)) -> dict[str, Any]:
    try:
        return {
            "models": service.client.list_models(),
            "configured_model": settings.model,
            "fallback_model": settings.fallback_model,
        }
    except GenerationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/demo-brief")
def demo_brief() -> dict[str, str]:
    return {"brief": DEMO_BRIEF}


def generation_route(workflow: str, request: BriefRequest, service: BackendService) -> GenerationResponse:
    try:
        output = service.generate(workflow, request.text, request.client_name, request.currency)
        return GenerationResponse(workflow=workflow, model=getattr(service, "last_model", service.settings.model), output=output)
    except GenerationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/analyze", response_model=GenerationResponse)
def analyze(request: BriefRequest, service: BackendService = Depends(get_service)) -> GenerationResponse:
    return generation_route("analysis", request, service)


@app.post("/api/proposal", response_model=GenerationResponse)
def proposal(request: BriefRequest, service: BackendService = Depends(get_service)) -> GenerationResponse:
    return generation_route("proposal", request, service)


@app.post("/api/scope", response_model=GenerationResponse)
def scope(request: BriefRequest, service: BackendService = Depends(get_service)) -> GenerationResponse:
    return generation_route("scope", request, service)


@app.post("/api/milestones", response_model=GenerationResponse)
def milestones(request: BriefRequest, service: BackendService = Depends(get_service)) -> GenerationResponse:
    return generation_route("milestones", request, service)


@app.post("/api/invoice", response_model=GenerationResponse)
def invoice(request: BriefRequest, service: BackendService = Depends(get_service)) -> GenerationResponse:
    return generation_route("invoice", request, service)


@app.post("/api/pricing")
def pricing(request: PricingRequest, service: BackendService = Depends(get_service)) -> dict[str, Any]:
    try:
        return service.pricing(request.items, request.hourly_rate, request.contingency_percent)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/history", response_model=list[HistoryRecord])
def history(service: BackendService = Depends(get_service)) -> list[dict[str, Any]]:
    """Local-only persistence endpoint; do not expose the server beyond loopback without auth."""
    return service.list_history()


@app.post("/api/history", status_code=status.HTTP_201_CREATED)
def save_history(request: SaveHistoryRequest, service: BackendService = Depends(get_service)) -> dict[str, str]:
    service.save_history(request.client, request.brief, request.workflow, request.output)
    return {"status": "saved"}


@app.delete("/api/history/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history(record_id: int, service: BackendService = Depends(get_service)) -> Response:
    if not service.delete_history(record_id):
        raise HTTPException(status_code=404, detail="History record not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete("/api/history", status_code=status.HTTP_204_NO_CONTENT)
def clear_history(service: BackendService = Depends(get_service)) -> Response:
    service.clear_history()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/exports/csv")
def export_csv(rows: str) -> Response:
    import json

    try:
        parsed = json.loads(rows)
        if not isinstance(parsed, list) or not all(isinstance(row, dict) for row in parsed):
            raise ValueError
        return Response(content=csv_bytes(parsed), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=export.csv"})
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail="Export rows must be a JSON array of objects.") from exc
