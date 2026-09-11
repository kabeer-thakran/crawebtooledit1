"""Step 10 — Generate Report.

Validates the dataset, renders the Word report via
:func:`rendering.docx_renderer.render`, and offers JSON save/resume so users
can pause and continue an assessment.
"""

from __future__ import annotations

import streamlit as st

from core.schema import CRAReport
from core.state import from_json, save_report, to_json
from rendering.docx_renderer import render as render_docx


def _validate(report: CRAReport) -> list[str]:
    """Return a list of human-readable missing/invalid input messages."""
    issues: list[str] = []
    p = report.project
    required = {
        "Project Name": p.project_name,
        "Client": p.client,
        "Job Number": p.job_number,
        "City": p.city,
        "Country": p.country,
        "Project Scope": p.project_scope,
        "EU Taxonomy Activity": p.taxonomy_activity,
    }
    for label, value in required.items():
        if not str(value).strip():
            issues.append(f"Missing: {label}")
    if not report.material_hazard_ids():
        issues.append("No material hazards selected (complete Phase 1, Steps 3–5).")
    return issues


def _safe_name(report: CRAReport) -> str:
    """Return a filesystem-safe filename for the generated report."""
    name = report.project.project_name or "Project"
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    return f"CRA_Report_{safe}_{report.project.report_date.isoformat()}.docx"


def render(report: CRAReport) -> None:
    """Render Step 10: validation, report generation and session save/resume."""
    st.header("Step 10 · Generate Report")

    st.subheader("Validate inputs")
    if st.button("Validate inputs", type="primary"):
        issues = _validate(report)
        if issues:
            st.warning("Some inputs are incomplete:")
            for issue in issues:
                st.markdown(f"- {issue}")
        else:
            st.success("All required inputs are present. Ready to generate.")

    st.subheader("Generate Word report")
    if st.button("Generate Word Report"):
        try:
            data = render_docx(report)
            st.download_button(
                "⬇️ Download report",
                data=data,
                file_name=_safe_name(report),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            st.success("Report generated.")
        except Exception as exc:  # surface rendering errors to the user
            st.error(f"Report generation failed: {exc}")

    st.divider()
    st.subheader("Save / resume session")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "⬇️ Download session as JSON",
            data=to_json(report),
            file_name="cra_session.json",
            mime="application/json",
        )
    with c2:
        uploaded = st.file_uploader("Upload session JSON", type=["json"])
        if uploaded is not None and st.button("Load session"):
            try:
                save_report(from_json(uploaded.getvalue()))
                st.success("Session loaded. Switch tabs to review.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not load session: {exc}")
