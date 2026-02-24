"""
pages/cleaning.py
==================
Data cleaning page — drop columns/rows, save checkpoints.
"""

import streamlit as st
from ui.components import page_header, divider, warn, shape_delta


def render():
    page_header("Data Cleaning", "Drop columns and rows, save checkpoints")

    if st.session_state.df is None:
        warn("Load data first on the Ingestion page.")
        return

    _init_cleaner()
    cleaner = st.session_state.cleaner

    # ── Persistent confirmation banner ─────────────────────────
    if st.session_state.get("cleaning_msg"):
        msg, detail = st.session_state.cleaning_msg
        st.success(f"✓ {msg}")
        if detail:
            st.caption(detail)
        st.session_state.cleaning_msg = None  # clear after showing once

    # ── Shape status ───────────────────────────────────────────
    shape = cleaner.get_shape()
    orig  = len(st.session_state.df.columns)
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows",          f"{shape[0]:,}")
    col2.metric("Columns",       f"{shape[1]:,}")
    col3.metric("Original cols", f"{orig:,}",
                delta=f"{shape[1] - orig:,}")

    divider()

    # ── Tabs ───────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Drop Columns", "Drop Rows", "Checkpoints", "Change History"]
    )

    # ── Tab 1: Drop columns ────────────────────────────────────
    with tab1:
        st.markdown("**By column name**")
        all_cols     = cleaner.get_columns()
        cols_to_drop = st.multiselect(
            "Select columns to drop",
            options=all_cols,
            label_visibility="collapsed",
        )
        if st.button("Drop Selected Columns", disabled=not cols_to_drop):
            sb = cleaner.get_shape()
            cleaner.drop_columns(cols_to_drop)
            sa = cleaner.get_shape()
            removed = sb[1] - sa[1]
            _log(f"Dropped {len(cols_to_drop)} columns by name")
            _set_msg(
                f"Dropped {removed} column{'s' if removed != 1 else ''}",
                f"Shape: {sb[0]:,} × {sb[1]:,}  →  {sa[0]:,} × {sa[1]:,}"
            )
            st.rerun()

        divider()

        st.markdown("**By prefix**")
        prefix_input = st.text_input(
            "Prefixes (comma-separated)",
            placeholder="e.g.  ind_1_, member_2_, tw_",
        )
        if st.button("Drop by Prefix", disabled=not prefix_input.strip()):
            prefixes = [p.strip() for p in prefix_input.split(",") if p.strip()]
            sb = cleaner.get_shape()
            cleaner.drop_columns_by_prefix(prefixes)
            sa = cleaner.get_shape()
            removed = sb[1] - sa[1]
            _log(f"Dropped columns with prefixes: {prefixes}")
            _set_msg(
                f"Dropped {removed} column{'s' if removed != 1 else ''} matching prefixes",
                f"Prefixes: {', '.join(prefixes)}  ·  Shape: {sb[0]:,} × {sb[1]:,}  →  {sa[0]:,} × {sa[1]:,}"
            )
            st.rerun()

        divider()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**By missing % threshold**")
            missing_thresh = st.slider("Drop if missing % >", 0, 100, 50)
            if st.button("Drop High-Missing Columns"):
                sb = cleaner.get_shape()
                cleaner.drop_columns_by_missing(missing_thresh)
                sa = cleaner.get_shape()
                removed = sb[1] - sa[1]
                _log(f"Dropped columns >{missing_thresh}% missing")
                _set_msg(
                    f"Dropped {removed} high-missing column{'s' if removed != 1 else ''}",
                    f"Threshold: >{missing_thresh}% missing  ·  Shape: {sb[0]:,} × {sb[1]:,}  →  {sa[0]:,} × {sa[1]:,}"
                )
                st.rerun()

        with col2:
            st.markdown("**By low variance**")
            var_thresh = st.number_input("Variance threshold", value=0.01, step=0.001, format="%.4f")
            if st.button("Drop Low-Variance Columns"):
                sb = cleaner.get_shape()
                cleaner.drop_low_variance(var_thresh)
                sa = cleaner.get_shape()
                removed = sb[1] - sa[1]
                _log(f"Dropped low-variance columns (threshold={var_thresh})")
                _set_msg(
                    f"Dropped {removed} low-variance column{'s' if removed != 1 else ''}",
                    f"Threshold: {var_thresh}  ·  Shape: {sb[0]:,} × {sb[1]:,}  →  {sa[0]:,} × {sa[1]:,}"
                )
                st.rerun()

    # ── Tab 2: Drop rows ───────────────────────────────────────
    with tab2:
        st.markdown("**Drop rows with missing target**")
        target = st.session_state.target
        st.caption(f"Current target: `{target}`")
        if st.button("Drop Rows Missing Target"):
            sb = cleaner.get_shape()
            cleaner.drop_rows_missing_target(target)
            sa = cleaner.get_shape()
            removed = sb[0] - sa[0]
            _log(f"Dropped {removed:,} rows with missing target")
            _set_msg(
                f"Dropped {removed:,} row{'s' if removed != 1 else ''} with missing target",
                f"Shape: {sb[0]:,} × {sb[1]:,}  →  {sa[0]:,} × {sa[1]:,}"
            )
            st.rerun()

        divider()

        st.markdown("**Drop rows by condition**")
        condition = st.text_input("Condition", placeholder="e.g.  age < 0")
        if st.button("Apply Condition", disabled=not condition.strip()):
            try:
                sb = cleaner.get_shape()
                cleaner.drop_rows_by_condition(condition.strip())
                sa = cleaner.get_shape()
                removed = sb[0] - sa[0]
                _log(f"Dropped rows where: {condition}")
                _set_msg(
                    f"Dropped {removed:,} row{'s' if removed != 1 else ''} matching condition",
                    f"Condition: {condition}  ·  Shape: {sb[0]:,} × {sb[1]:,}  →  {sa[0]:,} × {sa[1]:,}"
                )
                st.rerun()
            except Exception as e:
                st.error(f"Invalid condition: {e}")

    # ── Tab 3: Checkpoints ─────────────────────────────────────
    with tab3:
        st.markdown("Save up to 3 named checkpoints you can return to later.")

        import os
        existing = {}
        for slot in ("v1", "v2", "v3"):
            full_path = os.path.join(st.session_state.client_path,
                                     "data", "versions", f"{slot}.parquet")
            existing[slot] = os.path.exists(full_path)

        for slot in ("v1", "v2", "v3"):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                st.markdown(f"**{slot}**")
            with col2:
                if existing[slot]:
                    st.caption("✅ Saved")
                else:
                    st.text_input(f"Label for {slot}",
                                  placeholder="e.g. after_tw_drop",
                                  key=f"label_{slot}",
                                  label_visibility="collapsed")
            with col3:
                if not existing[slot]:
                    if st.button(f"Save {slot}", key=f"save_{slot}"):
                        cleaner.save_version(slot)
                        _log(f"Saved checkpoint {slot}")
                        _set_msg(f"Checkpoint {slot} saved",
                                 f"Shape: {cleaner.get_shape()[0]:,} × {cleaner.get_shape()[1]:,}")
                        st.rerun()
                else:
                    if st.button(f"Load {slot}", key=f"load_{slot}"):
                        cleaner.load_version(slot)
                        st.session_state.df_clean = cleaner.get_data()
                        _log(f"Loaded checkpoint {slot}")
                        _set_msg(f"Checkpoint {slot} restored",
                                 f"Shape: {cleaner.get_shape()[0]:,} × {cleaner.get_shape()[1]:,}")
                        st.rerun()

        divider()
        if st.button("↩  Reset to Original Data"):
            cleaner.reset()
            st.session_state.df_clean = cleaner.get_data()
            _log("Reset to original data")
            _set_msg("Reset to original data",
                     f"Shape: {cleaner.get_shape()[0]:,} × {cleaner.get_shape()[1]:,}")
            st.rerun()

    # ── Tab 4: History ─────────────────────────────────────────
    with tab4:
        try:
            history = cleaner.get_history()
            if history:
                for i, entry in enumerate(reversed(history), 1):
                    st.caption(f"{i}. {entry}")
            else:
                st.caption("No changes made yet.")
        except Exception:
            st.caption("History not available.")

    divider()

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("▶  Go to Feature Selection", type="primary"):
            st.session_state.df_clean = cleaner.get_data()
            st.session_state.page = "features"
            st.rerun()


def _init_cleaner():
    if st.session_state.cleaner is None:
        from cleaning import DataCleaner
        st.session_state.df_clean = st.session_state.df.copy()
        st.session_state.cleaner  = DataCleaner(
            st.session_state.df_clean,
            client=st.session_state.client,
        )


def _set_msg(msg: str, detail: str = ""):
    """Store confirmation message in session state so it survives rerun."""
    st.session_state.cleaning_msg = (msg, detail)


def _log(msg: str):
    import datetime
    st.session_state.log.append(
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    )
