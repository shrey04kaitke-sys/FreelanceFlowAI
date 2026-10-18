from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class BackendSettings:
    ollama_url: str = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
    model: str = os.getenv("OLLAMA_MODEL", "gemma3:1b")
    fallback_model: str = os.getenv("OLLAMA_FALLBACK_MODEL", "qwen2.5:3b")
    timeout_seconds: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))
    history_path: Path = Path(os.getenv("FREELANCEFLOW_HISTORY_PATH", "freelanceflow_history.sqlite3"))
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if origin.strip()
    )


settings = BackendSettings()
