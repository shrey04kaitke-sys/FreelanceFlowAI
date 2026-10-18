"""Run a small, reproducible local comparison without writing client data to disk."""

from dataclasses import replace

from backend.config import settings
from freelanceflow.demo import DEMO_BRIEF
from freelanceflow.ollama_client import GenerationError, OllamaClient
from freelanceflow.schemas import BriefInput, validate_output

SAMPLE_BRIEFS = {
    "bakery website": DEMO_BRIEF,
    "student portfolio": (
        "A computer science student needs a fast portfolio site with projects, an about page, "
        "contact form, accessible colors, and a simple way to add future projects. The student "
        "has screenshots but needs help organizing the content."
    ),
    "local service booking": (
        "A neighborhood bicycle repair shop wants a mobile site showing services, opening hours, "
        "and a request form for repair appointments. They have no online payments, no booking "
        "calendar, and have not decided who will maintain the site."
    ),
}


def run(model: str, brief: str) -> dict:
    client = OllamaClient(replace(settings, model=model))
    output = client.generate("analysis", BriefInput(brief))
    validate_output("analysis", output)
    return output


if __name__ == "__main__":
    for model in (settings.model, settings.fallback_model):
        print(f"\nMODEL: {model}")
        for name, brief in SAMPLE_BRIEFS.items():
            try:
                result = run(model, brief)
                print(
                    f"- {name}: objectives={len(result['objectives']) if isinstance(result['objectives'], list) else 'text'}, "
                    f"deliverables={len(result['deliverables']) if isinstance(result['deliverables'], list) else 'text'}, "
                    f"missing={len(result['missing_information']) if isinstance(result['missing_information'], list) else 'text'}, "
                    f"risks={len(result['risks']) if isinstance(result['risks'], list) else 'text'}"
                )
            except GenerationError as exc:
                print(f"- {name}: ERROR: {exc}")
