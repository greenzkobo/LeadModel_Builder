"""
menu/actions_models.py
=======================
Model-layer action handlers: training, evaluation, visualization, export, report, log.
"""

from session.hooks import log_train_models, log_model_comparison, log_export


def action_model_training(app):
    if app.df_clean is None:
        print("\n  ⚠ Please clean data first (Options 2, 4)")
        return
    from models import ModelTrainer

    print(f"\n  Current split: {int((1-app.test_size)*100)}/{int(app.test_size*100)}")
    if input("  Change split? (y/n): ").strip().lower() == 'y':
        pct = input("  Test % (e.g. 30): ").strip()
        app.test_size = float(pct) / 100

    print("\n  1. Random Forest  2. Logistic Regression  3. XGBoost  "
          "4. CatBoost  5. Gradient Boosting  A. All (except GB)\n")
    choice = input("  Choose (comma-sep or A): ").strip().upper()
    model_map = {'1':'Random Forest','2':'Logistic Regression',
                 '3':'XGBoost','4':'CatBoost','5':'Gradient Boosting'}

    if choice == 'A':
        models_to_train = ['Random Forest','Logistic Regression','XGBoost','CatBoost']
    else:
        models_to_train = [model_map[c.strip()] for c in choice.split(',')
                           if c.strip() in model_map]
    if not models_to_train:
        print("  No valid models selected.")
        return

    chk = app.session.active_checkpoint if app.session else 'current'
    try:
        app.trainer = ModelTrainer(app.df_clean, client=app.client,
                                   target=app.target, test_size=app.test_size)
        app.trainer.train_all(models=models_to_train)
        app.trainer.show_summary()
        if input("  Save models? (y/n): ").strip().lower() == 'y':
            app.trainer.save_models()
        log_train_models(app.session, models_to_train,
                         len(app.trainer.feature_names), chk)
        print("\n  ✓ Training complete!")
    except Exception as e:
        print(f"\n  ✗ Error: {e}")


def action_model_evaluation(app):
    if app.trainer is None or not app.trainer.models:
        print("\n  ⚠ Please train models first (Option 6)")
        return
    from models import ModelEvaluator
    try:
        app.evaluator = ModelEvaluator(app.trainer, client=app.client)
        app.evaluator.evaluate_all()
        app.evaluator.show_comparison()
        app.evaluator.save_report()

        winner = app.evaluator.get_winner()
        comp   = app.evaluator.get_comparison_df()
        if comp is not None and winner:
            metrics_dict = {
                row['Model']: {'lift_d1_val': row['Lift_D1_Val'],
                               'gains_d1_val': row['Gains_D1_Val'],
                               'auc_val': row['AUC_Val'], 'ks_val': row['KS_Val']}
                for _, row in comp.iterrows()
            }
            log_model_comparison(app.session, metrics_dict,
                                 winner, comp.iloc[0]['Lift_D1_Val'])
        print("\n  ✓ Evaluation complete!")
    except Exception as e:
        print(f"\n  ✗ Error: {e}")


def action_visualizations(app):
    if app.trainer is None or app.evaluator is None:
        print("\n  ⚠ Train and evaluate models first (Options 6, 7)")
        return
    from visualization import ModelVisualizer

    print("\n  1. All  2. ROC  3. Lift  4. Gains  "
          "5. Confusion matrices  6. Feature importance  7. Comparison bar  0. Back")
    choice = input("  Enter choice: ").strip()
    if choice == '0':
        return
    try:
        viz = ModelVisualizer(app.trainer, app.evaluator, client=app.client)
        dispatch = {'1': viz.plot_all, '2': viz.plot_roc_curves,
                    '3': viz.plot_lift_curves, '4': viz.plot_gains_curves,
                    '5': viz.plot_confusion_matrices,
                    '6': viz.plot_feature_importance,
                    '7': viz.plot_model_comparison_bar}
        if choice in dispatch:
            dispatch[choice]()
        print("\n  ✓ Done!")
    except Exception as e:
        print(f"\n  ✗ Error: {e}")


def action_export(app):
    if app.trainer is None or not app.trainer.models:
        print("\n  ⚠ Train models first (Option 6)")
        return
    from export import ScoringCodeExporter

    models = list(app.trainer.models.keys())
    print("\n  Available models:")
    for i, m in enumerate(models, 1):
        print(f"    {i}. {m}")
    print("    A. All")
    if app.evaluator:
        print(f"    W. Winner only ({app.evaluator.get_winner()})")
    print()
    choice = input("  Enter choice: ").strip().upper()

    try:
        exporter = ScoringCodeExporter(app.trainer, client=app.client)
        if choice == 'A':
            exporter.export_all(evaluator=app.evaluator)
            exported = models
        elif choice == 'W' and app.evaluator:
            exporter.export_winner(app.evaluator)
            exported = [app.evaluator.get_winner()]
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(models):
                    exporter.export_model(models[idx], evaluator=app.evaluator)
                    exported = [models[idx]]
                else:
                    print("  Invalid selection.")
                    return
            except ValueError:
                print("  Invalid input.")
                return

        metrics = {}
        if app.evaluator:
            for m in exported:
                vm = app.evaluator.val_metrics.get(m, {})
                metrics[m] = {'lift_d1_val': vm.get('Lift_Decile_1'),
                               'auc_val': vm.get('AUC'), 'ks_val': vm.get('KS_Statistic')}
        log_export(app.session, exported, metrics)
        print("\n  ✓ Export complete!")
    except Exception as e:
        print(f"\n  ✗ Error: {e}")


def action_generate_report(app):
    if app.trainer is None or app.evaluator is None:
        print("\n  ⚠ Train and evaluate models first (Options 6, 7)")
        return
    from reports import ReportGenerator
    try:
        rg = ReportGenerator(app.trainer, app.evaluator,
                             app.selector, client=app.client)
        rg.generate_full_report()
        print("\n  ✓ Report generated!")
    except Exception as e:
        print(f"\n  ✗ Error: {e}")


def action_view_log(app):
    if app.session:
        app.session.show_model_runs()
    else:
        print("\n  No active session.")


def action_settings(app):
    from config import BASE_DIR
    print(f"\n  1. Target variable:  {app.target}")
    print(f"  2. Test split:       {int(app.test_size*100)}%")
    print(f"  3. Base directory:   {BASE_DIR}")
    print("  0. Back\n")
    choice = input("  Enter choice: ").strip()
    if choice == '1':
        app.target = input("  New target name: ").strip()
        print(f"  ✓ Target → {app.target}")
    elif choice == '2':
        pct = input("  Test % (e.g. 30): ").strip()
        app.test_size = float(pct) / 100
        print(f"  ✓ Split → {int(app.test_size*100)}%")
    elif choice == '3':
        print("  Change BASE_DIR in config/settings.py")
