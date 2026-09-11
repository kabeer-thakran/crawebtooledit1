"""Step 2 — Phase 0: Preparation.

Provides editable "Typical text – to be adapted" boilerplate, a dynamic
receptor register (the assets assessed for vulnerability later), and a button
to apply suggested timeframe/scenario defaults.
"""

from __future__ import annotations

import streamlit as st

from core.schema import CRAReport, Period, Receptor, Scenario
from core.state import DEFAULT_RECEPTORS, save_report
from ui_helpers import info_tooltip

_DEFAULT_INTRO = (
    "This Climate Risk Assessment (CRA) has been prepared by Arup to assess the "
    "physical climate risks to the project in line with the EU Taxonomy "
    "Do No Significant Harm (DNSH) criteria for climate change adaptation."
)
_DEFAULT_METHOD = (
    "A semi-quantitative methodology is applied across two phases. Phase 1 screens "
    "the 33 standardised climate hazards for relevance at the site and materiality "
    "to the asset. Phase 2 assesses hazard likelihood, receptor vulnerability and "
    "combines them through a 5×5 risk matrix, before defining adaptation measures."
)
_DEFAULT_SCOPE = (
    "The assessment covers the asset and its immediate site context over the "
    "design lifespan, under the selected climate scenarios and time horizons."
)


def _apply_defaults(report: CRAReport) -> None:
    """Populate suggested timeframes, scenarios and boilerplate text."""
    p = report.project
    p.baseline_period = Period(start=1995, end=2014)
    p.mid_century_period = Period(start=2041, end=2060)
    p.end_century_period = Period(start=2081, end=2100)
    p.scenario_a = Scenario.A.value
    p.scenario_b = Scenario.B.value
    ph = report.phase0
    ph.introduction_text = ph.introduction_text or _DEFAULT_INTRO
    ph.methodology_text = ph.methodology_text or _DEFAULT_METHOD
    ph.scope_text = ph.scope_text or _DEFAULT_SCOPE
    if not ph.receptors:
        ph.receptors = list(DEFAULT_RECEPTORS)


def render(report: CRAReport) -> None:
    """Render the Phase 0 preparation content and persisted receptor register."""
    st.header("Phase 0 – Preparation")
    st.caption(
        "[Content placement note: scope and methodology text remain here; project metadata remains under Project Information.]"
    )
    ph = report.phase0

    if st.button("Apply suggested defaults", type="primary"):
        _apply_defaults(report)
        save_report(report)
        st.success("Suggested defaults applied.")

    st.subheader("Typical text — to be adapted")
    info_tooltip("Typical text", "[PLACEHOLDER: guidance to be reviewed with client]")
    ph.introduction_text = st.text_area(
        "Introduction", ph.introduction_text or _DEFAULT_INTRO, height=120
    )
    ph.methodology_text = st.text_area(
        "Methodology", ph.methodology_text or _DEFAULT_METHOD, height=140
    )
    ph.scope_text = st.text_area("Scope", ph.scope_text or _DEFAULT_SCOPE, height=100)

    st.subheader("Receptors")
    info_tooltip("Receptors", "[PLACEHOLDER: receptor guidance text]")
    st.caption("Asset systems assessed for vulnerability in Phase 2. Add or remove as needed.")
    if not ph.receptors:
        ph.receptors = list(DEFAULT_RECEPTORS)

    remove_id: str | None = None
    for i, receptor in enumerate(ph.receptors):
        with st.expander(f"{receptor.name or 'Receptor'} ({receptor.id})", expanded=False):
            c1, c2 = st.columns(2)
            receptor.id = c1.text_input("ID", receptor.id, key=f"rec_id_{i}")
            receptor.name = c2.text_input("Name", receptor.name, key=f"rec_name_{i}")
            receptor.description = st.text_input(
                "Description", receptor.description, key=f"rec_desc_{i}"
            )
            receptor.components = st.text_input(
                "Components", receptor.components, key=f"rec_comp_{i}"
            )
            if st.button("Remove", key=f"rec_del_{i}"):
                remove_id = receptor.id

    if remove_id is not None:
        ph.receptors = [r for r in ph.receptors if r.id != remove_id]
        save_report(report)
        st.rerun()

    if st.button("➕ Add receptor"):
        new_index = len(ph.receptors) + 1
        ph.receptors.append(Receptor(id=f"receptor_{new_index}", name=f"Receptor {new_index}"))
        save_report(report)
        st.rerun()

    save_report(report)
