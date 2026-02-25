"""
app.py
=======
ML Modeling Toolkit — Streamlit entry point.

Run from Leading Creation/ with:
    streamlit run app.py
"""

import streamlit as st
import os
import sys

# ── Path setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="ML Modeling Toolkit",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject styles ──────────────────────────────────────────────────────────────
from ui.styles import inject
inject()

# ── Session state init ─────────────────────────────────────────────────────────
def _init():
    defaults = {
        "page":        "home",
        "client":      None,
        "client_path": None,
        "df":          None,
        "df_clean":    None,
        "cleaner":     None,
        "selector":    None,
        "trainer":     None,
        "evaluator":   None,
        "target":      "",  # set by user on ingestion page
        "test_size":   0.30,
        "log":         [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ── Sidebar ────────────────────────────────────────────────────────────────────
from ui.sidebar import render as render_sidebar
render_sidebar()

# ── Page routing ───────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "home":
    from pages.home import render
    render()

elif page == "ingestion":
    from pages.ingestion import render
    render()

elif page == "cleaning":
    from pages.cleaning import render
    render()

elif page == "features":
    from pages.features import render
    render()

elif page == "training":
    from pages.training import render
    render()

elif page == "evaluation":
    from pages.evaluation import render
    render()

elif page == "visualizations":
    from pages.visualizations import render
    render()

elif page == "export":
    from pages.export import render
    render()

elif page == "settings":
    from pages.settings import render
    render()

elif page == "autorun":
    from pages.autorun import render
    render()

elif page == "log":
    from pages.log import render
    render()

elif page == "data_explorer":
    from pages.data_explorer import render
    render()

else:
    st.error(f"Unknown page: {page}")