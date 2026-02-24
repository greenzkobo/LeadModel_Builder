"""
menu/actions.py
================
Re-exports all action handlers from the data and model sub-modules.
Import from here so main.py has a single import point.
"""

from menu.actions_data import (
    action_data_ingestion,
    action_data_profiling,
    action_data_cleaning,
    action_feature_selection,
)

from menu.actions_models import (
    action_model_training,
    action_model_evaluation,
    action_visualizations,
    action_export,
    action_generate_report,
    action_view_log,
    action_settings,
)

__all__ = [
    'action_data_ingestion', 'action_data_profiling',
    'action_data_cleaning',  'action_feature_selection',
    'action_model_training', 'action_model_evaluation',
    'action_visualizations', 'action_export',
    'action_generate_report','action_view_log',
    'action_settings',
]
