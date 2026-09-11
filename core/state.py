"""Streamlit session-state helpers for the CRA workflow.

A single :class:`~core.schema.CRAReport` instance is stored under
``st.session_state[REPORT_KEY]`` and shared across every step page. These
helpers centralise initialisation, retrieval, persistence and JSON
import/export so individual pages never touch the raw session dict.
"""

from __future__ import annotations

import json

import streamlit as st

from core.hazards import all_hazards
from core.schema import (
    CRAReport,
    FinalSelection,
    HazardScreening,
    Phase0,
    Receptor,
)

#: Session-state key under which the live report is stored.
REPORT_KEY = "cra_report"

#: Default receptors pre-loaded in Phase 0 (typical Arup building receptors).
DEFAULT_RECEPTORS: tuple[Receptor, ...] = (
    Receptor(id="structural", name="Structural",
             description="Primary structure: foundations, frame, envelope load paths.",
             components="Foundations, columns, beams, slabs, cores"),
    Receptor(id="non_structural", name="Non-structural",
             description="Secondary elements and finishes.",
             components="Facade cladding, partitions, ceilings, roofing"),
    Receptor(id="building_services", name="Building services",
             description="MEP systems enabling operation.",
             components="HVAC, electrical, plumbing, fire, ICT"),
    Receptor(id="internal_assets", name="Internal assets",
             description="Contents and equipment within the asset.",
             components="Furniture, equipment, stock, data"),
    Receptor(id="site_context", name="Site context",
             description="External site, access and surrounding context.",
             components="Landscaping, access roads, drainage, utilities"),
)


def init_state() -> None:
    """Initialise the report and seed screening rows if not already present."""
    if REPORT_KEY not in st.session_state:
        report = CRAReport()
        report.phase0 = Phase0(receptors=list(DEFAULT_RECEPTORS))
        report.screening = [HazardScreening(hazard_id=h.id) for h in all_hazards()]
        report.final_selection = [FinalSelection(hazard_id=h.id) for h in all_hazards()]
        st.session_state[REPORT_KEY] = report


def get_report() -> CRAReport:
    """Return the live report, initialising session state on first access."""
    init_state()
    return st.session_state[REPORT_KEY]


def save_report(report: CRAReport) -> None:
    """Persist an updated report back into session state."""
    st.session_state[REPORT_KEY] = report


def to_json(report: CRAReport) -> str:
    """Serialise the report to indented JSON for download/resume."""
    return report.model_dump_json(indent=2)


def from_json(raw: str | bytes) -> CRAReport:
    """Rebuild a :class:`CRAReport` from previously exported JSON."""
    data = json.loads(raw)
    return CRAReport.model_validate(data)
