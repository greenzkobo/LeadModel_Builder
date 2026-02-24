"""
menu/auto_run.py
=================
Full pipeline auto-run (replaces action_auto_run in old main_menu.py).
Runs all steps in sequence with session logging at each stage.
"""

from session.hooks import (
    log_ingest, log_drop_columns, log_drop_rows,
    log_save_checkpoint, log_feature_selection,
    log_train_models, log_model_comparison, log_export,
)


# Prefixes always dropped in auto-clean
AUTO_DROP_PREFIXES = [
    'ind_1_', 'ind_2_',
    'member_2_', 'member_3_', 'member_4_', 'member_5_', 'member_6_',
    'householdsize', 'householdmembercount', 'markettargetage',
    'numberofadults', 'numberofsurnames', 'numberofchildren',
    'presenceofchildren', 'spouseindicator', 'occupancycount',
]

AUTO_DROP_COLS = [
    'age0_3', 'age4_7', 'age8_12', 'age13_17',
    'phhchild', 'phhw65p', 'phhsz3p', 'phhmarrd', 'phhspchld',
    'phhd25km', 'phhd50kp', 'phhd150k',
    'phhblack', 'phhasian', 'phhspnsh',
    'unmarried_partner_household', 'household_with_retirement_income',
    'vperhh', 'hhsglhfc',
    'RecordId', 'standardizedaddress', 'zipcode', 'apn', 'familyid',
    'locationid', 'individualid', 'standardizedname',
    'standardizedcitystzip', 'housenumber', 'streetname',
    'streetsuffix', 'unittype',
]


def run_auto_pipeline(app):
    """
    Run the complete pipeline automatically.
    app is the MLToolkit instance (holds client, df, trainer, etc.)
    """
    print("\n" + "="*60)
    print("  AUTO-RUN: FULL PIPELINE")
    print("="*60)

    # ── Step 1: Client ──────────────────────────────────────────
    if not app.client:
        print("\n  ✗ No client selected. Use Option 1 first.")
        return

    # ── Step 2: TW variables ────────────────────────────────────
    print("\n  Include TW variables (tw_*)? (y/n): ", end="")
    include_tw = input().strip().lower() == 'y'
    print(f"  → TW variables: {'included' if include_tw else 'excluded'}")

    # ── Step 3: Ingest ──────────────────────────────────────────
    _print_step(3, "Data Ingestion")
    from data.ingestion import load_data
    try:
        app.df = load_data(client=app.client)
        app.df_clean = app.df.copy()
        log_ingest(app.session, len(app.df), len(app.df.columns), app.client)
        print("  ✓ Data loaded")
    except Exception as e:
        print(f"  ✗ {e}")
        return

    # ── Step 4: Clean ───────────────────────────────────────────
    _print_step(4, "Data Cleaning")
    from cleaning import DataCleaner

    app.cleaner = DataCleaner(app.df, client=app.client)

    sb = app.cleaner.get_shape()
    app.cleaner.drop_columns_by_prefix(AUTO_DROP_PREFIXES)
    existing_drops = [c for c in AUTO_DROP_COLS if c in app.cleaner.get_columns()]
    if existing_drops:
        app.cleaner.drop_columns(existing_drops)
    if not include_tw:
        app.cleaner.drop_columns_by_prefix(['tw_'])
    app.cleaner.drop_columns_by_missing(threshold=50)
    app.cleaner.drop_low_variance(threshold=0.01)
    app.cleaner.drop_rows_missing_target(app.target)
    sa = app.cleaner.get_shape()

    log_drop_columns(app.session, 'auto_clean',
                     AUTO_DROP_PREFIXES + existing_drops, sb, sa)
    app.cleaner.save_version('v1')
    log_save_checkpoint(app.session, 'v1', 'auto_clean', sa)

    app.df_clean = app.cleaner.get_data()
    print("  ✓ Data cleaned")

    # ── Step 5: Feature Selection ───────────────────────────────
    _print_step(5, "Feature Selection")
    from features import FeatureSelector

    app.selector = FeatureSelector(app.df_clean,
                                   client=app.client, target=app.target)
    app.selector.run_analysis()
    app.selector.save_report()

    config = {'missing_threshold': 50, 'collinearity_threshold': 0.85, 'pareto': 0.80}
    log_feature_selection(
        app.session,
        features_in=app.df_clean.shape[1],
        features_out=len(app.selector.get_top_features(999)),
        dataset_checkpoint='v1',
        config=config,
        top_features=app.selector.get_top_features(10),
    )
    print("  ✓ Feature selection complete")

    # ── Step 6: Train ───────────────────────────────────────────
    _print_step(6, "Model Training")
    from models import ModelTrainer

    models_to_train = ['Random Forest', 'Logistic Regression', 'XGBoost', 'CatBoost']
    app.trainer = ModelTrainer(
        app.df_clean, client=app.client,
        target=app.target, test_size=app.test_size
    )
    app.trainer.train_all(models=models_to_train)
    app.trainer.save_models()
    log_train_models(app.session, models_to_train,
                     len(app.trainer.feature_names), 'v1')
    print("  ✓ Models trained")

    # ── Step 7: Evaluate ────────────────────────────────────────
    _print_step(7, "Model Evaluation")
    from models import ModelEvaluator

    app.evaluator = ModelEvaluator(app.trainer, client=app.client)
    app.evaluator.evaluate_all()
    app.evaluator.save_report()

    winner    = app.evaluator.get_winner()
    comp      = app.evaluator.get_comparison_df()
    best_lift = comp.iloc[0]['Lift_D1_Val']
    metrics_dict = {
        row['Model']: {
            'lift_d1_val':  row['Lift_D1_Val'],
            'gains_d1_val': row['Gains_D1_Val'],
            'auc_val':      row['AUC_Val'],
            'ks_val':       row['KS_Val'],
        }
        for _, row in comp.iterrows()
    }
    log_model_comparison(app.session, metrics_dict, winner, best_lift)
    print("  ✓ Models evaluated")

    # ── Step 8: Visualizations ──────────────────────────────────
    _print_step(8, "Visualizations")
    from visualization import ModelVisualizer

    viz = ModelVisualizer(app.trainer, app.evaluator, client=app.client)
    viz.plot_roc_curves()
    viz.plot_lift_curves()
    viz.plot_gains_curves()
    viz.plot_model_comparison_bar()
    viz.plot_feature_importance()
    print("  ✓ Visualizations saved")

    # ── Step 9: Export ──────────────────────────────────────────
    _print_step(9, "Export Scoring Code")
    from export import ScoringCodeExporter

    exporter = ScoringCodeExporter(app.trainer, client=app.client)
    exporter.export_winner(app.evaluator)

    winner_metrics = {
        winner: {
            'lift_d1_val': best_lift,
            'auc_val':     app.evaluator.val_metrics[winner].get('AUC'),
            'ks_val':      app.evaluator.val_metrics[winner].get('KS_Statistic'),
        }
    }
    log_export(app.session, [winner], winner_metrics)
    print("  ✓ Scoring code exported")

    # ── Step 10: Report ─────────────────────────────────────────
    _print_step(10, "Summary Report")
    from reports import ReportGenerator

    rg = ReportGenerator(app.trainer, app.evaluator,
                         app.selector, client=app.client)
    rg.generate_full_report()
    print("  ✓ Report generated")

    # ── Summary ─────────────────────────────────────────────────
    print("\n" + "="*60)
    print("  AUTO-RUN COMPLETE!")
    print("="*60)
    app.evaluator.show_comparison()
    print(f"\n  🏆 WINNER: {winner}")
    print(f"  Best Lift D1: {best_lift:.3f}")
    print("\n  Output files:")
    print("    reports/model_summary_report.txt  ← use for presentations")
    print("    reports/model_summary_data.xlsx")
    print("    reports/model_evaluation_report.xlsx")
    print("    outputs/visualizations/*.png")
    print("    outputs/scoring_code/*_scoring.py")
    print("="*60)


def _print_step(n: int, label: str):
    print(f"\n  STEP {n}: {label}")
    print("  " + "─" * 40)
