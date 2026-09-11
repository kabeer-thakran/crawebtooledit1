"""Arup CRA Tool — Streamlit entry point.

Launches the guided, tabbed Climate Risk Assessment workflow. The ten workflow
steps live in :mod:`pages` as ``render(report)`` functions and are mounted as
top-level :func:`st.tabs` (NIH-IDF-style stepwise navigation). A single
:class:`~core.schema.CRAReport` in ``st.session_state`` persists data across
all tabs.

Run with::

    streamlit run app.py
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import streamlit as st

from branding import APP_TITLE, configure_page, render_sidebar
from core.state import get_report
from ui_helpers import flow_breadcrumb

_PAGES_DIR = Path(__file__).parent / "pages"

# Ordered (tab label, module filename) pairs for the workflow.
_STEPS: tuple[tuple[str, str], ...] = (
    ("Introduction", "0_Introduction.py"),
    ("Project Information", "1_Project_Information.py"),
    ("Phase 0 – Preparation", "2_Phase0_Preparation.py"),
    ("Phase 1 – Spatial Screening", "3_Phase1_Spatial_Screening.py"),
    ("Phase 1 – Materiality", "4_Phase1_Materiality.py"),
    ("Phase 1 – Screening Results", "5_Phase1_Final_Selection.py"),
    ("Phase 2 – Hazard Thresholds", "6_Phase2_Hazard_Assessment.py"),
    ("Phase 2 – Hazard Assessment", "6b_Phase2_Hazard_Assessment.py"),
    ("Phase 2 – Vulnerability Assessment", "7_Phase2_Vulnerability.py"),
    ("Phase 2 – Risk Calculation", "8_Phase2_Risk.py"),
    ("Phase 2.2 – Adaptation Measures", "9_Phase2_Adaptation.py"),
    ("Generate Report", "10_Generate_Report.py"),
)


@st.cache_resource
def _load_step_module(filename: str) -> ModuleType:
    """Import a numbered step module from ``pages/`` by file path.

    Numeric filename prefixes are not importable with ``import``; this loads
    them via :mod:`importlib` so each step's ``render`` function can be mounted
    inside a tab. Cached so modules are imported once per server session.
    """
    path = _PAGES_DIR / filename
    spec = importlib.util.spec_from_file_location(f"cra_step_{path.stem}", path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"Cannot load step module: {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    """Configure the shell and render the ten workflow tabs."""
    configure_page(APP_TITLE)
    render_sidebar()
    report = get_report()

    st.title("Climate Risk Assessment")
    st.caption(
        "Guided semi-quantitative CRA workflow — complete each step left to right, "
        "then generate the Word report on the final tab."
    )
    flow_breadcrumb()

    tabs = st.tabs([label for label, _ in _STEPS])
    for tab, (_, filename) in zip(tabs, _STEPS):
        with tab:
            module = _load_step_module(filename)
            module.render(report)


if __name__ == "__main__":
    main()
