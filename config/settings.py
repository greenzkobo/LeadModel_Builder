"""
config/settings.py
==================
Base directory, defaults, and shared constants.
Edit BASE_DIR to match your machine.
"""

import os

# Base directory where all client folders are stored
BASE_DIR = r"C:\Users\tjdch\OneDrive\Desktop\Campeche Model Creation"

# Standard folder structure for each client
FOLDER_STRUCTURE = {
    "data": {
        "raw": None,
        "versions": None
    },
    "models": None,
    "outputs": {
        "visualizations": None,
        "scoring_code": None
    },
    "reports": None
}

# Default model parameters
DEFAULT_TEST_SIZE = 0.30
DEFAULT_RANDOM_STATE = 42
DEFAULT_TARGET = "IsTarget"

# Auto-drop prefixes (household/member columns)
AUTO_DROP_PREFIXES = [
    'ind_1_', 'ind_2_',
    'member_2_', 'member_3_', 'member_4_', 'member_5_', 'member_6_',
]

# Auto-drop identifier-style columns
AUTO_DROP_COLUMNS = [
    'RecordId', 'record_id', 'zipcode', 'zip_code', 'address',
    'householdsize', 'numberofadults', 'numberofchildren',
]

# Feature selection defaults
DEFAULT_MISSING_THRESHOLD = 50      # % missing to flag
DEFAULT_VARIANCE_THRESHOLD = 0.01   # near-zero variance cutoff
DEFAULT_CARDINALITY_THRESHOLD = 100 # unique values for high cardinality
DEFAULT_COLLINEARITY_THRESHOLD = 0.85
