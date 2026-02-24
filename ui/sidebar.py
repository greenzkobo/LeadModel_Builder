"""
ui/sidebar.py
==============
Sidebar navigation + live session status.
Called once per render from app.py.
"""

import streamlit as st
from ui.components import badge


def render():
    """Render the full sidebar."""
    with st.sidebar:
        # ── Logo / title ──────────────────────────────────────
        st.markdown(
            '<div style="padding: 0 0.5rem 1rem;">'
            '<div style="font-size:1.1rem;font-weight:700;color:#f1f5f9;">⚡ ML Toolkit</div>'
            '<div style="font-size:0.72rem;color:#475569;margin-top:2px;">Modeling Workspace</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # ── Client status ──────────────────────────────────────
        client = st.session_state.get("client")
        if client:
            st.markdown(
                f'<div style="background:#1e293b;border-radius:8px;padding:0.6rem 0.85rem;'
                f'margin-bottom:1rem;font-size:0.82rem;">'
                f'<div style="color:#64748b;font-size:0.7rem;text-transform:uppercase;'
                f'letter-spacing:0.05em;margin-bottom:3px;">Active Client</div>'
                f'<div style="color:#f1f5f9;font-weight:600;">{client}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="background:#1e293b;border-radius:8px;padding:0.6rem 0.85rem;'
                'margin-bottom:1rem;font-size:0.82rem;color:#475569;">'
                'No client selected</div>',
                unsafe_allow_html=True,
            )

        # ── Navigation ─────────────────────────────────────────
        st.markdown(
            '<div style="font-size:0.7rem;color:#475569;text-transform:uppercase;'
            'letter-spacing:0.06em;padding:0 0.5rem;margin-bottom:0.4rem;">Pipeline</div>',
            unsafe_allow_html=True,
        )

        nav_items = [
            ("🏠", "Home",            "home"),
            ("📂", "Data Ingestion",  "ingestion"),
            ("🧹", "Data Cleaning",    "cleaning"),
            ("🔎", "Data Explorer",    "data_explorer"),
            ("🔍", "Feature Selection","features"),
            ("🤖", "Model Training",  "training"),
            ("📊", "Evaluation",      "evaluation"),
            ("📈", "Visualizations",  "visualizations"),
            ("📤", "Export",          "export"),
        ]

        for icon, label, page_key in nav_items:
            status_dot = _nav_dot(page_key)
            if st.button(
                f"{icon}  {label}{status_dot}",
                key=f"nav_{page_key}",
                use_container_width=True,
            ):
                st.session_state.page = page_key
                st.rerun()

        st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.7rem;color:#475569;text-transform:uppercase;'
            'letter-spacing:0.06em;padding:0 0.5rem;margin-bottom:0.4rem;">Tools</div>',
            unsafe_allow_html=True,
        )

        if st.button("⚙️  Settings", key="nav_settings", use_container_width=True):
            st.session_state.page = "settings"
            st.rerun()

        if st.button("🚀  Auto-Run", key="nav_autorun", use_container_width=True):
            st.session_state.page = "autorun"
            st.rerun()

        if st.button("📋  Activity Log", key="nav_log", use_container_width=True):
            st.session_state.page = "log"
            st.rerun()

        # ── Pipeline progress ──────────────────────────────────
        st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)
        _pipeline_status()


def _nav_dot(page_key: str) -> str:
    """Return a status indicator for nav items based on session state."""
    s = st.session_state
    checks = {
        "ingestion":    s.get("df") is not None,
        "cleaning":     s.get("df_clean") is not None,
        "features":     s.get("selector") is not None,
        "training":     s.get("trainer") is not None,
        "evaluation":   s.get("evaluator") is not None,
        "visualizations": s.get("evaluator") is not None,
        "export":       s.get("evaluator") is not None,
    }
    if page_key in checks:
        return "  ✓" if checks[page_key] else ""
    return ""


def _pipeline_status():
    """Mini pipeline checklist at the bottom of the sidebar."""
    s = st.session_state
    steps = [
        ("Client",          s.get("client") is not None),
        ("Data loaded",     s.get("df") is not None),
        ("Data cleaned",    s.get("df_clean") is not None),
        ("Features",        s.get("selector") is not None),
        ("Models trained",  s.get("trainer") is not None),
        ("Evaluated",       s.get("evaluator") is not None),
    ]

    done  = sum(1 for _, v in steps if v)
    total = len(steps)

    st.markdown(
        f'<div style="font-size:0.7rem;color:#475569;text-transform:uppercase;'
        f'letter-spacing:0.06em;padding:0 0.5rem;margin-bottom:0.5rem;">'
        f'Progress  {done}/{total}</div>',
        unsafe_allow_html=True,
    )

    # Progress bar
    pct = int(done / total * 100)
    st.markdown(
        f'<div style="background:#1e293b;border-radius:999px;height:5px;margin:0 0.5rem 0.75rem;">'
        f'<div style="background:#3b82f6;border-radius:999px;height:5px;width:{pct}%;'
        f'transition:width 0.3s;"></div></div>',
        unsafe_allow_html=True,
    )

    for label, done_flag in steps:
        icon  = "✅" if done_flag else "⬜"
        color = "#4ade80" if done_flag else "#334155"
        st.markdown(
            f'<div style="font-size:0.78rem;color:{color};padding:1px 0.5rem;">'
            f'{icon}  {label}</div>',
            unsafe_allow_html=True,
        )
