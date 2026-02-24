"""
session/activity_log.py
========================
Append-only activity log saved as reports/logs/activity_log.json.

Every meaningful action in the toolkit appends one entry.
The file is never overwritten — only appended to.
The log viewer filters to model runs and metrics only.
"""

import os
import json
from datetime import datetime


def _log_path(client_path: str) -> str:
    """Return full path to the activity log file."""
    logs_dir = os.path.join(client_path, 'reports', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    return os.path.join(logs_dir, 'activity_log.json')


def append(client_path: str, action: str, details: str, extra: dict = None):
    """
    Append one entry to the activity log.

    Parameters:
    -----------
    client_path : str
        Full path to the client folder
    action : str
        Short action label, e.g. 'ingest', 'drop_columns', 'train_models'
    details : str
        Human-readable description of what happened
    extra : dict, optional
        Any additional structured data to store (metrics, column lists, etc.)
    """
    entry = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'action':    action,
        'details':   details,
    }
    if extra:
        entry.update(extra)

    path = _log_path(client_path)

    # Load existing log or start fresh
    log = _load(path)
    log.append(entry)

    # Write back atomically
    tmp = path + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(log, f, indent=2, default=str)
    os.replace(tmp, path)


def _load(path: str) -> list:
    """Load log from disk, return empty list if not found or corrupt."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def load_all(client_path: str) -> list:
    """Return the full log as a list of dicts."""
    return _load(_log_path(client_path))


def load_model_runs(client_path: str) -> list:
    """
    Return only model training and export entries.
    This is what gets displayed in the menu log viewer.
    """
    full_log = load_all(client_path)
    model_actions = {'train_models', 'export', 'model_comparison'}
    return [e for e in full_log if e.get('action') in model_actions]


def show_model_runs(client_path: str):
    """Print model runs and metrics to console."""
    runs = load_model_runs(client_path)

    print(f"\n{'='*70}")
    print("  MODEL RUN HISTORY")
    print('='*70)

    if not runs:
        print("  No model runs recorded yet.")
        print(f"{'='*70}\n")
        return

    for entry in runs:
        print(f"\n  [{entry['timestamp']}]  {entry['action'].upper()}")
        print(f"  {entry['details']}")

        # Show metrics if present
        if 'metrics' in entry:
            m = entry['metrics']
            for model_name, model_metrics in m.items():
                lift  = model_metrics.get('lift_d1_val', 'N/A')
                auc   = model_metrics.get('auc_val',     'N/A')
                ks    = model_metrics.get('ks_val',      'N/A')
                gains = model_metrics.get('gains_d1_val','N/A')
                print(f"    {model_name:<22} Lift D1: {lift:<8} "
                      f"AUC: {auc:<8} KS: {ks:<8} Gains D1: {gains}")

        # Show export info if present
        if 'models_exported' in entry:
            print(f"  Exported: {', '.join(entry['models_exported'])}")

        print(f"  {'─'*60}")

    print(f"{'='*70}\n")


def show_full_log(client_path: str, last_n: int = 50):
    """Print the full activity log (last N entries)."""
    full_log = load_all(client_path)

    print(f"\n{'='*70}")
    print(f"  FULL ACTIVITY LOG  (last {min(last_n, len(full_log))} entries)")
    print('='*70)

    if not full_log:
        print("  No activity recorded yet.")
    else:
        for entry in full_log[-last_n:]:
            print(f"\n  [{entry['timestamp']}]  {entry['action']}")
            print(f"  {entry['details']}")
            if 'shape_before' in entry and 'shape_after' in entry:
                sb = entry['shape_before']
                sa = entry['shape_after']
                print(f"  Shape: {sb[0]:,}×{sb[1]:,}  →  {sa[0]:,}×{sa[1]:,}")
            if 'columns_dropped' in entry:
                cols = entry['columns_dropped']
                preview = cols[:5]
                more = f" (+{len(cols)-5} more)" if len(cols) > 5 else ""
                print(f"  Dropped: {preview}{more}")

    print(f"{'='*70}\n")
