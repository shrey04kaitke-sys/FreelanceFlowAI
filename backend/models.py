from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BriefRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=20, max_length=20_000)
    client_name: str | None = Field(default=None, max_length=200)
    currency: str = Field(default="USD", pattern=r"^[A-Z]{3}$")

    @field_validator("text")
    @classmethod
    def non_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Brief must not be blank.")
        return value.strip()


class CostItemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: str = Field(min_length=1, max_length=300)
    hours: float = Field(default=0, ge=0, le=1_000_000)
    cost: float = Field(default=0, ge=0, le=1_000_000_000)


class PricingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: list[CostItemRequest] = Field(min_length=1, max_length=200)
    hourly_rate: float = Field(ge=0, le=1_000_000)
    contingency_percent: float = Field(default=0, ge=0, le=100)


class SaveHistoryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    client: str = Field(min_length=1, max_length=200)
    brief: str = Field(min_length=20, max_length=20_000)
    workflow: str = Field(min_length=1, max_length=50)
    output: dict[str, Any]


class GenerationResponse(BaseModel):
    workflow: str
    model: str
    output: dict[str, Any]


class HistoryRecord(BaseModel):
    id: int
    client: str
    workflow: str
    created_at: str
    output: dict[str, Any]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    ollama_reachable: bool
    model: str
    configured_model: str
    fallback_model: str
    history_enabled: bool
