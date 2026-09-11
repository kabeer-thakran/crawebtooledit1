"""Small reusable Streamlit widgets shared across the CRA step pages.

Keeps the score, Yes/No and scenario/horizon controls consistent everywhere
they appear in the workflow.
"""

from __future__ import annotations

import streamlit as st

from core.schema import SCORE_LABELS, Horizon, YesNo


def info_tooltip(title: str, text: str, *, key: str | None = None) -> None:
    """Render a reusable info popover with an inline ⓘ icon.

    The text remains visible and reviewable, while preserving the Streamlit
    component style used across the app. When final copy is not yet available,
    we insert a placeholder note for client review.
    """
    with st.popover("ⓘ", use_container_width=False):
        st.caption(f"**{title}**")
        st.write(text)


def flow_breadcrumb() -> None:
    """Render the full CRA flow sequence as a readable breadcrumb."""
    flow = (
        "Project Information >> Phase 0 – Preparation >> Phase 1 – Spatial Screening >> "
        "Phase 1 – Materiality >> Phase 1 – Screening Results >> Phase 2 – Hazard Thresholds >> "
        "Phase 2 – Hazard Assessment >> Phase 2 – Vulnerability Assessment >> "
        "Phase 2 – Risk Calculation >> Phase 2.2 – Adaptation Measures >> Generate Report"
    )
    st.markdown(
        f"<div class='cra-breadcrumb'>{flow}</div>",
        unsafe_allow_html=True,
    )


def score_select(label: str, value: int, key: str) -> int:
    """Render a 1–5 score dropdown with ``Very Low … Very High`` labels."""
    options = list(SCORE_LABELS.keys())
    return st.selectbox(
        label,
        options,
        index=options.index(value) if value in options else 0,
        format_func=lambda s: f"{s} – {SCORE_LABELS[s]}",
        key=key,
    )


def yesno_radio(label: str, value: YesNo, key: str) -> YesNo:
    """Render a horizontal Yes/No radio defaulting to the current value."""
    options = [YesNo.YES, YesNo.NO]
    index = options.index(value) if value in options else None
    choice = st.radio(
        label,
        options,
        index=index,
        format_func=lambda v: v.value,
        horizontal=True,
        key=key,
    )
    return choice if choice is not None else YesNo.UNKNOWN


def scenario_horizon_pairs(project) -> list[tuple[str, str]]:
    """Return the ``(scenario, horizon)`` combinations to assess.

    Uses the project's two scenarios across the three assessed horizons.
    """
    scenarios = [project.scenario_a, project.scenario_b]
    horizons = [Horizon.BASELINE.value, Horizon.MID.value, Horizon.END.value]
    return [(s, h) for s in scenarios for h in horizons]


def scenarios(project) -> list[str]:
    """Return the two project scenarios as a list."""
    return [project.scenario_a, project.scenario_b]
