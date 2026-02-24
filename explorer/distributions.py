"""
explorer/distributions.py
==========================
Feature distribution histograms overlaid by target class.
Pick any column — see how responders vs non-responders differ.
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import pandas as pd
import numpy as np


def render(df: pd.DataFrame, target: str):
    st.markdown(
        "Pick any column to see how its distribution differs "
        "between responders and non-responders."
    )

    numeric_cols = sorted([c for c in df.select_dtypes(include=[np.number]).columns
                           if c != target])
    if not numeric_cols:
        st.warning("No numeric columns found.")
        return

    col1, col2 = st.columns([3, 1])
    with col1:
        selected = st.selectbox("Select feature", numeric_cols, key="dist_col")
    with col2:
        bins = st.slider("Bins", 10, 100, 30, key="dist_bins")

    if selected:
        _plot_distribution(df, selected, target, bins)


def _plot_distribution(df, col, target, bins):
    data = df[[col, target]].dropna()
    if len(data) == 0:
        st.warning("No data available for this column.")
        return

    pos = data[data[target] == 1][col]
    neg = data[data[target] == 0][col]

    # ── Stats row ──────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Mean (all)",        f"{data[col].mean():.2f}")
    c2.metric("Mean (responders)", f"{pos.mean():.2f}" if len(pos) > 0 else "—")
    c3.metric("Median",            f"{data[col].median():.2f}")
    c4.metric("Missing %",
              f"{df[col].isna().sum() / len(df) * 100:.1f}%")
    c5.metric("Zero %",
              f"{(data[col] == 0).sum() / len(data) * 100:.1f}%")

    # ── Histogram ──────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(9, 4))

    # Use shared bin edges
    all_vals = data[col].values
    bin_edges = np.histogram_bin_edges(all_vals, bins=bins)

    ax.hist(neg, bins=bin_edges, alpha=0.6, color='#3b82f6',
            label=f'Non-Responder (n={len(neg):,})', density=True)
    ax.hist(pos, bins=bin_edges, alpha=0.6, color='#4ade80',
            label=f'Responder (n={len(pos):,})', density=True)

    # Mean lines
    ax.axvline(neg.mean(), color='#3b82f6', linestyle='--',
               linewidth=1.5, alpha=0.8)
    ax.axvline(pos.mean(), color='#4ade80', linestyle='--',
               linewidth=1.5, alpha=0.8)

    ax.set_title(f'Distribution of `{col}` by Target', fontsize=12, pad=10)
    ax.set_xlabel(col)
    ax.set_ylabel('Density')
    ax.legend(loc='upper right', fontsize=9)
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

    # ── Separation note ────────────────────────────────────────
    if len(pos) > 0 and len(neg) > 0:
        mean_diff = abs(pos.mean() - neg.mean())
        pooled_std = np.sqrt((pos.std()**2 + neg.std()**2) / 2)
        if pooled_std > 0:
            effect = mean_diff / pooled_std
            if effect > 0.8:
                st.success(f"✓ Strong separation (Cohen's d = {effect:.2f}) "
                           "— this feature likely has good predictive power")
            elif effect > 0.4:
                st.info(f"ℹ Moderate separation (Cohen's d = {effect:.2f})")
            else:
                st.caption(f"Weak separation (Cohen's d = {effect:.2f}) "
                           "— this feature may not be a strong predictor")
