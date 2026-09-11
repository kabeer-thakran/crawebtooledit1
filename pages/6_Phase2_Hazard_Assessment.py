"""Step 6 — Phase 2: Hazard Assessment.

For each material hazard, captures the likelihood score (1–5), a threshold
value/unit and a source for every scenario × horizon combination.
"""

from __future__ import annotations

import streamlit as st

from core.hazards import hazard_by_id
from core.schema import CRAReport, HazardAssessment
from core.state import save_report
from ui_helpers import score_select, scenario_horizon_pairs


def _assessment(
    report: CRAReport, hazard_id: str, scenario: str, horizon: str
) -> HazardAssessment:
    """Return the hazard assessment for a hazard × scenario × horizon, creating if absent."""
    for a in report.hazard_assessments:
        if a.hazard_id == hazard_id and a.scenario == scenario and a.horizon == horizon:
            return a
    a = HazardAssessment(hazard_id=hazard_id, scenario=scenario, horizon=horizon)
    report.hazard_assessments.append(a)
    return a


def render(report: CRAReport) -> None:
    """Render the hazard threshold inputs and persist likelihood/threshold values."""
    st.header("Phase 2 – Hazard Thresholds")
    material_ids = report.material_hazard_ids()
    if not material_ids:
        st.info("No material hazards yet. Complete Phase 1 (Steps 3–5) first.")
        return

    pairs = scenario_horizon_pairs(report.project)
    for hazard_id in material_ids:
        hazard = hazard_by_id(hazard_id)
        with st.expander(hazard.name, expanded=False):
            for scenario, horizon in pairs:
                st.markdown(f"**{scenario} · {horizon}**")
                a = _assessment(report, hazard_id, scenario, horizon)
                a.likelihood = score_select(
                    "Likelihood", a.likelihood, key=f"hz_l_{hazard_id}_{scenario}_{horizon}"
                )
                c1, c2, c3 = st.columns([1, 1, 2])
                a.threshold_value = c1.text_input(
                    "Threshold", a.threshold_value,
                    key=f"hz_tv_{hazard_id}_{scenario}_{horizon}",
                )
                a.threshold_unit = c2.text_input(
                    "Unit", a.threshold_unit, key=f"hz_tu_{hazard_id}_{scenario}_{horizon}"
                )
                a.source = c3.text_input(
                    "Source(s)", a.source, key=f"hz_src_{hazard_id}_{scenario}_{horizon}"
                )

    save_report(report)
