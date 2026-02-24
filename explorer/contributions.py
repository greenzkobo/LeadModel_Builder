"""
explorer/contributions.py
==========================
Column contributions — quick importance estimate before full training.
Uses a small Random Forest sample so it runs in seconds not minutes.
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import pandas as pd
import numpy as np


SAMPLE_SIZE = 20_000


def render(df: pd.DataFrame, target: str):
    st.markdown(
        "Quick importance estimate using a small Random Forest sample. "
        "Runs in seconds — gives you signal before committing to full training."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        top_n = st.slider("Top N features", 10, 50, 20, key="contrib_topn")
    with col2:
        sample_n = st.slider("Sample size", 5_000, 50_000, SAMPLE_SIZE,
                             5_000, key="contrib_sample",
                             help="Larger = more accurate, slower")
    with col3:
        model_type = st.selectbox("Algorithm", ["Random Forest", "XGBoost"],
                                  key="contrib_model")

    if st.button("▶  Run Contribution Analysis", type="primary", key="run_contrib"):
        _run(df, target, top_n, sample_n, model_type)

    result = st.session_state.get("contrib_df")
    if result is None:
        st.info("Run the analysis above to see column contributions.")
        return

    _show_chart(result, top_n, model_type)
    _show_table(result, top_n)


def _run(df, target, top_n, sample_n, model_type):
    try:
        numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns
                        if c != target]
        if not numeric_cols:
            st.error("No numeric columns found.")
            return

        with st.spinner(f"Running quick {model_type} on {sample_n:,} rows..."):
            sample = df[numeric_cols + [target]].dropna().sample(
                min(sample_n, len(df)), random_state=42
            )
            X = sample[numeric_cols].fillna(0)
            y = sample[target]

            if model_type == "Random Forest":
                from sklearn.ensemble import RandomForestClassifier
                mdl = RandomForestClassifier(n_estimators=50, max_depth=8,
                                             random_state=42, n_jobs=-1)
            else:
                from xgboost import XGBClassifier
                mdl = XGBClassifier(n_estimators=50, max_depth=6,
                                    random_state=42, eval_metric='logloss',
                                    verbosity=0)

            mdl.fit(X, y)
            importances = mdl.feature_importances_

        result = pd.DataFrame({
            'Feature':    numeric_cols,
            'Importance': importances,
        }).sort_values('Importance', ascending=False).reset_index(drop=True)

        result['Rank']    = result.index + 1
        result['Pct']     = (result['Importance'] / result['Importance'].sum() * 100).round(2)
        result['Cum_Pct'] = result['Pct'].cumsum().round(2)

        st.session_state.contrib_df = result
        st.rerun()

    except Exception as e:
        st.error(f"Contribution analysis failed: {e}")
        import traceback
        st.code(traceback.format_exc())


def _show_chart(result: pd.DataFrame, top_n: int, model_type: str):
    top = result.head(top_n)

    fig, ax = plt.subplots(figsize=(8, max(5, top_n * 0.35)))
    bars = ax.barh(top['Feature'][::-1], top['Importance'][::-1],
                   color='#3b82f6', edgecolor='none')
    ax.set_xlabel('Importance Score')
    ax.set_title(f'Top {top_n} Column Contributions — {model_type}', pad=12)
    ax.spines[['top', 'right']].set_visible(False)

    # Pareto line — cumulative %
    ax2 = ax.twiny()
    cum = top['Cum_Pct'].values[::-1]
    ax2.plot(cum, range(len(cum)), color='#f59e0b',
             linewidth=2, marker='o', markersize=3, label='Cumulative %')
    ax2.set_xlabel('Cumulative Importance %', color='#f59e0b')
    ax2.tick_params(axis='x', colors='#f59e0b')
    ax2.axvline(80, color='#f59e0b', linestyle='--', alpha=0.5, linewidth=1)
    ax2.set_xlim(0, 105)

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

    # Pareto note
    pareto_80 = (result['Cum_Pct'] <= 80).sum()
    st.caption(f"📊 Top {pareto_80} features explain 80% of total importance "
               f"(Pareto cutoff shown as dashed line)")


def _show_table(result: pd.DataFrame, top_n: int):
    with st.expander("View full table"):
        st.dataframe(
            result.head(top_n)[['Rank', 'Feature', 'Importance', 'Pct', 'Cum_Pct']],
            use_container_width=True,
            hide_index=True,
            column_config={
                'Importance': st.column_config.NumberColumn(format="%.5f"),
                'Pct':        st.column_config.NumberColumn(format="%.2f%%"),
                'Cum_Pct':    st.column_config.NumberColumn(format="%.1f%%"),
            }
        )
