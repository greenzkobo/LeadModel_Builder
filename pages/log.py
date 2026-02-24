"""
pages/log.py
=============
Activity log viewer — shows all actions taken this session.
"""

import streamlit as st
from ui.components import page_header, divider


def render():
    page_header("Activity Log", "Everything that happened this session")

    log = st.session_state.get("log", [])

    if not log:
        st.markdown(
            '<div style="text-align:center;padding:3rem;color:#475569;">'
            '<div style="font-size:2rem;margin-bottom:0.5rem;">📋</div>'
            '<div>No activity yet this session</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Clear Log"):
            st.session_state.log = []
            st.rerun()

    divider()

    for entry in reversed(log):
        st.markdown(
            f'<div style="font-family:monospace;font-size:0.8rem;'
            f'color:#94a3b8;padding:3px 0;border-bottom:1px solid #1e293b;">'
            f'{entry}</div>',
            unsafe_allow_html=True,
        )
