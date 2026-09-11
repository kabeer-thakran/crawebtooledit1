"""60-second smoke test for the CRA tool.

Loads the sample fixture, validates the Pydantic model and renders the Word
report — without launching Streamlit. Run with::

    python smoke_test.py
"""

from __future__ import annotations

from pathlib import Path

from core.schema import CRAReport
from rendering.docx_renderer import render

_ROOT = Path(__file__).parent
_SAMPLE = _ROOT / "samples" / "sample_report.json"
_OUTPUT = _ROOT / "samples" / "smoke_test_output.docx"


def main() -> None:
    """Render the sample report and assert a non-trivial .docx is produced."""
    report = CRAReport.model_validate_json(_SAMPLE.read_text(encoding="utf-8"))
    data = render(report)
    assert data[:2] == b"PK", "Output is not a valid .docx (zip) container"
    assert len(data) > 5_000, "Output document is unexpectedly small"
    _OUTPUT.write_bytes(data)
    print(f"OK — rendered {len(data):,} bytes to {_OUTPUT}")
    print(f"Material hazards: {report.material_hazard_ids()}")


if __name__ == "__main__":
    main()
