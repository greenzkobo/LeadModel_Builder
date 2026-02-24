"""
session/archive.py
===================
When a user starts fresh on a client that has an in-progress session,
archive a lightweight summary then reset the session state.

The archive is a single JSON file in reports/logs/.
Data files (parquet, models) are NOT deleted — just the session pointer resets.
"""

import os
import json
from datetime import datetime
from . import activity_log


def archive_session(client_path: str, state: dict) -> str:
    """
    Write an archive summary for the current session, then return the archive path.
    Does NOT reset the session — call reset_session() after this.

    Returns:
    --------
    str : path to the archive file
    """
    logs_dir = os.path.join(client_path, 'reports', 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    started    = state.get('started', 'unknown')
    archive_filename = f"session_archive_{timestamp}.json"
    archive_path     = os.path.join(logs_dir, archive_filename)

    # Pull model run history from activity log
    model_runs = activity_log.load_model_runs(client_path)

    summary = {
        'archived_at':       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'client':            state.get('client'),
        'session_started':   started,
        'session_status':    state.get('status'),
        'target':            state.get('target'),
        'checkpoints_saved': [
            k for k, v in state.get('checkpoints', {}).items()
            if v is not None
        ],
        'feature_set': state.get('feature_set', {}),
        'models':      state.get('models', {}),
        'exported':    state.get('exported', False),
        'models_exported': state.get('models_exported', []),
        'model_run_history': model_runs,
    }

    with open(archive_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"  ✓ Session archived: reports/logs/{archive_filename}")
    return archive_path


def list_archives(client_path: str) -> list:
    """Return list of archive file paths sorted newest first."""
    logs_dir = os.path.join(client_path, 'reports', 'logs')
    if not os.path.exists(logs_dir):
        return []
    files = [
        os.path.join(logs_dir, f)
        for f in os.listdir(logs_dir)
        if f.startswith('session_archive_') and f.endswith('.json')
    ]
    return sorted(files, reverse=True)


def show_archives(client_path: str):
    """Print a summary of all archived sessions."""
    archives = list_archives(client_path)

    print(f"\n  Past session archives ({len(archives)} found):")
    if not archives:
        print("    (none)")
        return

    for path in archives:
        try:
            with open(path, 'r') as f:
                a = json.load(f)
            exported_str = "✓ exported" if a.get('exported') else "not exported"
            models = a.get('models', {})
            winner = models.get('winner', 'none')
            lift   = models.get('best_lift')
            lift_str = f" — lift {lift:.3f}" if lift else ""
            print(f"    {a.get('archived_at')}  |  {exported_str}  "
                  f"|  winner: {winner}{lift_str}")
        except Exception:
            print(f"    (could not read {os.path.basename(path)})")
