"""
menu/actions_data.py
=====================
Data-layer action handlers: ingestion, profiling, cleaning, feature selection.
"""

from session.hooks import (
    log_ingest, log_drop_columns, log_drop_rows,
    log_save_checkpoint, log_feature_selection,
)


def action_data_ingestion(app):
    if not app.client:
        print("\n  ⚠ Please select a client first (Option 1)")
        return
    from data.ingestion import load_data
    try:
        app.df       = load_data(client=app.client)
        app.df_clean = app.df.copy()
        log_ingest(app.session, len(app.df), len(app.df.columns), app.client)
        print("\n  ✓ Data loaded successfully!")
    except Exception as e:
        print(f"\n  ✗ Error loading data: {e}")


def action_data_profiling(app):
    if app.df is None:
        print("\n  ⚠ Please load data first (Option 2)")
        return
    from data.profiling import profile_data
    try:
        profile_data(app.df, client=app.client, target=app.target)
        print("\n  ✓ Profiling complete — reports/data_profile.xlsx")
    except Exception as e:
        print(f"\n  ✗ Error profiling: {e}")


def action_data_cleaning(app):
    if app.df is None:
        print("\n  ⚠ Please load data first (Option 2)")
        return
    from cleaning import DataCleaner
    if app.cleaner is None or app.df_clean is None:
        app.df_clean = app.df.copy()
        app.cleaner  = DataCleaner(app.df_clean, client=app.client)

    while True:
        shape = app.cleaner.get_shape()
        print(f"\n{'─'*50}\n  DATA CLEANING  —  {shape[0]:,} × {shape[1]:,}\n{'─'*50}")
        print("  1. Drop columns by name        5. Drop rows (missing target)")
        print("  2. Drop columns by prefix      6. Drop rows by condition")
        print("  3. Drop by missing % threshold 7. Show change history")
        print("  4. Drop by low variance        8. Save checkpoint  9. Load  R. Reset  0. Back\n")

        choice = input("  Enter choice: ").strip().upper()

        if choice == '0':
            app.df_clean = app.cleaner.get_data()
            break
        elif choice == '1':
            cols = [c.strip() for c in input("  Column names (comma-sep): ").split(',') if c.strip()]
            sb = app.cleaner.get_shape()
            app.cleaner.drop_columns(cols)
            log_drop_columns(app.session, 'drop_columns_manual', cols, sb, app.cleaner.get_shape())
        elif choice == '2':
            pfx = [p.strip() for p in input("  Prefixes (comma-sep): ").split(',') if p.strip()]
            sb = app.cleaner.get_shape()
            app.cleaner.drop_columns_by_prefix(pfx)
            log_drop_columns(app.session, 'drop_columns_by_prefix', pfx, sb, app.cleaner.get_shape())
        elif choice == '3':
            t = input("  Missing % threshold (default 50): ").strip()
            threshold = float(t) if t else 50.0
            sb = app.cleaner.get_shape()
            app.cleaner.drop_columns_by_missing(threshold)
            log_drop_columns(app.session, 'drop_columns_by_missing', [f">{threshold}% missing"], sb, app.cleaner.get_shape())
        elif choice == '4':
            t = input("  Variance threshold (default 0.01): ").strip()
            threshold = float(t) if t else 0.01
            sb = app.cleaner.get_shape()
            app.cleaner.drop_low_variance(threshold)
            log_drop_columns(app.session, 'drop_low_variance', [f"variance<{threshold}"], sb, app.cleaner.get_shape())
        elif choice == '5':
            sb = app.cleaner.get_shape()
            app.cleaner.drop_rows_missing_target(app.target)
            sa = app.cleaner.get_shape()
            log_drop_rows(app.session, f"missing {app.target}", sb[0]-sa[0], sb, sa)
        elif choice == '6':
            cond = input("  Condition (e.g. age < 0): ").strip()
            sb = app.cleaner.get_shape()
            app.cleaner.drop_rows_by_condition(cond)
            sa = app.cleaner.get_shape()
            log_drop_rows(app.session, cond, sb[0]-sa[0], sb, sa)
        elif choice == '7':
            app.cleaner.show_history()
        elif choice == '8':
            existing = app.session.state.get('checkpoints', {}) if app.session else {}
            available = [k for k in ('v1','v2','v3') if not existing.get(k)]
            if not available:
                print("  ⚠ All checkpoint slots used (v1, v2, v3).")
            else:
                print(f"  Available: {available}")
                name  = input("  Slot (v1/v2/v3): ").strip().lower()
                label = input("  Label (e.g. after_tw_drop): ").strip()
                if name in ('v1','v2','v3'):
                    app.cleaner.save_version(name)
                    log_save_checkpoint(app.session, name, label, app.cleaner.get_shape())
        elif choice == '9':
            app.cleaner.show_versions()
            name = input("  Version to load: ").strip()
            app.cleaner.load_version(name)
            app.df_clean = app.cleaner.get_data()
        elif choice == 'R':
            app.cleaner.reset()
            app.df_clean = app.cleaner.get_data()
        input("\n  Press Enter to continue...")


def action_feature_selection(app):
    if app.df_clean is None:
        print("\n  ⚠ Please clean data first (Option 4)")
        return
    from features import FeatureSelector
    chk = app.session.active_checkpoint if app.session else 'current'
    try:
        app.selector = FeatureSelector(app.df_clean, client=app.client, target=app.target)
        app.selector.run_analysis()
        app.selector.show_suggestions()
        if input("\n  Show importance charts? (y/n): ").strip().lower() == 'y':
            app.selector.plot_importance_cutoff()
            app.selector.plot_correlation_heatmap(top_n=30)
        app.selector.save_report()
        config = {'missing_threshold': 50, 'collinearity_threshold': 0.85, 'pareto': 0.80}
        log_feature_selection(app.session,
            features_in=app.df_clean.shape[1],
            features_out=len(app.selector.get_top_features(999)),
            dataset_checkpoint=chk, config=config,
            top_features=app.selector.get_top_features(10))
        print("\n  ✓ Feature selection complete!")
    except Exception as e:
        print(f"\n  ✗ Error: {e}")
