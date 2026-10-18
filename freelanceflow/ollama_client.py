import json
from typing import Any

import requests

from .config import Settings
from .prompts import build_prompt
from .schemas import BriefInput


class GenerationError(RuntimeError):
    """A user-actionable generation failure."""


class OllamaClient:
    def __init__(self, settings: Settings, session: requests.Session | None = None) -> None:
        self.settings = settings
        self.session = session or requests.Session()

    def list_models(self) -> list[str]:
        try:
            response = self.session.get(f"{self.settings.ollama_url}/api/tags", timeout=10)
            response.raise_for_status()
            return [item["name"] for item in response.json().get("models", [])]
        except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
            raise GenerationError("Ollama is not reachable. Start Ollama and try again.") from exc

    def generate(self, workflow: str, brief: BriefInput, currency: str = "USD") -> dict[str, Any]:
        models = self.list_models()
        if self.settings.model not in models:
            raise GenerationError(f"Configured model '{self.settings.model}' is not installed. Set OLLAMA_MODEL to one from `ollama list`.")
        payload = {"model": self.settings.model, "prompt": build_prompt(workflow, brief.text, brief.client_name, currency), "stream": False, "format": "json"}
        try:
            response = self.session.post(f"{self.settings.ollama_url}/api/generate", json=payload, timeout=self.settings.timeout_seconds)
            response.raise_for_status()
            body = response.json()
            result = json.loads(body["response"])
            if not isinstance(result, dict):
                raise ValueError("JSON result was not an object")
            return result
        except requests.Timeout as exc:
            raise GenerationError("Ollama timed out. Try a shorter brief or increase OLLAMA_TIMEOUT_SECONDS.") from exc
        except requests.RequestException as exc:
            raise GenerationError("Ollama could not generate a response. Check that the local service is running.") from exc
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            raise GenerationError("Ollama returned malformed structured data. Please try again.") from exc
