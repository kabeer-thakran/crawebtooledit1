"""Step 5 — Phase 1 / Step 3: Final Selection.

Auto-computes which hazards are *material* — those answered YES in both spatial
screening (Step 3) and materiality screening (Step 4, for any receptor) — and
presents an editable comments column.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.hazards import hazard_by_id
from core.schema import CRAReport, FinalSelection, YesNo
from core.state import save_report


def _compute_material(report: CRAReport) -> dict[str, bool]:
    """Return ``{hazard_id: material}`` from Step 3 and Step 4 answers."""
    yes_site = {s.hazard_id for s in report.screening if s.at_site == YesNo.YES}
    significant = {
        c.hazard_id for c in report.materiality if c.significant == YesNo.YES
    }
    return {s.hazard_id: (s.hazard_id in yes_site and s.hazard_id in significant)
            for s in report.screening}


def _selection_map(report: CRAReport) -> dict[str, FinalSelection]:
    """Return final-selection rows keyed by hazard id, creating any missing."""
    existing = {fs.hazard_id: fs for fs in report.final_selection}
    for s in report.screening:
        existing.setdefault(s.hazard_id, FinalSelection(hazard_id=s.hazard_id))
    report.final_selection = list(existing.values())
    return existing


def render(report: CRAReport) -> None:
    """Render the Phase 1 screening results and persist final selection."""
    st.header("Phase 1 – Screening Results")

    material = _compute_material(report)
    sel = _selection_map(report)
    for hazard_id, is_material in material.items():
        sel[hazard_id].material = is_material

    rows = []
    for hazard_id, fs in sel.items():
        if not fs.material:
            continue
        hazard = hazard_by_id(hazard_id)
        rows.append(
            {
                "Hazard": hazard.name,
                "Group": hazard.group,
                "Category": hazard.category,
                "Material": "Yes",
                "Comments": fs.comments,
                "_id": hazard_id,
            }
        )

    if not rows:
        st.info("No material hazards yet. Complete Steps 3 and 4 to populate this list.")
        save_report(report)
        return

    st.caption("Material = YES in both spatial and materiality screening. Edit comments below.")
    df = pd.DataFrame(rows)
    edited = st.data_editor(
        df.drop(columns=["_id"]),
        disabled=["Hazard", "Group", "Category", "Material"],
        use_container_width=True,
        hide_index=True,
        key="final_selection_editor",
    )
    for i, hazard_id in enumerate(df["_id"]):
        sel[hazard_id].comments = str(edited.iloc[i]["Comments"])

    st.metric("Material hazards", len(rows))
    save_report(report)
