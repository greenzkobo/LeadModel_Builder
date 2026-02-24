"""
Data Profiling Script
=====================
Generate summary statistics, missing value analysis, and predictor screening.

Usage:
    from data_profiling import profile_data
    
    profile = profile_data(df, client="Humana", target="IsTarget")
"""

import os
import pandas as pd
import numpy as np
from config import get_client_path, create_folder_structure


def calculate_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate missing value statistics for each column."""
    missing_count = df.isnull().sum()
    missing_pct = (missing_count / len(df)) * 100
    
    missing_df = pd.DataFrame({
        'Column': missing_count.index,
        'Missing_Count': missing_count.values,
        'Missing_Pct': missing_pct.values,
        'Present_Count': len(df) - missing_count.values,
        'Present_Pct': 100 - missing_pct.values
    })
    
    return missing_df.sort_values('Missing_Pct', ascending=False).reset_index(drop=True)


def calculate_numeric_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate summary statistics for numeric columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        return pd.DataFrame()
    
    stats = []
    for col in numeric_cols:
        col_data = df[col].dropna()
        stats.append({
            'Column': col,
            'Count': len(col_data),
            'Missing': df[col].isnull().sum(),
            'Missing_Pct': (df[col].isnull().sum() / len(df)) * 100,
            'Min': col_data.min() if len(col_data) > 0 else np.nan,
            'Max': col_data.max() if len(col_data) > 0 else np.nan,
            'Mean': col_data.mean() if len(col_data) > 0 else np.nan,
            'Median': col_data.median() if len(col_data) > 0 else np.nan,
            'Std': col_data.std() if len(col_data) > 0 else np.nan,
            'Zeros': (col_data == 0).sum() if len(col_data) > 0 else 0,
            'Zeros_Pct': ((col_data == 0).sum() / len(col_data) * 100) if len(col_data) > 0 else 0
        })
    
    return pd.DataFrame(stats)


def calculate_categorical_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate summary statistics for categorical columns."""
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if not cat_cols:
        return pd.DataFrame()
    
    stats = []
    for col in cat_cols:
        col_data = df[col].dropna()
        value_counts = col_data.value_counts()
        
        stats.append({
            'Column': col,
            'Count': len(col_data),
            'Missing': df[col].isnull().sum(),
            'Missing_Pct': (df[col].isnull().sum() / len(df)) * 100,
            'Unique_Values': col_data.nunique(),
            'Top_Value': value_counts.index[0] if len(value_counts) > 0 else np.nan,
            'Top_Value_Count': value_counts.iloc[0] if len(value_counts) > 0 else 0,
            'Top_Value_Pct': (value_counts.iloc[0] / len(col_data) * 100) if len(col_data) > 0 else 0
        })
    
    return pd.DataFrame(stats)


def predictor_screening(df: pd.DataFrame, target: str, top_n: int = 50) -> pd.DataFrame:
    """
    Quick predictor screening using correlation and basic importance.
    For numeric target: Pearson correlation
    For categorical target: Point-biserial correlation (treats target as 0/1)
    """
    if target not in df.columns:
        print(f"  Warning: Target '{target}' not found in data. Skipping predictor screening.")
        return pd.DataFrame()
    
    # Get numeric columns (excluding target)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if target in numeric_cols:
        numeric_cols.remove(target)
    
    if not numeric_cols:
        print("  Warning: No numeric columns for predictor screening.")
        return pd.DataFrame()
    
    # Calculate correlations with target
    target_series = pd.to_numeric(df[target], errors='coerce')
    
    correlations = []
    for col in numeric_cols:
        try:
            col_data = pd.to_numeric(df[col], errors='coerce')
            # Only calculate if we have enough non-null pairs
            valid_mask = ~(target_series.isnull() | col_data.isnull())
            if valid_mask.sum() > 10:
                corr = target_series[valid_mask].corr(col_data[valid_mask])
                correlations.append({
                    'Column': col,
                    'Correlation': corr,
                    'Abs_Correlation': abs(corr),
                    'Direction': 'Positive' if corr > 0 else 'Negative',
                    'Valid_Pairs': valid_mask.sum()
                })
        except Exception:
            continue
    
    if not correlations:
        return pd.DataFrame()
    
    corr_df = pd.DataFrame(correlations)
    corr_df = corr_df.sort_values('Abs_Correlation', ascending=False).reset_index(drop=True)
    corr_df['Rank'] = range(1, len(corr_df) + 1)
    
    # Calculate portion (like JMP)
    total_abs_corr = corr_df['Abs_Correlation'].sum()
    if total_abs_corr > 0:
        corr_df['Portion'] = corr_df['Abs_Correlation'] / total_abs_corr
    else:
        corr_df['Portion'] = 0
    
    return corr_df.head(top_n)


def print_summary(df: pd.DataFrame, missing_df: pd.DataFrame, 
                  numeric_stats: pd.DataFrame, cat_stats: pd.DataFrame,
                  predictor_df: pd.DataFrame, target: str):
    """Print summary to screen."""
    
    print(f"\n{'='*60}")
    print("DATA PROFILE SUMMARY")
    print('='*60)
    
    # Basic info
    print(f"\n  Total Rows: {len(df):,}")
    print(f"  Total Columns: {len(df.columns):,}")
    print(f"    - Numeric: {len(numeric_stats) if len(numeric_stats) > 0 else 0}")
    print(f"    - Categorical: {len(cat_stats) if len(cat_stats) > 0 else 0}")
    
    # Missing value summary
    cols_with_missing = (missing_df['Missing_Count'] > 0).sum()
    print(f"\n  Columns with missing values: {cols_with_missing}")
    
    if cols_with_missing > 0:
        high_missing = missing_df[missing_df['Missing_Pct'] > 50]
        if len(high_missing) > 0:
            print(f"  Columns with >50% missing: {len(high_missing)}")
            print(f"    Top 5: {list(high_missing['Column'].head())}")
    
    # Target distribution
    if target in df.columns:
        print(f"\n  Target Variable: {target}")
        target_counts = df[target].value_counts()
        print(f"    Distribution:")
        for val, count in target_counts.head(5).items():
            pct = count / len(df) * 100
            print(f"      {val}: {count:,} ({pct:.1f}%)")
    
    # Top predictors
    if len(predictor_df) > 0:
        print(f"\n  Top 10 Predictors (by correlation with {target}):")
        print(f"    {'Rank':<6} {'Column':<40} {'Corr':<10} {'Portion':<10}")
        print(f"    {'-'*66}")
        for _, row in predictor_df.head(10).iterrows():
            print(f"    {row['Rank']:<6} {row['Column'][:38]:<40} {row['Correlation']:>8.4f}  {row['Portion']:>8.4f}")
    
    print(f"\n{'='*60}\n")


def profile_data(df: pd.DataFrame, client: str, target: str = "IsTarget", 
                 top_n_predictors: int = 50, save_report: bool = True) -> dict:
    """
    Generate comprehensive data profile.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Data to profile
    client : str
        Client name (for saving report)
    target : str, default "IsTarget"
        Target variable name for predictor screening
    top_n_predictors : int, default 50
        Number of top predictors to return
    save_report : bool, default True
        Save report to Excel in reports/ folder
    
    Returns:
    --------
    dict with keys: 'missing', 'numeric_stats', 'categorical_stats', 'predictors'
    """
    print(f"\n{'='*60}")
    print(f"DATA PROFILING: {client}")
    print('='*60)
    
    # Ensure folder structure exists
    create_folder_structure(client)
    client_path = get_client_path(client)
    
    print("\n  Analyzing missing values...")
    missing_df = calculate_missing(df)
    
    print("  Calculating numeric statistics...")
    numeric_stats = calculate_numeric_stats(df)
    
    print("  Calculating categorical statistics...")
    cat_stats = calculate_categorical_stats(df)
    
    print(f"  Running predictor screening (target: {target})...")
    predictor_df = predictor_screening(df, target, top_n_predictors)
    
    # Print summary to screen
    print_summary(df, missing_df, numeric_stats, cat_stats, predictor_df, target)
    
    # Save to Excel
    if save_report:
        report_path = os.path.join(client_path, 'reports', 'data_profile.xlsx')
        
        with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Metric': ['Total Rows', 'Total Columns', 'Numeric Columns', 
                          'Categorical Columns', 'Columns with Missing', 'Target Variable'],
                'Value': [len(df), len(df.columns), len(numeric_stats), 
                         len(cat_stats), (missing_df['Missing_Count'] > 0).sum(), target]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # Missing values sheet
            missing_df.to_excel(writer, sheet_name='Missing_Values', index=False)
            
            # Numeric stats sheet
            if len(numeric_stats) > 0:
                numeric_stats.to_excel(writer, sheet_name='Numeric_Stats', index=False)
            
            # Categorical stats sheet
            if len(cat_stats) > 0:
                cat_stats.to_excel(writer, sheet_name='Categorical_Stats', index=False)
            
            # Predictor screening sheet
            if len(predictor_df) > 0:
                predictor_df.to_excel(writer, sheet_name='Predictor_Screening', index=False)
        
        print(f"  ✓ Report saved: reports/data_profile.xlsx")
    
    return {
        'missing': missing_df,
        'numeric_stats': numeric_stats,
        'categorical_stats': cat_stats,
        'predictors': predictor_df
    }


# Quick test when run directly
if __name__ == "__main__":
    print("Data Profiling Module")
    print("-" * 30)
    print("\nUsage:")
    print("  from data_profiling import profile_data")
    print('  profile = profile_data(df, client="Humana", target="IsTarget")')
