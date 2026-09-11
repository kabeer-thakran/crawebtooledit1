"""Step 8 — Phase 2: Risk Calculation.

Combines hazard likelihood (Step 6) with receptor vulnerability (Step 7)
through the 5×5 risk matrix and visualises the result as colour-coded Plotly
heatmaps — three dimensions (Direct / Operational / H&S) for each selected
scenario × horizon.
"""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from core.hazards import hazard_by_id
from core.matrix import RISK_COLOURS, RISK_LEVELS, risk_level
from core.schema import CRAReport
from core.state import save_report
from ui_helpers import scenario_horizon_pairs

_DIMENSIONS = ("direct", "operational", "health_safety")
_DIMENSION_LABELS = {
    "direct": "Direct",
    "operational": "Operational",
    "health_safety": "Health & Safety",
}


def _likelihood(report: CRAReport, hazard_id: str, scenario: str, horizon: str) -> int:
    """Return the likelihood score for a hazard at a scenario × horizon (default 1)."""
    for a in report.hazard_assessments:
        if a.hazard_id == hazard_id and a.scenario == scenario and a.horizon == horizon:
            return a.likelihood
    return 1


def _vulnerability(report: CRAReport, hazard_id: str, receptor_id: str, dimension: str) -> int:
    """Return the vulnerability score for a hazard × receptor in a dimension (default 1)."""
    for v in report.vulnerability:
        if v.hazard_id == hazard_id and v.receptor_id == receptor_id:
            return int(getattr(v, dimension))
    return 1


def _heatmap(report: CRAReport, scenario: str, horizon: str, dimension: str) -> go.Figure | None:
    """Build a hazard × receptor risk heatmap for one dimension and scenario × horizon."""
    material_ids = report.material_hazard_ids()
    receptors = report.phase0.receptors
    if not material_ids or not receptors:
        return None

    rank = {lvl: i for i, lvl in enumerate(RISK_LEVELS)}
    z: list[list[int]] = []
    text: list[list[str]] = []
    y_labels: list[str] = []
    for hazard_id in material_ids:
        likelihood = _likelihood(report, hazard_id, scenario, horizon)
        row_z, row_t = [], []
        for receptor in receptors:
            vuln = _vulnerability(report, hazard_id, receptor.id, dimension)
            level = risk_level(likelihood, vuln)
            row_z.append(rank[level])
            row_t.append(level)
        z.append(row_z)
        text.append(row_t)
        y_labels.append(hazard_by_id(hazard_id).name)

    colourscale = [
        [i / (len(RISK_LEVELS) - 1), RISK_COLOURS[lvl]] for i, lvl in enumerate(RISK_LEVELS)
    ]
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=[r.name for r in receptors],
            y=y_labels,
            text=text,
            texttemplate="%{text}",
            colorscale=colourscale,
            zmin=0,
            zmax=len(RISK_LEVELS) - 1,
            showscale=False,
            xgap=2,
            ygap=2,
        )
    )
    fig.update_layout(
        title=f"{_DIMENSION_LABELS[dimension]} — {scenario} · {horizon}",
        height=120 + 36 * len(material_ids),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def render(report: CRAReport) -> None:
    """Render the risk matrices and heatmaps across all combinations."""
    st.header("Phase 2 – Risk Calculation")
    if not report.material_hazard_ids():
        st.info("No material hazards yet. Complete Phase 1 (Steps 3–5) first.")
        return

    st.caption("Risk = Hazard likelihood × Receptor vulnerability (5×5 matrix, Table 5).")
    pairs = scenario_horizon_pairs(report.project)
    for scenario, horizon in pairs:
        st.subheader(f"{scenario} · {horizon}")
        cols = st.columns(len(_DIMENSIONS))
        for col, dimension in zip(cols, _DIMENSIONS, strict=True):
            fig = _heatmap(report, scenario, horizon, dimension)
            if fig is not None:
                col.plotly_chart(fig, use_container_width=True)

    save_report(report)
