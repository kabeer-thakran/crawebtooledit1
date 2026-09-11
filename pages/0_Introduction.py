"""Introduction landing page for the CRA workflow.

This page acts as the front matter before Project Information and should be
reviewed by the client before final copy is locked in.
"""

from __future__ import annotations

import streamlit as st

from core.schema import CRAReport


def render(report: CRAReport) -> None:
    """Render the introductory landing page with placeholder client copy."""
    st.header("Introduction")
    st.caption("[PLACEHOLDER: draft landing page content pending client review]")

    st.markdown(
        """
        <div class='cra-placeholder'>
        <strong>Draft note:</strong> This introduction page is intentionally provisional and contains placeholder copy for client review before final wording is approved.
        </div>
        """,
        unsafe_allow_html=True,
    )

    sections = {
        "Scope": "[PLACEHOLDER: Scope description to be provided by client]",
        "Methodology": "[PLACEHOLDER: Methodology summary to be provided by client]",
        "Instructions": "[PLACEHOLDER: Instructions for how to complete the CRA workflow]",
        "Expected Outputs": "[PLACEHOLDER: Expected Outputs to be provided by client]",
    }

    for title, content in sections.items():
        with st.container(border=True):
            st.subheader(title)
            st.write(content)

    st.info(
        "[PLACEHOLDER: This section should be reviewed against the Excel workbook instructions sheet before sign-off.]"
    )
