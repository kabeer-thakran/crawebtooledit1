# Arup CRA Web Tool — R&A Skill Network Pilot

An interactive Streamlit app that turns the standardised Arup semi-quantitative
**Climate Risk Assessment (CRA)** workbook into a guided, tabbed web workflow
and produces a downloadable **Word report** matching the Arup template.

> Champion: **Dr. Dinesh Kumar** — Data & Workflow (Digital & AI), Resilience &
> Adaptation Skill Network. MVP build.

---

## ✨ What it does

A 10-step tabbed workflow (NIH-IDF-style), persisted in `st.session_state`:

| Step | Tab | Purpose |
|------|-----|---------|
| 1 | Project Information | Metadata, map location picker, EU Taxonomy classification, timeframes & scenarios |
| 2 | Phase 0 — Preparation | Adaptable boilerplate text + receptor register |
| 3 | Phase 1 — Spatial Screening | All 33 hazards grouped; is each present at the site? |
| 4 | Phase 1 — Materiality | Hazard × receptor significance (for "Yes" hazards) |
| 5 | Phase 1 — Final Selection | Auto-computes material hazards (Yes in both screens) |
| 6 | Phase 2 — Hazard Assessment | Likelihood + threshold per scenario × horizon |
| 7 | Phase 2 — Vulnerability | Direct / Operational / H&S scores per hazard × receptor |
| 8 | Phase 2 — Risk | 5×5 risk matrix → colour-coded Plotly heatmaps |
| 9 | Phase 2.2 — Adaptation | Measures for hazards with risk ≥ Moderate |
| 10 | Generate Report | Validate, render `.docx`, save/resume JSON |

---

## 🚀 Quickstart

### With `uv` (recommended)

```powershell
cd cra_web_tool
uv venv
uv pip install -r requirements.txt
uv run streamlit run app.py
```

### With pip

```powershell
cd cra_web_tool
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The app opens at <http://localhost:8501>.

---

## ⏱ 60-second smoke test (no UI)

Render the Word report from the bundled fixture and confirm a valid `.docx`:

```powershell
python smoke_test.py
```

Expected output:

```
OK — rendered NN,NNN bytes to samples\smoke_test_output.docx
Material hazards: ['heat_wave', 'flood_pluvial']
```

Open `samples/smoke_test_output.docx` to inspect the generated report. This
works **without** the Arup template — the renderer falls back to a
fully-structured report when `templates/cra_template.docx` is absent.

---

## 📄 Preparing the Word template (one-time)

1. Copy the two reference files into `samples/` (exact names):
   - `20260528_Final_version_ENG.xlsm`
   - `Template-Final version-ENG.docx`
2. Convert the Arup `[Placeholder]` template to a `docxtpl` Jinja2 template:

   ```powershell
   python -m rendering.prepare_template
   ```

   This rewrites tokens like `[Project_Name]` → `{{ project_name }}` and
   `[Substantial_Contribution/DNSH]` → `{{ substantial_contribution_or_dnsh }}`,
   preserving all Arup styling, headings, tables and the "Instructions for
   Editing" banner. Output: `templates/cra_template.docx`.

Once present, `Generate Report` fills the scalar placeholders via the template
and appends the dynamic CRA tables (10, 11, 17–19, 20–29).

> **MVP note:** dynamic tables are appended after the template body rather than
> spliced at exact in-document anchors. Positional anchoring is a planned
> enhancement.

---

## 🗂 Project structure

```
cra_web_tool/
├── app.py                 # Streamlit entry point (st.tabs over the 10 steps)
├── branding.py            # Page config, Arup palette, sidebar
├── ui_helpers.py          # Shared score / Yes-No widgets
├── smoke_test.py          # Headless render test
├── pages/                 # render(report) per step (1..10)
├── core/
│   ├── schema.py          # Pydantic v2 models (CRAReport aggregate)
│   ├── hazards.py         # The 33 standardised climate hazards
│   ├── matrix.py          # 5×5 risk matrix (Table 5)
│   ├── analysis.py        # Risk computation (shared by UI + renderer)
│   └── state.py           # Session-state helpers
├── rendering/
│   ├── prepare_template.py # One-time [Placeholder] → {{ jinja }} converter
│   └── docx_renderer.py    # render(report) -> bytes
├── templates/             # Pre-processed template lands here
├── assets/                # arup_logo.png (optional)
├── samples/               # Reference files + sample_report.json
├── requirements.txt
├── pyproject.toml
└── .streamlit/config.toml # Arup theme; hides auto page-nav (tabs are used)
```

---

## 🎨 Branding

- Title: **Arup CRA Tool — R&A Skill Network Pilot**
- Colours: primary `#E61E28` (Arup red), secondary `#005AAA`
- Sidebar: logo (or text fallback), version, champion, feedback link
  (placeholders).

---

## ☁️ Deployment

### Streamlit Community Cloud

1. Push this folder to a GitHub repo.
2. On <https://share.streamlit.io>, create an app pointing at `app.py`.
3. Set **Python 3.11** and `requirements.txt`; deploy.

### Azure App Service (Linux)

```powershell
az webapp up --runtime "PYTHON:3.11" --name cra-web-tool --resource-group <rg> --sku B1
```

Set the startup command:

```
python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0
```

App Service listens on `PORT=8000`; align Streamlit's `--server.port`
accordingly. No environment variables are required for the MVP.

---

## 🔌 Clean hooks for later (not built yet)

- **AI drafting layer** — expand "Typical text – to be adapted" via an LLM
  (`core.schema.Phase0` fields are the insertion points).
- **Databricks climate auto-fill** — populate `HazardAssessment` from CMIP6 /
  ERA5 / IPCC Atlas given `ProjectInfo.location`.
- **Azure AD SSO** — front the app for the R&A Skill Network membership.
- **Multilingual (EN/ES/IT)** — template selection + i18n of boilerplate.

---

## 🧪 Code standards

- Type hints throughout; `mypy`-oriented config in `pyproject.toml`.
- `ruff` formatting/linting (`ruff check .`, `ruff format .`).
- One docstring per public function describing its CRA-workflow role.
- No hardcoded paths — `pathlib.Path(__file__)` everywhere.

### Reconciliation note

The Excel/Word attachments arrived as binary headers only, so the **33-hazard
catalogue** was built from the EU Taxonomy (Climate Delegated Act, Appendix A)
classification and the **risk matrix** from the spec (Table 5). After running
`prepare_template.py` against the real `.docx`, reconcile hazard wording and the
EU Taxonomy activity dropdowns in `core/hazards.py` and `core/schema.py`
(`TAXONOMY_ACTIVITIES`) against the workbook if exact wording must match.
