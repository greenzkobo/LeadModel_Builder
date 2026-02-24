"""
pages/autorun.py
=================
Auto-run page — full pipeline in one click with live progress feedback.
"""

import streamlit as st
from ui.components import page_header, divider, warn, success


def render():
    page_header("Auto-Run", "Run the full pipeline in one click")

    if not st.session_state.client:
        warn("Select a client on the Home page first.")
        return

    if st.session_state.df is None:
        warn("Load your data on the Ingestion page first.")
        return

    # ── Config ─────────────────────────────────────────────────
    st.markdown("#### Pipeline Configuration")

    col1, col2 = st.columns(2)
    with col1:
        include_tw = st.toggle("Include TW variables (tw_*)", value=True)
        st.caption("TrueWorth propensity scores — disable to test model without them")
    with col2:
        test_pct = st.slider("Validation %", 10, 40,
                             int(st.session_state.test_size * 100), 5)
        st.session_state.test_size = test_pct / 100

    divider()

    # ── Model selection ────────────────────────────────────────
    st.markdown("#### Models to Train")
    st.caption("Select which algorithms to include in this run")

    col1, col2 = st.columns(2)
    with col1:
        run_rf  = st.checkbox("Random Forest",       value=True)
        run_xgb = st.checkbox("XGBoost",             value=True)
        run_cat = st.checkbox("CatBoost",            value=True)
    with col2:
        run_lr  = st.checkbox("Logistic Regression", value=True)
        run_gb  = st.checkbox("Gradient Boosting (slow)", value=False)

    models_to_train = []
    if run_rf:  models_to_train.append("Random Forest")
    if run_xgb: models_to_train.append("XGBoost")
    if run_cat: models_to_train.append("CatBoost")
    if run_lr:  models_to_train.append("Logistic Regression")
    if run_gb:  models_to_train.append("Gradient Boosting")

    if not models_to_train:
        warn("Select at least one model.")
        return

    divider()

    # ── Steps preview ──────────────────────────────────────────
    st.markdown("#### Steps")
    steps = [
        "Data Cleaning        (auto-drop household, ID, high-missing, low-variance cols)",
        "Feature Selection    (collinearity + pareto cutoff)",
        f"Train {len(models_to_train)} Model(s)   ({', '.join(models_to_train)})",
        "Evaluate & Compare   (lift, gains, AUC, KS)",
        "Save Visualizations  (ROC, lift, gains, feature importance)",
        "Export Winner        (scoring code + model pickle)",
        "Generate Report      (txt + xlsx)",
    ]
    for i, step in enumerate(steps, 1):
        st.caption(f"{i}. {step}")

    divider()

    if st.button("🚀  Run Full Pipeline", type="primary", use_container_width=True):
        _run_pipeline(include_tw, models_to_train)


def _run_pipeline(include_tw: bool, models_to_train: list):
    client    = st.session_state.client
    target    = st.session_state.target
    test_size = st.session_state.test_size
    df_raw    = st.session_state.df

    progress = st.progress(0)
    status   = st.empty()

    try:
        # ── Step 1: Clean ──────────────────────────────────────
        status.info("Step 1/7 — Data Cleaning...")
        from cleaning import DataCleaner

        AUTO_PREFIXES = [
            'ind_1_', 'ind_2_',
            'member_2_', 'member_3_', 'member_4_', 'member_5_', 'member_6_',
            'householdsize', 'householdmembercount', 'markettargetage',
            'numberofadults', 'numberofsurnames', 'numberofchildren',
            'presenceofchildren', 'spouseindicator', 'occupancycount',
        ]
        AUTO_COLS = [
            'age0_3','age4_7','age8_12','age13_17',
            'phhchild','phhw65p','phhsz3p','phhmarrd','phhspchld',
            'phhd25km','phhd50kp','phhd150k',
            'phhblack','phhasian','phhspnsh',
            'unmarried_partner_household','household_with_retirement_income',
            'vperhh','hhsglhfc',
            'RecordId','standardizedaddress','zipcode','apn','familyid',
            'locationid','individualid','standardizedname',
            'standardizedcitystzip','housenumber','streetname',
            'streetsuffix','unittype',
        ]

        cleaner = DataCleaner(df_raw, client=client)
        cleaner.drop_columns_by_prefix(AUTO_PREFIXES)
        existing = [c for c in AUTO_COLS if c in cleaner.get_columns()]
        if existing:
            cleaner.drop_columns(existing)
        if not include_tw:
            cleaner.drop_columns_by_prefix(['tw_'])
        cleaner.drop_columns_by_missing(threshold=50)
        cleaner.drop_low_variance(threshold=0.01)
        cleaner.drop_rows_missing_target(target)
        cleaner.save_version('v1')

        df_clean = cleaner.get_data()
        st.session_state.cleaner  = cleaner
        st.session_state.df_clean = df_clean
        _log(f"Cleaning complete — {df_clean.shape[0]:,} × {df_clean.shape[1]:,}")
        progress.progress(15)

        # ── Step 2: Feature Selection ──────────────────────────
        status.info("Step 2/7 — Feature Selection...")
        from features import FeatureSelector

        selector = FeatureSelector(df_clean, client=client, target=target)
        selector.run_analysis()
        selector.save_report()
        st.session_state.selector = selector
        _log("Feature selection complete")
        progress.progress(30)

        # ── Step 3: Train ──────────────────────────────────────
        status.info(f"Step 3/7 — Training {len(models_to_train)} model(s)...")
        from models import ModelTrainer

        trainer = ModelTrainer(df_clean, client=client,
                               target=target, test_size=test_size)
        trainer.train_all(models=models_to_train)
        trainer.save_models()
        st.session_state.trainer   = trainer
        st.session_state.evaluator = None
        _log(f"Training complete — {', '.join(models_to_train)}")
        progress.progress(55)

        # ── Step 4: Evaluate ───────────────────────────────────
        status.info("Step 4/7 — Evaluating Models...")
        from models import ModelEvaluator

        evaluator = ModelEvaluator(trainer, client=client)
        evaluator.evaluate_all()
        evaluator.save_report()
        st.session_state.evaluator = evaluator
        winner    = evaluator.get_winner()
        comp      = evaluator.get_comparison_df()
        best_lift = comp.iloc[0]['Lift_D1_Val'] if comp is not None else 0
        _log(f"Evaluation complete — winner: {winner}, lift: {best_lift:.3f}")
        progress.progress(65)

        # ── Step 5: Visualizations ─────────────────────────────
        status.info("Step 5/7 — Saving Visualizations...")
        import matplotlib
        matplotlib.use("Agg")
        from visualization import ModelVisualizer

        viz = ModelVisualizer(trainer, evaluator, client=client)
        viz.plot_roc_curves(save=True)
        viz.plot_lift_curves(save=True)
        viz.plot_gains_curves(save=True)
        viz.plot_model_comparison_bar(save=True)
        viz.plot_feature_importance(save=True)
        _log("Visualizations saved")
        progress.progress(78)

        # ── Step 6: Export ─────────────────────────────────────
        status.info("Step 6/7 — Exporting Scoring Code...")
        from export import ScoringCodeExporter

        exporter = ScoringCodeExporter(trainer, client=client)
        exporter.export_winner(evaluator)
        _log(f"Exported scoring code for {winner}")
        progress.progress(88)

        # ── Step 7: Report ─────────────────────────────────────
        status.info("Step 7/7 — Generating Report...")
        from reports import ReportGenerator

        rg = ReportGenerator(trainer, evaluator, selector, client=client)
        rg.generate_full_report()
        _log("Report generated")
        progress.progress(100)

        # ── Done ───────────────────────────────────────────────
        status.empty()
        st.balloons()
        st.success(
            f"✅ Pipeline complete!  "
            f"🏆 Winner: **{winner}**  ·  "
            f"Lift D1: **{best_lift:.3f}**  ·  "
            f"Models trained: **{len(models_to_train)}**"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊  View Results", type="primary"):
                st.session_state.page = "evaluation"
                st.rerun()
        with col2:
            if st.button("📤  Go to Export"):
                st.session_state.page = "export"
                st.rerun()

    except Exception as e:
        status.empty()
        progress.empty()
        st.error(f"Pipeline failed: {e}")
        import traceback
        st.code(traceback.format_exc(), language="python")


def _log(msg: str):
    import datetime
    st.session_state.log.append(
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    )
