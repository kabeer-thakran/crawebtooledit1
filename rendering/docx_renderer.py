"""Render a filled :class:`~core.schema.CRAReport` into a Word ``.docx``.

If the pre-processed Jinja2 template (``templates/cra_template.docx``, produced
by :mod:`rendering.prepare_template`) is present, scalar placeholders are filled
via ``docxtpl`` and the dynamic CRA tables are appended. If it is absent (e.g.
during the smoke-test before the Arup template has been processed), a complete,
structured report is built from scratch so a valid document is always produced.
"""

from __future__ import annotations

import io
from pathlib import Path

from docx import Document
from docx.document import Document as DocumentType
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import RGBColor

from core.analysis import (
    DIMENSION_LABELS,
    DIMENSIONS,
    peak_risk_per_hazard,
    risk_for,
)
from core.hazards import hazard_by_id
from core.matrix import RISK_COLOURS, RISK_LABELS, RISK_RANK, is_at_least
from core.schema import CRAReport, Horizon

_ROOT = Path(__file__).resolve().parent.parent
_TEMPLATE = _ROOT / "templates" / "cra_template.docx"

_ARUP_BLUE = RGBColor(0x00, 0x5A, 0xAA)


# ---------------------------------------------------------------------------
# Scalar context
# ---------------------------------------------------------------------------


def build_context(report: CRAReport) -> dict[str, str]:
    """Return the scalar Jinja2 context mapping for the template placeholders."""
    p = report.project
    context = {
        "project_name": p.project_name,
        "client": p.client,
        "date": p.report_date.isoformat(),
        "job_number": p.job_number,
        "document_version": p.document_version,
        "address": p.address,
        "city": p.city,
        "country": p.country,
        "latitude": f"{p.location.lat:.5f}",
        "longitude": f"{p.location.lng:.5f}",
        "asset_type": p.asset_type.value,
        "project_scope": p.project_scope,
        "eu_taxonomy_sector": p.taxonomy_sector.value,
        "eu_taxonomy_activity": p.taxonomy_activity,
        "substantial_contribution_or_dnsh": p.contribution_mode.value,
        "lifespan": str(p.lifespan_years),
        "baseline_period": p.baseline_period.label(),
        "reference_period": p.reference_period.label(),
        "mid_century_period": p.mid_century_period.label(),
        "end_century_period": p.end_century_period.label(),
        "scenario_a": p.scenario_a,
        "scenario_b": p.scenario_b,
    }

    # Receptor_1..5 / Desc_Receptor_1..5 — fill from the receptor register,
    # leaving any unused slots blank so the template placeholders disappear.
    for i in range(1, 6):
        receptor = report.phase0.receptors[i - 1] if i <= len(report.phase0.receptors) else None
        context[f"receptor_{i}"] = receptor.name if receptor else ""
        context[f"desc_receptor_{i}"] = (receptor.description or receptor.components) if receptor else ""

    # Hazard_1..10 — the material hazards taken forward to Phase 2 / adaptation.
    material_ids = report.material_hazard_ids()
    for i in range(1, 11):
        hazard_id = material_ids[i - 1] if i <= len(material_ids) else None
        context[f"hazard_{i}"] = hazard_by_id(hazard_id).name if hazard_id else ""

    return context


# ---------------------------------------------------------------------------
# Low-level docx helpers
# ---------------------------------------------------------------------------


def _shade_cell(cell, hex_colour: str) -> None:
    """Apply a solid background fill (hex, no '#') to a table cell."""
    shading = OxmlElement("w:shd")
    shading.set(qn("w:val"), "clear")
    shading.set(qn("w:color"), "auto")
    shading.set(qn("w:fill"), hex_colour.lstrip("#"))
    cell._tc.get_or_add_tcPr().append(shading)


def _add_table(document: DocumentType, headers: list[str], rows: list[list[str]]):
    """Add a styled table with a bold header row and return it."""
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        for run in cell.paragraphs[0].runs:
            run.font.bold = True
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = str(value)
    return table


def _heading(document: DocumentType, text: str, level: int = 1) -> None:
    """Add a heading, applying the Arup blue accent colour."""
    paragraph = document.add_heading(text, level=level)
    for run in paragraph.runs:
        run.font.color.rgb = _ARUP_BLUE


# ---------------------------------------------------------------------------
# Dynamic CRA tables
# ---------------------------------------------------------------------------


def _scenario_horizons(report: CRAReport) -> list[tuple[str, str]]:
    """Return the ordered scenario × horizon column combinations for risk tables."""
    scenarios = [report.project.scenario_a, report.project.scenario_b]
    horizons = [Horizon.BASELINE.value, Horizon.MID.value, Horizon.END.value]
    return [(s, h) for s in scenarios for h in horizons]


def _peak_dimension_risk(
    report: CRAReport, hazard_id: str, dimension: str, scenario: str, horizon: str
) -> str:
    """Return the worst risk level across receptors for a hazard/dimension/scenario/horizon."""
    best = "VL"
    for receptor in report.phase0.receptors:
        level = risk_for(report, hazard_id, receptor.id, dimension, scenario, horizon)
        if RISK_RANK[level] > RISK_RANK[best]:
            best = level
    return best


def _table_hazard_screening(document: DocumentType, report: CRAReport) -> None:
    """Table 10 — full hazard screening results."""
    _heading(document, "Table 10 — Hazard Screening Results", level=2)
    rows = []
    for s in report.screening:
        h = hazard_by_id(s.hazard_id)
        rows.append([h.name, h.group, h.category, s.at_site.value or "-", s.comments, s.source])
    _add_table(document, ["Hazard", "Group", "Category", "At site", "Comments", "Source"], rows)


def _table_hazard_summary(document: DocumentType, report: CRAReport) -> None:
    """Table 11 — climate hazards summary (material hazards only)."""
    _heading(document, "Table 11 — Climate Hazards Summary (Material)", level=2)
    rows = []
    for fs in report.final_selection:
        if not fs.material:
            continue
        h = hazard_by_id(fs.hazard_id)
        rows.append([h.name, h.group, h.category, fs.comments])
    _add_table(document, ["Hazard", "Group", "Category", "Comments"], rows or [["—", "—", "—", "—"]])


def _table_risk_dimension(
    document: DocumentType, report: CRAReport, dimension: str, table_no: int
) -> None:
    """Tables 17–19 — risk per dimension across scenario × horizon."""
    _heading(
        document,
        f"Table {table_no} — {DIMENSION_LABELS[dimension]} Risk",
        level=2,
    )
    combos = _scenario_horizons(report)
    headers = ["Hazard"] + [f"{s}\n{h}" for s, h in combos]
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        for run in cell.paragraphs[0].runs:
            run.font.bold = True

    for hazard_id in report.material_hazard_ids():
        cells = table.add_row().cells
        cells[0].text = hazard_by_id(hazard_id).name
        for j, (scenario, horizon) in enumerate(combos, start=1):
            level = _peak_dimension_risk(report, hazard_id, dimension, scenario, horizon)
            cells[j].text = RISK_LABELS[level]
            _shade_cell(cells[j], RISK_COLOURS[level])


def _tables_adaptation(document: DocumentType, report: CRAReport) -> None:
    """Tables 20–29 — adaptation plan, one table per material hazard (max 10)."""
    _heading(document, "Adaptation Plan", level=1)
    peaks = peak_risk_per_hazard(report)
    at_risk = [hid for hid, lvl in peaks.items() if is_at_least(lvl, "M")][:10]
    if not at_risk:
        document.add_paragraph("No hazards reach Moderate risk; no adaptation measures required.")
        return
    for n, hazard_id in enumerate(at_risk, start=20):
        hazard = hazard_by_id(hazard_id)
        _heading(document, f"Table {n} — Adaptation: {hazard.name}", level=2)
        measures = [m for m in report.adaptation if m.hazard_id == hazard_id]
        rows = [
            [
                m.description,
                "Physical" if m.physical else "Non-physical",
                m.priority,
                f"{m.timeframe_years} yr",
                m.indicative_cost,
                m.notes,
            ]
            for m in measures
        ] or [["(no measures defined)", "", "", "", "", ""]]
        _add_table(
            document,
            ["Measure", "Type", "Priority", "Timeframe", "Indicative cost", "Notes"],
            rows,
        )


def _receptor_bullets(document: DocumentType, report: CRAReport) -> None:
    """Fill the bullet list of receptors under Section 1.2."""
    _heading(document, "1.2 Receptors", level=2)
    for receptor in report.phase0.receptors:
        text = receptor.name
        if receptor.components:
            text += f" — {receptor.components}"
        document.add_paragraph(text, style="List Bullet")


def append_dynamic_content(document: DocumentType, report: CRAReport) -> None:
    """Append the receptor list and all dynamic CRA tables to ``document``."""
    _receptor_bullets(document, report)
    _table_hazard_screening(document, report)
    _table_hazard_summary(document, report)
    for offset, dimension in enumerate(DIMENSIONS):
        _table_risk_dimension(document, report, dimension, table_no=17 + offset)
    _tables_adaptation(document, report)


# ---------------------------------------------------------------------------
# Fallback (no template) — full structured report
# ---------------------------------------------------------------------------


def _build_from_scratch(report: CRAReport) -> DocumentType:
    """Build a complete structured report when no template is available."""
    document = Document()
    ctx = build_context(report)

    title = document.add_heading("Climate Risk Assessment", level=0)
    for run in title.runs:
        run.font.color.rgb = _ARUP_BLUE

    meta = [
        ("Project", ctx["project_name"]),
        ("Client", ctx["client"]),
        ("Date", ctx["date"]),
        ("Job number", ctx["job_number"]),
        ("Document version", ctx["document_version"]),
        ("Location", f"{ctx['city']}, {ctx['country']} ({ctx['latitude']}, {ctx['longitude']})"),
        ("Asset type", ctx["asset_type"]),
        ("EU Taxonomy sector", ctx["eu_taxonomy_sector"]),
        ("EU Taxonomy activity", ctx["eu_taxonomy_activity"]),
        ("Substantial Contribution / DNSH", ctx["substantial_contribution_or_dnsh"]),
        ("Lifespan (years)", ctx["lifespan"]),
        ("Scenarios", f"{ctx['scenario_a']} / {ctx['scenario_b']}"),
        ("Horizons", f"{ctx['baseline_period']}, {ctx['mid_century_period']}, "
                     f"{ctx['end_century_period']}"),
    ]
    _add_table(document, ["Field", "Value"], [[k, v] for k, v in meta])

    _heading(document, "1. Introduction", level=1)
    document.add_paragraph(report.phase0.introduction_text)
    _heading(document, "1.1 Methodology", level=2)
    document.add_paragraph(report.phase0.methodology_text)
    document.add_paragraph(report.phase0.scope_text)

    append_dynamic_content(document, report)
    return document


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def render(report: CRAReport) -> bytes:
    """Render ``report`` to Word and return the ``.docx`` file as bytes.

    Uses the pre-processed Arup template when available, otherwise builds a
    structured report from scratch. This is the single function called by the
    Generate Report step.
    """
    if _TEMPLATE.exists():
        from docxtpl import DocxTemplate  # imported lazily; only needed with a template

        tpl = DocxTemplate(str(_TEMPLATE))
        tpl.render(build_context(report))
        buffer = io.BytesIO()
        tpl.save(buffer)
        buffer.seek(0)
        document = Document(buffer)
        document.add_page_break()
        append_dynamic_content(document, report)
    else:
        document = _build_from_scratch(report)

    out = io.BytesIO()
    document.save(out)
    return out.getvalue()
