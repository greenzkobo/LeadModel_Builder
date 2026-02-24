"""
explorer/compare.py
====================
Compare multiple features side by side.
Pick 2-5 columns — see their distributions and stats together.
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import pandas as pd
import numpy as np


def render(df: pd.DataFrame, target: str):
    st.markdown(
        "Compare 2–5 features side by side. "
        "Useful for spotting redundant or correlated columns before training."
    )

    numeric_cols = sorted([c for c in df.select_dtypes(include=[np.number]).columns
                           if c != target])
    if not numeric_cols:
        st.warning("No numeric columns found.")
        return

    selected = st.multiselect(
        "Select 2–5 features to compare",
        options=numeric_cols,
        max_selections=5,
        key="compare_cols",
        placeholder="Pick columns...",
    )

    if len(selected) < 2:
        st.info("Select at least 2 features to compare.")
        return

    _show_stats_table(df, selected, target)
    st.markdown("<br>", unsafe_allow_html=True)
    _show_side_by_side(df, selected, target)


def _show_stats_table(df, cols, target):
    """Summary stats table for selected columns."""
    st.markdown("**Summary Statistics**")
    rows = []
    for col in cols:
        data  = df[col].dropna()
        pos   = df[df[target] == 1][col].dropna()
        neg   = df[df[target] == 0][col].dropna()
        rows.append({
            'Feature':         col,
            'Mean (all)':      round(data.mean(), 3),
            'Mean (resp)':     round(pos.mean(), 3) if len(pos) > 0 else None,
            'Mean (non-resp)': round(neg.mean(), 3) if len(neg) > 0 else None,
            'Std Dev':         round(data.std(), 3),
            'Missing %':       round(df[col].isna().sum() / len(df) * 100, 1),
            'Zero %':          round((data == 0).sum() / len(data) * 100, 1),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _show_side_by_side(df, cols, target):
    """Side by side histograms."""
    st.markdown("**Distributions by Target**")

    n     = len(cols)
    ncols = min(n, 3)
    nrows = (n + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols,
                              figsize=(5 * ncols, 4 * nrows),
                              squeeze=False)

    colors = ['#3b82f6', '#4ade80', '#f59e0b', '#a78bfa', '#f87171']

    for i, col in enumerate(cols):
        row, c = divmod(i, ncols)
        ax = axes[row][c]

        data = df[[col, target]].dropna()
        pos  = data[data[target] == 1][col]
        neg  = data[data[target] == 0][col]

        bin_edges = np.histogram_bin_edges(data[col].values, bins=30)
        ax.hist(neg, bins=bin_edges, alpha=0.6,
                color='#3b82f6', label='Non-Resp', density=True)
        ax.hist(pos, bins=bin_edges, alpha=0.6,
                color='#4ade80', label='Resp', density=True)
        ax.axvline(neg.mean(), color='#3b82f6', linestyle='--',
                   linewidth=1.2, alpha=0.8)
        ax.axvline(pos.mean(), color='#4ade80', linestyle='--',
                   linewidth=1.2, alpha=0.8)
        ax.set_title(col, fontsize=10)
        ax.spines[['top', 'right']].set_visible(False)
        ax.legend(fontsize=7)

    # Hide unused subplots
    for i in range(len(cols), nrows * ncols):
        row, c = divmod(i, ncols)
        axes[row][c].set_visible(False)

    plt.suptitle('Feature Distributions by Target Class',
                 fontsize=12, y=1.02)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()
