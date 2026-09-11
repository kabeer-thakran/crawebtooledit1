"""Shared branding and layout helpers for the Arup CRA tool.

Centralises page configuration, the Arup colour palette and the sidebar so
every page (the entry point and the ten step pages) presents a consistent,
lightly Arup-branded shell.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

#: Arup brand colours (light-touch theming for the MVP).
ARUP_RED = "#E61E28"
ARUP_BLUE = "#005AAA"

APP_TITLE = "Arup CRA Tool — R&A Skill Network Pilot"
APP_VERSION = "0.1.0 (MVP)"
CHAMPION = "Dr. Dinesh Kumar — Data & Workflow (Digital & AI) Champion"
FEEDBACK_URL = "https://forms.office.com/"  # placeholder feedback form

_ASSETS = Path(__file__).parent / "assets"


def configure_page(page_title: str) -> None:
    """Apply shared page config and inject the Arup accent CSS.

    Call once at the top of every page module.
    """
    st.set_page_config(
        page_title=page_title,
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        f"""
        <style>
        :root {{ --arup-red: {ARUP_RED}; --arup-blue: {ARUP_BLUE}; }}
        h1, h2, h3 {{ color: {ARUP_BLUE}; }}
        .stButton > button[kind="primary"] {{
            background-color: {ARUP_RED}; border-color: {ARUP_RED};
        }}
        div[data-testid="stMetricValue"] {{ color: {ARUP_BLUE}; }}
        .cra-breadcrumb {{
            font-size: 0.78rem; color: #4b5563; letter-spacing: 0.03em;
            margin: 0.25rem 0 1rem 0; padding: 0.4rem 0.6rem; border-left: 3px solid {ARUP_RED};
            background: rgba(230, 30, 40, 0.04); border-radius: 6px;
        }}
        .cra-tag {{
            display: inline-block; margin-right: 0.4rem; padding: 0.15rem 0.5rem;
            border-radius: 999px; font-size: 0.72rem; font-weight: 600; color: white;
        }}
        .cra-water-chronic {{ background: rgba(13, 110, 253, 0.18); color: #0b3d8d; }}
        .cra-water-acute {{ background: rgba(0, 90, 170, 0.28); color: #072b5c; }}
        .cra-placeholder {{
            padding: 0.8rem 1rem; border-left: 4px solid {ARUP_RED};
            background: rgba(230, 30, 40, 0.05); border-radius: 8px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    """Render the shared sidebar: logo, version, champion and feedback link."""
    with st.sidebar:
        logo = _ASSETS / "arup_logo.png"
        if logo.exists():
            st.image(str(logo), use_container_width=True)
        else:
            st.markdown("### :red[ARUP] · CRA")
        st.caption(APP_TITLE)
        st.divider()
        st.markdown(f"**Version:** {APP_VERSION}")
        st.markdown(f"**Champion:** {CHAMPION}")
        st.markdown(f"[Share feedback]({FEEDBACK_URL})")
