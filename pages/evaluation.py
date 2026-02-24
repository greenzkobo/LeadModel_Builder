"""
pages/evaluation.py
====================
Model evaluation page — metrics table, winner highlight, decile analysis.
"""

import streamlit as st
from ui.components import page_header, divider, warn, success, metric_grid


def render():
    page_header("Model Evaluation", "Compare models and identify the winner")

    if st.session_state.trainer is None:
        warn("Train models first on the Training page.")
        return

    if st.session_state.evaluator is None:
        if st.button("▶  Run Evaluation", type="primary"):
            _evaluate()
        return

    evaluator = st.session_state.evaluator
    winner    = evaluator.get_winner()

    # ── Winner banner ──────────────────────────────────────────
    if winner:
        try:
            m = evaluator.val_metrics[winner]
            st.markdown(
                f'<div style="background:#052e16;border:1px solid #166534;'
                f'border-radius:10px;padding:1rem 1.5rem;margin-bottom:1rem;">'
                f'<div style="font-size:0.72rem;color:#4ade80;text-transform:uppercase;'
                f'letter-spacing:0.05em;">🏆 Winner</div>'
                f'<div style="font-size:1.3rem;font-weight:700;color:#f1f5f9;margin:4px 0;">'
                f'{winner}</div>'
                f'<div style="font-size:0.82rem;color:#94a3b8;">'
                f'Lift D1: <b>{m.get("Lift_Decile_1", 0):.3f}</b> &nbsp;·&nbsp; '
                f'AUC: <b>{m.get("AUC", 0):.4f}</b> &nbsp;·&nbsp; '
                f'KS: <b>{m.get("KS_Statistic", 0):.4f}</b>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
        except Exception:
            st.success(f"🏆 Winner: {winner}")

    divider()

    # ── Comparison table ───────────────────────────────────────
    st.markdown("#### Model Comparison")
    try:
        comp_df = evaluator.get_comparison_df()
        if comp_df is not None:
            st.dataframe(
                comp_df.style.highlight_max(
                    subset=["Lift_D1_Val", "AUC_Val", "KS_Val"],
                    color="#1a4731",
                ),
                use_container_width=True,
                hide_index=True,
            )
    except Exception as e:
        st.caption(f"Could not display comparison: {e}")

    divider()

    # ── Decile table ───────────────────────────────────────────
    st.markdown(f"#### Decile Analysis — {winner}")
    try:
        decile_df = evaluator.get_decile_table(winner, "val")
        if decile_df is not None:
            st.dataframe(decile_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.caption(f"Decile table not available: {e}")

    divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("▶  View Charts", type="primary"):
            st.session_state.page = "visualizations"
            st.rerun()
    with col2:
        if st.button("▶  Export Winner"):
            st.session_state.page = "export"
            st.rerun()
    with col3:
        if st.button("↺  Re-run Evaluation"):
            st.session_state.evaluator = None
            st.rerun()


def _evaluate():
    try:
        from models import ModelEvaluator
        with st.spinner("Evaluating models..."):
            evaluator = ModelEvaluator(
                st.session_state.trainer,
                client=st.session_state.client,
            )
            evaluator.evaluate_all()
            evaluator.save_report()

        st.session_state.evaluator = evaluator
        winner = evaluator.get_winner()
        comp   = evaluator.get_comparison_df()
        best   = comp.iloc[0]["Lift_D1_Val"] if comp is not None else 0
        _log(f"Evaluation complete — winner: {winner}, lift D1: {best:.3f}")
        success(f"Evaluation complete — winner: {winner}")
        st.rerun()
    except Exception as e:
        st.error(f"Evaluation failed: {e}")


def _log(msg: str):
    import datetime
    st.session_state.log.append(
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    )
