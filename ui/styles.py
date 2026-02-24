"""
ui/styles.py
=============
All custom CSS injected once at app startup.
"""

CSS = """
<style>
/* ── Layout ─────────────────────────────────────────── */
[data-testid="stSidebar"] {
    min-width: 230px !important;
    max-width: 230px !important;
    background: #0a0f1e;
    border-right: 1px solid #1e293b;
}
[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
.main .block-container { padding-top: 2rem; max-width: 1100px; }

/* ── Sidebar nav buttons ────────────────────────────── */
div[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    text-align: left;
    background: transparent;
    border: none;
    border-radius: 7px;
    padding: 0.45rem 0.85rem;
    font-size: 0.88rem;
    font-weight: 400;
    color: #94a3b8;
    transition: all 0.15s;
    margin-bottom: 1px;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: #1e293b;
    color: #f1f5f9;
}

/* ── Cards ──────────────────────────────────────────── */
.card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.card-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #f1f5f9;
    margin-bottom: 0.2rem;
}
.card-sub {
    font-size: 0.8rem;
    color: #475569;
}

/* ── Metric row ─────────────────────────────────────── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
    margin: 1rem 0;
}
.metric-box {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}
.metric-label { font-size: 0.72rem; color: #64748b; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
.metric-value { font-size: 1.55rem; font-weight: 700; color: #f1f5f9; }
.metric-sub   { font-size: 0.7rem; color: #475569; margin-top: 2px; }

/* ── Status badges ──────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
}
.badge-green  { background: #052e16; color: #4ade80; border: 1px solid #166534; }
.badge-yellow { background: #1c1008; color: #fbbf24; border: 1px solid #92400e; }
.badge-blue   { background: #0c1a3a; color: #60a5fa; border: 1px solid #1e40af; }
.badge-gray   { background: #1e293b; color: #64748b; border: 1px solid #334155; }

/* ── Page header ────────────────────────────────────── */
.page-header { margin-bottom: 1.5rem; }
.page-title  { font-size: 1.4rem; font-weight: 700; color: #f1f5f9; }
.page-desc   { font-size: 0.85rem; color: #64748b; margin-top: 2px; }

/* ── Divider ────────────────────────────────────────── */
.divider { height: 1px; background: #1e293b; margin: 1.25rem 0; }

/* ── Step status row ────────────────────────────────── */
.step-row {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid #1e293b;
    font-size: 0.85rem;
    color: #94a3b8;
}
.step-row:last-child { border-bottom: none; }
.step-icon { font-size: 1rem; width: 24px; text-align: center; }
.step-done  { color: #4ade80; }
.step-ready { color: #60a5fa; }
.step-wait  { color: #334155; }

/* ── Hide streamlit chrome ──────────────────────────── */
#MainMenu  { visibility: hidden; }
footer     { visibility: hidden; }
header     { visibility: hidden; }
</style>
"""


def inject():
    """Call once at the top of app.py to inject all styles."""
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)
