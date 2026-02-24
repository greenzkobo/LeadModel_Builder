"""
config/folder_structure.py
===========================
Client folder creation and path utilities.
"""

import os
from config.settings import BASE_DIR, FOLDER_STRUCTURE


def get_client_path(client: str) -> str:
    """Get full path to client folder."""
    return os.path.join(BASE_DIR, client)


def create_folder_structure(client: str) -> str:
    """
    Create standard folder structure for a client.
    Returns the client path.
    """
    client_path = get_client_path(client)

    def _create_folders(base_path, structure):
        for folder, subfolders in structure.items():
            folder_path = os.path.join(base_path, folder)
            os.makedirs(folder_path, exist_ok=True)
            if subfolders:
                _create_folders(folder_path, subfolders)

    _create_folders(client_path, FOLDER_STRUCTURE)
    print(f"✓ Folder structure ready: {client_path}")
    return client_path


def list_clients() -> list:
    """List all existing client folders."""
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR, exist_ok=True)
        return []

    clients = [
        d for d in os.listdir(BASE_DIR)
        if os.path.isdir(os.path.join(BASE_DIR, d))
    ]
    return sorted(clients)


def get_paths(client: str) -> dict:
    """
    Return all standard paths for a client as a dict.
    Convenient so modules don't have to build paths manually.
    """
    base = get_client_path(client)
    return {
        'client':        base,
        'raw':           os.path.join(base, 'data', 'raw'),
        'versions':      os.path.join(base, 'data', 'versions'),
        'models':        os.path.join(base, 'models'),
        'visualizations':os.path.join(base, 'outputs', 'visualizations'),
        'scoring_code':  os.path.join(base, 'outputs', 'scoring_code'),
        'reports':       os.path.join(base, 'reports'),
    }
