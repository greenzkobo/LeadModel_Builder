"""
ui/components.py
=================
Reusable Streamlit UI components used across pages.
"""

import streamlit as st


def page_header(title: str, desc: str = ""):
    st.markdown(
        f'<div class="page-header">'
        f'<div class="page-title">{title}</div>'
        f'<div class="page-desc">{desc}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def badge(text: str, color: str = "gray") -> str:
    """Return HTML badge string. color: green | yellow | blue | gray"""
    return f'<span class="badge badge-{color}">{text}</span>'


def metric_grid(metrics: list):
    """
    Render a row of metric boxes.
    metrics = [{"label": "Lift D1", "value": "2.31", "sub": "validation"}, ...]
    """
    cols = "".join([
        f'<div class="metric-box">'
        f'<div class="metric-label">{m["label"]}</div>'
        f'<div class="metric-value">{m["value"]}</div>'
        f'<div class="metric-sub">{m.get("sub", "")}</div>'
        f'</div>'
        for m in metrics
    ])
    st.markdown(f'<div class="metric-grid">{cols}</div>', unsafe_allow_html=True)


def card(title: str, subtitle: str = "", content_fn=None):
    """Render a card container. Pass content_fn for Streamlit widgets inside."""
    st.markdown(
        f'<div class="card">'
        f'<div class="card-title">{title}</div>'
        f'<div class="card-sub">{subtitle}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if content_fn:
        content_fn()


def divider():
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


def step_status(steps: list):
    """
    Render a pipeline step checklist.
    steps = [{"label": "Data Ingestion", "status": "done|ready|wait"}]
    """
    icons = {"done": "✅", "ready": "🔵", "wait": "⬜"}
    css   = {"done": "step-done", "ready": "step-ready", "wait": "step-wait"}

    rows = "".join([
        f'<div class="step-row">'
        f'<span class="step-icon {css[s["status"]]}">{icons[s["status"]]}</span>'
        f'<span>{s["label"]}</span>'
        f'</div>'
        for s in steps
    ])
    st.markdown(rows, unsafe_allow_html=True)


def success(msg: str):
    st.success(f"✓ {msg}")


def warn(msg: str):
    st.warning(f"⚠ {msg}")


def error(msg: str):
    st.error(f"✗ {msg}")


def shape_delta(before: tuple, after: tuple):
    """Show before → after shape change."""
    dropped_cols = before[1] - after[1]
    dropped_rows = before[0] - after[0]
    parts = []
    if dropped_cols:
        parts.append(f"{dropped_cols:,} columns removed")
    if dropped_rows:
        parts.append(f"{dropped_rows:,} rows removed")
    summary = " · ".join(parts) if parts else "No change"
    st.caption(
        f"Shape: **{before[0]:,} × {before[1]:,}** → "
        f"**{after[0]:,} × {after[1]:,}**  —  {summary}"
    )
