"""
ui/styles.py
=============
Professional light theme — clean analytics dashboard aesthetic.
Typography: DM Sans (headings) + Inter (body/data)
Palette: Deep navy (#0B1F3A) + White + Slate accents + Emerald highlights
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Root variables ──────────────────────────────────── */
:root {
    --navy:      #0B1F3A;
    --navy-mid:  #1A3A5C;
    --navy-light:#2E5F8A;
    --emerald:   #059669;
    --emerald-lt:#D1FAE5;
    --amber:     #D97706;
    --amber-lt:  #FEF3C7;
    --red:       #DC2626;
    --red-lt:    #FEE2E2;
    --blue:      #2563EB;
    --blue-lt:   #DBEAFE;
    --white:     #FFFFFF;
    --bg:        #F8FAFC;
    --bg-card:   #FFFFFF;
    --border:    #E2E8F0;
    --border-mid:#CBD5E1;
    --text-primary:   #0B1F3A;
    --text-secondary: #475569;
    --text-muted:     #94A3B8;
    --shadow-sm: 0 1px 3px rgba(11,31,58,0.06), 0 1px 2px rgba(11,31,58,0.04);
    --shadow-md: 0 4px 12px rgba(11,31,58,0.08), 0 2px 4px rgba(11,31,58,0.04);
    --shadow-lg: 0 10px 30px rgba(11,31,58,0.12), 0 4px 8px rgba(11,31,58,0.06);
    --radius:    10px;
    --radius-sm: 6px;
    --radius-lg: 14px;
}

/* ── Global ──────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'DM Sans', -apple-system, sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text-primary) !important;
}

/* ── Main content area ───────────────────────────────── */
.main .block-container {
    padding-top: 2rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 1200px !important;
    background: var(--bg) !important;
}

/* ── Sidebar ─────────────────────────────────────────── */
[data-testid="stSidebar"] {
    min-width: 250px !important;
    max-width: 250px !important;
    background: var(--navy) !important;
    border-right: none !important;
    box-shadow: 4px 0 20px rgba(11,31,58,0.15) !important;
}
[data-testid="stSidebar"] .block-container {
    padding-top: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}

/* ── Sidebar brand header ────────────────────────────── */
.sidebar-brand {
    padding: 1.5rem 1.25rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 0.5rem;
}
.sidebar-brand-name {
    font-size: 1rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.01em;
    line-height: 1.2;
}
.sidebar-brand-sub {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.4);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 2px;
}
.sidebar-client-pill {
    display: inline-block;
    margin-top: 0.6rem;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 999px;
    padding: 3px 10px;
    font-size: 0.72rem;
    color: rgba(255,255,255,0.7);
    font-family: 'DM Mono', monospace;
}

/* ── Sidebar nav section labels ──────────────────────── */
.sidebar-section {
    padding: 0.6rem 1.25rem 0.25rem;
    font-size: 0.62rem;
    font-weight: 600;
    color: rgba(255,255,255,0.3);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ── Sidebar nav buttons ─────────────────────────────── */
div[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    text-align: left !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 0.6rem 1.25rem !important;
    font-size: 0.83rem !important;
    font-weight: 400 !important;
    color: rgba(255,255,255,0.6) !important;
    transition: all 0.15s ease !important;
    margin: 0 !important;
    border-left: 3px solid transparent !important;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.06) !important;
    color: #FFFFFF !important;
    border-left-color: rgba(255,255,255,0.2) !important;
}
div[data-testid="stSidebar"] .stButton > button[data-active="true"],
div[data-testid="stSidebar"] .stButton > button:focus {
    background: rgba(5,150,105,0.15) !important;
    color: #FFFFFF !important;
    border-left-color: var(--emerald) !important;
    font-weight: 500 !important;
}

/* ── Sidebar progress bar ────────────────────────────── */
.sidebar-progress {
    padding: 1rem 1.25rem;
    border-top: 1px solid rgba(255,255,255,0.08);
    margin-top: auto;
}
.sidebar-progress-label {
    font-size: 0.68rem;
    color: rgba(255,255,255,0.35);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
}
.sidebar-progress-bar-bg {
    height: 4px;
    background: rgba(255,255,255,0.1);
    border-radius: 999px;
    overflow: hidden;
}
.sidebar-progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--emerald), #10B981);
    border-radius: 999px;
    transition: width 0.4s ease;
}
.sidebar-progress-steps {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.4);
    margin-top: 0.4rem;
    text-align: right;
}

/* ── Page header ─────────────────────────────────────── */
.page-header {
    margin-bottom: 1.75rem;
    padding-bottom: 1.25rem;
    border-bottom: 2px solid var(--border);
}
.page-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--navy);
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.page-desc {
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-top: 0.3rem;
    font-weight: 400;
}

/* ── Metric cards ────────────────────────────────────── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1.25rem 0;
}
.metric-box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1.25rem;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s ease;
    position: relative;
    overflow: hidden;
}
.metric-box::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--navy), var(--navy-light));
    opacity: 0;
    transition: opacity 0.2s;
}
.metric-box:hover { box-shadow: var(--shadow-md); }
.metric-box:hover::before { opacity: 1; }
.metric-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.4rem;
}
.metric-value {
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--navy);
    letter-spacing: -0.02em;
    line-height: 1;
}
.metric-sub {
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 0.3rem;
}
.metric-delta-up   { color: var(--emerald); font-weight: 600; font-size: 0.75rem; }
.metric-delta-down { color: var(--red);     font-weight: 600; font-size: 0.75rem; }

/* ── Cards ───────────────────────────────────────────── */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1rem;
}
.card-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--navy);
    margin-bottom: 0.25rem;
}
.card-sub {
    font-size: 0.8rem;
    color: var(--text-muted);
}

/* ── Winner banner ───────────────────────────────────── */
.winner-banner {
    background: linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 100%);
    border-radius: var(--radius-lg);
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-lg);
    color: white;
    position: relative;
    overflow: hidden;
}
.winner-banner::after {
    content: '🏆';
    position: absolute;
    right: 1.5rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 3rem;
    opacity: 0.15;
}
.winner-label {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: rgba(255,255,255,0.5);
    margin-bottom: 0.3rem;
}
.winner-name {
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: white;
}
.winner-metrics {
    display: flex;
    gap: 2rem;
    margin-top: 0.75rem;
}
.winner-metric-item { display: flex; flex-direction: column; }
.winner-metric-val  {
    font-size: 1.2rem;
    font-weight: 700;
    color: #4ADE80;
    font-family: 'DM Mono', monospace;
}
.winner-metric-lbl  { font-size: 0.68rem; color: rgba(255,255,255,0.45); margin-top: 1px; }

/* ── Status badges ───────────────────────────────────── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.badge-green  { background: var(--emerald-lt); color: #065F46; border: 1px solid #A7F3D0; }
.badge-yellow { background: var(--amber-lt);   color: #92400E; border: 1px solid #FDE68A; }
.badge-blue   { background: var(--blue-lt);    color: #1E40AF; border: 1px solid #BFDBFE; }
.badge-red    { background: var(--red-lt);     color: #991B1B; border: 1px solid #FECACA; }
.badge-gray   { background: #F1F5F9;           color: #475569; border: 1px solid #E2E8F0; }
.badge-navy   { background: var(--navy);       color: white;   border: none; }

/* ── Alerts ──────────────────────────────────────────── */
.alert {
    padding: 0.85rem 1.1rem;
    border-radius: var(--radius-sm);
    font-size: 0.85rem;
    margin: 0.75rem 0;
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
}
.alert-success {
    background: var(--emerald-lt);
    border: 1px solid #A7F3D0;
    color: #065F46;
}
.alert-warning {
    background: var(--amber-lt);
    border: 1px solid #FDE68A;
    color: #92400E;
}
.alert-error {
    background: var(--red-lt);
    border: 1px solid #FECACA;
    color: #991B1B;
}
.alert-info {
    background: var(--blue-lt);
    border: 1px solid #BFDBFE;
    color: #1E40AF;
}

/* ── Divider ─────────────────────────────────────────── */
.divider {
    height: 1px;
    background: var(--border);
    margin: 1.5rem 0;
}

/* ── Section heading ─────────────────────────────────── */
.section-heading {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--navy);
    margin: 1.25rem 0 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-heading::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
    margin-left: 0.5rem;
}

/* ── Step status ─────────────────────────────────────── */
.step-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.85rem;
    color: var(--text-secondary);
}
.step-row:last-child { border-bottom: none; }
.step-icon { font-size: 1rem; width: 24px; text-align: center; }
.step-done  { color: var(--emerald); font-weight: 500; }
.step-ready { color: var(--blue); }
.step-wait  { color: var(--text-muted); }

/* ── Table overrides ─────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
}

/* ── Tab overrides ───────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 0 !important;
    border-bottom: 2px solid var(--border) !important;
    background: transparent !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    padding: 0.6rem 1.1rem !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -2px !important;
    background: transparent !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--navy) !important;
    border-bottom-color: var(--navy) !important;
    font-weight: 600 !important;
}

/* ── Button overrides ────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: var(--navy) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1.25rem !important;
    box-shadow: 0 2px 6px rgba(11,31,58,0.2) !important;
    transition: all 0.15s !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--navy-mid) !important;
    box-shadow: 0 4px 12px rgba(11,31,58,0.3) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: white !important;
    color: var(--navy) !important;
    border: 1px solid var(--border-mid) !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: var(--navy) !important;
    background: var(--bg) !important;
}

/* ── Input overrides ─────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] select,
[data-testid="stNumberInput"] input {
    border: 1px solid var(--border-mid) !important;
    border-radius: var(--radius-sm) !important;
    background: white !important;
    color: var(--text-primary) !important;
    font-size: 0.875rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--navy) !important;
    box-shadow: 0 0 0 3px rgba(11,31,58,0.08) !important;
}

/* ── Slider ──────────────────────────────────────────── */
[data-testid="stSlider"] [data-testid="stTickBar"] { color: var(--text-muted) !important; }
[data-testid="stSlider"] > div > div > div > div {
    background: var(--navy) !important;
}

/* ── Metric (native Streamlit) ───────────────────────── */
[data-testid="metric-container"] {
    background: white !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1rem 1.1rem !important;
    box-shadow: var(--shadow-sm) !important;
}
[data-testid="metric-container"] label {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: var(--text-muted) !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--navy) !important;
    letter-spacing: -0.02em !important;
}

/* ── Expander ────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    background: white !important;
}

/* ── Progress bar ────────────────────────────────────── */
[data-testid="stProgress"] > div > div {
    background: var(--navy) !important;
}

/* ── Success / warning / error / info boxes ──────────── */
[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    border: none !important;
    font-size: 0.85rem !important;
}

/* ── Hide streamlit chrome ───────────────────────────── */
#MainMenu  { visibility: hidden; }
footer     { visibility: hidden; }
header     { visibility: hidden; }

/* ── Scrollbar ───────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb {
    background: var(--border-mid);
    border-radius: 999px;
}
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }
</style>
"""


def inject():
    """Call once at the top of app.py to inject all styles."""
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)
