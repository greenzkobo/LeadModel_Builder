"""
ui/styles.py
=============
Dark professional theme — deep navy background, light text, emerald accents.
Clean and business-like without being harsh.
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&display=swap');

/* ── Variables ───────────────────────────────────────── */
:root {
    --bg:         #0D1117;
    --bg-card:    #161B22;
    --bg-hover:   #1C2433;
    --border:     #30363D;
    --border-mid: #3D444D;
    --ink:        #E6EDF3;
    --ink-mid:    #B0BABF;
    --muted:      #7D8590;
    --emerald:    #3FB950;
    --emerald-dim:#1A3A2A;
    --blue:       #58A6FF;
    --amber:      #E3B341;
    --red:        #F85149;
    --navy:       #1F3A5F;
    --shadow:     0 1px 4px rgba(0,0,0,0.3);
    --shadow-md:  0 4px 16px rgba(0,0,0,0.4);
}

/* ── Global ──────────────────────────────────────────── */
html, body, .stApp, [class*="css"] {
    font-family: 'Sora', system-ui, sans-serif !important;
    background: var(--bg) !important;
    color: var(--ink) !important;
}

/* ── Main content ────────────────────────────────────── */
.main .block-container {
    padding: 2rem 2.5rem 3rem !important;
    max-width: 1150px !important;
    background: var(--bg) !important;
}

/* ── Sidebar ─────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0A0F16 !important;
    min-width: 240px !important;
    max-width: 240px !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .block-container {
    padding: 0 !important;
}

/* ── Sidebar buttons ─────────────────────────────────── */
[data-testid="stSidebar"] button {
    width: 100% !important;
    text-align: left !important;
    background: transparent !important;
    border: none !important;
    border-left: 3px solid transparent !important;
    border-radius: 0 !important;
    padding: 0.55rem 1.1rem !important;
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    color: var(--muted) !important;
    transition: all 0.15s !important;
    margin: 0 !important;
    font-family: 'Sora', system-ui, sans-serif !important;
}
[data-testid="stSidebar"] button:hover {
    background: var(--bg-hover) !important;
    color: var(--ink) !important;
    border-left-color: var(--border-mid) !important;
}
[data-testid="stSidebar"] button:focus {
    background: var(--emerald-dim) !important;
    color: var(--emerald) !important;
    border-left-color: var(--emerald) !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    outline: none !important;
}

/* ── Page headers ────────────────────────────────────── */
.page-header {
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}
.page-title {
    font-size: 1.55rem;
    font-weight: 700;
    color: var(--ink);
    letter-spacing: -0.025em;
    line-height: 1.2;
}
.page-desc {
    font-size: 0.85rem;
    color: var(--muted);
    margin-top: 0.25rem;
}

/* ── Streamlit native elements ───────────────────────── */
p, span, label, div {
    color: var(--ink) !important;
}

/* ── Native metrics ──────────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1rem 1.15rem !important;
    box-shadow: var(--shadow) !important;
}
[data-testid="stMetricLabel"] p {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: var(--muted) !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--ink) !important;
    letter-spacing: -0.02em !important;
}

/* ── Buttons ─────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: var(--navy) !important;
    color: var(--ink) !important;
    border: 1px solid #2D5A8E !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
    padding: 0.5rem 1.3rem !important;
    box-shadow: var(--shadow) !important;
    transition: all 0.15s !important;
    font-family: 'Sora', system-ui, sans-serif !important;
}
.stButton > button[kind="primary"]:hover {
    background: #264D7E !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--bg-card) !important;
    color: var(--ink-mid) !important;
    border: 1px solid var(--border-mid) !important;
    border-radius: 7px !important;
    font-weight: 500 !important;
    font-size: 0.84rem !important;
    font-family: 'Sora', system-ui, sans-serif !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: var(--blue) !important;
    color: var(--ink) !important;
}

/* ── Tabs ────────────────────────────────────────────── */
[data-baseweb="tab-list"] {
    border-bottom: 1px solid var(--border) !important;
    background: transparent !important;
    gap: 0 !important;
}
[data-baseweb="tab"] {
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: var(--muted) !important;
    padding: 0.55rem 1rem !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1px !important;
    background: transparent !important;
    font-family: 'Sora', system-ui, sans-serif !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    color: var(--ink) !important;
    border-bottom-color: var(--blue) !important;
    font-weight: 600 !important;
}

/* ── Inputs ──────────────────────────────────────────── */
input, textarea, [data-baseweb="select"] > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-mid) !important;
    border-radius: 7px !important;
    color: var(--ink) !important;
    font-family: 'Sora', system-ui, sans-serif !important;
}
input:focus, textarea:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(88,166,255,0.1) !important;
}

/* ── Selectbox dropdown ──────────────────────────────── */
[data-baseweb="popover"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
[data-baseweb="menu"] {
    background: var(--bg-card) !important;
}
[role="option"] {
    background: var(--bg-card) !important;
    color: var(--ink) !important;
}
[role="option"]:hover {
    background: var(--bg-hover) !important;
}

/* ── Dataframe ───────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* ── Expander ────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    background: var(--bg-card) !important;
}

/* ── Alerts ──────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-size: 0.85rem !important;
}

/* ── Progress bar ────────────────────────────────────── */
[data-testid="stProgress"] > div > div > div > div {
    background: var(--emerald) !important;
}

/* ── Custom components ───────────────────────────────── */
.divider { height: 1px; background: var(--border); margin: 1.25rem 0; }

.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.35rem 1.5rem;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
}
.card-title { font-size: 0.93rem; font-weight: 600; color: var(--ink); }
.card-sub   { font-size: 0.8rem; color: var(--muted); }

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.9rem;
    margin: 1.1rem 0;
}
.metric-box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.15rem;
    box-shadow: var(--shadow);
}
.metric-label {
    font-size: 0.67rem;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.35rem;
}
.metric-value {
    font-size: 1.55rem;
    font-weight: 700;
    color: var(--ink);
    letter-spacing: -0.02em;
}
.metric-sub { font-size: 0.7rem; color: var(--muted); margin-top: 0.2rem; }

.winner-banner {
    background: linear-gradient(135deg, #0D1F35 0%, #1F3A5F 100%);
    border: 1px solid #2D5A8E;
    border-radius: 12px;
    padding: 1.4rem 1.75rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-md);
}
.winner-label {
    font-size: 0.67rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin-bottom: 0.25rem;
}
.winner-name {
    font-size: 1.45rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--ink);
}
.winner-metrics { display: flex; gap: 2rem; margin-top: 0.7rem; }
.winner-metric-item { display: flex; flex-direction: column; }
.winner-metric-val  { font-size: 1.15rem; font-weight: 700; color: var(--emerald); }
.winner-metric-lbl  { font-size: 0.67rem; color: var(--muted); margin-top: 2px; }

.badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 9px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
}
.badge-green  { background: #0A2A14; color: var(--emerald); border: 1px solid #1A5C2A; }
.badge-yellow { background: #2A1E00; color: var(--amber);   border: 1px solid #5C4200; }
.badge-blue   { background: #0A1E3A; color: var(--blue);    border: 1px solid #1A3A6E; }
.badge-red    { background: #2A0A0A; color: var(--red);     border: 1px solid #5C1A1A; }
.badge-gray   { background: var(--bg-hover); color: var(--muted); border: 1px solid var(--border); }

.alert {
    padding: 0.8rem 1rem;
    border-radius: 8px;
    font-size: 0.84rem;
    margin: 0.6rem 0;
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
}
.alert-success { background: #0A2A14; border: 1px solid #1A5C2A; color: #4ADE80; }
.alert-warning { background: #2A1E00; border: 1px solid #5C4200; color: #FCD34D; }
.alert-error   { background: #2A0A0A; border: 1px solid #5C1A1A; color: #FCA5A5; }
.alert-info    { background: #0A1E3A; border: 1px solid #1A3A6E; color: #93C5FD; }

.page-header { margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border); }
.page-title  { font-size: 1.55rem; font-weight: 700; color: var(--ink); letter-spacing: -0.025em; }
.page-desc   { font-size: 0.85rem; color: var(--muted); margin-top: 0.25rem; }

.section-heading {
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--ink-mid);
    margin: 1.25rem 0 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.step-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.55rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.84rem;
    color: var(--ink-mid);
}
.step-row:last-child { border-bottom: none; }
.step-done  { color: var(--emerald); font-weight: 500; }
.step-ready { color: var(--blue); }
.step-wait  { color: var(--muted); }

/* ── Scrollbar ───────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border-mid); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }

/* ── Hide Streamlit chrome ───────────────────────────── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
</style>
"""


def inject():
    """Call once at app startup to inject all styles."""
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)
