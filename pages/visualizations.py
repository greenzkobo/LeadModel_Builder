"""
pages/visualizations.py
========================
Always renders fresh from current trainer/evaluator in session state.
"""

import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ui.components import page_header, divider, warn


def render():
    page_header("Visualizations", "Model performance charts")

    if st.session_state.trainer is None:
        warn("Train models first on the Training page.")
        return

    if st.session_state.evaluator is None:
        warn("Evaluate models first on the Evaluation page.")
        return

    trainer   = st.session_state.trainer
    evaluator = st.session_state.evaluator

    models = list(trainer.get_trained_models().keys())
    winner = evaluator.get_winner()
    st.caption(f"Models: {', '.join(models)}  ·  Winner: **{winner}**")

    divider()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "ROC Curves", "Lift Curves", "Gains Curves",
        "Feature Importance", "Model Comparison"
    ])

    with tab1:
        _render("ROC Curves",         _plot_roc,        trainer, evaluator)
    with tab2:
        _render("Lift Curves",        _plot_lift,       trainer, evaluator)
    with tab3:
        _render("Gains Curves",       _plot_gains,      trainer, evaluator)
    with tab4:
        _render("Feature Importance", _plot_importance, trainer, evaluator)
    with tab5:
        _render("Model Comparison",   _plot_comparison, trainer, evaluator)


def _render(title, plot_fn, trainer, evaluator):
    try:
        plt.close("all")
        plot_fn(trainer, evaluator)
        fig = plt.gcf()
        st.pyplot(fig, use_container_width=True)
        plt.close("all")
    except Exception as e:
        st.error(f"Could not render {title}: {e}")
        import traceback
        st.code(traceback.format_exc(), language="python")


def _plot_roc(trainer, evaluator):
    from visualization import roc
    roc.plot_roc_curves(
        trainer.get_trained_models(),
        trainer.get_validation_data()[1],
        dataset_label="Validation",
        prob_key='y_val_prob',
        save_path=None,
    )


def _plot_lift(trainer, evaluator):
    from visualization import lift
    lift.plot_lift_curves(
        trainer.get_trained_models(),
        trainer.get_validation_data()[1],
        dataset_label="Validation",
        prob_key='y_val_prob',
        save_path=None,
    )


def _plot_gains(trainer, evaluator):
    from visualization import gains
    gains.plot_gains_curves(
        trainer.get_trained_models(),
        trainer.get_validation_data()[1],
        dataset_label="Validation",
        prob_key='y_val_prob',
        save_path=None,
    )


def _plot_importance(trainer, evaluator):
    from visualization import importance
    models        = trainer.get_trained_models()
    feature_names = trainer.get_feature_names()
    winner        = evaluator.get_winner()
    if winner not in models:
        st.warning(f"Winner '{winner}' not found.")
        return
    importance.plot_feature_importance(
        models[winner]['model'],
        feature_names,
        model_name=winner,
        top_n=20,
        save_path=None,
    )


def _plot_comparison(trainer, evaluator):
    from visualization import comparison
    comp_df = evaluator.get_comparison_df()
    if comp_df is None:
        st.warning("No comparison data available.")
        return
    comparison.plot_model_comparison_bar(comp_df, save_path=None)
