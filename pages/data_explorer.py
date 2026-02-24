"""
pages/data_explorer.py
=======================
Data Explorer — pre-model visualizations available as soon as data is loaded.
Target distribution, column contributions, feature distributions, comparisons.
"""

import streamlit as st
from ui.components import page_header, divider, warn


def render():
    page_header("Data Explorer", "Explore your data before committing to training")

    if st.session_state.df is None:
        warn("Load your data first on the Ingestion page.")
        return

    # Use clean data if available, otherwise raw
    df     = st.session_state.df_clean if st.session_state.df_clean is not None \
             else st.session_state.df
    target = st.session_state.target

    # Which dataset is being shown
    using = "cleaned data" if st.session_state.df_clean is not None else "raw data"
    st.caption(
        f"Using **{using}** — "
        f"{df.shape[0]:,} rows × {df.shape[1]:,} columns  ·  "
        f"Target: `{target}`"
    )

    divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Target Distribution",
        "📊 Column Contributions",
        "📈 Feature Distributions",
        "🔀 Compare Features",
    ])

    with tab1:
        from explorer.target_dist import render as render_target
        render_target(df, target)

    with tab2:
        from explorer.contributions import render as render_contrib
        render_contrib(df, target)

    with tab3:
        from explorer.distributions import render as render_dist
        render_dist(df, target)

    with tab4:
        from explorer.compare import render as render_compare
        render_compare(df, target)
