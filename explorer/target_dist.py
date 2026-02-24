"""
explorer/target_dist.py
========================
Target distribution charts — responder vs non-responder breakdown.
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import pandas as pd
import numpy as np


def render(df: pd.DataFrame, target: str):
    if target not in df.columns:
        st.warning(f"Target column `{target}` not found. Check Settings.")
        return

    y = pd.to_numeric(df[target], errors='coerce').dropna()
    total     = len(y)
    if total == 0:
        st.warning("No valid values found in target column.")
        return

    n_pos     = int((y == 1).sum())
    n_neg     = int((y == 0).sum())
    resp_rate = n_pos / total * 100 if total > 0 else 0.0

    # ── Metrics ────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records",  f"{total:,}")
    col2.metric("Responders",     f"{n_pos:,}")
    col3.metric("Non-Responders", f"{n_neg:,}")
    col4.metric("Response Rate",  f"{resp_rate:.2f}%")

    if resp_rate < 1:
        st.warning(f"⚠ Very low response rate ({resp_rate:.2f}%) — "
                   "model will need to handle class imbalance.")
    elif resp_rate > 30:
        st.info(f"ℹ High response rate ({resp_rate:.2f}%) — "
                "unusually high for a lead model, worth verifying.")

    if n_pos == 0 or n_neg == 0:
        st.error("Target column has only one class — cannot build a model.")
        return

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(5, 4))
        bars = ax.bar(
            ['Non-Responder\n(0)', 'Responder\n(1)'],
            [n_neg, n_pos],
            color=['#3b82f6', '#4ade80'], edgecolor='none', width=0.5
        )
        ax.bar_label(bars, labels=[f'{n_neg:,}', f'{n_pos:,}'],
                     padding=4, fontsize=10)
        ax.set_title('Response Distribution', fontsize=12, pad=10)
        ax.set_ylabel('Count')
        ax.spines[['top', 'right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with col2:
        fig, ax = plt.subplots(figsize=(5, 4))
        non_resp_pct = 100 - resp_rate
        ax.pie(
            [float(n_neg), float(n_pos)],
            labels=[f'Non-Responder\n{non_resp_pct:.1f}%',
                    f'Responder\n{resp_rate:.1f}%'],
            colors=['#3b82f6', '#4ade80'],
            startangle=90,
            wedgeprops={'edgecolor': 'white', 'linewidth': 2}
        )
        ax.set_title('Response Rate', fontsize=12, pad=10)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    # ── Score decile breakdown if score column exists ──────────
    score_cols = [c for c in df.columns
                  if 'score' in c.lower() or 'prob' in c.lower()]
    if score_cols:
        st.markdown("**Response rate by score decile**")
        score_col = st.selectbox("Score column", score_cols, key="td_score_col")
        try:
            temp = df[[score_col, target]].dropna()
            temp = temp.copy()
            temp[target] = pd.to_numeric(temp[target], errors='coerce')
            temp['decile'] = pd.qcut(
                pd.to_numeric(temp[score_col], errors='coerce'),
                10, labels=[f'D{i}' for i in range(1, 11)]
            )
            decile_rates = temp.groupby('decile')[target].mean() * 100
            fig, ax = plt.subplots(figsize=(8, 3))
            decile_rates.plot(kind='bar', ax=ax, color='#3b82f6', edgecolor='none')
            ax.set_title('Response Rate by Score Decile')
            ax.set_ylabel('Response Rate %')
            ax.set_xlabel('')
            ax.spines[['top', 'right']].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close()
        except Exception:
            pass
