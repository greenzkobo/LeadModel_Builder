"""
pages/home.py
==============
Home page — client selection, session status, quick actions.
"""

import streamlit as st
from ui.components import page_header, divider, success, warn, step_status


def render():
    page_header("Home", "Select a client and manage your session")

    # ── Client selection ───────────────────────────────────────
    st.markdown("#### Client")

    try:
        from config import list_clients, create_folder_structure, get_paths
        clients = list_clients()
    except Exception as e:
        st.error(f"Could not load config: {e}")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        if clients:
            options = ["— select —"] + clients + ["➕ Create new client"]
            current_idx = 0
            if st.session_state.client in clients:
                current_idx = clients.index(st.session_state.client) + 1

            choice = st.selectbox(
                "Existing clients",
                options,
                index=current_idx,
                label_visibility="collapsed",
            )

            if choice == "➕ Create new client":
                new_name = st.text_input("New client name", placeholder="e.g. HISC_TEST")
                if st.button("Create", type="primary"):
                    if new_name.strip():
                        create_folder_structure(new_name.strip())
                        _set_client(new_name.strip(), get_paths(new_name.strip())['client'])
                        success(f"Created and selected: {new_name}")
                        st.rerun()
                    else:
                        warn("Please enter a client name.")

            elif choice != "— select —":
                if choice != st.session_state.client:
                    _set_client(choice, get_paths(choice)['client'])
                    st.rerun()
        else:
            st.info("No clients found. Create one below.")
            new_name = st.text_input("New client name", placeholder="e.g. HISC_TEST")
            if st.button("Create Client", type="primary"):
                if new_name.strip():
                    create_folder_structure(new_name.strip())
                    _set_client(new_name.strip(), get_paths(new_name.strip())['client'])
                    success(f"Created: {new_name}")
                    st.rerun()

    with col2:
        if st.session_state.client:
            st.markdown(
                f'<div style="background:#052e16;border:1px solid #166534;border-radius:8px;'
                f'padding:0.75rem 1rem;margin-top:0.5rem;">'
                f'<div style="font-size:0.7rem;color:#4ade80;text-transform:uppercase;'
                f'letter-spacing:0.05em;">Active</div>'
                f'<div style="font-size:1rem;font-weight:600;color:#f1f5f9;margin-top:2px;">'
                f'{st.session_state.client}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    divider()

    # ── Session overview ───────────────────────────────────────
    if not st.session_state.client:
        st.markdown(
            '<div style="text-align:center;padding:3rem;color:#475569;">'
            '<div style="font-size:2rem;margin-bottom:0.5rem;">👆</div>'
            '<div>Select a client above to get started</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown("#### Session Status")

    s = st.session_state
    pipeline_steps = [
        {"label": "Data Ingestion",   "status": "done" if s.df is not None else "ready"},
        {"label": "Data Cleaning",    "status": "done" if s.df_clean is not None else ("ready" if s.df is not None else "wait")},
        {"label": "Feature Selection","status": "done" if s.selector is not None else ("ready" if s.df_clean is not None else "wait")},
        {"label": "Model Training",   "status": "done" if s.trainer is not None else ("ready" if s.selector is not None else "wait")},
        {"label": "Evaluation",       "status": "done" if s.evaluator is not None else ("ready" if s.trainer is not None else "wait")},
        {"label": "Export",           "status": "ready" if s.evaluator is not None else "wait"},
    ]
    step_status(pipeline_steps)

    divider()

    # ── Quick actions ──────────────────────────────────────────
    st.markdown("#### Quick Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🚀  Auto-Run Pipeline", use_container_width=True, type="primary"):
            st.session_state.page = "autorun"
            st.rerun()

    with col2:
        if st.button("📂  Load Data", use_container_width=True):
            st.session_state.page = "ingestion"
            st.rerun()

    with col3:
        if st.session_state.evaluator:
            if st.button("📤  Export Winner", use_container_width=True):
                st.session_state.page = "export"
                st.rerun()
        else:
            st.button("📤  Export Winner", use_container_width=True, disabled=True)

    # ── Activity log preview ───────────────────────────────────
    if st.session_state.log:
        divider()
        st.markdown("#### Recent Activity")
        for entry in reversed(st.session_state.log[-5:]):
            st.caption(entry)


def _set_client(name: str, path: str):
    """Set client and reset all data state."""
    st.session_state.client      = name
    st.session_state.client_path = path
    st.session_state.df          = None
    st.session_state.df_clean    = None
    st.session_state.cleaner     = None
    st.session_state.selector    = None
    st.session_state.trainer     = None
    st.session_state.evaluator   = None
    st.session_state.log         = []
