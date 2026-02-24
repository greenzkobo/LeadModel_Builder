"""
evaluation/__init__.py
=======================
Public API for the evaluation package.
"""

from .metrics import (
    lift_at_decile,
    gains_at_decile,
    ks_statistic,
    calculate_all_metrics,
    get_confusion_matrix,
)
from .decile import build_decile_table, show_decile_table

__all__ = [
    'lift_at_decile', 'gains_at_decile', 'ks_statistic',
    'calculate_all_metrics', 'get_confusion_matrix',
    'build_decile_table', 'show_decile_table',
]
