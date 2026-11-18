#!/usr/bin/env python3
"""
Build Pressure Features
Pressure-X Feature Engineering — SupeRR Selector Season 2

Creates transparent, interpretable pressure indicators for batting and bowling.
Defines pressure contexts with documented thresholds.
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
        # Defending context - pressure on bowler when batting team is ahead or catching up
        rrr = row['required_run_rate']
        crr = row['current_run_rate']
        wickets_taken = row['wickets_before']
        balls_rem = row['legal_balls_remaining']

        # Batting team's required run rate relative to current
        # If RRR < CRR, batting team is ahead (low pressure for bowler)
        # If RRR > CRR, batting team behind (pressure on batting, not bowling)
        # Bowling pressure HIGH when: defending low total, death overs, few wickets taken

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

    # Legal ball faced by striker
    # Striker faces the ball unless it's a wide (striker doesn't face wide)
    # For wides, striker doesn't face a legal ball
    df['striker_faces_legal'] = df.apply(
        lambda r: 1 if (is_legal_ball(r['extras_type']) and r['striker_id'] == r['striker_id']) else 0, axis=1
    )
    # Actually simpler: striker faces all legal balls, non-striker faces none
    # But on wides, striker may still be the one "facing"
    # Standard: legal ball = striker faces it
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
    # For bowler: dot = legal ball, 0 batter runs, 0 byes/legbyes
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
    print("=" * 60)
    print("BUILD PRESSURE FEATURES - Pressure-X")
    print("=" * 60)

    # Load match state datasets
    ipl = pd.read_csv("data/processed/ipl_match_state.csv")
    t20i = pd.read_csv("data/processed/t20i_match_state.csv")

    print(f"Loaded IPL match state: {len(ipl)} rows")
    print(f"Loaded T20I match state: {len(t20i)} rows")

    # Add pressure features
    print("\n--- Adding pressure features ---")
    ipl = add_pressure_features(ipl)
    t20i = add_pressure_features(t20i)

    # Add batter features
    print("\n--- Adding batter features ---")
    ipl = add_batter_features(ipl)
    t20i = add_batter_features(t20i)

    # Add bowler features
    print("\n--- Adding bowler features ---")
    ipl = add_bowler_features(ipl)
    t20i = add_bowler_features(t20i)

    # Verify pressure distribution
    print("\n--- Pressure Distribution (IPL) ---")
    print("Batting pressure:")
    print(ipl['batting_pressure'].value_counts())
    print("\nBowling pressure:")
    print(ipl['bowling_pressure'].value_counts())

    print("\n--- Pressure Distribution (T20I) ---")
    print("Batting pressure:")
    print(t20i['batting_pressure'].value_counts())
    print("\nBowling pressure:")
    print(t20i['bowling_pressure'].value_counts())

    # Save pressure-enhanced datasets
    out_dir = Path("data/processed")
    ipl.to_csv(out_dir / "ipl_pressure_deliveries.csv", index=False)
    t20i.to_csv(out_dir / "t20i_pressure_deliveries.csv", index=False)

    print(f"\n--- Saved ---")
    print(f"  IPL pressure: data/processed/ipl_pressure_deliveries.csv ({len(ipl)} rows)")
    print(f"  T20I pressure: data/processed/t20i_pressure_deliveries.csv ({len(t20i)} rows)")

    # Sample check
    print("\n--- Sample: High pressure deliveries ---")
    high_bat = ipl[ipl['batting_pressure'] == 'high']
    print(f"IPL high batting pressure: {len(high_bat)} deliveries")
    extreme_bat = ipl[ipl['batting_pressure'] == 'extreme']
    print(f"IPL extreme batting pressure: {len(extreme_bat)} deliveries")

    high_bowl = ipl[ipl['bowling_pressure'] == 'high']
    print(f"IPL high bowling pressure: {len(high_bowl)} deliveries")
    extreme_bowl = ipl[ipl['bowling_pressure'] == 'extreme']
    print(f"IPL extreme bowling pressure: {len(extreme_bowl)} deliveries")

    print("\n" + "=" * 60)
    print("PRESSURE FEATURES BUILT")
    print("=" * 60)


if __name__ == "__main__":
    main()