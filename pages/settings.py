"""
pages/settings.py
==================
Settings page — target variable, train/test split, base directory.
"""

import streamlit as st
from ui.components import page_header, divider, success


def render():
    page_header("Settings", "Configure target variable and pipeline defaults")

    # ── Target variable ────────────────────────────────────────
    st.markdown("#### Target Variable")
    st.caption("The column your models will predict. Must exist in your dataset.")

    new_target = st.text_input(
        "Target column name",
        value=st.session_state.target,
        placeholder="e.g. IsTarget",
    )
    if new_target != st.session_state.target:
        if st.button("Save Target", type="primary"):
            st.session_state.target = new_target.strip()
            success(f"Target set to: {st.session_state.target}")
            st.rerun()

    divider()

    # ── Train / test split ─────────────────────────────────────
    st.markdown("#### Train / Validation Split")

    test_pct = st.slider(
        "Validation %",
        min_value=10,
        max_value=40,
        value=int(st.session_state.test_size * 100),
        step=5,
        help="Percentage of data held out for validation"
    )
    st.caption(f"Train: **{100 - test_pct}%**  ·  Validation: **{test_pct}%**")

    if test_pct / 100 != st.session_state.test_size:
        if st.button("Save Split", type="primary"):
            st.session_state.test_size = test_pct / 100
            success(f"Split set to {100-test_pct}/{test_pct}")
            st.rerun()

    divider()

    # ── Base directory ─────────────────────────────────────────
    st.markdown("#### Base Directory")
    try:
        from config import BASE_DIR
        st.code(BASE_DIR, language=None)
        st.caption("To change this, edit BASE_DIR in config/settings.py")
    except Exception as e:
        st.caption(f"Could not load BASE_DIR: {e}")

    divider()

    # ── Current session summary ────────────────────────────────
    st.markdown("#### Current Session")

    s = st.session_state
    rows = [
        ("Client",       s.client or "—"),
        ("Target",       s.target),
        ("Test split",   f"{int(s.test_size * 100)}%"),
        ("Data loaded",  f"{len(s.df):,} × {len(s.df.columns):,}" if s.df is not None else "—"),
        ("Clean data",   f"{len(s.df_clean):,} × {len(s.df_clean.columns):,}" if s.df_clean is not None else "—"),
        ("Models",       ", ".join(s.trainer.get_trained_models().keys()) if s.trainer else "—"),
        ("Winner",       s.evaluator.get_winner() if s.evaluator else "—"),
    ]

    for label, value in rows:
        col1, col2 = st.columns([1, 2])
        col1.caption(label)
        col2.markdown(f"**{value}**")
