from dataclasses import replace
from typing import Any

from freelanceflow.history import HistoryStore
from freelanceflow.ollama_client import GenerationError, OllamaClient
from freelanceflow.pricing import CostItem, calculate_estimate
from freelanceflow.schemas import BriefInput, REQUIRED_KEYS, validate_output

from .config import BackendSettings
from .models import CostItemRequest


class BackendService:
    def __init__(self, settings: BackendSettings) -> None:
        self.settings = settings
        self.client = OllamaClient(settings)
        self.history = HistoryStore(settings.history_path)

    def health(self) -> dict[str, Any]:
        try:
            self.client.list_models()
            reachable = True
        except GenerationError:
            reachable = False
        return {
            "status": "ok",
            "ollama_reachable": reachable,
            "model": self.settings.model,
            "history_enabled": True,
        }

    def generate(self, workflow: str, text: str, client_name: str | None, currency: str) -> dict[str, Any]:
        brief = BriefInput(text=text, client_name=client_name)
        available = self.client.list_models()
        selected = next(
            (model for model in (self.settings.model, self.settings.fallback_model) if model in available),
            None,
        )
        if selected is None:
            raise GenerationError(
                f"Neither configured model '{self.settings.model}' nor fallback '{self.settings.fallback_model}' is installed."
            )
        client = (
            self.client
            if selected == self.settings.model or not isinstance(self.client, OllamaClient)
            else OllamaClient(replace(self.settings, model=selected))
        )
        output = client.generate(workflow, brief, currency=currency)
        self.last_model = selected
        missing_fields = REQUIRED_KEYS[workflow] - output.keys()
        for field in missing_fields:
            output[field] = "TBD"
        if workflow == "invoice":
            from uuid import uuid4
            from datetime import date

            output["reference"] = f"FF-{date.today():%Y%m%d}-{uuid4().hex[:8].upper()}"
            output["status"] = "DRAFT"
        validate_output(workflow, output)
        return output

    def pricing(self, items: list[CostItemRequest], hourly_rate: float, contingency_percent: float) -> dict[str, Any]:
        cost_items = [CostItem(item.description, item.hours, item.cost) for item in items]
        return calculate_estimate(cost_items, hourly_rate, contingency_percent)

    def save_history(self, client: str, brief: str, workflow: str, output: dict[str, Any]) -> None:
        self.history.save(client, brief, workflow, output)

    def list_history(self) -> list[dict[str, Any]]:
        return self.history.list_records()

    def delete_history(self, record_id: int) -> bool:
        return self.history.delete(record_id)

    def clear_history(self) -> None:
        self.history.clear()
