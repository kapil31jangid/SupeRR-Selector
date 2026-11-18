"""
Dashboard Data Loader
Loads and caches verified CSV datasets from outputs/ directory.
"""

from pathlib import Path
from typing import Dict, Tuple
import pandas as pd
import streamlit as st

from src.utilities.paths import OUTPUTS_DIR, SUPPORTING_EVIDENCE_DIR


@st.cache_data
def load_final_batters() -> pd.DataFrame:
    """Load verified final Top 10 batters."""
    df = pd.read_csv(OUTPUTS_DIR / "final_combined_top10_batters.csv")
    return df


@st.cache_data
def load_final_bowlers() -> pd.DataFrame:
    """Load verified final Top 10 bowlers."""
    df = pd.read_csv(OUTPUTS_DIR / "final_combined_top10_bowlers.csv")
    return df


@st.cache_data
def load_final_reserves() -> pd.DataFrame:
    """Load verified final reserves."""
    df = pd.read_csv(OUTPUTS_DIR / "final_combined_reserves.csv")
    return df


@st.cache_data
def load_scouting_priority_scores() -> pd.DataFrame:
    """Load full candidate pool 4-dimension scouting scores."""
    p = SUPPORTING_EVIDENCE_DIR / "rr_scouting_priority_scores.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_bowling_deployment() -> pd.DataFrame:
    """Load verified bowling deployment boundaries."""
    p = SUPPORTING_EVIDENCE_DIR / "bowling_deployment_validation.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_zero_opportunity_audit() -> pd.DataFrame:
    """Load bowling phase delivery counts."""
    p = SUPPORTING_EVIDENCE_DIR / "bowling_zero_opportunity_audit.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_current_form_audit() -> pd.DataFrame:
    """Load verified current form evidence logs."""
    p = SUPPORTING_EVIDENCE_DIR / "current_form_source_verification.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_retained_players() -> pd.DataFrame:
    """Load 184 excluded retained players."""
    p = SUPPORTING_EVIDENCE_DIR / "retained_players.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


def get_all_shortlist_players() -> pd.DataFrame:
    """Combine batters, bowlers and reserves for lookup."""
    batters = load_final_batters().copy()
    batters['role'] = 'Batter'
    bowlers = load_final_bowlers().copy()
    bowlers['role'] = 'Bowler'
    reserves = load_final_reserves().copy()

    # Standardize score columns
    batters['pressure_or_eq_score'] = batters['validated_historical_pressure_score']
    bowlers['pressure_or_eq_score'] = bowlers['validated_evidence_qualified_score']
    reserves['pressure_or_eq_score'] = reserves['validated_pressure_or_eq_score']

    common_cols = ['player_id', 'player_name', 'role', 'country', 'nationality',
                   'age_as_of_2027_04_01', 'development_category', 'pressure_or_eq_score',
                   'verified_rr_scouting_score', 'current_form_rating']

    combined = pd.concat([
        batters[common_cols],
        bowlers[common_cols],
        reserves[common_cols]
    ], ignore_index=True)
    return combined
