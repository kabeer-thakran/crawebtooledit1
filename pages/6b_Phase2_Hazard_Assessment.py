"""Phase 2 — Hazard Assessment placeholder.

This tab is intentionally scaffolded as a placeholder because the Excel source
sheet was not available in the repository. The client can review this page once
that sheet is supplied and the final calculations are confirmed.
"""

from __future__ import annotations

import streamlit as st

from core.schema import CRAReport


def render(report: CRAReport) -> None:
    """Render the hazard assessment page with a placeholder migration note."""
    st.header("Phase 2 – Hazard Assessment")
    st.warning(
        "[PLACEHOLDER: content to be migrated from Excel 'Hazard Assessment' sheet]"
    )

    st.markdown(
        """
        This tab is reserved for the hazard assessment outputs, calculations, or summary tables
        currently defined in the Excel workbook. At this stage, the exact source content has not
        been included in this repository, so the section is intentionally left as a reviewable placeholder.
        """
    )

    st.markdown(
        """
        <div class='cra-placeholder'>
        <strong>Migration note:</strong> Once the Excel sheet is available, this tab should be populated with the exact calculations, output tables, and method text used by the workbook.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "[PLACEHOLDER: summary table / calculation block to be inserted here after workbook review]"
    )
