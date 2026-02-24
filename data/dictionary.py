"""
Data Dictionary Script
======================
Look up column descriptions from the data dictionary.

Usage:
    from data_dictionary import DataDictionary
    
    dd = DataDictionary(client="Humana")
    dd.lookup("tw_winelover")
    dd.show_columns(df)
"""

import os
import pandas as pd
from config import get_client_path, create_folder_structure, BASE_DIR


class DataDictionary:
    """
    Load and query the data dictionary for column descriptions.
    """
    
    def __init__(self, dict_path: str = None, client: str = None):
        """
        Initialize data dictionary.
        
        Parameters:
        -----------
        dict_path : str, optional
            Path to data dictionary CSV. If None, looks in client folder or base folder.
        client : str, optional
            Client name (to look for dictionary in client folder)
        """
        self.client = client
        self.dict_df = None
        self.column_map = {}
        
        # Try to find dictionary file
        if dict_path and os.path.exists(dict_path):
            self._load_dictionary(dict_path)
        else:
            # Search in common locations
            search_paths = []
            
            if client:
                client_path = get_client_path(client)
                search_paths.append(os.path.join(client_path, 'data_dictionary.csv'))
                search_paths.append(os.path.join(client_path, 'List_Installs_Data_Dictionary.csv'))
            
            search_paths.append(os.path.join(BASE_DIR, 'data_dictionary.csv'))
            search_paths.append(os.path.join(BASE_DIR, 'List_Installs_Data_Dictionary.csv'))
            search_paths.append(os.path.join(BASE_DIR, 'List_Installs_Data_Dictionary__1_.csv'))
            
            for path in search_paths:
                if os.path.exists(path):
                    self._load_dictionary(path)
                    break
            
            if self.dict_df is None:
                print("  ⚠ Data dictionary not found.")
                print("  Place 'data_dictionary.csv' in your client folder or base folder.")
                print(f"  Base folder: {BASE_DIR}")
    
    def _load_dictionary(self, path: str):
        """Load the data dictionary CSV."""
        try:
            self.dict_df = pd.read_csv(path, encoding='utf-8', on_bad_lines='skip')
            self._build_column_map()
            print(f"  ✓ Loaded data dictionary: {os.path.basename(path)}")
            print(f"    {len(self.column_map)} column definitions found")
        except Exception as e:
            print(f"  ✗ Error loading dictionary: {e}")
    
    def _build_column_map(self):
        """Build a mapping of column names to descriptions."""
        if self.dict_df is None:
            return
        
        # Try to identify the column name and description columns
        # Common column names in data dictionaries
        name_candidates = ['DATABASE ITEM NAME', 'FIELD NAME', 'Column', 'column', 'Name', 'name', 
                          'Variable', 'variable', 'RAW LAYOUT NAME', 'Field']
        desc_candidates = ['FIELD DESCRIPTION', 'Description', 'description', 'Desc', 'desc',
                          'Definition', 'definition', 'DESCRIPTION']
        
        name_col = None
        desc_col = None
        
        for col in self.dict_df.columns:
            col_lower = col.lower().strip()
            if name_col is None and any(c.lower() in col_lower for c in name_candidates):
                name_col = col
            if desc_col is None and any(c.lower() in col_lower for c in desc_candidates):
                desc_col = col
        
        if name_col is None or desc_col is None:
            print(f"  ⚠ Could not identify name/description columns.")
            print(f"    Columns found: {list(self.dict_df.columns)}")
            return
        
        # Also look for the actual field names in layout columns
        layout_candidates = ['List Install', 'Universe', 'Balance']
        layout_cols = [c for c in self.dict_df.columns if any(lc in c for lc in layout_candidates)]
        
        # Build the map
        for _, row in self.dict_df.iterrows():
            name = str(row[name_col]).strip().lower() if pd.notna(row[name_col]) else None
            desc = str(row[desc_col]).strip() if pd.notna(row[desc_col]) else ""
            
            if name and name != 'nan':
                self.column_map[name] = desc
            
            # Also map from layout column names (these often have the actual field names)
            for lc in layout_cols:
                if pd.notna(row[lc]):
                    field_names = str(row[lc]).strip().split('\n')
                    for fn in field_names:
                        fn_clean = fn.strip().lower()
                        if fn_clean and fn_clean != 'nan':
                            self.column_map[fn_clean] = desc
    
    def lookup(self, column_name: str) -> str:
        """
        Look up description for a single column.
        
        Parameters:
        -----------
        column_name : str
            Column name to look up
        
        Returns:
        --------
        str : Description or "Not found"
        """
        name_lower = column_name.lower().strip()
        
        if name_lower in self.column_map:
            return self.column_map[name_lower]
        
        # Try partial match
        for key, desc in self.column_map.items():
            if name_lower in key or key in name_lower:
                return f"(Partial match: {key}) {desc}"
        
        return "Not found in data dictionary"
    
    def lookup_multiple(self, column_names: list) -> pd.DataFrame:
        """
        Look up descriptions for multiple columns.
        
        Parameters:
        -----------
        column_names : list
            List of column names
        
        Returns:
        --------
        pd.DataFrame with columns and descriptions
        """
        results = []
        for col in column_names:
            results.append({
                'Column': col,
                'Description': self.lookup(col)
            })
        return pd.DataFrame(results)
    
    def show_columns(self, df: pd.DataFrame, save: bool = False, client: str = None):
        """
        Show descriptions for all columns in a dataframe.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Dataframe to describe
        save : bool, default False
            Save to Excel file
        client : str, optional
            Client name for saving
        """
        print(f"\n{'='*80}")
        print(f"COLUMN DESCRIPTIONS ({len(df.columns)} columns)")
        print('='*80)
        
        results = []
        found = 0
        not_found = 0
        
        for col in df.columns:
            desc = self.lookup(col)
            if desc != "Not found in data dictionary":
                found += 1
            else:
                not_found += 1
            
            results.append({
                'Column': col,
                'Description': desc[:100] + '...' if len(desc) > 100 else desc
            })
        
        # Print summary
        print(f"\n  Found descriptions: {found}")
        print(f"  Not found: {not_found}")
        
        # Print table
        print(f"\n  {'Column':<40} {'Description':<60}")
        print(f"  {'-'*40} {'-'*60}")
        
        for r in results[:50]:  # Show first 50
            col_display = r['Column'][:38] if len(r['Column']) > 38 else r['Column']
            desc_display = r['Description'][:58] if len(r['Description']) > 58 else r['Description']
            print(f"  {col_display:<40} {desc_display:<60}")
        
        if len(results) > 50:
            print(f"\n  ... and {len(results) - 50} more columns")
        
        # Save if requested
        if save and client:
            results_df = pd.DataFrame(results)
            client_path = get_client_path(client)
            report_path = os.path.join(client_path, 'reports', 'column_descriptions.xlsx')
            results_df.to_excel(report_path, index=False)
            print(f"\n  ✓ Saved: reports/column_descriptions.xlsx")
        
        print(f"\n{'='*80}\n")
        
        return pd.DataFrame(results)
    
    def search(self, keyword: str) -> pd.DataFrame:
        """
        Search for columns containing a keyword in name or description.
        
        Parameters:
        -----------
        keyword : str
            Keyword to search for
        
        Returns:
        --------
        pd.DataFrame with matching columns
        """
        keyword_lower = keyword.lower()
        results = []
        
        for col, desc in self.column_map.items():
            if keyword_lower in col.lower() or keyword_lower in desc.lower():
                results.append({
                    'Column': col,
                    'Description': desc[:100] + '...' if len(desc) > 100 else desc
                })
        
        print(f"\n  Found {len(results)} columns matching '{keyword}':\n")
        for r in results[:20]:
            print(f"    {r['Column']:<35} {r['Description'][:50]}")
        
        if len(results) > 20:
            print(f"\n    ... and {len(results) - 20} more")
        
        return pd.DataFrame(results)
    
    def show_by_prefix(self, prefix: str) -> pd.DataFrame:
        """
        Show all columns with a given prefix.
        
        Parameters:
        -----------
        prefix : str
            Prefix to filter by (e.g., 'tw_', 'lhi_')
        
        Returns:
        --------
        pd.DataFrame with matching columns
        """
        prefix_lower = prefix.lower()
        results = []
        
        for col, desc in self.column_map.items():
            if col.startswith(prefix_lower):
                results.append({
                    'Column': col,
                    'Description': desc[:100] + '...' if len(desc) > 100 else desc
                })
        
        print(f"\n  Found {len(results)} columns with prefix '{prefix}':\n")
        print(f"  {'Column':<40} {'Description':<60}")
        print(f"  {'-'*40} {'-'*60}")
        
        for r in results[:30]:
            col_display = r['Column'][:38] if len(r['Column']) > 38 else r['Column']
            desc_display = r['Description'][:58] if len(r['Description']) > 58 else r['Description']
            print(f"  {col_display:<40} {desc_display:<60}")
        
        if len(results) > 30:
            print(f"\n  ... and {len(results) - 30} more")
        
        return pd.DataFrame(results)


# Quick test when run directly
if __name__ == "__main__":
    print("Data Dictionary Module")
    print("-" * 30)
    print("\nUsage:")
    print("  from data_dictionary import DataDictionary")
    print('  dd = DataDictionary(client="Humana")')
    print('  dd.lookup("tw_winelover")')
    print('  dd.show_columns(df)')
    print('  dd.search("income")')
    print('  dd.show_by_prefix("tw_")')
