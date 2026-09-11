"""Pydantic v2 data model for the Arup CRA workflow.

The :class:`CRAReport` aggregate is the single source of truth that flows
through the ten workflow steps and is finally rendered into the Word report.
Every step page reads from and writes to one section of this model via the
session-state helpers in :mod:`core.state`.
"""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Controlled vocabularies
# ---------------------------------------------------------------------------


class YesNo(str, Enum):
    """A simple Yes/No/Unknown screening answer."""

    YES = "Yes"
    NO = "No"
    UNKNOWN = ""


class AssetType(str, Enum):
    """Top-level asset typology used to tailor receptors and guidance."""

    BUILDING = "Building"
    TRANSPORT = "Transport"
    OTHER = "Other"


class TaxonomySector(str, Enum):
    """EU Taxonomy economic sector for the assessed activity."""

    CONSTRUCTION_REAL_ESTATE = "Construction & real estate"
    TRANSPORT = "Transport"


class ContributionMode(str, Enum):
    """Whether the assessment supports Substantial Contribution or DNSH."""

    SUBSTANTIAL_CONTRIBUTION = "Substantial Contribution"
    DNSH = "DNSH"


class Scenario(str, Enum):
    """Climate scenarios assessed (IPCC AR6 SSP-RCP pathways)."""

    A = "SSP2-4.5"
    B = "SSP5-8.5"


class Horizon(str, Enum):
    """Time horizons assessed across the asset lifespan."""

    BASELINE = "Baseline"
    MID = "Mid-century"
    END = "End-century"


#: EU Taxonomy activities keyed by sector — replicate the workbook
#: "Project_Information" dropdown. Extend as the workbook evolves.
TAXONOMY_ACTIVITIES: dict[str, list[str]] = {
    TaxonomySector.CONSTRUCTION_REAL_ESTATE.value: [
        "7.1 Construction of new buildings",
        "7.2 Renovation of existing buildings",
        "7.7 Acquisition and ownership of buildings",
    ],
    TaxonomySector.TRANSPORT.value: [
        "6.13 Infrastructure for personal mobility, cycle logistics",
        "6.14 Infrastructure for rail transport",
        "6.15 Infrastructure enabling low-carbon road transport and public transport",
        "6.16 Infrastructure enabling low carbon water transport",
    ],
}

#: 1–5 score labels shared by likelihood and vulnerability scales.
SCORE_LABELS: dict[int, str] = {
    1: "Very Low",
    2: "Low",
    3: "Medium",
    4: "High",
    5: "Very High",
}


# ---------------------------------------------------------------------------
# Project information (Step 1)
# ---------------------------------------------------------------------------


class LatLng(BaseModel):
    """A WGS84 geographic coordinate captured from the Folium map picker."""

    lat: float = Field(default=28.6139, ge=-90, le=90)
    lng: float = Field(default=77.2090, ge=-180, le=180)


class MapRectangle(BaseModel):
    """Rectangular site extent (km) rendered around the selected location."""

    width_km: float = Field(default=10.0, ge=0.1, le=500.0)
    height_km: float = Field(default=10.0, ge=0.1, le=500.0)


class Period(BaseModel):
    """A climate analysis period delimited by start and end calendar years."""

    start: int = Field(ge=1850, le=2150)
    end: int = Field(ge=1850, le=2150)

    def label(self) -> str:
        """Return a human-readable ``start–end`` label for report tables."""
        return f"{self.start}\u2013{self.end}"


class ProjectInfo(BaseModel):
    """Project metadata gathered in Step 1 and used to populate the report header."""

    project_name: str = ""
    client: str = ""
    report_date: date = Field(default_factory=date.today)
    job_number: str = ""
    document_version: str = "0.1"

    address: str = ""
    city: str = ""
    country: str = ""
    location: LatLng = Field(default_factory=LatLng)
    map_rectangle: MapRectangle = Field(default_factory=MapRectangle)

    asset_type: AssetType = AssetType.BUILDING
    project_scope: str = ""

    taxonomy_sector: TaxonomySector = TaxonomySector.CONSTRUCTION_REAL_ESTATE
    taxonomy_activity: str = ""
    contribution_mode: ContributionMode = ContributionMode.SUBSTANTIAL_CONTRIBUTION

    lifespan_years: int = Field(default=60, ge=1, le=200)

    baseline_period: Period = Field(default_factory=lambda: Period(start=1995, end=2014))
    reference_period: Period = Field(default_factory=lambda: Period(start=2015, end=2024))
    mid_century_period: Period = Field(default_factory=lambda: Period(start=2041, end=2060))
    end_century_period: Period = Field(default_factory=lambda: Period(start=2081, end=2100))

    scenario_a: str = Scenario.A.value
    scenario_b: str = Scenario.B.value


# ---------------------------------------------------------------------------
# Phase 0 — Preparation (Step 2)
# ---------------------------------------------------------------------------


class Receptor(BaseModel):
    """An asset receptor (system/component grouping) assessed for vulnerability."""

    id: str
    name: str
    description: str = ""
    components: str = ""


class Phase0(BaseModel):
    """Phase 0 preparation: adaptable boilerplate text and the receptor register."""

    introduction_text: str = ""
    methodology_text: str = ""
    scope_text: str = ""
    receptors: list[Receptor] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase 1 — Screening (Steps 3–5)
# ---------------------------------------------------------------------------


class HazardScreening(BaseModel):
    """Step 1 spatial screening answer for a single hazard."""

    hazard_id: str
    at_site: YesNo = YesNo.UNKNOWN
    comments: str = ""
    source: str = ""


class MaterialityCell(BaseModel):
    """Step 2 materiality answer for one hazard × receptor combination."""

    hazard_id: str
    receptor_id: str
    significant: YesNo = YesNo.UNKNOWN
    comment: str = ""
    source: str = ""


class FinalSelection(BaseModel):
    """Step 3 final-selection record: material if YES in both Step 1 and Step 2."""

    hazard_id: str
    material: bool = False
    comments: str = ""


# ---------------------------------------------------------------------------
# Phase 2 — Assessment (Steps 6–9)
# ---------------------------------------------------------------------------


class HazardAssessment(BaseModel):
    """Step 6 hazard likelihood for one hazard × scenario × horizon."""

    hazard_id: str
    scenario: str
    horizon: str
    likelihood: int = Field(default=1, ge=1, le=5)
    threshold_value: str = ""
    threshold_unit: str = ""
    source: str = ""


class VulnerabilityAssessment(BaseModel):
    """Step 7 vulnerability scores for one hazard × receptor (three dimensions)."""

    hazard_id: str
    receptor_id: str
    direct: int = Field(default=1, ge=1, le=5)
    operational: int = Field(default=1, ge=1, le=5)
    health_safety: int = Field(default=1, ge=1, le=5)
    justification: str = ""


class AdaptationMeasure(BaseModel):
    """Step 9 adaptation measure proposed for a hazard with risk ≥ Moderate."""

    hazard_id: str
    description: str = ""
    physical: bool = True
    priority: str = "Medium"
    timeframe_years: int = Field(default=5, ge=0, le=200)
    indicative_cost: str = ""
    notes: str = ""


# ---------------------------------------------------------------------------
# Aggregate report
# ---------------------------------------------------------------------------


class CRAReport(BaseModel):
    """The complete CRA dataset — the aggregate persisted across all steps."""

    project: ProjectInfo = Field(default_factory=ProjectInfo)
    phase0: Phase0 = Field(default_factory=Phase0)
    screening: list[HazardScreening] = Field(default_factory=list)
    materiality: list[MaterialityCell] = Field(default_factory=list)
    final_selection: list[FinalSelection] = Field(default_factory=list)
    hazard_assessments: list[HazardAssessment] = Field(default_factory=list)
    vulnerability: list[VulnerabilityAssessment] = Field(default_factory=list)
    adaptation: list[AdaptationMeasure] = Field(default_factory=list)

    def material_hazard_ids(self) -> list[str]:
        """Return ids of hazards flagged material in the final selection step."""
        return [fs.hazard_id for fs in self.final_selection if fs.material]
