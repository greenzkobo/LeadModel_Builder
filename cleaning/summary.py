"""
cleaning/summary.py
====================
Tracks and displays the cleaning change history.
Used internally by DataCleaner — not called directly by users.
"""

from datetime import datetime


class CleaningHistory:
    """Tracks all changes made during cleaning for audit trail and logging."""

    def __init__(self):
        self.history = []

    def record(self, action: str, details: str,
               cols_before: int, cols_after: int,
               rows_before: int, rows_after: int):
        """Record a cleaning action."""
        self.history.append({
            'timestamp':   datetime.now().strftime("%H:%M:%S"),
            'action':      action,
            'details':     details,
            'cols_removed': cols_before - cols_after,
            'rows_removed': rows_before - rows_after,
            'shape_after': (rows_after, cols_after),
        })

    def clear(self):
        """Clear all history (used on reset)."""
        self.history = []

    def show(self, current_shape: tuple):
        """Print the full change history."""
        print(f"\n{'='*60}")
        print("CHANGE HISTORY")
        print('='*60)

        if not self.history:
            print("  No changes made yet.")
        else:
            for i, h in enumerate(self.history, 1):
                print(f"\n  [{i}] {h['timestamp']} - {h['action']}")
                print(f"      {h['details']}")
                print(f"      Removed: {h['cols_removed']} cols, {h['rows_removed']} rows")
                print(f"      Shape after: {h['shape_after'][0]:,} × {h['shape_after'][1]:,}")

        rows, cols = current_shape
        print(f"\n  Current shape: {rows:,} rows × {cols:,} columns")
        print(f"{'='*60}\n")

    def to_dict(self) -> list:
        """Return history as a list of dicts (for experiment logging)."""
        return self.history.copy()

    def get_all_dropped_columns(self) -> list:
        """Aggregate all columns dropped across all actions."""
        dropped = []
        for h in self.history:
            if 'dropped_columns' in h:
                dropped.extend(h['dropped_columns'])
        return dropped
