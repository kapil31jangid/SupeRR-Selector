#!/usr/bin/env python3
"""
Build Complete Performance Database
PRESSURE-X 2.0 — Consolidates all player performance metrics by competition and season.
Creates player_performance_by_competition.csv, player_performance_by_season.csv,
player_pressure_metrics.csv, player_domestic_metrics.csv, player_bowling_phase_metrics.csv,
player_current_form.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utilities.paths import PROCESSED_DATA_DIR, SUPPORTING_EVIDENCE_DIR, RAW_DATA_DIR


def build_performance_database():
    print("=" * 70)
    print("BUILDING COMPLETE PERFORMANCE DATABASE")
    print("=" * 70)

    # Load processed season features (main source)
    print("\n[1/6] Loading season features...")
    bat_season = pd.read_csv(PROCESSED_DATA_DIR / "all_competition_batter_season_features.csv", low_memory=False)
    bowl_season = pd.read_csv(PROCESSED_DATA_DIR / "all_competition_bowler_season_features.csv", low_memory=False)
    print(f"  Batter seasons: {len(bat_season)}")
    print(f"  Bowler seasons: {len(bowl_season)}")

    # Load match features for granular analysis
    print("\n[2/6] Loading match features...")
    bat_match = pd.read_csv(PROCESSED_DATA_DIR / "all_competition_batter_match_features.csv", low_memory=False)
    bowl_match = pd.read_csv(PROCESSED_DATA_DIR / "all_competition_bowler_match_features.csv", low_memory=False)
    print(f"  Batter matches: {len(bat_match)}")
    print(f"  Bowler matches: {len(bowl_match)}")

    # Load IPL-only features
    print("\n[3/6] Loading IPL-only features...")
    bat_ipl_season = pd.read_csv(PROCESSED_DATA_DIR / "ipl_only_batter_season_features.csv", low_memory=False)
    bowl_ipl_season = pd.read_csv(PROCESSED_DATA_DIR / "ipl_only_bowler_season_features.csv", low_memory=False)
    bat_ipl_match = pd.read_csv(PROCESSED_DATA_DIR / "ipl_only_batter_match_features.csv", low_memory=False)
    bowl_ipl_match = pd.read_csv(PROCESSED_DATA_DIR / "ipl_only_bowler_match_features.csv", low_memory=False)

    # Load player master for metadata
    print("\n[4/6] Loading player master...")
    player_master = pd.read_csv(PROCESSED_DATA_DIR / "player_master.csv", low_memory=False)

    # Load current form verification
    print("\n[5/6] Loading current form...")
    current_form = pd.read_csv(SUPPORTING_EVIDENCE_DIR / "current_form_source_verification.csv")

    # Load competitions for tier mapping
    comps = pd.read_csv(RAW_DATA_DIR / "competitions.csv")
    comp_tier_map = comps[['comp_id', 'comp_name', 'season']].copy()

    # ===== 1. PLAYER PERFORMANCE BY COMPETITION =====
    print("\n[BUILD] Building player_performance_by_competition...")

    # Batter competition-level from match features
    bat_comp = bat_match.groupby(['striker_id', 'striker_name', 'comp_id', 'comp_type', 'comp_tier', 'season']).agg(
        matches=('match_id', 'nunique'),
        innings=('innings', 'count'),
        total_balls=('balls_faced', 'sum'),
        total_runs=('runs_scored', 'sum'),
        total_fours=('fours', 'sum'),
        total_sixes=('sixes', 'sum'),
        total_boundaries=('boundaries', 'sum'),
        total_dismissals=('dismissed', 'sum'),
        # Pressure balls
        low_balls=('low_pressure_balls', 'sum'),
        low_runs=('low_pressure_runs', 'sum'),
        low_dismissals=('low_pressure_dismissals', 'sum'),
        low_boundaries=('low_pressure_boundaries', 'sum'),
        med_balls=('medium_pressure_balls', 'sum'),
        med_runs=('medium_pressure_runs', 'sum'),
        med_dismissals=('medium_pressure_dismissals', 'sum'),
        med_boundaries=('medium_pressure_boundaries', 'sum'),
        high_balls=('high_pressure_balls', 'sum'),
        high_runs=('high_pressure_runs', 'sum'),
        high_dismissals=('high_pressure_dismissals', 'sum'),
        high_boundaries=('high_pressure_boundaries', 'sum'),
        extreme_balls=('extreme_pressure_balls', 'sum'),
        extreme_runs=('extreme_pressure_runs', 'sum'),
        extreme_dismissals=('extreme_pressure_dismissals', 'sum'),
        extreme_boundaries=('extreme_pressure_boundaries', 'sum'),
        high_extreme_balls=('high_extreme_balls', 'sum'),
        high_extreme_runs=('high_extreme_runs', 'sum'),
        high_extreme_dismissals=('high_extreme_dismissals', 'sum'),
        high_extreme_boundaries=('high_extreme_boundaries', 'sum'),
        # Chase
        chase_balls=('chase_balls', 'sum'),
        chase_runs=('chase_runs', 'sum'),
        chase_dismissals=('chase_dismissals', 'sum'),
        chase_boundaries=('chase_boundaries', 'sum'),
        # Phase
        pp_balls=('powerplay_balls', 'sum'),
        pp_runs=('powerplay_runs', 'sum'),
        mid_balls=('middle_balls', 'sum'),
        mid_runs=('middle_runs', 'sum'),
        death_balls=('death_balls', 'sum'),
        death_runs=('death_runs', 'sum'),
    ).reset_index()

    # Calculate rates
    for prefix, balls_col, runs_col, dismissals_col, boundaries_col in [
        ('', 'total_balls', 'total_runs', 'total_dismissals', 'total_boundaries'),
        ('low_', 'low_balls', 'low_runs', 'low_dismissals', 'low_boundaries'),
        ('med_', 'med_balls', 'med_runs', 'med_dismissals', 'med_boundaries'),
        ('high_', 'high_balls', 'high_runs', 'high_dismissals', 'high_boundaries'),
        ('extreme_', 'extreme_balls', 'extreme_runs', 'extreme_dismissals', 'extreme_boundaries'),
        ('he_', 'high_extreme_balls', 'high_extreme_runs', 'high_extreme_dismissals', 'high_extreme_boundaries'),
        ('chase_', 'chase_balls', 'chase_runs', 'chase_dismissals', 'chase_boundaries'),
        ('pp_', 'pp_balls', 'pp_runs', None, None),
        ('mid_', 'mid_balls', 'mid_runs', None, None),
        ('death_', 'death_balls', 'death_runs', None, None),
    ]:
        b_col = f'{prefix}{balls_col}' if prefix else balls_col
        r_col = f'{prefix}{runs_col}' if prefix else runs_col
        d_col = f'{prefix}{dismissals_col}' if prefix and dismissals_col else (dismissals_col if not prefix else None)
        bdy_col = f'{prefix}{boundaries_col}' if prefix and boundaries_col else (boundaries_col if not prefix else None)

        if b_col in bat_comp.columns and r_col in bat_comp.columns:
            bat_comp[f'{prefix}strike_rate'] = np.where(bat_comp[b_col] > 0,
                                                        bat_comp[r_col] / bat_comp[b_col] * 100, 0)
        if d_col and d_col in bat_comp.columns and b_col in bat_comp.columns:
            bat_comp[f'{prefix}dismissal_rate'] = np.where(bat_comp[b_col] > 0,
                                                           bat_comp[d_col] / bat_comp[b_col], 0)
        if bdy_col and bdy_col in bat_comp.columns and b_col in bat_comp.columns:
            bat_comp[f'{prefix}boundary_pct'] = np.where(bat_comp[b_col] > 0,
                                                         bat_comp[bdy_col] / bat_comp[b_col] * 100, 0)

    # Bowler competition-level
    bowl_comp = bowl_match.groupby(['bowler_id', 'bowler_name', 'comp_id', 'comp_type', 'comp_tier', 'season']).agg(
        matches=('match_id', 'nunique'),
        innings=('innings', 'count'),
        total_balls=('balls_bowled', 'sum'),
        total_runs=('runs_conceded', 'sum'),
        total_wickets=('wickets', 'sum'),
        total_dots=('dots', 'sum'),
        total_boundaries=('boundaries_conceded', 'sum'),
        # Pressure
        low_balls=('low_pressure_balls', 'sum'),
        low_runs=('low_pressure_runs', 'sum'),
        low_wickets=('low_pressure_wickets', 'sum'),
        low_dots=('low_pressure_dots', 'sum'),
        low_boundaries=('low_pressure_boundaries', 'sum'),
        med_balls=('medium_pressure_balls', 'sum'),
        med_runs=('medium_pressure_runs', 'sum'),
        med_wickets=('medium_pressure_wickets', 'sum'),
        med_dots=('medium_pressure_dots', 'sum'),
        med_boundaries=('medium_pressure_boundaries', 'sum'),
        high_balls=('high_pressure_balls', 'sum'),
        high_runs=('high_pressure_runs', 'sum'),
        high_wickets=('high_pressure_wickets', 'sum'),
        high_dots=('high_pressure_dots', 'sum'),
        high_boundaries=('high_pressure_boundaries', 'sum'),
        extreme_balls=('extreme_pressure_balls', 'sum'),
        extreme_runs=('extreme_pressure_runs', 'sum'),
        extreme_wickets=('extreme_pressure_wickets', 'sum'),
        extreme_dots=('extreme_pressure_dots', 'sum'),
        extreme_boundaries=('extreme_pressure_boundaries', 'sum'),
        high_extreme_balls=('high_extreme_balls', 'sum'),
        high_extreme_runs=('high_extreme_runs', 'sum'),
        high_extreme_wickets=('high_extreme_wickets', 'sum'),
        high_extreme_dots=('high_extreme_dots', 'sum'),
        high_extreme_boundaries=('high_extreme_boundaries', 'sum'),
        # Defend
        defend_balls=('defend_balls', 'sum'),
        defend_runs=('defend_runs', 'sum'),
        defend_wickets=('defend_wickets', 'sum'),
        defend_dots=('defend_dots', 'sum'),
        # Phase
        pp_balls=('powerplay_balls', 'sum'),
        pp_runs=('powerplay_runs', 'sum'),
        pp_wickets=('powerplay_wickets', 'sum'),
        mid_balls=('middle_balls', 'sum'),
        mid_runs=('middle_runs', 'sum'),
        mid_wickets=('middle_wickets', 'sum'),
        death_balls=('death_balls', 'sum'),
        death_runs=('death_runs', 'sum'),
        death_wickets=('death_wickets', 'sum'),
    ).reset_index()

    # Bowler rates
    for prefix, balls_col, runs_col, wickets_col, dots_col, boundaries_col in [
        ('', 'total_balls', 'total_runs', 'total_wickets', 'total_dots', 'total_boundaries'),
        ('low_', 'low_balls', 'low_runs', 'low_wickets', 'low_dots', 'low_boundaries'),
        ('med_', 'med_balls', 'med_runs', 'med_wickets', 'med_dots', 'med_boundaries'),
        ('high_', 'high_balls', 'high_runs', 'high_wickets', 'high_dots', 'high_boundaries'),
        ('extreme_', 'extreme_balls', 'extreme_runs', 'extreme_wickets', 'extreme_dots', 'extreme_boundaries'),
        ('he_', 'high_extreme_balls', 'high_extreme_runs', 'high_extreme_wickets', 'high_extreme_dots', 'high_extreme_boundaries'),
        ('defend_', 'defend_balls', 'defend_runs', 'defend_wickets', 'defend_dots', None),
        ('pp_', 'pp_balls', 'pp_runs', 'pp_wickets', None, None),
        ('mid_', 'mid_balls', 'mid_runs', 'mid_wickets', None, None),
        ('death_', 'death_balls', 'death_runs', 'death_wickets', None, None),
    ]:
        b_col = f'{prefix}{balls_col}' if prefix else balls_col
        r_col = f'{prefix}{runs_col}' if prefix else runs_col
        w_col = f'{prefix}{wickets_col}' if prefix and wickets_col else (wickets_col if not prefix else None)
        d_col = f'{prefix}{dots_col}' if prefix and dots_col else (dots_col if not prefix else None)
        bdy_col = f'{prefix}{boundaries_col}' if prefix and boundaries_col else (boundaries_col if not prefix else None)

        if b_col in bowl_comp.columns and r_col in bowl_comp.columns:
            bowl_comp[f'{prefix}economy'] = np.where(bowl_comp[b_col] > 0,
                                                     bowl_comp[r_col] / bowl_comp[b_col] * 6, 0)
        if w_col and w_col in bowl_comp.columns and b_col in bowl_comp.columns:
            bowl_comp[f'{prefix}wicket_rate'] = np.where(bowl_comp[b_col] > 0,
                                                         bowl_comp[w_col] / bowl_comp[b_col], 0)
            bowl_comp[f'{prefix}wickets_per_over'] = np.where(bowl_comp[b_col] > 0,
                                                              bowl_comp[w_col] / bowl_comp[b_col] * 6, 0)
        if d_col and d_col in bowl_comp.columns and b_col in bowl_comp.columns:
            bowl_comp[f'{prefix}dot_ball_pct'] = np.where(bowl_comp[b_col] > 0,
                                                          bowl_comp[d_col] / bowl_comp[b_col] * 100, 0)
        if bdy_col and bdy_col in bowl_comp.columns and b_col in bowl_comp.columns:
            bowl_comp[f'{prefix}boundary_concession_pct'] = np.where(bowl_comp[b_col] > 0,
                                                                     bowl_comp[bdy_col] / bowl_comp[b_col] * 100, 0)

    # Add comp_name
    bat_comp = bat_comp.merge(comps[['comp_id', 'comp_name']], on='comp_id', how='left')
    bowl_comp = bowl_comp.merge(comps[['comp_id', 'comp_name']], on='comp_id', how='left')

    # Save competition-level
    bat_comp.to_csv(PROCESSED_DATA_DIR / "player_performance_by_competition_batter.csv", index=False)
    bowl_comp.to_csv(PROCESSED_DATA_DIR / "player_performance_by_competition_bowler.csv", index=False)
    print(f"  Batter competition records: {len(bat_comp)}")
    print(f"  Bowler competition records: {len(bowl_comp)}")

    # ===== 2. PLAYER PERFORMANCE BY SEASON (from season features) =====
    print("\n[BUILD] Building player_performance_by_season...")

    # Batter season - use the comprehensive season features
    bat_season_out = bat_season.copy()
    bat_season_out.to_csv(PROCESSED_DATA_DIR / "player_performance_by_season_batter.csv", index=False)

    bowl_season_out = bowl_season.copy()
    bowl_season_out.to_csv(PROCESSED_DATA_DIR / "player_performance_by_season_bowler.csv", index=False)

    print(f"  Batter season records: {len(bat_season_out)}")
    print(f"  Bowler season records: {len(bowl_season_out)}")

    # ===== 3. PLAYER PRESSURE METRICS =====
    print("\n[BUILD] Building player_pressure_metrics...")

    # Combine batter and bowler pressure metrics into unified view
    pressure_cols_bat = ['striker_id', 'striker_name', 'season', 'comp_types', 'comp_tiers'] + \
                       [c for c in bat_season.columns if any(x in c for x in
                       ['high_extreme', 'chase_', 'powerplay', 'middle', 'death_', 'low_pressure', 'medium_pressure', 'high_pressure', 'extreme_pressure'])]

    pressure_cols_bowl = ['bowler_id', 'bowler_name', 'season', 'comp_types', 'comp_tiers'] + \
                        [c for c in bowl_season.columns if any(x in c for x in
                        ['high_extreme', 'defend_', 'powerplay', 'middle', 'death_', 'low_pressure', 'medium_pressure', 'high_pressure', 'extreme_pressure'])]

    bat_pressure = bat_season[pressure_cols_bat].copy()
    bat_pressure.columns = ['player_id', 'player_name', 'season', 'comp_types', 'comp_tiers'] + \
                          [c for c in bat_pressure.columns[5:]]

    bowl_pressure = bowl_season[pressure_cols_bowl].copy()
    bowl_pressure.columns = ['player_id', 'player_name', 'season', 'comp_types', 'comp_tiers'] + \
                           [c for c in bowl_pressure.columns[5:]]

    # Save pressure metrics
    bat_pressure.to_csv(PROCESSED_DATA_DIR / "player_pressure_metrics_batter.csv", index=False)
    bowl_pressure.to_csv(PROCESSED_DATA_DIR / "player_pressure_metrics_bowler.csv", index=False)
    print(f"  Batter pressure records: {len(bat_pressure)}")
    print(f"  Bowler pressure records: {len(bowl_pressure)}")

    # ===== 4. PLAYER DOMESTIC METRICS =====
    print("\n[BUILD] Building player_domestic_metrics...")

    # Filter for domestic competitions (comp_tiers contains 4, 5 and Other_T20)
    # The comp_tiers column is a list string like "[np.int64(1), np.int64(2)]"
    def has_tier(tiers_str, target_tiers):
        if not isinstance(tiers_str, str):
            return False
        # Parse the string representation of list
        import re
        # Find all numbers in the string
        nums = re.findall(r'\d+', tiers_str)
        return any(int(n) in target_tiers for n in nums)

    def has_type(types_str, target_types):
        if not isinstance(types_str, str):
            return False
        return any(t in types_str for t in target_types)

    bat_domestic = bat_season[
        bat_season['comp_tiers'].apply(lambda x: has_tier(x, [4, 5])) |
        bat_season['comp_types'].apply(lambda x: has_type(x, ['Other_T20', 'Domestic']))
    ].copy()
    bowl_domestic = bowl_season[
        bowl_season['comp_tiers'].apply(lambda x: has_tier(x, [4, 5])) |
        bowl_season['comp_types'].apply(lambda x: has_type(x, ['Other_T20', 'Domestic']))
    ].copy()

    bat_domestic.to_csv(PROCESSED_DATA_DIR / "player_domestic_metrics_batter.csv", index=False)
    bowl_domestic.to_csv(PROCESSED_DATA_DIR / "player_domestic_metrics_bowler.csv", index=False)
    print(f"  Batter domestic records: {len(bat_domestic)}")
    print(f"  Bowler domestic records: {len(bowl_domestic)}")

    # ===== 5. PLAYER BOWLING PHASE METRICS =====
    print("\n[BUILD] Building player_bowling_phase_metrics...")

    # Extract phase-specific metrics from bowl_season
    phase_cols = ['bowler_id', 'bowler_name', 'season', 'comp_types', 'comp_tiers'] + \
                 [c for c in bowl_season.columns if any(x in c for x in
                 ['powerplay', 'middle', 'death_']) and not any(y in c for y in ['_adj', '_comp_adj', '_pop_adj', '_shrunk'])]

    bowl_phase = bowl_season[phase_cols].copy()
    bowl_phase.to_csv(PROCESSED_DATA_DIR / "player_bowling_phase_metrics.csv", index=False)
    print(f"  Bowler phase records: {len(bowl_phase)}")

    # ===== 6. PLAYER CURRENT FORM =====
    print("\n[BUILD] Building player_current_form...")

    # Merge current form verification with player master
    current_form_merged = current_form.merge(
        player_master[['player_id', 'canonical_name', 'final_nationality', 'primary_role']],
        left_on='player_id', right_on='player_id', how='left'
    )
    current_form_merged.to_csv(PROCESSED_DATA_DIR / "player_current_form.csv", index=False)
    print(f"  Current form records: {len(current_form_merged)}")

    print("\n" + "=" * 70)
    print("PERFORMANCE DATABASE BUILD COMPLETE")
    print("=" * 70)
    print("\nOutput files:")
    for f in [
        "player_performance_by_competition_batter.csv",
        "player_performance_by_competition_bowler.csv",
        "player_performance_by_season_batter.csv",
        "player_performance_by_season_bowler.csv",
        "player_pressure_metrics_batter.csv",
        "player_pressure_metrics_bowler.csv",
        "player_domestic_metrics_batter.csv",
        "player_domestic_metrics_bowler.csv",
        "player_bowling_phase_metrics.csv",
        "player_current_form.csv"
    ]:
        path = PROCESSED_DATA_DIR / f
        if path.exists():
            print(f"  [OK] {f} ({path.stat().st_size / 1024:.1f} KB)")

    return True


if __name__ == "__main__":
    build_performance_database()