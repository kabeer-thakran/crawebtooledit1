"""One-time script: convert the Arup ``[Placeholder]`` Word template to Jinja2.

Opens ``samples/Template-Final version-ENG.docx``, rewrites every bracketed
token such as ``[Project_Name]`` and ``[Substantial_Contribution/DNSH]`` into a
``docxtpl`` Jinja2 placeholder (``{{ project_name }}``,
``{{ substantial_contribution_or_dnsh }}``), and saves the result to
``templates/cra_template.docx`` while preserving all Arup styling, headings,
tables and the "Instructions for Editing" banner.

Run once after placing the reference template in ``samples/``::

    python -m rendering.prepare_template
"""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.document import Document as DocumentType
from docx.table import _Cell

_ROOT = Path(__file__).resolve().parent.parent
_SOURCE = _ROOT / "samples" / "Template-Final version-ENG.docx"
_TARGET = _ROOT / "templates" / "cra_template.docx"

# Matches a bracketed placeholder token, e.g. [Project_Name] or
# [Substantial_Contribution/DNSH]. Excludes nested brackets.
_TOKEN_RE = re.compile(r"\[([^\[\]]+?)\]")

# Explicit slug overrides where the literal slug differs from the render
# context key (see :func:`rendering.docx_renderer.build_context`).
_OVERRIDES: dict[str, str] = {
    "substantial_contribution/dnsh": "substantial_contribution_or_dnsh",
    "substantial_contribution / dnsh": "substantial_contribution_or_dnsh",
    "jn": "job_number",
    "version": "document_version",
    "baseline_period": "baseline_period",
}

# Allow-list of *data* tokens that are filled from the CRA model. Every other
# bracketed token in the Arup template is an editorial instruction (e.g.
# "[Add an image if apply]") or a dynamic-table marker (``[Table_*]``) and is
# deliberately left as literal text for the user to complete or for the
# renderer to populate separately.
_DATA_TOKENS: frozenset[str] = frozenset(
    {
        "client", "project_name", "city", "country", "address", "date",
        "job_number", "document_version", "asset_type", "project_scope",
        "eu_taxonomy_activity", "eu_taxonomy_sector",
        "substantial_contribution_or_dnsh",
        "scenario_a", "scenario_b", "baseline_period", "reference_period",
        "mid_century_period", "end_century_period", "lifespan",
    }
    | {f"receptor_{i}" for i in range(1, 6)}
    | {f"desc_receptor_{i}" for i in range(1, 6)}
    | {f"hazard_{i}" for i in range(1, 11)}
)


def slugify(token: str) -> str:
    """Convert a placeholder token to a snake_case Jinja2 variable name.

    ``[Substantial_Contribution/DNSH]`` → ``substantial_contribution_or_dnsh``.
    """
    text = token.strip().lower().replace("/", " or ")
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return _OVERRIDES.get(text, text)


def _convert_text(text: str) -> str:
    """Replace allow-listed bracketed tokens with Jinja2 placeholders.

    Tokens not in :data:`_DATA_TOKENS` (editorial guidance and ``[Table_*]``
    markers) are preserved verbatim.
    """

    def _sub(match: "re.Match[str]") -> str:
        slug = slugify(match.group(1))
        if slug in _DATA_TOKENS:
            return f"{{{{ {slug} }}}}"
        return match.group(0)

    return _TOKEN_RE.sub(_sub, text)


def _convert_paragraph(paragraph) -> None:
    """Rewrite placeholders within a paragraph, preserving its paragraph style.

    If a token spans multiple runs the runs are collapsed into the first run so
    the replacement still succeeds; otherwise per-run formatting is preserved.
    """
    full = paragraph.text
    if "[" not in full:
        return
    converted = _convert_text(full)
    if converted == full:
        return
    # Collapse runs: write converted text to the first run, clear the rest.
    if paragraph.runs:
        paragraph.runs[0].text = converted
        for run in paragraph.runs[1:]:
            run.text = ""
    else:  # pragma: no cover - defensive
        paragraph.add_run(converted)


def _convert_cell(cell: _Cell) -> None:
    """Recursively convert placeholders inside a table cell."""
    for paragraph in cell.paragraphs:
        _convert_paragraph(paragraph)
    for table in cell.tables:
        _convert_table(table)


def _convert_table(table) -> None:
    """Convert placeholders inside every cell of a table."""
    for row in table.rows:
        for cell in row.cells:
            _convert_cell(cell)


def convert_document(document: DocumentType) -> None:
    """Convert all placeholders in body paragraphs and tables in place."""
    for paragraph in document.paragraphs:
        _convert_paragraph(paragraph)
    for table in document.tables:
        _convert_table(table)


def main() -> None:
    """Convert the reference template and write ``templates/cra_template.docx``."""
    if not _SOURCE.exists():
        raise FileNotFoundError(
            f"Reference template not found: {_SOURCE}. "
            "Place 'Template-Final version-ENG.docx' in the samples/ folder first."
        )
    document = Document(str(_SOURCE))
    convert_document(document)
    _TARGET.parent.mkdir(parents=True, exist_ok=True)
    document.save(str(_TARGET))
    print(f"Converted template written to: {_TARGET}")


if __name__ == "__main__":
    main()
