"""Semi-quantitative 5×5 risk matrix for the CRA workflow.

Combines a hazard *likelihood* score with a receptor *vulnerability* score to
produce a *risk* level, exactly as defined in the Word template
(Section 2.1, Table 5).
"""

from __future__ import annotations

#: Ordered risk levels from lowest to highest severity.
RISK_LEVELS: tuple[str, ...] = ("VL", "L", "M", "H", "VH")

#: Long-form labels for risk levels (for tables and legends).
RISK_LABELS: dict[str, str] = {
    "VL": "Very Low",
    "L": "Low",
    "M": "Medium",
    "H": "High",
    "VH": "Very High",
}

#: Hex colours for risk levels (green → red) used by Plotly heatmaps and docx.
RISK_COLOURS: dict[str, str] = {
    "VL": "#1A9850",
    "L": "#A6D96A",
    "M": "#FEE08B",
    "H": "#F46D43",
    "VH": "#D73027",
}

# Matrix indexed as [likelihood_score - 1][vulnerability_score - 1].
# Rows = hazard likelihood (VL..VH); columns = vulnerability (VL..VH).
_MATRIX: tuple[tuple[str, ...], ...] = (
    ("VL", "VL", "L", "M", "M"),   # likelihood VL
    ("VL", "L", "M", "M", "H"),    # likelihood L
    ("L", "L", "M", "H", "H"),     # likelihood M
    ("L", "M", "H", "H", "VH"),    # likelihood H
    ("L", "M", "H", "VH", "VH"),   # likelihood VH
)

#: Numeric severity rank used for thresholds (e.g. "risk ≥ Moderate").
RISK_RANK: dict[str, int] = {level: i for i, level in enumerate(RISK_LEVELS)}


def risk_level(likelihood: int, vulnerability: int) -> str:
    """Return the risk level code for a likelihood × vulnerability pair.

    Both scores are on the 1–5 scale (Very Low … Very High). This is the single
    point at which hazard and vulnerability scores are combined in the workflow.
    """
    if not (1 <= likelihood <= 5 and 1 <= vulnerability <= 5):
        raise ValueError("likelihood and vulnerability must be in 1..5")
    return _MATRIX[likelihood - 1][vulnerability - 1]


def is_at_least(level: str, threshold: str) -> bool:
    """Return ``True`` if ``level`` is at least as severe as ``threshold``."""
    return RISK_RANK[level] >= RISK_RANK[threshold]
