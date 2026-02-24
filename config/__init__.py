"""
config/__init__.py
==================
Public API for the config package.

Backward compatible: old code that did
    from config import get_client_path, create_folder_structure
will still work.
"""

from config.settings import (
    BASE_DIR,
    FOLDER_STRUCTURE,
    DEFAULT_TEST_SIZE,
    DEFAULT_RANDOM_STATE,
    DEFAULT_TARGET,
    AUTO_DROP_PREFIXES,
    AUTO_DROP_COLUMNS,
    DEFAULT_MISSING_THRESHOLD,
    DEFAULT_VARIANCE_THRESHOLD,
    DEFAULT_CARDINALITY_THRESHOLD,
    DEFAULT_COLLINEARITY_THRESHOLD,
)

from config.folder_structure import (
    get_client_path,
    create_folder_structure,
    list_clients,
    get_paths,
)

__all__ = [
    'BASE_DIR', 'FOLDER_STRUCTURE',
    'DEFAULT_TEST_SIZE', 'DEFAULT_RANDOM_STATE', 'DEFAULT_TARGET',
    'AUTO_DROP_PREFIXES', 'AUTO_DROP_COLUMNS',
    'DEFAULT_MISSING_THRESHOLD', 'DEFAULT_VARIANCE_THRESHOLD',
    'DEFAULT_CARDINALITY_THRESHOLD', 'DEFAULT_COLLINEARITY_THRESHOLD',
    'get_client_path', 'create_folder_structure', 'list_clients', 'get_paths',
]
