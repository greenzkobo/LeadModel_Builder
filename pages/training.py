"""
pages/training.py
==================
Model training page — select models, configure split, train.
"""

import streamlit as st
from ui.components import page_header, divider, warn, success


def render():
    page_header("Model Training", "Select algorithms and train your models")

    if st.session_state.df_clean is None:
        warn("Clean your data first.")
        return

    # ── Config ─────────────────────────────────────────────────
    st.markdown("#### Configuration")

    col1, col2 = st.columns(2)
    with col1:
        test_pct = st.slider(
            "Validation split %",
            10, 40,
            int(st.session_state.test_size * 100),
            5,
        )
        st.session_state.test_size = test_pct / 100
        st.caption(f"Train: {100-test_pct}%  |  Validation: {test_pct}%")

    with col2:
        st.markdown("**Select models to train**")
        model_options = {
            "Random Forest":       st.checkbox("Random Forest",       value=True),
            "XGBoost":             st.checkbox("XGBoost",             value=True),
            "CatBoost":            st.checkbox("CatBoost",            value=True),
            "Logistic Regression": st.checkbox("Logistic Regression", value=True),
            "Gradient Boosting":   st.checkbox("Gradient Boosting (slow)", value=False),
        }

    models_to_train = [m for m, selected in model_options.items() if selected]

    if not models_to_train:
        warn("Select at least one model.")
        return

    divider()

    # ── Data info ──────────────────────────────────────────────
    df     = st.session_state.df_clean
    target = st.session_state.target
    n_rows = len(df)
    train_n = int(n_rows * (1 - st.session_state.test_size))
    val_n   = n_rows - train_n

    n_features = len([c for c in df.columns if c != target])

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total rows",       f"{n_rows:,}")
    col2.metric("Training rows",    f"{train_n:,}")
    col3.metric("Validation rows",  f"{val_n:,}")
    col4.metric("Total columns",    f"{len(df.columns):,}")
    col5.metric("Feature columns",  f"{n_features:,}", help="Excludes target column")

    divider()

    if st.button("▶  Train Models", type="primary"):
        _train(models_to_train)

    # ── Results ────────────────────────────────────────────────
    if st.session_state.trainer is not None:
        divider()
        st.markdown("#### Trained Models")
        trainer = st.session_state.trainer
        try:
            for name in trainer.get_trained_models():
                st.markdown(f"✅ **{name}**")
        except Exception:
            st.caption("Models trained — proceed to evaluation.")

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("▶  Go to Evaluation", type="primary"):
                st.session_state.page = "evaluation"
                st.rerun()


def _train(models_to_train: list):
    try:
        from models import ModelTrainer
        with st.spinner(f"Training {len(models_to_train)} models..."):
            trainer = ModelTrainer(
                st.session_state.df_clean,
                client=st.session_state.client,
                target=st.session_state.target,
                test_size=st.session_state.test_size,
            )
            trainer.train_all(models=models_to_train)
            trainer.save_models()

        st.session_state.trainer   = trainer
        st.session_state.evaluator = None  # reset eval when retrained
        _log(f"Trained: {', '.join(models_to_train)}")
        success(f"Trained {len(models_to_train)} models")
        st.rerun()
    except Exception as e:
        st.error(f"Training failed: {e}")


def _log(msg: str):
    import datetime
    st.session_state.log.append(
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    )
