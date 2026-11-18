"""
Player Identity Normalization Module
Standardizes canonical database player IDs and aliases across competitions.
"""

from typing import Dict, Optional
import pandas as pd


# Canonical ID overrides verified in Task 07M Forensic Audit
CANONICAL_ID_MAPPINGS: Dict[int, int] = {
    1998: 7533,  # Simarjeet Singh (corrected from birth year typo)
    3807: 5034,  # Murugan Ashwin (corrected from truncated key)
    1991: 1071   # Jaydev Unadkat (corrected from birth year typo)
}

# Verified Name Aliases
CANONICAL_NAME_ALIASES: Dict[str, str] = {
    "Jake McGurk": "Jake Fraser-McGurk",
    "J Fraser-McGurk": "Jake Fraser-McGurk",
    "M Shahrukh Khan": "M Shahrukh Khan",
    "Shahrukh Khan": "M Shahrukh Khan",
    "Ripon Mondol": "Ripon Mondol",
    "Matthew Forde": "Matthew Forde",
    "Ben Sears": "Benjamin Sears"
}


def normalize_player_id(player_id: int) -> int:
    """Return verified canonical player ID."""
    return CANONICAL_ID_MAPPINGS.get(int(player_id), int(player_id))


def normalize_player_name(name: str) -> str:
    """Return standard player name."""
    clean_name = str(name).strip()
    return CANONICAL_NAME_ALIASES.get(clean_name, clean_name)


def standardize_player_dataframe(df: pd.DataFrame, id_col: str = 'player_id', name_col: str = 'player_name') -> pd.DataFrame:
    """Apply normalization across dataframe."""
    out = df.copy()
    if id_col in out.columns:
        out[id_col] = out[id_col].apply(lambda x: normalize_player_id(x) if pd.notna(x) else x)
    if name_col in out.columns:
        out[name_col] = out[name_col].apply(lambda x: normalize_player_name(x) if pd.notna(x) else x)
    return out

