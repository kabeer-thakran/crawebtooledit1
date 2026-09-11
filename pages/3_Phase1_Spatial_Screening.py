"""Step 3 — Phase 1 / Step 1: Spatial Screening.

Presents all 33 standardised hazards grouped by Temperature / Wind / Water /
Solid mass (and Chronic / Acute) and captures whether each hazard is present
at the site, with comments and a source.
"""

from __future__ import annotations

import streamlit as st

from core.hazards import hazards_grouped
from core.schema import CRAReport, HazardScreening, YesNo
from core.state import save_report
from ui_helpers import info_tooltip

# Hazards plausibly present at a Delhi (semi-arid, monsoonal) site — used by the
# MVP auto-suggest stub. Replace with a climate-zone lookup in a later iteration.
_DELHI_YES = {
    "temp_changing", "heat_stress", "temp_variability", "heat_wave", "cold_wave",
    "precip_rain", "hydro_variability", "water_stress", "drought",
    "heavy_precip_rain", "flood_pluvial", "flood_fluvial", "storm", "soil_erosion",
    "subsidence",
}


def _screening_map(report: CRAReport) -> dict[str, HazardScreening]:
    """Return screening rows keyed by hazard id, creating any that are missing."""
    existing = {s.hazard_id: s for s in report.screening}
    return existing


def _auto_suggest(report: CRAReport) -> None:
    """Pre-fill Yes/No screening answers from the site's climate (MVP stub)."""
    city = report.project.city.strip().lower()
    smap = _screening_map(report)
    if city == "delhi":
        for hazard_id, row in smap.items():
            row.at_site = YesNo.YES if hazard_id in _DELHI_YES else YesNo.NO
    else:
        st.toast("Auto-suggest currently only stubs Delhi; other cities left blank.")


def render(report: CRAReport) -> None:
    """Render the spatial screening assessment and persist hazard answers."""
    st.header("Phase 1 – Spatial Screening")
    st.caption("Is each hazard present at the project site?")
    info_tooltip(
        "Spatial screening",
        "[PLACEHOLDER: screening guidance to be reviewed with client]",
    )
    st.markdown(
        """
        <style>
        .water-hazard-tag { display: inline-block; margin: 0 0.35rem 0.25rem 0; padding: 0.15rem 0.5rem; border-radius: 999px; font-size: 0.7rem; font-weight: 700; }
        .water-chronic { background: rgba(13, 110, 253, 0.18); color: #0b3d8d; }
        .water-acute { background: rgba(0, 90, 170, 0.28); color: #072b5c; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Auto-suggest (based on city)", type="primary"):
        _auto_suggest(report)
        save_report(report)
        st.rerun()

    smap = _screening_map(report)
    grouped = hazards_grouped()
    for group, categories in grouped.items():
        st.subheader(group)
        for category, hazards in categories.items():
            if not hazards:
                continue
            st.markdown(f"**{category}-related hazards**")
            for hazard in hazards:
                row = smap[hazard.id]
                tag_class = ""
                if hazard.group == "Water":
                    tag_class = "water-chronic" if hazard.category == "Chronic" else "water-acute"
                    tag_label = f"{hazard.category} water hazard"
                else:
                    tag_label = f"{hazard.group} hazard"
                with st.container(border=True):
                    if hazard.group == "Water":
                        st.markdown(
                            f"<span class='water-hazard-tag {tag_class}'>{tag_label}</span>",
                            unsafe_allow_html=True,
                        )
                    st.markdown(f"**{hazard.name}** — {hazard.definition}")
                    c1, c2, c3 = st.columns([1, 2, 2])
                    options = [YesNo.YES, YesNo.NO]
                    idx = options.index(row.at_site) if row.at_site in options else None
                    choice = c1.radio(
                        "Hazard at the site?",
                        options,
                        index=idx,
                        format_func=lambda v: v.value,
                        key=f"scr_{hazard.id}",
                    )
                    row.at_site = choice if choice is not None else YesNo.UNKNOWN
                    row.comments = c2.text_area(
                        "Comments", row.comments, key=f"scr_c_{hazard.id}", height=80
                    )
                    row.source = c3.text_area(
                        "Source(s)", row.source, key=f"scr_s_{hazard.id}", height=80
                    )

    save_report(report)
