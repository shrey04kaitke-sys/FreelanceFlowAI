"""Streamlit entry point for FreelanceFlow AI."""

from __future__ import annotations

import json
from uuid import uuid4
from datetime import date

import streamlit as st

from freelanceflow.config import settings
from freelanceflow.demo import DEMO_BRIEF
from freelanceflow.exports import csv_bytes, markdown_bytes
from freelanceflow.history import HistoryStore
from freelanceflow.ollama_client import GenerationError, OllamaClient
from freelanceflow.pricing import CostItem, calculate_estimate
from freelanceflow.prompts import WORKFLOW_LABELS
from freelanceflow.schemas import BriefInput, validate_output

st.set_page_config(page_title="FreelanceFlow AI", page_icon="⚡", layout="wide")

if "brief" not in st.session_state:
    st.session_state.brief = ""
if "generated" not in st.session_state:
    st.session_state.generated = {}


@st.cache_resource
def get_client() -> OllamaClient:
    return OllamaClient(settings)


@st.cache_resource
def get_history() -> HistoryStore:
    return HistoryStore(settings.history_path)


def download_button(label: str, value: str, filename: str, mime: str = "text/markdown") -> None:
    st.download_button(label, data=value.encode("utf-8"), file_name=filename, mime=mime)


st.title("⚡ FreelanceFlow AI")
st.caption("Turn a rough brief into a reviewable proposal, scope, plan, estimate, and invoice draft — locally.")

with st.sidebar:
    st.subheader("Local setup")
    st.success(f"Ollama model: `{settings.model}`")
    st.caption("Inference stays on this computer. Generated content is untrusted and should be reviewed.")
    with st.expander("Privacy notice"):
        st.write("Your brief is sent only to the Ollama server configured on this machine. Nothing is uploaded by this app.")
        st.write("History is optional and stored in a local SQLite file. You can delete it below.")
    if st.button("Load demo brief", use_container_width=True):
        st.session_state.brief = DEMO_BRIEF
        st.rerun()
    if st.button("Delete local history", use_container_width=True):
        get_history().clear()
        st.success("Local history deleted.")

brief = st.text_area(
    "Client brief",
    value=st.session_state.brief,
    height=220,
    placeholder="Paste the client's rough requirements, constraints, budget, and desired outcome...",
)
st.session_state.brief = brief

if not brief.strip():
    st.info("Start with a client brief, or load the demo brief from the sidebar.")
    st.stop()

col1, col2 = st.columns([2, 1])
with col1:
    client_name = st.text_input("Client name (optional)", placeholder="Leave blank if unknown")
with col2:
    currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "INR"], index=0)

try:
    brief_input = BriefInput(text=brief, client_name=client_name or None)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

tabs = st.tabs(["Analyze", "Proposal", "Scope", "Milestones", "Pricing", "Invoice"])

def run_workflow(workflow: str) -> None:
    try:
        with st.spinner(f"Generating {WORKFLOW_LABELS[workflow].lower()} locally..."):
            result = get_client().generate(workflow, brief_input, currency=currency)
        if workflow == "invoice":
            result["reference"] = f"FF-{date.today().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"
            result["status"] = "DRAFT"
        validate_output(workflow, result)
        st.session_state.generated[workflow] = result
        st.rerun()
    except (GenerationError, ValueError) as exc:
        st.error(str(exc))


def render_result(workflow: str, filename: str) -> None:
    result = st.session_state.generated.get(workflow)
    if not result:
        st.info("No document generated yet.")
        if st.button(f"Generate {WORKFLOW_LABELS[workflow]}", key=f"generate-{workflow}"):
            run_workflow(workflow)
        return
    text = json.dumps(result, indent=2)
    edited = st.text_area("Review and edit this JSON-backed draft", text, height=420, key=f"edit-{workflow}")
    try:
        parsed = json.loads(edited)
        validate_output(workflow, parsed)
        st.session_state.generated[workflow] = parsed
    except (json.JSONDecodeError, ValueError) as exc:
        st.warning(f"Draft is not export-ready until corrected: {exc}")
    markdown = _to_markdown(WORKFLOW_LABELS[workflow], st.session_state.generated[workflow])
    download_button("Download Markdown", markdown, filename)
    download_button("Download text", markdown, filename.replace(".md", ".txt"), "text/plain")
    if st.checkbox("Save this project locally", key=f"save-{workflow}"):
        get_history().save(client_name or "Unnamed client", brief, workflow, st.session_state.generated[workflow])
        st.caption("Saved locally with your consent.")


def _to_markdown(title: str, data: dict) -> str:
    lines = [f"# {title}", "", f"_Generated locally on {date.today().isoformat()}. Review before use._", ""]
    for key, value in data.items():
        heading = key.replace("_", " ").title()
        lines.append(f"## {heading}")
        if isinstance(value, list):
            lines.extend(f"- {item}" if not isinstance(item, dict) else f"- {json.dumps(item)}" for item in value)
        elif isinstance(value, dict):
            lines.extend(f"- **{k.replace('_', ' ').title()}:** {v}" for k, v in value.items())
        else:
            lines.append(str(value))
        lines.append("")
    return "\n".join(lines)


with tabs[0]:
    render_result("analysis", "brief-analysis.md")
with tabs[1]:
    render_result("proposal", "proposal.md")
with tabs[2]:
    render_result("scope", "scope-of-work.md")
with tabs[3]:
    result = st.session_state.generated.get("milestones")
    if not result:
        st.info("Generate a milestone plan from the brief.")
        if st.button("Generate Milestones"):
            run_workflow("milestones")
    else:
        st.dataframe(result["milestones"], use_container_width=True, hide_index=True)
        st.download_button("Download milestones CSV", csv_bytes(result["milestones"]), "milestones.csv", "text/csv")
        render_result("milestones", "milestones.md")
with tabs[4]:
    st.subheader("Transparent estimate")
    st.caption("Enter your own assumptions. This tool does not verify market rates.")
    rate = st.number_input("Hourly rate", min_value=0.0, value=75.0, step=5.0)
    tax = st.number_input("Contingency percentage", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
    raw_items = st.data_editor(
        [{"description": "Discovery and planning", "hours": 8.0, "cost": 0.0}],
        num_rows="dynamic",
        use_container_width=True,
    )
    if st.button("Calculate estimate"):
        try:
            rows = raw_items.to_dict("records") if hasattr(raw_items, "to_dict") else raw_items
            items = [CostItem(str(row["description"]), float(row["hours"]), float(row["cost"])) for row in rows]
            estimate = calculate_estimate(items, rate, tax)
            st.session_state.generated["pricing"] = estimate
        except (KeyError, TypeError, ValueError) as exc:
            st.error(f"Check the pricing rows: {exc}")
    if "pricing" in st.session_state.generated:
        pricing = st.session_state.generated["pricing"]
        st.metric("Estimated total", f"{currency} {pricing['total']:.2f}")
        st.json(pricing)
        st.download_button("Download cost CSV", csv_bytes(pricing["items"]), "cost-breakdown.csv", "text/csv")
with tabs[5]:
    result = st.session_state.generated.get("invoice")
    if not result:
        st.info("Generate a draft invoice after reviewing your estimate.")
        if st.button("Generate Invoice Draft"):
            run_workflow("invoice")
    else:
        st.warning("DRAFT ONLY — not a tax-compliant invoice. Review with a qualified professional.")
        render_result("invoice", "invoice-draft.md")
