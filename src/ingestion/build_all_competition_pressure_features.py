#!/usr/bin/env python3
"""
Build Pressure Features for All Competitions
Task 07 — Pressure-X Multi-Competition Evidence Engine

Applies the same transparent pressure methodology to all competitions.
Creates pressure categories (low/medium/high/extreme) for batting and bowling,
plus continuous pressure metrics.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def define_batting_pressure(row):
    """
    Define batting pressure category based on match situation.

    For 2nd innings (chase): uses required run rate, wickets remaining, balls remaining
    For 1st innings: uses phase, wickets lost, scoring rate vs par
    """
    if row['innings'] == 2:
        # Chase context
        rrr = row['required_run_rate']
        wickets_rem = 10 - row['wickets_before']
        balls_rem = row['legal_balls_remaining']
        runs_req = row['required_runs']

        # Extreme pressure: RRR > 12 OR <30 balls & RRR > 10 OR <5 wickets & RRR > 8
        if (rrr > 12) or (balls_rem < 30 and rrr > 10) or (wickets_rem <= 5 and rrr > 8):
            return 'extreme'
        # High pressure: RRR 9-12 OR death overs (over 16) with RRR > 7
        elif (rrr >= 9) or (row['overid'] >= 16 and rrr > 7):
            return 'high'
        # Medium pressure: RRR 7-9 OR middle overs with wickets down
        elif (rrr >= 7) or (row['phase'] == 'middle' and wickets_rem <= 6):
            return 'medium'
        else:
            return 'low'
    else:
        # 1st innings - no target
        # Use scoring rate relative to phase expectations
        crr = row['current_run_rate']
        wickets_lost = row['wickets_before']
        phase = row['phase']

        # Extreme: collapsed (5+ wickets in powerplay, 7+ in middle, all out risk in death)
        if (phase == 'powerplay' and wickets_lost >= 4) or \
           (phase == 'middle' and wickets_lost >= 6) or \
           (phase == 'death' and wickets_lost >= 8):
            return 'extreme'
        # High: slow scoring + wickets
        elif (phase == 'powerplay' and crr < 6 and wickets_lost >= 2) or \
             (phase == 'middle' and crr < 7 and wickets_lost >= 4) or \
             (phase == 'death' and crr < 9 and wickets_lost >= 6):
            return 'high'
        # Medium: moderate pressure
        elif (phase == 'powerplay' and wickets_lost >= 2) or \
             (phase == 'middle' and wickets_lost >= 3) or \
             (phase == 'death' and wickets_lost >= 4):
            return 'medium'
        else:
            return 'low'


def define_bowling_pressure(row):
    """
    Define bowling pressure category.

    For 2nd innings (defending): based on required run rate for batting team,
    wickets taken, balls remaining
    For 1st innings: based on opposition scoring rate, phase, wickets taken
    """
    if row['innings'] == 2:
        # Defending context - pressure on bowler when batting team is comfortable
        rrr = row['required_run_rate']
        crr = row['current_run_rate']
        wickets_taken = row['wickets_before']
        balls_rem = row['legal_balls_remaining']

        # Extreme: death overs, <3 wickets taken, RRR < 8 (batting team comfortable)
        if row['overid'] >= 17 and wickets_taken <= 2 and rrr < 8:
            return 'extreme'
        # High: middle/death, few wickets, batting team on track
        elif row['overid'] >= 12 and wickets_taken <= 3 and rrr < 9:
            return 'high'
        # Medium: powerplay with no wickets, or middle with 1-2 wickets
        elif (row['phase'] == 'powerplay' and wickets_taken == 0) or \
             (row['phase'] == 'middle' and wickets_taken <= 2):
            return 'medium'
        else:
            return 'low'
    else:
        # 1st innings - bowling pressure when batters scoring freely
        crr = row['current_run_rate']
        wickets_taken = row['wickets_before']
        phase = row['phase']

        # Extreme: powerplay >10 RPO with 0 wickets, middle >9 with <2 wickets
        if (phase == 'powerplay' and crr > 10 and wickets_taken == 0) or \
           (phase == 'middle' and crr > 9 and wickets_taken <= 1) or \
           (phase == 'death' and crr > 11 and wickets_taken <= 3):
            return 'extreme'
        # High: above par scoring
        elif (phase == 'powerplay' and crr > 9) or \
             (phase == 'middle' and crr > 8) or \
             (phase == 'death' and crr > 10):
            return 'high'
        # Medium: par scoring
        elif (phase == 'powerplay' and crr > 7) or \
             (phase == 'middle' and crr > 7) or \
             (phase == 'death' and crr > 9):
            return 'medium'
        else:
            return 'low'


def add_pressure_features(df):
    """Add all pressure-related features to the match state DataFrame."""
    df = df.copy()

    # Batting pressure category
    df['batting_pressure'] = df.apply(define_batting_pressure, axis=1)

    # Bowling pressure category
    df['bowling_pressure'] = df.apply(define_bowling_pressure, axis=1)

    # Continuous pressure metrics
    # For 2nd innings
    mask_2nd = df['innings'] == 2
    df.loc[mask_2nd, 'rrr_minus_crr'] = df.loc[mask_2nd, 'required_run_rate'] - df.loc[mask_2nd, 'current_run_rate']
    df.loc[mask_2nd, 'wickets_remaining'] = 10 - df.loc[mask_2nd, 'wickets_before']
    df.loc[mask_2nd, 'balls_per_wicket'] = np.where(
        df.loc[mask_2nd, 'wickets_before'] > 0,
        df.loc[mask_2nd, 'legal_balls_before'] / df.loc[mask_2nd, 'wickets_before'],
        df.loc[mask_2nd, 'legal_balls_before']
    )

    # For 1st innings
    mask_1st = df['innings'] == 1
    df.loc[mask_1st, 'wickets_remaining'] = 10 - df.loc[mask_1st, 'wickets_before']
    df.loc[mask_1st, 'par_score_estimate'] = df.loc[mask_1st, 'current_run_rate'] * 20  # projected

    # Delivery-level context flags
    df['is_death_over'] = df['overid'] >= 16
    df['is_powerplay'] = df['overid'] <= 6
    df['is_middle_over'] = (df['overid'] > 6) & (df['overid'] < 16)

    # Chase context (2nd innings only)
    df['is_chase'] = df['innings'] == 2
    df.loc[mask_2nd, 'chase_difficulty'] = df.loc[mask_2nd, 'required_run_rate'] / 6.0  # normalized

    # Wickets in hand pressure
    df['wickets_in_hand'] = 10 - df['wickets_before']
    df['low_wickets'] = df['wickets_in_hand'] <= 3
    df['medium_wickets'] = (df['wickets_in_hand'] > 3) & (df['wickets_in_hand'] <= 6)
    df['high_wickets'] = df['wickets_in_hand'] > 6

    return df


def add_batter_features(df):
    """Add batter-specific features at delivery level."""
    df = df.copy()

    # Batter runs (already in 'runs' column)
    df['batter_runs'] = df['runs']

    # Boundary indicators
    df['is_four'] = df['is_four'].astype(int)
    df['is_six'] = df['is_six'].astype(int)
    df['is_boundary'] = ((df['is_four'] == 1) | (df['is_six'] == 1)).astype(int)

    # Dismissal indicator
    df['is_dismissed'] = df['is_wicket'].astype(int)

    # Legal ball faced by striker (striker faces all legal balls)
    df['balls_faced'] = df['is_legal'].astype(int)

    # Runs per legal ball faced (strike rate component)
    df['runs_per_ball_faced'] = np.where(
        df['balls_faced'] == 1,
        df['batter_runs'],
        0
    )

    return df


def add_bowler_features(df):
    """Add bowler-specific features at delivery level."""
    df = df.copy()

    # Bowler runs conceded (per v2 rules)
    def bowler_runs(row):
        et = row['extras_type']
        if et == 'wide':
            return row['extras1_runs']
        elif et == 'Overstep':
            return row['runs'] + row['extras1_runs']
        elif et in ['byes', 'legbyes', 'Penalty']:
            return 0
        elif et == 'other':
            return np.nan  # excluded from primary
        else:
            return row['runs']

    df['bowler_runs_conceded'] = df.apply(bowler_runs, axis=1)

    # Legal ball bowled
    df['legal_ball_bowled'] = df['is_legal'].astype(int)

    # Dot ball (legal ball with 0 runs scored off bat + no byes/legbyes)
    df['is_dot'] = np.where(
        (df['legal_ball_bowled'] == 1) &
        (df['runs'] == 0) &
        (df['extras1_runs'] == 0),
        1, 0
    )

    # Boundary conceded
    df['boundary_conceded'] = np.where(
        (df['legal_ball_bowled'] == 1) &
        ((df['is_four'] == 1) | (df['is_six'] == 1)),
        1, 0
    )

    # Wicket taken (bowler credited)
    bowler_wicket_types = ['Bowled', 'Caught', 'LBW', 'Stump', 'Hit Wicket',
                           'Obstructing the field', 'Obstracting the field']
    df['bowler_wicket'] = np.where(
        (df['is_wicket']) & (df['dismissal_type'].isin(bowler_wicket_types)),
        1, 0
    )

    return df


def is_legal_ball(extras_type):
    """Determine if a delivery counts as a legal ball."""
    if pd.isna(extras_type):
        return True
    return extras_type not in ['wide', 'Overstep']


def main():
    print("=" * 70)
    print("BUILD ALL-COMPETITION PRESSURE FEATURES — Task 07")
    print("=" * 70)

    # Load all-competition match state
    state = pd.read_csv("data/processed/all_competition_match_state.csv")

    print(f"Loaded match state: {len(state)} rows")
    print(f"Competitions: {state['comp_id'].nunique()}")
    print(f"Comp types: {state['comp_type'].unique()}")

    # Add pressure features
    print("\n--- Adding pressure features ---")
    state = add_pressure_features(state)

    # Add batter features
    print("\n--- Adding batter features ---")
    state = add_batter_features(state)

    # Add bowler features
    print("\n--- Adding bowler features ---")
    state = add_bowler_features(state)

    # Verify pressure distribution overall
    print("\n--- Pressure Distribution (All Competitions) ---")
    print("Batting pressure:")
    print(state['batting_pressure'].value_counts())
    print("\nBowling pressure:")
    print(state['bowling_pressure'].value_counts())

    # By competition type
    print("\n--- Pressure Distribution by Competition Type ---")
    for comp_type in ['IPL', 'T20I', 'Other_T20']:
        subset = state[state['comp_type'] == comp_type]
        if len(subset) > 0:
            print(f"\n{comp_type}:")
            print(f"  Batting: {subset['batting_pressure'].value_counts().to_dict()}")
            print(f"  Bowling: {subset['bowling_pressure'].value_counts().to_dict()}")

    # Save pressure-enhanced dataset
    out_dir = Path("data/processed")
    out_path = out_dir / "all_competition_pressure_deliveries.csv"
    state.to_csv(out_path, index=False)

    print(f"\n--- Saved ---")
    print(f"  All-competition pressure: {out_path} ({len(state)} rows)")

    # Also save per-competition-type splits
    for comp_type in ['IPL', 'T20I', 'Other_T20']:
        subset = state[state['comp_type'] == comp_type]
        if len(subset) > 0:
            subset_path = out_dir / f"{comp_type.lower()}_pressure_deliveries_from_all.csv"
            subset.to_csv(subset_path, index=False)
            print(f"  {comp_type} pressure: {subset_path} ({len(subset)} rows)")

    # Sample check
    print("\n--- Sample: High pressure deliveries ---")
    high_bat = state[state['batting_pressure'] == 'high']
    print(f"High batting pressure: {len(high_bat)} deliveries")
    extreme_bat = state[state['batting_pressure'] == 'extreme']
    print(f"Extreme batting pressure: {len(extreme_bat)} deliveries")

    high_bowl = state[state['bowling_pressure'] == 'high']
    print(f"High bowling pressure: {len(high_bowl)} deliveries")
    extreme_bowl = state[state['bowling_pressure'] == 'extreme']
    print(f"Extreme bowling pressure: {len(extreme_bowl)} deliveries")

    print("\n" + "=" * 70)
    print("ALL-COMPETITION PRESSURE FEATURES BUILT")
    print("=" * 70)


if __name__ == "__main__":
    main()