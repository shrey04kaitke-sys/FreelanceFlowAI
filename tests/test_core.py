import json
from pathlib import Path

import pytest

from freelanceflow.exports import csv_bytes
from freelanceflow.history import HistoryStore
from freelanceflow.ollama_client import GenerationError, OllamaClient
from freelanceflow.pricing import CostItem, calculate_estimate
from freelanceflow.schemas import BriefInput, validate_output


def test_pricing_arithmetic():
    result = calculate_estimate([CostItem("Build", 10, 25)], 50, 10)
    assert result["subtotal"] == 525
    assert result["contingency"] == 52.5
    assert result["total"] == 577.5


def test_pricing_rejects_negative():
    with pytest.raises(ValueError):
        CostItem("Bad", -1, 0)


def test_brief_validation():
    with pytest.raises(ValueError):
        BriefInput("too short")
    assert BriefInput("A sufficiently detailed client requirement.") .text.startswith("A")


def test_structured_output_validation():
    with pytest.raises(ValueError):
        validate_output("analysis", {"objectives": []})
    valid = {key: [] for key in ("objectives", "deliverables", "assumptions", "missing_information", "risks")}
    assert validate_output("analysis", valid) == valid


def test_invoice_must_be_draft():
    value = {"reference": "X", "status": "FINAL", "line_items": [], "payment_terms": "TBD"}
    with pytest.raises(ValueError):
        validate_output("invoice", value)


def test_csv_export():
    output = csv_bytes([{"name": "Discovery", "duration": "2 days"}]).decode()
    assert "name,duration" in output
    assert "Discovery,2 days" in output


def test_csv_export_neutralizes_spreadsheet_formulas():
    output = csv_bytes([{"description": "=HYPERLINK(\"https://example.com\")"}]).decode()
    assert "'=HYPERLINK" in output


def test_history_consent_store_and_delete(tmp_path: Path):
    store = HistoryStore(tmp_path / "history.sqlite3")
    store.save("Client", "Brief", "analysis", {"risks": []})
    store.clear()
    with __import__("sqlite3").connect(tmp_path / "history.sqlite3") as connection:
        assert connection.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 0


class FakeSession:
    def get(self, *_args, **_kwargs):
        return FakeResponse({"models": [{"name": "qwen2.5:3b"}]})

    def post(self, *_args, **_kwargs):
        return FakeResponse({"response": json.dumps({"objectives": [], "deliverables": [], "assumptions": [], "missing_information": [], "risks": []})})


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def raise_for_status(self):
        return None

    def json(self):
        return self.body


def test_ollama_generation_is_parsed():
    from freelanceflow.config import Settings
    client = OllamaClient(Settings(), FakeSession())
    result = client.generate("analysis", BriefInput("A sufficiently detailed client requirement."))
    assert result["objectives"] == []


def test_ollama_model_missing():
    from freelanceflow.config import Settings
    class Missing(FakeSession):
        def get(self, *_args, **_kwargs):
            return FakeResponse({"models": []})
    with pytest.raises(GenerationError):
        OllamaClient(Settings(), Missing()).generate("analysis", BriefInput("A sufficiently detailed client requirement."))
