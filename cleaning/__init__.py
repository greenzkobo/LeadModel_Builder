"""
cleaning/__init__.py
=====================
Public API for the cleaning package.

Usage (unchanged from old data_cleaning.py):
    from cleaning import DataCleaner

    cleaner = DataCleaner(df, client="Humana")
    cleaner.drop_columns(['RecordId', 'zipcode'])
    cleaner.drop_columns_by_prefix(['ind_1_', 'ind_2_'])
    cleaner.drop_columns_by_missing(threshold=50)
    cleaner.save_version("v1_cleaned")
    df_clean = cleaner.get_data()
"""

import pandas as pd
from config import get_client_path, create_folder_structure, get_paths
from . import columns as col_ops
from . import rows as row_ops
from . import versioning
from .summary import CleaningHistory


class DataCleaner:
    """
    Interactive data cleaning with version control.
    Delegates to focused sub-modules for each operation type.
    """

    def __init__(self, df: pd.DataFrame, client: str, protected_cols: list = None):
        self.original_df = df.copy()
        self.df = df.copy()
        self.client = client
        self._history = CleaningHistory()
        self.protected_cols = protected_cols or []

        create_folder_structure(client)
        paths = get_paths(client)
        self.client_path = paths['client']
        self.versions_path = paths['versions']

        print(f"\n{'='*60}")
        print(f"DATA CLEANER: {client}")
        print('='*60)
        print(f"  Starting shape: {self.df.shape[0]:,} rows × {self.df.shape[1]:,} columns")
        print(f"{'='*60}\n")

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def get_data(self) -> pd.DataFrame:
        return self.df.copy()

    def get_shape(self) -> tuple:
        return self.df.shape

    def get_columns(self) -> list:
        return self.df.columns.tolist()

    def reset(self):
        self.df = self.original_df.copy()
        self._history.clear()
        print(f"  ✓ Reset to original: {self.df.shape[0]:,} × {self.df.shape[1]:,}")

    def show_history(self):
        self._history.show(self.df.shape)

    def get_cleaning_summary(self) -> dict:
        """Return history as dict (used by experiment logger)."""
        return {
            'shape_original': self.original_df.shape,
            'shape_current':  self.df.shape,
            'history':        self._history.to_dict(),
        }

    # ------------------------------------------------------------------
    # Column operations
    # ------------------------------------------------------------------

    def _record(self, action, details, cb, rb):
        self._history.record(action, details, cb, len(self.df.columns), rb, len(self.df))

    def drop_columns(self, columns: list):
        cb, rb = len(self.df.columns), len(self.df)
        columns = [c for c in columns if c not in self.protected_cols]
        self.df, dropped = col_ops.drop_by_name(self.df, columns)
        self._record("drop_columns", f"Dropped: {dropped[:3]}{'...' if len(dropped)>3 else ''}", cb, rb)

    def drop_columns_by_prefix(self, prefixes: list):
        cb, rb = len(self.df.columns), len(self.df)
        self.df, dropped = col_ops.drop_by_prefix(self.df, prefixes, exclude=self.protected_cols)
        self._record("drop_columns_by_prefix", f"Prefixes: {prefixes}", cb, rb)

    def drop_columns_by_suffix(self, suffixes: list):
        cb, rb = len(self.df.columns), len(self.df)
        self.df, dropped = col_ops.drop_by_suffix(self.df, suffixes)
        self._record("drop_columns_by_suffix", f"Suffixes: {suffixes}", cb, rb)

    def drop_columns_by_pattern(self, pattern: str):
        cb, rb = len(self.df.columns), len(self.df)
        self.df, dropped = col_ops.drop_by_pattern(self.df, pattern)
        self._record("drop_columns_by_pattern", f"Pattern: {pattern}", cb, rb)

    def drop_columns_by_missing(self, threshold: float = 50, exclude: list = None):
        cb, rb = len(self.df.columns), len(self.df)
        combined_exclude = list(set((exclude or []) + self.protected_cols))
        self.df, dropped = col_ops.drop_by_missing(self.df, threshold, combined_exclude)
        self._record("drop_columns_by_missing", f"Threshold: {threshold}%", cb, rb)

    def drop_low_variance(self, threshold: float = 0.01, exclude: list = None):
        cb, rb = len(self.df.columns), len(self.df)
        combined_exclude = list(set((exclude or []) + self.protected_cols))
        self.df, dropped = col_ops.drop_low_variance(self.df, threshold, combined_exclude)
        self._record("drop_low_variance", f"Threshold: {threshold}", cb, rb)

    def keep_columns(self, columns: list, always_keep: list = None):
        cb, rb = len(self.df.columns), len(self.df)
        self.df, dropped = col_ops.keep_by_name(self.df, columns, always_keep)
        self._record("keep_columns", f"Kept {len(columns)} cols", cb, rb)

    def add_column(self, name: str, values):
        cb, rb = len(self.df.columns), len(self.df)
        self.df = col_ops.add_column(self.df, name, values)
        self._record("add_column", f"Added: {name}", cb, rb)

    def add_column_formula(self, name: str, formula: str):
        cb, rb = len(self.df.columns), len(self.df)
        self.df = col_ops.add_column_formula(self.df, name, formula)
        self._record("add_column_formula", f"{name} = {formula}", cb, rb)

    # ------------------------------------------------------------------
    # Row operations
    # ------------------------------------------------------------------

    def drop_rows_by_condition(self, condition: str):
        cb, rb = len(self.df.columns), len(self.df)
        self.df, count = row_ops.drop_by_condition(self.df, condition)
        self._record("drop_rows_by_condition", f"Where: {condition}", cb, rb)

    def drop_rows_missing_target(self, target: str = "IsTarget"):
        cb, rb = len(self.df.columns), len(self.df)
        self.df, count = row_ops.drop_missing_target(self.df, target)
        self._record("drop_rows_missing_target", f"Target: {target}", cb, rb)

    def drop_duplicates(self, subset: list = None):
        cb, rb = len(self.df.columns), len(self.df)
        self.df, count = row_ops.drop_duplicates(self.df, subset)
        self._record("drop_duplicates", f"Subset: {subset}", cb, rb)

    def filter_by_value(self, column: str, values: list, keep: bool = True):
        cb, rb = len(self.df.columns), len(self.df)
        self.df, count = row_ops.filter_by_value(self.df, column, values, keep)
        self._record("filter_by_value", f"{column} in {values} (keep={keep})", cb, rb)

    # ------------------------------------------------------------------
    # Version control
    # ------------------------------------------------------------------

    def save_version(self, name: str):
        versioning.save_version(self.df, self.versions_path, name)

    def load_version(self, name: str):
        df = versioning.load_version(self.versions_path, name)
        if df is not None:
            self.df = df

    def list_versions(self) -> list:
        return versioning.list_versions(self.versions_path)

    def show_versions(self):
        versioning.show_versions(self.versions_path)


__all__ = ['DataCleaner']
