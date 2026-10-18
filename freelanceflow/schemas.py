from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BriefInput:
    text: str
    client_name: str | None = None

    def __post_init__(self) -> None:
        cleaned = self.text.strip()
        if len(cleaned) < 20:
            raise ValueError("Please provide at least 20 characters of project requirements.")
        if len(cleaned) > 20000:
            raise ValueError("Briefs are limited to 20,000 characters.")
        if self.client_name and len(self.client_name.strip()) > 200:
            raise ValueError("Client name is limited to 200 characters.")


REQUIRED_KEYS = {
    "analysis": {"objectives", "deliverables", "assumptions", "missing_information", "risks"},
    "proposal": {"project_overview", "approach", "deliverables", "exclusions", "timeline", "terms"},
    "scope": {"deliverables", "acceptance_criteria", "dependencies", "out_of_scope"},
    "milestones": {"milestones"},
    "invoice": {"reference", "status", "line_items", "payment_terms"},
}


def validate_output(workflow: str, value: Any) -> dict:
    if not isinstance(value, dict):
        raise ValueError("The model returned an invalid structured response.")
    missing = REQUIRED_KEYS.get(workflow, set()) - value.keys()
    if missing:
        raise ValueError(f"The model response is missing: {', '.join(sorted(missing))}.")
    for key in REQUIRED_KEYS[workflow]:
        if not isinstance(value[key], (list, str, dict)):
            raise ValueError(f"The model field '{key}' has an unsupported type.")
    if workflow == "invoice" and value["status"] != "DRAFT":
        raise ValueError("Invoice output must remain labelled DRAFT.")
    return value
