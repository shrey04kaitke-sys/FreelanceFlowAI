import json
from pathlib import Path

import requests
import pytest
from fastapi.testclient import TestClient

from backend.config import BackendSettings
from backend.main import app, get_service
from backend.services import BackendService
from freelanceflow.config import Settings
from freelanceflow.ollama_client import GenerationError, OllamaClient
from freelanceflow.schemas import BriefInput


ANALYSIS = {
    "objectives": ["Launch a useful site"],
    "deliverables": ["Responsive website"],
    "assumptions": ["Client supplies assets"],
    "missing_information": ["Final copy"],
    "risks": ["Scope expansion"],
}


class FakeClient:
    def list_models(self):
        return ["qwen2.5:3b"]

    def generate(self, workflow, brief, currency="USD"):
        if workflow == "invoice":
            return {"reference": "server-replaced", "status": "DRAFT", "line_items": [], "payment_terms": "TBD"}
        return {
            "objectives": [],
            "deliverables": [],
            "assumptions": [],
            "missing_information": [],
            "risks": [],
        } if workflow == "analysis" else {
            "project_overview": "Draft",
            "approach": [],
            "deliverables": [],
            "exclusions": [],
            "timeline": "TBD",
            "terms": [],
        }


def service(tmp_path: Path) -> BackendService:
    configured = BackendSettings(history_path=tmp_path / "history.sqlite3")
    instance = BackendService(configured)
    instance.client = FakeClient()
    return instance


def test_analyze_endpoint_and_validation(tmp_path, monkeypatch):
    instance = service(tmp_path)
    app.dependency_overrides[get_service] = lambda: instance
    client = TestClient(app)
    response = client.post("/api/analyze", json={"text": "A sufficiently detailed client requirement."})
    assert response.status_code == 200
    assert response.json()["output"]["objectives"] == []
    assert response.json()["model"] == "qwen2.5:3b"
    invalid = client.post("/api/analyze", json={"text": "short"})
    assert invalid.status_code == 422
    app.dependency_overrides.clear()


def test_pricing_and_invoice_are_safe(tmp_path):
    instance = service(tmp_path)
    app.dependency_overrides[get_service] = lambda: instance
    client = TestClient(app)
    pricing = client.post("/api/pricing", json={"items": [{"description": "Build", "hours": 10, "cost": 25}], "hourly_rate": 50, "contingency_percent": 10})
    assert pricing.status_code == 200
    assert pricing.json()["total"] == 577.5
    invoice = client.post("/api/invoice", json={"text": "A sufficiently detailed client requirement."})
    assert invoice.status_code == 200
    assert invoice.json()["output"]["status"] == "DRAFT"
    app.dependency_overrides.clear()


def test_history_create_list_delete(tmp_path):
    instance = service(tmp_path)
    app.dependency_overrides[get_service] = lambda: instance
    client = TestClient(app)
    saved = client.post("/api/history", json={"client": "Client", "brief": "A sufficiently detailed client requirement.", "workflow": "analysis", "output": ANALYSIS})
    assert saved.status_code == 201
    records = client.get("/api/history")
    assert records.status_code == 200
    record_id = records.json()[0]["id"]
    assert client.delete(f"/api/history/{record_id}").status_code == 204
    assert client.get("/api/history").json() == []
    app.dependency_overrides.clear()


def test_csv_export():
    response = TestClient(app).get("/api/exports/csv", params={"rows": json.dumps([{"name": "Discovery"}])})
    assert response.status_code == 200
    assert "Discovery" in response.text


class ErrorResponse:
    def __init__(self, body):
        self.body = body

    def raise_for_status(self):
        return None

    def json(self):
        return self.body


class ErrorSession:
    def __init__(self, response=None, timeout=False):
        self.response = response
        self.timeout = timeout

    def get(self, *_args, **_kwargs):
        if self.timeout:
            raise requests.Timeout()
        return ErrorResponse({"models": [{"name": "qwen2.5:3b"}]})

    def post(self, *_args, **_kwargs):
        if self.timeout:
            raise requests.Timeout()
        return ErrorResponse(self.response or {"response": "not-json"})


def test_malformed_generation_is_reported():
    client = OllamaClient(Settings(), ErrorSession())
    with pytest.raises(GenerationError, match="malformed"):
        client.generate("analysis", BriefInput("A sufficiently detailed client requirement."))


def test_generation_timeout_is_reported():
    client = OllamaClient(Settings(), ErrorSession(timeout=True))
    with pytest.raises(GenerationError, match="not reachable"):
        client.generate("analysis", BriefInput("A sufficiently detailed client requirement."))


def test_missing_configured_model_is_reported():
    session = ErrorSession()
    session.get = lambda *_args, **_kwargs: ErrorResponse({"models": []})
    client = OllamaClient(Settings(), session)
    with pytest.raises(GenerationError, match="not installed"):
        client.generate("analysis", BriefInput("A sufficiently detailed client requirement."))
