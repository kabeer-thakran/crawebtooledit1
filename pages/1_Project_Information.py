"""Step 1 — Project Information.

Captures project metadata, location (via a Folium map picker), EU Taxonomy
classification and the timeframes/scenarios that drive the rest of the CRA.
"""

from __future__ import annotations

from math import cos, radians
from datetime import date

import streamlit as st

from core.schema import (
    TAXONOMY_ACTIVITIES,
    AssetType,
    ContributionMode,
    CRAReport,
    LatLng,
    MapRectangle,
    Period,
    Scenario,
    TaxonomySector,
)
from core.state import save_report
from ui_helpers import info_tooltip

try:  # optional map dependency — degrade gracefully if not installed
    import folium
    from streamlit_folium import st_folium

    _HAS_MAP = True
except Exception:  # pragma: no cover - optional import
    _HAS_MAP = False


def _rectangle_bounds(loc: LatLng, rectangle: MapRectangle) -> list[list[float]]:
    """Compute rectangle bounds from center location and size in km."""
    lat_deg_per_km = 1.0 / 110.574
    lng_scale = max(cos(radians(loc.lat)), 0.1)
    lng_deg_per_km = 1.0 / (111.320 * lng_scale)

    half_h = rectangle.height_km / 2.0
    half_w = rectangle.width_km / 2.0

    south = loc.lat - (half_h * lat_deg_per_km)
    north = loc.lat + (half_h * lat_deg_per_km)
    west = loc.lng - (half_w * lng_deg_per_km)
    east = loc.lng + (half_w * lng_deg_per_km)
    return [[south, west], [north, east]]


def _location_picker(loc: LatLng, rectangle: MapRectangle) -> tuple[LatLng, MapRectangle]:
    """Render the interactive map and return updated location and rectangle."""
    st.caption("Map rectangle extent")
    c1, c2 = st.columns(2)
    rectangle.width_km = c1.number_input(
        "Rectangle width (km)", min_value=0.1, max_value=500.0, value=float(rectangle.width_km)
    )
    rectangle.height_km = c2.number_input(
        "Rectangle height (km)", min_value=0.1, max_value=500.0, value=float(rectangle.height_km)
    )

    if not _HAS_MAP:
        st.info("Install `folium` and `streamlit-folium` to enable the map picker.")
        col1, col2 = st.columns(2)
        lat = col1.number_input("Latitude", value=loc.lat, format="%.5f")
        lng = col2.number_input("Longitude", value=loc.lng, format="%.5f")
        return LatLng(lat=lat, lng=lng), rectangle

    fmap = folium.Map(location=[loc.lat, loc.lng], zoom_start=11)
    folium.Marker([loc.lat, loc.lng], tooltip="Project site").add_to(fmap)
    folium.Rectangle(
        bounds=_rectangle_bounds(loc, rectangle),
        color="#1f4e79",
        weight=2,
        fill=True,
        fill_opacity=0.12,
        tooltip="Site rectangle",
    ).add_to(fmap)
    fmap.add_child(folium.LatLngPopup())
    result = st_folium(fmap, height=380, use_container_width=True, key="loc_map")

    clicked = result.get("last_clicked") if result else None
    if clicked:
        return LatLng(lat=clicked["lat"], lng=clicked["lng"]), rectangle
    return loc, rectangle


def render(report: CRAReport) -> None:
    """Render the Project Information step and persist project data."""
    st.header("Project Information")
    p = report.project

    with st.container(border=True):
        st.subheader("Project metadata")
        info_tooltip(
            "Project metadata",
            "[PLACEHOLDER: project metadata guidance to be reviewed with the client]",
        )
    c1, c2, c3 = st.columns(3)
    p.project_name = c1.text_input("Project Name *", p.project_name)
    p.client = c2.text_input("Client *", p.client)
    p.report_date = c3.date_input("Date *", p.report_date or date.today())

    c1, c2, c3 = st.columns(3)
    p.job_number = c1.text_input("Job Number *", p.job_number)
    p.document_version = c2.text_input("Document Version *", p.document_version)
    p.asset_type = AssetType(
        c3.selectbox(
            "Asset Type *",
            [a.value for a in AssetType],
            index=[a.value for a in AssetType].index(p.asset_type.value),
        )
    )

    st.subheader("Location")
    info_tooltip("Location", "[PLACEHOLDER: location guidance text]")
    c1, c2, c3 = st.columns(3)
    p.address = c1.text_input("Address *", p.address)
    p.city = c2.text_input("City *", p.city)
    p.country = c3.text_input("Country *", p.country)
    p.location, p.map_rectangle = _location_picker(p.location, p.map_rectangle)
    st.caption(f"Selected coordinates: {p.location.lat:.5f}, {p.location.lng:.5f}")

    p.project_scope = st.text_area("Project Scope *", p.project_scope)

    st.subheader("EU Taxonomy classification")
    info_tooltip("EU Taxonomy classification", "[PLACEHOLDER: taxonomy guidance text]")
    c1, c2 = st.columns(2)
    p.taxonomy_sector = TaxonomySector(
        c1.selectbox(
            "EU Taxonomy Sector *",
            [s.value for s in TaxonomySector],
            index=[s.value for s in TaxonomySector].index(p.taxonomy_sector.value),
        )
    )
    activities = TAXONOMY_ACTIVITIES[p.taxonomy_sector.value]
    activity_index = activities.index(p.taxonomy_activity) if p.taxonomy_activity in activities else 0
    p.taxonomy_activity = c2.selectbox("EU Taxonomy Activity *", activities, index=activity_index)

    p.contribution_mode = ContributionMode(
        st.radio(
            "Substantial Contribution vs DNSH *",
            [m.value for m in ContributionMode],
            index=[m.value for m in ContributionMode].index(p.contribution_mode.value),
            horizontal=True,
        )
    )

    st.subheader("Timeframes & scenarios")
    info_tooltip("Timeframes & scenarios", "[PLACEHOLDER: timeframe guidance text]")
    p.lifespan_years = st.number_input(
        "Lifespan (years) *", min_value=1, max_value=200, value=p.lifespan_years
    )

    def period_inputs(label: str, period: Period, key: str) -> Period:
        c1, c2 = st.columns(2)
        start = c1.number_input(f"{label} start", value=period.start, key=f"{key}_s")
        end = c2.number_input(f"{label} end", value=period.end, key=f"{key}_e")
        return Period(start=int(start), end=int(end))

    p.baseline_period = period_inputs("Baseline Period", p.baseline_period, "baseline")
    p.reference_period = period_inputs("Reference Period", p.reference_period, "reference")
    p.mid_century_period = period_inputs("Mid-Century Period", p.mid_century_period, "mid")
    p.end_century_period = period_inputs("End-Century Period", p.end_century_period, "end")

    c1, c2 = st.columns(2)
    p.scenario_a = c1.text_input("Scenario A", p.scenario_a or Scenario.A.value)
    p.scenario_b = c2.text_input("Scenario B", p.scenario_b or Scenario.B.value)

    save_report(report)
    st.success("Project information saved to session.")
