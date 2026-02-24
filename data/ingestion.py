"""
Data Ingestion Script
=====================
Load CSV/TXT files from client folder into pandas DataFrame.

Usage:
    from data_ingestion import load_data
    
    df = load_data(client="Humana")
"""

import os
import pandas as pd
from config import get_client_path, create_folder_structure, BASE_DIR


def detect_delimiter(file_path: str, n_lines: int = 5) -> str:
    """
    Auto-detect delimiter by checking first few lines.
    Default: tab. Also checks for comma and pipe.
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        sample = ''.join([f.readline() for _ in range(n_lines)])
    
    # Count occurrences of each delimiter
    tab_count = sample.count('\t')
    comma_count = sample.count(',')
    pipe_count = sample.count('|')
    
    counts = {'\t': tab_count, ',': comma_count, '|': pipe_count}
    delimiter = max(counts, key=counts.get)
    
    delimiter_names = {'\t': 'tab', ',': 'comma', '|': 'pipe'}
    print(f"  Detected delimiter: {delimiter_names[delimiter]}")
    
    return delimiter


def list_data_files(client_path: str) -> list:
    """
    Find all CSV and TXT files in the client folder.
    Looks in root and data/raw subfolder.
    """
    valid_extensions = ('.csv', '.txt')
    files = []
    
    # Check root client folder
    for f in os.listdir(client_path):
        if f.lower().endswith(valid_extensions):
            files.append(os.path.join(client_path, f))
    
    # Check data/raw subfolder if exists
    raw_path = os.path.join(client_path, 'data', 'raw')
    if os.path.exists(raw_path):
        for f in os.listdir(raw_path):
            if f.lower().endswith(valid_extensions):
                files.append(os.path.join(raw_path, f))
    
    return files


def select_file(files: list) -> str:
    """
    If multiple files, show numbered list and let user pick.
    """
    if len(files) == 0:
        raise FileNotFoundError("No CSV or TXT files found in client folder.")
    
    if len(files) == 1:
        print(f"  Found file: {os.path.basename(files[0])}")
        return files[0]
    
    # Multiple files - let user choose
    print("\n  Multiple data files found:")
    for i, f in enumerate(files, 1):
        print(f"    {i}. {os.path.basename(f)}")
    
    while True:
        try:
            choice = int(input("\n  Enter number to select file: "))
            if 1 <= choice <= len(files):
                return files[choice - 1]
            print(f"  Please enter a number between 1 and {len(files)}")
        except ValueError:
            print("  Please enter a valid number")


def load_data(client: str, file_path: str = None, save_parquet: bool = True) -> pd.DataFrame:
    """
    Load data from client folder.
    
    Parameters:
    -----------
    client : str
        Client name (folder name in Campeche Model Creation)
    file_path : str, optional
        Specific file to load. If None, scans folder for CSV/TXT files.
    save_parquet : bool, default True
        Save ingested data as parquet in data/raw/ for faster future loading.
    
    Returns:
    --------
    pd.DataFrame
        Loaded data
    """
    print(f"\n{'='*50}")
    print(f"DATA INGESTION: {client}")
    print('='*50)
    
    # Create folder structure if needed
    client_path = create_folder_structure(client)
    
    # Find or select file
    if file_path is None:
        files = list_data_files(client_path)
        file_path = select_file(files)
    
    print(f"\n  Loading: {os.path.basename(file_path)}")
    
    # Detect delimiter
    delimiter = detect_delimiter(file_path)
    
    # Load data
    try:
        df = pd.read_csv(
            file_path, 
            delimiter=delimiter,
            low_memory=False,
            encoding='utf-8',
            on_bad_lines='warn'
        )
    except UnicodeDecodeError:
        # Try latin-1 encoding as fallback
        df = pd.read_csv(
            file_path, 
            delimiter=delimiter,
            low_memory=False,
            encoding='latin-1',
            on_bad_lines='warn'
        )
    
    print(f"\n  ✓ Loaded successfully!")
    print(f"    Rows: {len(df):,}")
    print(f"    Columns: {len(df.columns):,}")
    
    # Save as parquet for faster future loading
    if save_parquet:
        parquet_path = os.path.join(client_path, 'data', 'raw', 'ingested_data.parquet')
        df.to_parquet(parquet_path, index=False)
        print(f"    Saved to: data/raw/ingested_data.parquet")
    
    # Quick preview
    print(f"\n  Column types:")
    type_counts = df.dtypes.value_counts()
    for dtype, count in type_counts.items():
        print(f"    {dtype}: {count}")
    
    print(f"\n  First 5 columns: {list(df.columns[:5])}")
    print(f"  Last 5 columns: {list(df.columns[-5:])}")
    
    print(f"\n{'='*50}\n")
    
    return df


def load_parquet(client: str, version: str = None) -> pd.DataFrame:
    """
    Load previously saved parquet file.
    
    Parameters:
    -----------
    client : str
        Client name
    version : str, optional
        Version name to load from data/versions/. 
        If None, loads from data/raw/ingested_data.parquet
    
    Returns:
    --------
    pd.DataFrame
    """
    client_path = get_client_path(client)
    
    if version:
        parquet_path = os.path.join(client_path, 'data', 'versions', f'{version}.parquet')
    else:
        parquet_path = os.path.join(client_path, 'data', 'raw', 'ingested_data.parquet')
    
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"File not found: {parquet_path}")
    
    df = pd.read_parquet(parquet_path)
    print(f"✓ Loaded: {parquet_path}")
    print(f"  Rows: {len(df):,} | Columns: {len(df.columns):,}")
    
    return df


def list_versions(client: str) -> list:
    """List all saved versions for a client."""
    versions_path = os.path.join(get_client_path(client), 'data', 'versions')
    
    if not os.path.exists(versions_path):
        return []
    
    versions = [
        f.replace('.parquet', '') 
        for f in os.listdir(versions_path) 
        if f.endswith('.parquet')
    ]
    return sorted(versions)


# Quick test when run directly
if __name__ == "__main__":
    print("Data Ingestion Module")
    print("-" * 30)
    print(f"Base directory: {BASE_DIR}")
    print("\nUsage:")
    print("  from data_ingestion import load_data")
    print('  df = load_data(client="Humana")')
