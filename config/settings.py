"""
config/settings.py
==================
Base directory, defaults, and shared constants.
BASE_DIR is detected automatically based on environment.
"""

import os

# ── Base directory ─────────────────────────────────────────────────────────────
# On Hugging Face / Linux: uses /app/client_data
# On local Windows:        uses the folder next to this project
def _get_base_dir() -> str:
    # Hugging Face Spaces — writable directory
    if os.path.exists("/app"):
        data_dir = "/app/client_data"
        os.makedirs(data_dir, exist_ok=True)
        return data_dir

    # Local Windows — use the project's parent folder
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, "client_data")

BASE_DIR = _get_base_dir()

# ── Folder structure per client ────────────────────────────────────────────────
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

# ── Model defaults ─────────────────────────────────────────────────────────────
DEFAULT_TEST_SIZE        = 0.30
DEFAULT_RANDOM_STATE     = 42
DEFAULT_TARGET           = "IsTarget"

# ── Auto-drop prefixes (household/member columns) ──────────────────────────────
AUTO_DROP_PREFIXES = [
    'ind_1_', 'ind_2_',
    'member_2_', 'member_3_', 'member_4_', 'member_5_', 'member_6_',
]

# ── Auto-drop identifier-style columns ─────────────────────────────────────────
AUTO_DROP_COLUMNS = [
    'RecordId', 'record_id', 'zipcode', 'zip_code', 'address',
    'householdsize', 'numberofadults', 'numberofchildren',
]

# ── Feature selection defaults ─────────────────────────────────────────────────
DEFAULT_MISSING_THRESHOLD     = 50      # % missing to flag
DEFAULT_VARIANCE_THRESHOLD    = 0.01    # near-zero variance cutoff
DEFAULT_CARDINALITY_THRESHOLD = 100     # unique values for high cardinality
DEFAULT_COLLINEARITY_THRESHOLD = 0.85
