"""
Delivery and Match Data Cleaning Module
"""

import pandas as pd
import numpy as np


def filter_valid_deliveries(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter valid deliveries:
    - Retains legitimate match deliveries.
    - Flags or handles extras (wides, no-balls) consistently with ICC T20 rules.
    - Excludes corrupted or abandoned partial deliveries.
    """
    clean_df = df.copy()

    # Filter out abandoned / partial matches if recorded
    if 'is_abandoned' in clean_df.columns:
        clean_df = clean_df[~clean_df['is_abandoned'].astype(bool)]

    # Standardize wide/no-ball indicators
    if 'is_wide' in clean_df.columns:
        clean_df['is_legal_ball'] = ~(clean_df['is_wide'].fillna(0).astype(bool) | 
                                      clean_df['is_no_ball'].fillna(0).astype(bool))
    elif 'wides' in clean_df.columns:
        clean_df['is_legal_ball'] = (clean_df['wides'].fillna(0) == 0) & (clean_df['noballs'].fillna(0) == 0)

    return clean_df
