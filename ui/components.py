"""
ui/components.py
=================
Reusable UI components matching the professional light theme.
"""

import streamlit as st


def page_header(title: str, subtitle: str = ""):
    st.markdown(
        f'<div class="page-header">'
        f'<div class="page-title">{title}</div>'
        f'{"<div class=page-desc>" + subtitle + "</div>" if subtitle else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )


def section_heading(title: str):
    st.markdown(
        f'<div class="section-heading">{title}</div>',
        unsafe_allow_html=True,
    )


def divider():
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


def metric_grid(metrics: dict):
    """
    metrics = {"Label": ("value", "sublabel"), ...}
    """
    cols_html = ""
    for label, val in metrics.items():
        value   = val[0] if isinstance(val, tuple) else val
        sub     = val[1] if isinstance(val, tuple) else ""
        cols_html += (
            f'<div class="metric-box">'
            f'<div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div>'
            f'{"<div class=metric-sub>" + sub + "</div>" if sub else ""}'
            f'</div>'
        )
    st.markdown(
        f'<div class="metric-grid">{cols_html}</div>',
        unsafe_allow_html=True,
    )


def card(title: str, subtitle: str = "", content: str = ""):
    st.markdown(
        f'<div class="card">'
        f'<div class="card-title">{title}</div>'
        f'{"<div class=card-sub>" + subtitle + "</div>" if subtitle else ""}'
        f'{"<div style=margin-top:0.75rem>" + content + "</div>" if content else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )


def badge(label: str, color: str = "gray"):
    """color: green | yellow | blue | red | gray | navy"""
    st.markdown(
        f'<span class="badge badge-{color}">{label}</span>',
        unsafe_allow_html=True,
    )


def winner_banner(model_name: str, lift: float, auc: float, ks: float):
    st.markdown(
        f'<div class="winner-banner">'
        f'<div class="winner-label">🏆 Best Model</div>'
        f'<div class="winner-name">{model_name}</div>'
        f'<div class="winner-metrics">'
        f'  <div class="winner-metric-item">'
        f'    <span class="winner-metric-val">{lift:.3f}</span>'
        f'    <span class="winner-metric-lbl">Lift D1</span>'
        f'  </div>'
        f'  <div class="winner-metric-item">'
        f'    <span class="winner-metric-val">{auc:.3f}</span>'
        f'    <span class="winner-metric-lbl">AUC</span>'
        f'  </div>'
        f'  <div class="winner-metric-item">'
        f'    <span class="winner-metric-val">{ks:.3f}</span>'
        f'    <span class="winner-metric-lbl">KS</span>'
        f'  </div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def alert(msg: str, kind: str = "info"):
    """kind: success | warning | error | info"""
    icons = {"success": "✓", "warning": "⚠", "error": "✕", "info": "ℹ"}
    icon  = icons.get(kind, "ℹ")
    st.markdown(
        f'<div class="alert alert-{kind}">'
        f'<span>{icon}</span><span>{msg}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def success(msg: str): alert(msg, "success")
def warn(msg: str):    alert(msg, "warning")
def error(msg: str):   alert(msg, "error")


def shape_delta(before: tuple, after: tuple):
    rows_diff = after[0] - before[0]
    cols_diff = after[1] - before[1]
    rows_str  = f"{rows_diff:+,}" if rows_diff != 0 else "—"
    cols_str  = f"{cols_diff:+,}" if cols_diff != 0 else "—"
    st.markdown(
        f'<div style="font-size:0.8rem;color:#475569;padding:0.4rem 0;">'
        f'Shape: <b>{before[0]:,} × {before[1]:,}</b> → '
        f'<b>{after[0]:,} × {after[1]:,}</b> &nbsp;'
        f'<span style="color:#DC2626">{cols_str} cols</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def step_status(step: str, status: str, detail: str = ""):
    """status: done | ready | wait"""
    icons = {"done": "✓", "ready": "→", "wait": "○"}
    css   = {"done": "step-done", "ready": "step-ready", "wait": "step-wait"}
    icon  = icons.get(status, "○")
    cls   = css.get(status, "step-wait")
    st.markdown(
        f'<div class="step-row {cls}">'
        f'<span class="step-icon">{icon}</span>'
        f'<span>{step}</span>'
        f'{"<span style=margin-left:auto;font-size:0.75rem;color:#94A3B8>" + detail + "</span>" if detail else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )
