"""
session/state.py
=================
Atomic read/write of session.json in the client root folder.
Tracks current session status, active checkpoints, and model state.
"""

import os
import json
from datetime import datetime


def _session_path(client_path: str) -> str:
    return os.path.join(client_path, 'session.json')


def load(client_path: str) -> dict:
    """Load session state. Returns None if no session exists."""
    path = _session_path(client_path)
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save(client_path: str, state: dict):
    """
    Save session state atomically (write to .tmp then rename).
    Always updates last_active timestamp before saving.
    """
    state['last_active'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path = _session_path(client_path)
    tmp  = path + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(state, f, indent=2, default=str)
    os.replace(tmp, path)


def new_session(client: str, client_path: str, target: str = "IsTarget") -> dict:
    """Create and save a fresh session state. Returns the state dict."""
    state = {
        'client':           client,
        'status':           'in_progress',
        'started':          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'last_active':      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'target':           target,
        'active_checkpoint':'scratch',
        'checkpoints': {
            'scratch': None,
            'v1':      None,
            'v2':      None,
            'v3':      None,
            'current': None,
        },
        'feature_set': {
            'exists':              False,
            'features':            0,
            'dataset_checkpoint':  None,
            'config':              {},
        },
        'models': {
            'count':      0,
            'trained':    [],
            'winner':     None,
            'best_lift':  None,
        },
        'exported':  False,
    }
    save(client_path, state)
    return state


def update_checkpoint(state: dict, name: str, shape: list,
                      label: str = None, file: str = None) -> dict:
    """Record a saved checkpoint in session state."""
    state['checkpoints'][name] = {
        'shape': shape,
        'label': label or name,
        'file':  file or f"data/{name}.parquet",
        'saved': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    state['active_checkpoint'] = name
    return state


def update_feature_set(state: dict, features_in: int, features_out: int,
                       dataset_checkpoint: str, config: dict) -> dict:
    """Update feature set info in session state."""
    state['feature_set'] = {
        'exists':             True,
        'features_in':        features_in,
        'features':           features_out,
        'dataset_checkpoint': dataset_checkpoint,
        'config':             config,
        'run_at':             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return state


def update_models(state: dict, trained: list,
                  winner: str = None, best_lift: float = None) -> dict:
    """Update model info in session state."""
    state['models'] = {
        'count':     len(trained),
        'trained':   trained,
        'winner':    winner,
        'best_lift': best_lift,
    }
    return state


def mark_exported(state: dict, models_exported: list) -> dict:
    """Mark session as exported."""
    state['exported']          = True
    state['status']            = 'exported'
    state['models_exported']   = models_exported
    state['exported_at']       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return state


def is_in_progress(state: dict) -> bool:
    return state is not None and state.get('status') == 'in_progress'


def format_summary(state: dict) -> str:
    """Return a one-line session summary for display in menus."""
    if state is None:
        return "No session"
    last = state.get('last_active', 'unknown')
    chk  = state.get('active_checkpoint', 'scratch')
    models = state.get('models', {})
    count  = models.get('count', 0)
    best   = models.get('best_lift')
    lift_str = f" | Best lift: {best:.3f}" if best else ""
    return (f"Last active: {last} | Checkpoint: {chk} | "
            f"Models: {count}{lift_str}")
