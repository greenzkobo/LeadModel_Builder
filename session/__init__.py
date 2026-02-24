"""
session/__init__.py
====================
SessionManager — the single object that owns session state and logging.

Every module that changes state calls:
    session.log(action, details, extra)
    session.save()

Usage:
    from session import SessionManager

    session = SessionManager(client="HISC_TEST", client_path="/path/to/client")
    session.log("ingest", "Loaded 200k rows × 612 cols")
    session.update_checkpoint("v1", shape=[200000, 413], label="after_manual_drops")
    session.save()
"""

import os
from config import get_paths, create_folder_structure
from . import state as state_mod
from . import activity_log as log_mod
from . import archive as archive_mod


class SessionManager:
    """
    Owns session.json state and activity_log.json.
    Passed through the menu to all modules.
    """

    def __init__(self, client: str, client_path: str):
        self.client      = client
        self.client_path = client_path
        self._state      = None

    # ------------------------------------------------------------------
    # Startup
    # ------------------------------------------------------------------

    def load_or_create(self) -> dict:
        """
        Load existing session if in-progress, otherwise create fresh.
        Returns the state dict. Call this on startup after client is chosen.
        """
        existing = state_mod.load(self.client_path)
        if state_mod.is_in_progress(existing):
            self._state = existing
            print(f"  ✓ Resumed session — {state_mod.format_summary(self._state)}")
        else:
            self._state = state_mod.new_session(self.client, self.client_path)
            print(f"  ✓ New session started for {self.client}")
        return self._state

    def start_fresh(self):
        """
        Archive current session (if any) and start a new one.
        Data files are preserved — only session pointer resets.
        """
        existing = state_mod.load(self.client_path)
        if existing:
            archive_mod.archive_session(self.client_path, existing)
        self._state = state_mod.new_session(self.client, self.client_path)
        print(f"  ✓ Fresh session started for {self.client}")

    def has_active_session(self) -> bool:
        """Return True if an in-progress session exists on disk."""
        return state_mod.is_in_progress(state_mod.load(self.client_path))

    def get_existing_state(self) -> dict:
        """Peek at existing session state without loading it."""
        return state_mod.load(self.client_path)

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def log(self, action: str, details: str, extra: dict = None):
        """Append an entry to the activity log."""
        log_mod.append(self.client_path, action, details, extra)

    def show_model_runs(self):
        """Display model runs and metrics from the log."""
        log_mod.show_model_runs(self.client_path)

    def show_full_log(self):
        """Display the full activity log."""
        log_mod.show_full_log(self.client_path)

    # ------------------------------------------------------------------
    # State updates — each wraps state_mod and auto-saves
    # ------------------------------------------------------------------

    def save(self):
        """Persist current state to session.json."""
        if self._state:
            state_mod.save(self.client_path, self._state)

    def update_checkpoint(self, name: str, shape: list,
                          label: str = None, file: str = None):
        self._state = state_mod.update_checkpoint(
            self._state, name, shape, label, file)
        self.save()

    def update_feature_set(self, features_in: int, features_out: int,
                           dataset_checkpoint: str, config: dict):
        self._state = state_mod.update_feature_set(
            self._state, features_in, features_out, dataset_checkpoint, config)
        self.save()

    def update_models(self, trained: list,
                      winner: str = None, best_lift: float = None):
        self._state = state_mod.update_models(
            self._state, trained, winner, best_lift)
        self.save()

    def mark_exported(self, models_exported: list):
        self._state = state_mod.mark_exported(self._state, models_exported)
        self.save()

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    @property
    def state(self) -> dict:
        return self._state

    @property
    def target(self) -> str:
        return self._state.get('target', 'IsTarget') if self._state else 'IsTarget'

    @property
    def active_checkpoint(self) -> str:
        return self._state.get('active_checkpoint', 'scratch') if self._state else 'scratch'

    @property
    def has_feature_set(self) -> bool:
        return self._state.get('feature_set', {}).get('exists', False) if self._state else False

    @property
    def model_count(self) -> int:
        return self._state.get('models', {}).get('count', 0) if self._state else 0

    def summary_line(self) -> str:
        return state_mod.format_summary(self._state)

    # ------------------------------------------------------------------
    # Archive
    # ------------------------------------------------------------------

    def show_archives(self):
        archive_mod.show_archives(self.client_path)


__all__ = ['SessionManager']
