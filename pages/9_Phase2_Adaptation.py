"""Step 9 — Phase 2.2: Adaptation Measures.

For each material hazard whose peak risk is Moderate or higher, lets the user
add one or more adaptation measures (description, type, priority, timeframe,
indicative cost and notes).
"""

from __future__ import annotations

import streamlit as st

from core.analysis import peak_risk_per_hazard
from core.hazards import hazard_by_id
from core.matrix import RISK_LABELS, is_at_least
from core.schema import AdaptationMeasure, CRAReport
from core.state import save_report

_PRIORITIES = ("Low", "Medium", "High")


def render(report: CRAReport) -> None:
    """Render the adaptation measures for at-risk hazards."""
    st.header("Phase 2.2 – Adaptation Measures")
    peaks = peak_risk_per_hazard(report)
    at_risk = {hid: lvl for hid, lvl in peaks.items() if is_at_least(lvl, "M")}

    if not at_risk:
        st.info(
            "No hazards currently reach Moderate risk or above. "
            "Complete Steps 6–8, or no adaptation measures are required."
        )
        save_report(report)
        return

    st.caption("Add adaptation measures for hazards with peak risk ≥ Moderate.")
    for hazard_id, level in at_risk.items():
        hazard = hazard_by_id(hazard_id)
        with st.expander(f"{hazard.name} — peak risk: {RISK_LABELS[level]}", expanded=False):
            measures = [m for m in report.adaptation if m.hazard_id == hazard_id]
            for i, measure in enumerate(measures):
                st.markdown(f"**Measure {i + 1}**")
                measure.description = st.text_area(
                    "Description", measure.description, key=f"ad_d_{hazard_id}_{i}", height=70
                )
                c1, c2, c3 = st.columns(3)
                measure.physical = c1.selectbox(
                    "Type", [True, False],
                    index=0 if measure.physical else 1,
                    format_func=lambda b: "Physical" if b else "Non-physical",
                    key=f"ad_t_{hazard_id}_{i}",
                )
                measure.priority = c2.selectbox(
                    "Priority", _PRIORITIES,
                    index=_PRIORITIES.index(measure.priority)
                    if measure.priority in _PRIORITIES else 1,
                    key=f"ad_p_{hazard_id}_{i}",
                )
                measure.timeframe_years = c3.number_input(
                    "Timeframe (years)", min_value=0, max_value=200,
                    value=measure.timeframe_years, key=f"ad_tf_{hazard_id}_{i}",
                )
                c4, c5 = st.columns(2)
                measure.indicative_cost = c4.text_input(
                    "Indicative cost", measure.indicative_cost, key=f"ad_c_{hazard_id}_{i}"
                )
                measure.notes = c5.text_input(
                    "Notes", measure.notes, key=f"ad_n_{hazard_id}_{i}"
                )
                if st.button("Remove measure", key=f"ad_del_{hazard_id}_{i}"):
                    report.adaptation.remove(measure)
                    save_report(report)
                    st.rerun()

            if st.button("➕ Add measure", key=f"ad_add_{hazard_id}"):
                report.adaptation.append(AdaptationMeasure(hazard_id=hazard_id))
                save_report(report)
                st.rerun()

    save_report(report)
