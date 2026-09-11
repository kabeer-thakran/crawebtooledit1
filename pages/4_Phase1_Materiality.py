"""Step 4 — Phase 1 / Step 2: Materiality Screening.

For hazards flagged present at the site (Step 3), assess whether each hazard
has a significant impact on each receptor, with comment and source.
"""

from __future__ import annotations

import streamlit as st

from core.hazards import hazard_by_id
from core.schema import CRAReport, MaterialityCell, YesNo
from core.state import save_report


def _yes_hazard_ids(report: CRAReport) -> list[str]:
    """Return hazard ids answered YES in spatial screening (Step 3)."""
    return [s.hazard_id for s in report.screening if s.at_site == YesNo.YES]


def _cell(report: CRAReport, hazard_id: str, receptor_id: str) -> MaterialityCell:
    """Return the materiality cell for a hazard × receptor, creating if absent."""
    for c in report.materiality:
        if c.hazard_id == hazard_id and c.receptor_id == receptor_id:
            return c
    cell = MaterialityCell(hazard_id=hazard_id, receptor_id=receptor_id)
    report.materiality.append(cell)
    return cell


def render(report: CRAReport) -> None:
    """Render Step 4 and persist materiality answers per hazard × receptor."""
    st.header("Step 4 · Phase 1 — Materiality Screening")
    yes_ids = _yes_hazard_ids(report)
    if not yes_ids:
        st.info("No hazards marked 'Yes' in Step 3 yet. Complete spatial screening first.")
        return

    receptors = report.phase0.receptors
    if not receptors:
        st.warning("No receptors defined. Add receptors in Step 2 first.")
        return

    st.caption("Does the hazard have a significant impact on each receptor?")
    for hazard_id in yes_ids:
        hazard = hazard_by_id(hazard_id)
        with st.expander(hazard.name, expanded=False):
            for receptor in receptors:
                cell = _cell(report, hazard_id, receptor.id)
                st.markdown(f"**{receptor.name}**")
                c1, c2, c3 = st.columns([1, 2, 2])
                options = [YesNo.YES, YesNo.NO]
                idx = options.index(cell.significant) if cell.significant in options else None
                choice = c1.radio(
                    "Significant impact?",
                    options,
                    index=idx,
                    format_func=lambda v: v.value,
                    key=f"mat_{hazard_id}_{receptor.id}",
                )
                cell.significant = choice if choice is not None else YesNo.UNKNOWN
                cell.comment = c2.text_input(
                    "Comment", cell.comment, key=f"mat_c_{hazard_id}_{receptor.id}"
                )
                cell.source = c3.text_input(
                    "Source", cell.source, key=f"mat_s_{hazard_id}_{receptor.id}"
                )

    save_report(report)
