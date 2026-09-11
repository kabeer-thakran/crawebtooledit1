"""Standardised climate hazard catalogue for the CRA workflow.

The list mirrors the EU Taxonomy (Climate Delegated Act, Appendix A)
classification of climate-related hazards, expanded to the 36 granular
hazards used by the Arup standardised CRA workbook
(``20260528_Final_version_ENG.xlsm``). Names follow the *Ph_1. Step 1
Spatial Screening* sheet (the canonical workflow list); definitions follow
Appendix A.1 of the Word report template (``Table 13``).

Hazards are organised by *group* (Temperature / Wind / Water / Solid mass)
and *category* (Chronic / Acute). Definitions are sourced from the workbook
Glossary sheet (paraphrased for the MVP — reconcile against the workbook if
wording must match exactly).
"""

from __future__ import annotations

from dataclasses import dataclass

#: The four EU-Taxonomy hazard groups, in canonical display order.
HAZARD_GROUPS: tuple[str, ...] = ("Temperature", "Wind", "Water", "Solid mass")

#: The two temporal categories for each hazard.
HAZARD_CATEGORIES: tuple[str, ...] = ("Chronic", "Acute")


@dataclass(frozen=True)
class Hazard:
    """A single standardised climate hazard.

    Used throughout the CRA workflow as the immutable reference identity for a
    hazard; user answers (screening, materiality, scoring) are keyed by
    :attr:`id`.
    """

    id: str
    name: str
    group: str
    category: str
    definition: str


# fmt: off
_HAZARDS: tuple[Hazard, ...] = (
    # --- Temperature · Chronic ---------------------------------------------
    Hazard("temp_changing", "Changing temperature (air, freshwater, marine water)", "Temperature", "Chronic",
           "Long-term mean temperature changes in air and water."),
    Hazard("heat_stress", "Heat stress", "Temperature", "Chronic",
           "A range of conditions in organisms when the body absorbs excess heat during "
           "overexposure to high air or water temperatures. This is a consequence of heat wave."),
    Hazard("temp_variability", "Temperature variability", "Temperature", "Chronic",
           "Extent of day-to-day or month-to-month changes between temperatures at one location."),
    Hazard("permafrost", "Permafrost thawing", "Temperature", "Chronic",
           "Progressive loss of ground ice in permafrost, usually due to heat input."),
    # --- Temperature · Acute -----------------------------------------------
    Hazard("heat_wave", "Heat wave", "Temperature", "Acute",
           "Period of abnormal heat defined with respect to a temperature threshold "
           "lasting from 2 days to several months."),
    Hazard("cold_wave", "Cold wave/frost", "Temperature", "Acute",
           "A spell of cold weather over a wide area; including late frosts and alternate frosts."),
    Hazard("wildfire", "Wildfire", "Temperature", "Acute",
           "Large and destructive fire originating from combustible vegetation and ignition "
           "sources, such as lightning or human activity."),
    # --- Wind · Chronic -----------------------------------------------------
    Hazard("wind_patterns", "Changing wind patterns", "Wind", "Chronic",
           "Change in wind regime in terms of intensity and distribution. Extreme events are not considered."),
    # --- Wind · Acute -------------------------------------------------------
    Hazard("cyclone", "Cyclone, hurricane, typhoon and Medicane", "Wind", "Acute",
           "A windstorm above 32 m/s called a hurricane, typhoon or cyclone depending on its "
           "geographical location; includes the Medicane (Mediterranean tropical-like cyclones)."),
    Hazard("storm", "Storm (including blizzards, dust and sandstorms)", "Wind", "Acute",
           "Severe wind event (10-minute average wind speed between 89 and 102 km/h); "
           "includes blizzards, dust and sandstorms."),
    Hazard("tornado", "Tornado", "Wind", "Acute",
           "A column of air in contact with the ground, rotating around a vertically oriented "
           "axis and located under a cumuliform cloud."),
    # --- Water · Chronic ----------------------------------------------------
    Hazard("precip_rain", "Changing precipitation patterns and types (Rain)", "Water", "Chronic",
           "Change in the temporal or spatial distribution of rainfall or in the amount of "
           "rainfall accumulated at a specific location."),
    Hazard("precip_hail", "Changing precipitation patterns and types (Hail)", "Water", "Chronic",
           "Change in the temporal or spatial distribution of hail or in the amount of hail "
           "falling at a specific location."),
    Hazard("precip_snow_ice", "Changing precipitation patterns and types (Snow/ice)", "Water", "Chronic",
           "Change in the temporal or spatial distribution of snow/ice or the amount of snow/ice "
           "falling at a specific location. Extreme events are not considered."),
    Hazard("hydro_variability", "Precipitation or hydrological variability", "Water", "Chronic",
           "Changes in water availability and water levels due to changes in components of the "
           "hydrological cycle; can also cause drought, water stress and reduced water level."),
    Hazard("water_stress", "Water stress", "Water", "Chronic",
           "A situation where there is not enough water of sufficient quality to meet the demand "
           "of people and the environment."),
    Hazard("ocean_acidification", "Ocean acidification", "Water", "Chronic",
           "A reduction in ocean pH over a prolonged period caused primarily by the absorption "
           "of carbon dioxide (CO2)."),
    Hazard("saline_intrusion", "Saline intrusion", "Water", "Chronic",
           "Saline intrusion into a freshwater area."),
    Hazard("sea_level_rise", "Sea level rise", "Water", "Chronic",
           "An increase in mean ocean level."),
    # --- Water · Acute ------------------------------------------------------
    Hazard("drought", "Drought", "Water", "Acute",
           "An exceptional period of water scarcity for existing ecosystems and the human "
           "population (due to low rainfall, high temperature and/or wind)."),
    Hazard("heavy_precip_rain", "Heavy precipitation (Rain)", "Water", "Acute",
           "An extreme/heavy precipitation event of very high magnitude with very rare "
           "occurrence at a particular place."),
    Hazard("heavy_precip_hail", "Heavy precipitation (Hail)", "Water", "Acute",
           "Storm with hail with a minimum diameter of a certain threshold (1.5, 2 or 5 mm)."),
    Hazard("heavy_precip_snow", "Heavy precipitation (Snow)", "Water", "Acute",
           "Events in which large amounts of snow fall in a short period of time, leading to "
           "disruptions of infrastructure services."),
    Hazard("heavy_precip_ice", "Heavy precipitation (Ice)", "Water", "Acute",
           "Precipitation event containing mainly ice pellets or rainwater that freezes "
           "immediately after coming into contact with hard objects, leading to ice formation."),
    Hazard("flood_groundwater", "Flood (Ground water)", "Water", "Acute",
           "Inundation caused by a rising groundwater table."),
    Hazard("flood_fluvial", "Flood (Fluvial)", "Water", "Acute",
           "The overflowing of the normal confines of a stream or other body of water, or the "
           "accumulation of water over areas that are not normally submerged."),
    Hazard("flood_coastal", "Flood (Coastal)", "Water", "Acute",
           "An unusual accumulation of water above the ground caused by high tide."),
    Hazard("flood_pluvial", "Flood (Pluvial)", "Water", "Acute",
           "Accumulation of water above the ground caused by heavy rain, melting snow and rapid "
           "runoff from paved areas."),
    Hazard("glof", "Glacial lake outburst", "Water", "Acute",
           "A sudden release of water from a glacial lake."),
    # --- Solid mass · Chronic ----------------------------------------------
    Hazard("coastal_erosion", "Coastal erosion", "Solid mass", "Chronic",
           "The landward displacement of the coastline caused by the force of waves and currents."),
    Hazard("soil_degradation", "Soil degradation", "Solid mass", "Chronic",
           "The process(es) of reducing soil quality, making it less suitable for a specific "
           "purpose such as crop production."),
    Hazard("soil_erosion", "Soil erosion", "Solid mass", "Chronic",
           "Soil removal, often due to natural transport (water, wind) but amplified or even "
           "triggered by anthropogenic activities."),
    Hazard("solifluction", "Solifluction", "Solid mass", "Chronic",
           "A landslide phenomenon in which surface sediments saturated with water due to "
           "thawing move slowly down the slope."),
    # --- Solid mass · Acute -------------------------------------------------
    Hazard("avalanche", "Avalanche", "Solid mass", "Acute",
           "A mass of snow, ice, earth or rock, or a mixture thereof, falling from a mountainside."),
    Hazard("landslide", "Landslide", "Solid mass", "Acute",
           "More or less rapid displacement of large masses of soil or rock downwards."),
    Hazard("subsidence", "Subsidence", "Solid mass", "Acute",
           "Process by which the ground in an area sinks gradually to a lower level than the "
           "surrounding ground."),
)
# fmt: on


def all_hazards() -> tuple[Hazard, ...]:
    """Return the full, ordered catalogue of standardised climate hazards."""
    return _HAZARDS


def hazard_by_id(hazard_id: str) -> Hazard:
    """Return the :class:`Hazard` matching ``hazard_id`` (raises ``KeyError``)."""
    for hazard in _HAZARDS:
        if hazard.id == hazard_id:
            return hazard
    raise KeyError(f"Unknown hazard id: {hazard_id!r}")


def hazards_grouped() -> dict[str, dict[str, list[Hazard]]]:
    """Return hazards nested as ``{group: {category: [Hazard, ...]}}``.

    Drives the grouped/sub-grouped rendering of the spatial screening table.
    """
    grouped: dict[str, dict[str, list[Hazard]]] = {
        group: {category: [] for category in HAZARD_CATEGORIES} for group in HAZARD_GROUPS
    }
    for hazard in _HAZARDS:
        grouped[hazard.group][hazard.category].append(hazard)
    return grouped


assert len(_HAZARDS) == 36, "Expected 36 standardised climate hazards"
