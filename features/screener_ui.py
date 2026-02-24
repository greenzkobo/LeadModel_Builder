"""
features/screener_ui.py
========================
Streamlit UI for the Column Screener tab.
Calls screener.py for logic, displays table + suggestions, handles confirm.
"""

import streamlit as st
import pandas as pd
from ui.components import divider


def render_screener(df: pd.DataFrame, target: str):
    """Render the full column screener tab."""

    st.markdown("Score every feature across 4 signals and get drop suggestions.")

    # ── Config ────────────────────────────────────────────────
    with st.expander("Thresholds", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            p_thresh = st.slider("P-value cutoff", 0.01, 0.20, 0.05, 0.01,
                                 help="p > threshold = weak predictor")
        with col2:
            imp_pctile = st.slider("Importance percentile", 5, 40, 20, 5,
                                   help="Bottom X% = low importance")
        with col3:
            coll_thresh = st.slider("Collinearity threshold", 0.70, 0.99, 0.85, 0.05,
                                    help="r > threshold = collinear")
        with col4:
            var_pctile = st.slider("Variance percentile", 1, 20, 5, 1,
                                   help="Bottom X% = low variance")

    if st.button("▶  Run Column Screener", type="primary"):
        _run_screener(df, target, p_thresh, imp_pctile, coll_thresh, var_pctile)

    # ── Results ────────────────────────────────────────────────
    scored = st.session_state.get("screener_df")
    if scored is None:
        st.info("Run the screener above to see results.")
        return

    divider()
    _show_summary(scored)
    divider()
    _show_table(scored)
    divider()
    _show_confirm(scored, df)


def _run_screener(df, target, p_thresh, imp_pctile, coll_thresh, var_pctile):
    """Run the scoring engine and store results."""
    try:
        from features.screener import score_features
        # Override module-level thresholds with user values
        import features.screener as sc
        sc.P_VALUE_THRESH      = p_thresh
        sc.IMPORTANCE_PCTILE   = imp_pctile
        sc.COLLINEARITY_THRESH = coll_thresh
        sc.VARIANCE_PCTILE     = var_pctile

        with st.spinner("Scoring features — running quick Random Forest sample..."):
            scored = score_features(df, target)

        st.session_state.screener_df = scored
        st.rerun()
    except Exception as e:
        st.error(f"Screener failed: {e}")
        import traceback
        st.code(traceback.format_exc())


def _show_summary(scored: pd.DataFrame):
    """Show drop/review/keep counts."""
    drops   = (scored['Suggestion'] == '🔴 Drop').sum()
    reviews = (scored['Suggestion'] == '🟡 Review').sum()
    keeps   = (scored['Suggestion'] == '✅ Keep').sum()
    cats    = (scored['Suggestion'] == '⬜ Categorical').sum()
    total   = len(scored)

    st.markdown("#### Screening Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔴 Drop",     drops,   help="Failed 2+ checks")
    col2.metric("🟡 Review",   reviews, help="Failed 1 check")
    col3.metric("✅ Keep",     keeps,   help="Passed all checks")
    col4.metric("Total",       total)

    if drops > 0:
        st.markdown(
            f'<div style="background:#1a0a0a;border:1px solid #7f1d1d;border-radius:8px;'
            f'padding:0.75rem 1rem;margin-top:0.5rem;font-size:0.85rem;color:#fca5a5;">'
            f'Suggested drops will reduce from <b>{total}</b> to '
            f'<b>{total - drops}</b> features '
            f'({round(drops/total*100)}% reduction)</div>',
            unsafe_allow_html=True,
        )


def _show_table(scored: pd.DataFrame):
    """Show the full scored feature table with filters."""
    st.markdown("#### Feature Scores")

    filter_col1, filter_col2 = st.columns([2, 1])
    with filter_col1:
        show_filter = st.multiselect(
            "Filter by suggestion",
            ["🔴 Drop", "🟡 Review", "✅ Keep", "⬜ Categorical"],
            default=["🔴 Drop", "🟡 Review", "✅ Keep", "⬜ Categorical"],
            label_visibility="collapsed",
        )
    with filter_col2:
        search = st.text_input("Search feature name", placeholder="e.g. age",
                               label_visibility="collapsed")

    filtered = scored[scored['Suggestion'].isin(show_filter)]
    if search:
        filtered = filtered[filtered['Feature'].str.contains(search, case=False, na=False)]

    # Format for display
    display = filtered[[
        'Feature', 'Suggestion', 'P_Value', 'Importance',
        'Max_Collinearity', 'Correlated_With', 'Variance',
        'Missing_Pct', 'Zero_Pct', 'Reason'
    ]].copy()

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        height=400,
        column_config={
            'P_Value':          st.column_config.NumberColumn(format="%.4f"),
            'Importance':       st.column_config.NumberColumn(format="%.5f"),
            'Max_Collinearity': st.column_config.NumberColumn(format="%.3f"),
            'Variance':         st.column_config.NumberColumn(format="%.5f"),
            'Missing_Pct':      st.column_config.NumberColumn(format="%.1f%%"),
            'Zero_Pct':         st.column_config.NumberColumn(format="%.1f%%"),
        }
    )
    st.caption(f"Showing {len(filtered):,} of {len(scored):,} features")


def _show_confirm(scored: pd.DataFrame, df: pd.DataFrame):
    """Confirm drop section — apply suggestions or custom select."""
    from features.screener import get_drop_candidates

    suggested_drops = get_drop_candidates(scored)

    st.markdown("#### Apply Drops")

    if not suggested_drops:
        st.success("No columns suggested for dropping — your feature set looks clean!")
        return

    # Pre-populate multiselect with suggested drops
    all_features = [c for c in df.columns
                    if c != st.session_state.get('target', 'IsTarget')]

    confirmed_drops = st.multiselect(
        f"Columns to drop ({len(suggested_drops)} suggested — add or remove as needed)",
        options=all_features,
        default=suggested_drops,
        key="screener_confirmed_drops",
    )

    if not confirmed_drops:
        st.caption("No columns selected to drop.")
        return

    st.markdown(
        f'<div style="font-size:0.82rem;color:#64748b;margin-bottom:0.5rem;">'
        f'Will drop <b>{len(confirmed_drops)}</b> columns  ·  '
        f'Remaining: <b>{len(df.columns) - 1 - len(confirmed_drops)}</b> features</div>',
        unsafe_allow_html=True,
    )

    if st.button(f"✓  Apply — Drop {len(confirmed_drops)} Columns", type="primary"):
        _apply_drops(confirmed_drops)


def _apply_drops(cols_to_drop: list):
    """Apply confirmed drops to the cleaner."""
    cleaner = st.session_state.get('cleaner')
    if cleaner is None:
        st.error("No active cleaner — go to Data Cleaning first.")
        return

    try:
        sb = cleaner.get_shape()
        cleaner.drop_columns(cols_to_drop)
        sa = cleaner.get_shape()
        st.session_state.df_clean = cleaner.get_data()

        import datetime
        st.session_state.log.append(
            f"[{datetime.datetime.now().strftime('%H:%M:%S')}] "
            f"Screener dropped {len(cols_to_drop)} columns — "
            f"{sb[1]:,} → {sa[1]:,}"
        )
        st.session_state.screener_msg = (
            f"Dropped {len(cols_to_drop)} columns via screener",
            f"Shape: {sb[0]:,} × {sb[1]:,}  →  {sa[0]:,} × {sa[1]:,}"
        )
        st.session_state.screener_df = None  # clear so screener reruns fresh
        st.rerun()

    except Exception as e:
        st.error(f"Drop failed: {e}")
