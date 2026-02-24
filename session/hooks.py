"""
session/hooks.py
=================
Convenience functions for wiring session logging into existing modules.
Import and call these at the relevant points — no module needs to know
about SessionManager internals beyond calling these functions.

Each hook takes a SessionManager (or None — all are no-ops if session=None)
plus the relevant data, and handles both the log write and state update.
"""


def log_ingest(session, rows: int, cols: int, filename: str):
    """Called after data is loaded from disk."""
    if session is None:
        return
    session.log(
        action='ingest',
        details=f"Loaded {filename} — {rows:,} rows × {cols:,} cols",
        extra={'shape': [rows, cols], 'file': filename}
    )
    session.save()


def log_drop_columns(session, action_label: str,
                     columns_dropped: list,
                     shape_before: tuple, shape_after: tuple):
    """Called after any column drop operation in DataCleaner."""
    if session is None:
        return
    session.log(
        action=action_label,
        details=(f"Dropped {len(columns_dropped)} cols — "
                 f"{shape_before[1]:,} → {shape_after[1]:,} cols"),
        extra={
            'columns_dropped': columns_dropped,
            'shape_before':    list(shape_before),
            'shape_after':     list(shape_after),
        }
    )
    session.save()


def log_drop_rows(session, condition: str,
                  rows_dropped: int,
                  shape_before: tuple, shape_after: tuple):
    """Called after any row drop operation in DataCleaner."""
    if session is None:
        return
    session.log(
        action='drop_rows',
        details=f"Dropped {rows_dropped:,} rows — condition: {condition}",
        extra={
            'condition':    condition,
            'rows_dropped': rows_dropped,
            'shape_before': list(shape_before),
            'shape_after':  list(shape_after),
        }
    )
    session.save()


def log_save_checkpoint(session, checkpoint_name: str,
                        label: str, shape: tuple):
    """Called when user saves a named checkpoint (v1, v2, v3)."""
    if session is None:
        return
    session.log(
        action='save_checkpoint',
        details=f"Saved checkpoint '{checkpoint_name}' ({label}) — "
                f"{shape[0]:,} × {shape[1]:,}",
        extra={'checkpoint': checkpoint_name, 'label': label, 'shape': list(shape)}
    )
    session.update_checkpoint(checkpoint_name, list(shape), label)


def log_feature_selection(session, features_in: int, features_out: int,
                          dataset_checkpoint: str, config: dict,
                          top_features: list = None):
    """Called after FeatureSelector.run_analysis() completes."""
    if session is None:
        return
    extra = {
        'features_in':         features_in,
        'features_out':        features_out,
        'dataset_checkpoint':  dataset_checkpoint,
        'config':              config,
    }
    if top_features:
        extra['top_features'] = top_features[:10]  # store top 10 only

    session.log(
        action='feature_selection',
        details=(f"FS run — {features_in} in → {features_out} out | "
                 f"collinearity: {config.get('collinearity_threshold', '?')} | "
                 f"pareto: {config.get('pareto', '?')}"),
        extra=extra
    )
    session.update_feature_set(features_in, features_out, dataset_checkpoint, config)


def log_train_models(session, models_trained: list,
                     feature_count: int, dataset_checkpoint: str):
    """Called after ModelTrainer.train_all() completes."""
    if session is None:
        return
    session.log(
        action='train_models',
        details=(f"Trained {len(models_trained)} models on {dataset_checkpoint} — "
                 f"{feature_count} features"),
        extra={
            'models':              models_trained,
            'feature_count':       feature_count,
            'dataset_checkpoint':  dataset_checkpoint,
        }
    )
    session.save()


def log_model_comparison(session, comparison_dict: dict,
                         winner: str, best_lift: float):
    """
    Called after ModelEvaluator.evaluate_all() completes.
    comparison_dict: {model_name: {lift_d1_val, auc_val, ks_val, gains_d1_val}}
    """
    if session is None:
        return
    session.log(
        action='model_comparison',
        details=f"Winner: {winner} — Lift D1: {best_lift:.3f}",
        extra={'metrics': comparison_dict, 'winner': winner}
    )
    trained = list(comparison_dict.keys())
    session.update_models(trained, winner=winner, best_lift=best_lift)


def log_export(session, models_exported: list, metrics: dict):
    """Called when scoring code is exported."""
    if session is None:
        return
    model_str = ', '.join(models_exported)
    session.log(
        action='export',
        details=f"Exported: {model_str}",
        extra={
            'models_exported': models_exported,
            'metrics':         {m: metrics.get(m, {}) for m in models_exported},
        }
    )
    session.mark_exported(models_exported)
