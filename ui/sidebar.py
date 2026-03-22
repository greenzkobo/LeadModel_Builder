"""
ui/sidebar.py
==============
Professional sidebar with branding, navigation, and pipeline progress.
"""

import streamlit as st


# ── Nav structure ──────────────────────────────────────────────
NAV_SECTIONS = [
    ("DATA", [
        ("📂", "Ingestion",         "ingestion"),
        ("🧹", "Cleaning",          "cleaning"),
        ("🔎", "Data Explorer",     "data_explorer"),
        ("🧩", "Segmentation",      "segmentation"),
    ]),
    ("MODELLING", [
        ("🔍", "Feature Selection", "features"),
        ("🤖", "Training",          "training"),
        ("📊", "Evaluation",        "evaluation"),
        ("📈", "Visualizations",    "visualizations"),
    ]),
    ("OUTPUT", [
        ("📤", "Export",            "export"),
        ("⚡", "Auto-Run",          "autorun"),
    ]),
    ("SYSTEM", [
        ("⚙️", "Settings",          "settings"),
        ("📋", "Activity Log",      "log"),
    ]),
]

PIPELINE_STEPS = ["df", "df_clean", "selector", "trainer", "evaluator"]


def render():
    with st.sidebar:
        _render_brand()
        _render_nav()
        _render_pipeline_progress()


def _render_brand():
    client = st.session_state.get("client") or ""
    client_html = (
        f'<div class="sidebar-client-pill">⬡ {client}</div>'
        if client else
        '<div class="sidebar-client-pill" style="opacity:0.4">No client selected</div>'
    )
    st.markdown(
        f'<div class="sidebar-brand">'
        f'  <div class="sidebar-brand-name">LeadModel Builder</div>'
        f'  <div class="sidebar-brand-sub">ML Modeling Toolkit</div>'
        f'  {client_html}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Home button
    if st.button("🏠  Home", key="nav_home",
                 use_container_width=True):
        st.session_state.page = "home"
        st.rerun()


def _render_nav():
    current = st.session_state.get("page", "home")

    for section_label, items in NAV_SECTIONS:
        st.markdown(
            f'<div class="sidebar-section">{section_label}</div>',
            unsafe_allow_html=True,
        )
        for icon, label, page_key in items:
            _step_complete = _is_step_available(page_key)
            dot = " ✓" if _step_complete else ""
            btn_label = f"{icon}  {label}{dot}"

            if st.button(btn_label, key=f"nav_{page_key}",
                         use_container_width=True):
                st.session_state.page = page_key
                st.rerun()


def _render_pipeline_progress():
    completed = sum(
        1 for key in PIPELINE_STEPS
        if st.session_state.get(key) is not None
    )
    total = len(PIPELINE_STEPS)
    pct   = int(completed / total * 100)

    st.markdown(
        f'<div class="sidebar-progress">'
        f'  <div class="sidebar-progress-label">Pipeline Progress</div>'
        f'  <div class="sidebar-progress-bar-bg">'
        f'    <div class="sidebar-progress-bar-fill" style="width:{pct}%"></div>'
        f'  </div>'
        f'  <div class="sidebar-progress-steps">{completed} / {total} steps complete</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _is_step_available(page_key: str) -> bool:
    """Return True if this page's prerequisite state exists."""
    checks = {
        "ingestion":   lambda: st.session_state.get("df") is not None,
        "cleaning":    lambda: st.session_state.get("df") is not None,
        "data_explorer": lambda: st.session_state.get("df") is not None,
        "segmentation":  lambda: st.session_state.get("df_clean") is not None,
        "features":    lambda: st.session_state.get("df_clean") is not None,
        "training":    lambda: st.session_state.get("df_clean") is not None,
        "evaluation":  lambda: st.session_state.get("trainer") is not None,
        "visualizations": lambda: st.session_state.get("evaluator") is not None,
        "export":      lambda: st.session_state.get("evaluator") is not None,
    }
    check = checks.get(page_key)
    return check() if check else False
