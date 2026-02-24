"""
pages/features.py
==================
Feature selection page — screener, importance with dimension reduction, collinearity.
"""

import streamlit as st
from ui.components import page_header, divider, warn


def render():
    page_header("Feature Selection", "Analyze and reduce your feature set")

    if st.session_state.df_clean is None:
        warn("Clean your data first on the Cleaning page.")
        return

    # ── Persistent confirmations ───────────────────────────────
    for msg_key in ("screener_msg", "importance_msg"):
        if st.session_state.get(msg_key):
            msg, detail = st.session_state[msg_key]
            st.success(f"✓ {msg}")
            if detail:
                st.caption(detail)
            st.session_state[msg_key] = None

    df     = st.session_state.df_clean
    client = st.session_state.client
    target = st.session_state.target

    col1, col2 = st.columns(2)
    col1.metric("Rows",     f"{df.shape[0]:,}")
    col2.metric("Features", f"{df.shape[1] - 1:,}", help="Excludes target column")

    divider()

    tab1, tab2, tab3 = st.tabs([
        "📊 Column Screener",
        "🌲 Feature Importance",
        "🔗 Collinearity",
    ])

    with tab1:
        from features.screener_ui import render_screener
        render_screener(df, target)

    with tab2:
        _render_importance(df, client, target)

    with tab3:
        _render_collinearity(df, target)

    divider()
    if st.button("▶  Proceed to Model Training", type="primary"):
        st.session_state.page = "training"
        st.rerun()


def _render_importance(df, client, target):
    """Feature importance tab with dimension reduction controls."""

    if st.button("▶  Run Feature Selection", type="primary", key="run_fs"):
        try:
            from features import FeatureSelector
            with st.spinner("Running feature selection..."):
                selector = FeatureSelector(df, client=client, target=target)
                selector.run_analysis()
                selector.save_report()
            st.session_state.selector = selector
            st.session_state.imp_drop_preview = None
            _log("Feature selection complete")
            st.rerun()
        except Exception as e:
            st.error(f"Feature selection failed: {e}")

    selector = st.session_state.selector
    if selector is None:
        st.info("Run feature selection above to see results.")
        return

    imp_df = selector.importance_df
    if imp_df is None or imp_df.empty:
        st.warning("No importance data available.")
        return

    feat_col = imp_df.columns[0]
    imp_col  = imp_df.columns[1]
    total_features = len(imp_df)

    # ── View controls ──────────────────────────────────────────
    top_n = st.slider("Show top N features", 10, min(200, total_features),
                      min(30, total_features), key="imp_view_slider")

    st.dataframe(
        imp_df.head(top_n),
        use_container_width=True,
        hide_index=True,
        height=350,
    )
    st.bar_chart(
        imp_df.head(top_n).set_index(feat_col)[imp_col]
    )

    divider()

    # ── Dimension reduction ────────────────────────────────────
    st.markdown("#### Dimension Reduction")
    st.caption(f"Currently {total_features} features — select a method to reduce")

    method = st.radio(
        "Cutoff method",
        ["Top N", "Drop Bottom %", "Pareto"],
        horizontal=True,
        key="imp_method",
    )

    keep_cols = []

    if method == "Top N":
        n = st.slider("Keep top N features", 10, total_features,
                      min(50, total_features), key="imp_topn")
        keep_cols = imp_df[feat_col].head(n).tolist()
        drop_count = total_features - n
        st.caption(f"Keeping: **{n}** features  ·  Dropping: **{drop_count}**")

    elif method == "Drop Bottom %":
        pct = st.slider("Drop bottom %", 5, 80, 30, key="imp_botpct")
        n_keep = int(total_features * (1 - pct / 100))
        keep_cols = imp_df[feat_col].head(n_keep).tolist()
        drop_count = total_features - n_keep
        st.caption(f"Keeping: **{n_keep}** features  ·  "
                   f"Dropping: **{drop_count}** ({pct}% of total)")

    elif method == "Pareto":
        pct = st.slider("Keep features explaining X% of importance",
                        50, 99, 80, key="imp_pareto")
        imp_df_copy = imp_df.copy()
        imp_df_copy['cum_pct'] = (
            imp_df_copy[imp_col].cumsum() / imp_df_copy[imp_col].sum() * 100
        )
        keep_mask = imp_df_copy['cum_pct'] <= pct
        # Always keep at least the first row
        if keep_mask.sum() == 0:
            keep_mask.iloc[0] = True
        keep_cols = imp_df_copy.loc[keep_mask, feat_col].tolist()
        drop_count = total_features - len(keep_cols)
        st.caption(f"Keeping: **{len(keep_cols)}** features explain "
                   f"**{pct}%** of importance  ·  Dropping: **{drop_count}**")

    if not keep_cols:
        return

    # ── Preview ────────────────────────────────────────────────
    all_feature_cols = [c for c in df.columns if c != target]
    drop_cols = [c for c in all_feature_cols if c not in keep_cols]

    if st.button("👁  Preview Drops", key="imp_preview"):
        st.session_state.imp_drop_preview = drop_cols
        st.rerun()

    preview = st.session_state.get("imp_drop_preview")
    if preview is not None:
        st.markdown(
            f'<div style="background:#1a0a0a;border:1px solid #7f1d1d;'
            f'border-radius:8px;padding:1rem;margin:0.5rem 0;">'
            f'<div style="color:#fca5a5;font-weight:600;margin-bottom:0.5rem;">'
            f'Will drop {len(preview)} features</div>'
            f'<div style="color:#ef4444;font-size:0.8rem;">'
            f'{", ".join(preview[:20])}'
            f'{"... +" + str(len(preview)-20) + " more" if len(preview) > 20 else ""}'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        with st.expander(f"View all {len(preview)} columns to be dropped"):
            st.write(preview)

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button(f"✓  Confirm Drop {len(preview)} Columns",
                         type="primary", key="imp_confirm"):
                _apply_importance_drops(drop_cols, df)
        with col2:
            if st.button("✗  Cancel", key="imp_cancel"):
                st.session_state.imp_drop_preview = None
                st.rerun()


def _apply_importance_drops(drop_cols: list, df):
    cleaner = st.session_state.get("cleaner")
    if cleaner is None:
        st.error("No active cleaner — go to Data Cleaning first.")
        return
    try:
        sb = cleaner.get_shape()
        # Only drop cols that still exist
        existing = [c for c in drop_cols if c in cleaner.get_columns()]
        cleaner.drop_columns(existing)
        sa = cleaner.get_shape()
        st.session_state.df_clean = cleaner.get_data()
        st.session_state.selector = None       # reset — needs rerun on new data
        st.session_state.imp_drop_preview = None
        st.session_state.importance_msg = (
            f"Dropped {len(existing)} low-importance features",
            f"Shape: {sb[0]:,} × {sb[1]:,}  →  {sa[0]:,} × {sa[1]:,}"
        )
        _log(f"Importance drop: {sb[1]} → {sa[1]} features")
        st.rerun()
    except Exception as e:
        st.error(f"Drop failed: {e}")


def _render_collinearity(df, target):
    selector = st.session_state.selector
    if selector is None:
        st.info("Run Feature Selection first (Feature Importance tab).")
        return
    try:
        pairs = selector.collinear_pairs
        if pairs is not None and not pairs.empty:
            st.caption(f"{len(pairs)} collinear pairs found")
            st.dataframe(pairs, use_container_width=True, hide_index=True)
        else:
            st.caption("No collinear pairs above threshold.")
    except Exception as e:
        st.caption(f"Collinearity data not available: {e}")


def _log(msg: str):
    import datetime
    st.session_state.log.append(
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    )
