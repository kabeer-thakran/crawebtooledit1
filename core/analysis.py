"""Risk analytics derived from a :class:`~core.schema.CRAReport`.

Pure functions (no Streamlit) that combine hazard likelihood and receptor
vulnerability through the risk matrix. Shared by the risk/adaptation steps and
the Word report renderer so the numbers always agree.
"""

from __future__ import annotations

from core.matrix import RISK_RANK, risk_level
from core.schema import CRAReport, Horizon

DIMENSIONS: tuple[str, ...] = ("direct", "operational", "health_safety")
DIMENSION_LABELS: dict[str, str] = {
    "direct": "Direct",
    "operational": "Operational",
    "health_safety": "Health & Safety",
}


def likelihood_for(report: CRAReport, hazard_id: str, scenario: str, horizon: str) -> int:
    """Return the likelihood score for a hazard at a scenario × horizon (default 1)."""
    for a in report.hazard_assessments:
        if a.hazard_id == hazard_id and a.scenario == scenario and a.horizon == horizon:
            return a.likelihood
    return 1


def vulnerability_for(report: CRAReport, hazard_id: str, receptor_id: str, dimension: str) -> int:
    """Return the vulnerability score for a hazard × receptor in a dimension (default 1)."""
    for v in report.vulnerability:
        if v.hazard_id == hazard_id and v.receptor_id == receptor_id:
            return int(getattr(v, dimension))
    return 1


def risk_for(
    report: CRAReport, hazard_id: str, receptor_id: str, dimension: str,
    scenario: str, horizon: str,
) -> str:
    """Return the risk level for one hazard/receptor/dimension/scenario/horizon."""
    likelihood = likelihood_for(report, hazard_id, scenario, horizon)
    vuln = vulnerability_for(report, hazard_id, receptor_id, dimension)
    return risk_level(likelihood, vuln)


def peak_risk_per_hazard(report: CRAReport) -> dict[str, str]:
    """Return the worst-case risk level per material hazard across all combinations.

    Considers every dimension, receptor, scenario and horizon; used to decide
    which hazards require adaptation measures (risk ≥ Moderate).
    """
    scenarios = [report.project.scenario_a, report.project.scenario_b]
    horizons = [Horizon.BASELINE.value, Horizon.MID.value, Horizon.END.value]
    peaks: dict[str, str] = {}
    for hazard_id in report.material_hazard_ids():
        best = "VL"
        for receptor in report.phase0.receptors:
            for dimension in DIMENSIONS:
                for scenario in scenarios:
                    for horizon in horizons:
                        level = risk_for(
                            report, hazard_id, receptor.id, dimension, scenario, horizon
                        )
                        if RISK_RANK[level] > RISK_RANK[best]:
                            best = level
        peaks[hazard_id] = best
    return peaks
