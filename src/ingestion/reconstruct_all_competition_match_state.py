#!/usr/bin/env python3
"""
Reconstruct Match State for All Competitions
Task 07 — Pressure-X Multi-Competition Evidence Engine

Processes the unified all_competition_deliveries.csv and reconstructs
pre-delivery match state for every delivery across all competitions.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def is_legal_ball(extras_type):
    """Determine if a delivery counts as a legal ball."""
    if pd.isna(extras_type):
        return True
    return extras_type not in ['wide', 'Overstep']


def classify_phase(over_num):
    """Classify innings phase based on over number."""
    if over_num <= 6:
        return 'powerplay'
    elif over_num <= 15:
        return 'middle'
    else:
        return 'death'


def reconstruct_innings_state(innings_df):
    """
    Reconstruct pre-delivery state for a single innings.
    Returns DataFrame with state columns added.
    """
    df = innings_df.sort_values(['overid', 'over_ball_num', 'innings_ball_num']).copy().reset_index(drop=True)

    # Mark legal balls
    df['is_legal'] = df['extras_type'].apply(is_legal_ball)

    # Cumulative legal balls bowled BEFORE each delivery
    df['legal_balls_before'] = df['is_legal'].cumsum().shift(1, fill_value=0).astype(int)

    # Cumulative runs scored BEFORE each delivery
    df['runs_before'] = df['runs'].cumsum().shift(1, fill_value=0).astype(int)

    # Cumulative extras runs before (for total team score)
    df['extras1_before'] = df['extras1_runs'].cumsum().shift(1, fill_value=0).astype(int)
    df['extras2_before'] = df['extras_2_runs'].cumsum().shift(1, fill_value=0).astype(int)

    # Total team score before delivery (batter runs + extras)
    df['team_score_before'] = df['runs_before'] + df['extras1_before'] + df['extras2_before']

    # Wickets fallen BEFORE each delivery
    df['wickets_before'] = df['is_wicket'].cumsum().shift(1, fill_value=0).astype(int)

    # Current over (1-indexed)
    df['over_number'] = df['overid']

    # Legal balls remaining in innings (assuming 20 overs = 120 legal balls)
    # For shortened matches, this will be adjusted later if needed
    df['legal_balls_remaining'] = 120 - df['legal_balls_before']
    df['legal_balls_remaining'] = df['legal_balls_remaining'].clip(lower=0)

    # Current run rate (runs per over) before delivery
    df['current_run_rate'] = np.where(
        df['legal_balls_before'] > 0,
        df['team_score_before'] / (df['legal_balls_before'] / 6.0),
        0.0
    )

    # Phase
    df['phase'] = df['overid'].apply(classify_phase)

    return df


def reconstruct_match_state(df):
    """
    Reconstruct pre-delivery state for all matches and innings.
    """
    results = []

    for (match_id, innings), group in df.groupby(['match_id', 'innings']):
        innings_state = reconstruct_innings_state(group)
        results.append(innings_state)

    return pd.concat(results, ignore_index=True)


def add_second_innings_context(df, matches_df):
    """
    Add 2nd innings chase context: target, required runs, required run rate.
    """
    df = df.copy()

    # Compute first innings total for each match from the deliveries data
    first_inn_totals = df[df['innings'] == 1].groupby('match_id').apply(
        lambda x: x['team_score_before'].iloc[-1] + x['runs'].iloc[-1] + x['extras1_runs'].iloc[-1] + x['extras_2_runs'].iloc[-1]
    ).reset_index()
    first_inn_totals.columns = ['match_id', 'first_innings_total']

    # Get revised target and overs from matches.csv
    match_info = matches_df[['match_id', 'revised_target', 'first_inn_revised_overs', 'second_inn_revised_overs']].copy()
    match_info = match_info.merge(first_inn_totals, on='match_id', how='left')

    # Determine effective target for 2nd innings
    # If revised_target exists and > 0, use it; otherwise first_innings_total + 1
    match_info['effective_target'] = match_info['revised_target'].where(
        match_info['revised_target'].notna() & (match_info['revised_target'] > 0),
        match_info['first_innings_total'] + 1
    )

    # Merge target into 2nd innings deliveries
    target_map = match_info.set_index('match_id')['effective_target'].to_dict()
    overs_map = match_info.set_index('match_id')['second_inn_revised_overs'].to_dict()

    df['target'] = df['match_id'].map(target_map)

    # For 2nd innings, calculate required runs and required run rate
    mask_2nd = df['innings'] == 2

    # Required runs = target - current score
    df.loc[mask_2nd, 'required_runs'] = df.loc[mask_2nd, 'target'] - df.loc[mask_2nd, 'team_score_before']
    df.loc[mask_2nd, 'required_runs'] = df.loc[mask_2nd, 'required_runs'].clip(lower=0)

    # Legal balls remaining for 2nd innings (use revised overs if available, else 120)
    df.loc[mask_2nd, 'max_legal_balls'] = df.loc[mask_2nd, 'match_id'].map(overs_map).apply(
        lambda x: int(x * 6) if pd.notna(x) and x > 0 else 120
    )
    df.loc[mask_2nd, 'legal_balls_remaining'] = df.loc[mask_2nd, 'max_legal_balls'] - df.loc[mask_2nd, 'legal_balls_before']
    df.loc[mask_2nd, 'legal_balls_remaining'] = df.loc[mask_2nd, 'legal_balls_remaining'].clip(lower=0)

    # Required run rate
    df.loc[mask_2nd, 'required_run_rate'] = np.where(
        df.loc[mask_2nd, 'legal_balls_remaining'] > 0,
        df.loc[mask_2nd, 'required_runs'] / (df.loc[mask_2nd, 'legal_balls_remaining'] / 6.0),
        0.0
    )

    # Chase pressure indicators
    df.loc[mask_2nd, 'runs_per_ball_required'] = np.where(
        df.loc[mask_2nd, 'legal_balls_remaining'] > 0,
        df.loc[mask_2nd, 'required_runs'] / df.loc[mask_2nd, 'legal_balls_remaining'],
        0.0
    )

    # First innings: no target
    mask_1st = df['innings'] == 1
    df.loc[mask_1st, 'target'] = np.nan
    df.loc[mask_1st, 'required_runs'] = np.nan
    df.loc[mask_1st, 'required_run_rate'] = np.nan
    df.loc[mask_1st, 'runs_per_ball_required'] = np.nan

    return df


def validate_no_leakage(df, name="Dataset"):
    """Validate no future leakage within each innings."""
    issues = []

    for (mid, inn), group in df.groupby(['match_id', 'innings']):
        group = group.sort_values(['overid', 'over_ball_num', 'innings_ball_num'])

        # Legal balls before should be non-decreasing
        lb = group['legal_balls_before'].values
        if not np.all(np.diff(lb) >= 0):
            issues.append(f"{name} match {mid} inn {inn}: legal_balls_before decreases")

        # Wickets before should be non-decreasing
        wb = group['wickets_before'].values
        if not np.all(np.diff(wb) >= 0):
            issues.append(f"{name} match {mid} inn {inn}: wickets_before decreases")

        # Team score before should be non-decreasing
        ts = group['team_score_before'].values
        if not np.all(np.diff(ts) >= 0):
            issues.append(f"{name} match {mid} inn {inn}: team_score_before decreases")

        # Legal balls remaining should be non-increasing
        lbr = group['legal_balls_remaining'].values
        if not np.all(np.diff(lbr) <= 0):
            issues.append(f"{name} match {mid} inn {inn}: legal_balls_remaining increases")

    return issues


def main():
    print("=" * 70)
    print("RECONSTRUCT ALL-COMPETITION MATCH STATE — Task 07")
    print("=" * 70)

    # Load unified primary deliveries
    primary = pd.read_csv("data/processed/all_competition_deliveries.csv")
    matches = pd.read_csv("data/raw/matches.csv")
    comp_info = pd.read_csv("data/processed/competition_info.csv")

    print(f"Loaded primary deliveries: {len(primary)} rows")
    print(f"Loaded matches: {len(matches)} rows")
    print(f"Loaded competition info: {len(comp_info)} rows")

    # Reconstruct state
    print("\n--- Reconstructing match state for all competitions ---")
    state = reconstruct_match_state(primary)
    print(f"State shape after reconstruction: {state.shape}")

    # Add second innings context
    print("\n--- Adding 2nd innings chase context ---")
    state = add_second_innings_context(state, matches)
    print(f"State shape after 2nd innings context: {state.shape}")

    # Validate no leakage
    print("\n--- Leakage Validation ---")
    issues = validate_no_leakage(state, "All-Competition")
    if issues:
        print(f"WARNING: {len(issues)} leakage issues found:")
        for issue in issues[:10]:
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
    else:
        print("No future leakage detected [OK]")

    # Validate key columns
    print("\n--- Column Validation ---")
    print(f"Matches with state: {state['match_id'].nunique()}")
    print(f"Innings covered: {sorted(state['innings'].unique())}")
    print(f"Competitions: {state['comp_id'].nunique()}")
    print(f"Comp types: {state['comp_type'].unique()}")
    print(f"Phases: {state['phase'].unique()}")
    print(f"Legal balls range: {state['legal_balls_before'].min()} - {state['legal_balls_before'].max()}")
    print(f"2nd innings with target: {state[state['innings']==2]['target'].notna().sum()} deliveries")

    # Save unified match state
    out_dir = Path("data/processed")
    state_path = out_dir / "all_competition_match_state.csv"
    state.to_csv(state_path, index=False)
    print(f"\n--- Saved ---")
    print(f"  All-competition match state: {state_path} ({len(state)} rows)")

    # Also save per-competition-type splits for easier downstream processing
    for comp_type in ['IPL', 'T20I', 'Other_T20']:
        subset = state[state['comp_type'] == comp_type]
        if len(subset) > 0:
            subset_path = out_dir / f"{comp_type.lower()}_match_state_from_all.csv"
            subset.to_csv(subset_path, index=False)
            print(f"  {comp_type} match state: {subset_path} ({len(subset)} rows)")

    # Sample verification
    print("\n--- Sample Verification ---")
    # Pick a known match
    sample_matches = state['match_id'].unique()[:3]
    for mid in sample_matches:
        for inn in [1, 2]:
            sample = state[(state['match_id'] == mid) & (state['innings'] == inn)]
            if len(sample) > 0:
                print(f"\nMatch {mid}, Innings {inn} (first 5 deliveries):")
                cols = ['match_id', 'innings', 'overid', 'over_ball_num', 'team_score_before', 'wickets_before',
                        'legal_balls_before', 'legal_balls_remaining', 'target', 'required_runs',
                        'current_run_rate', 'required_run_rate', 'phase', 'comp_type']
                print(sample[cols].head().to_string())

    print("\n" + "=" * 70)
    print("ALL-COMPETITION MATCH STATE RECONSTRUCTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()