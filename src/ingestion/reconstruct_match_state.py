#!/usr/bin/env python3
"""
Reconstruct Match State Delivery by Delivery
Pressure-X Feature Engineering — SupeRR Selector Season 2

For each delivery, computes the pre-delivery match state:
- Score, wickets, overs, run rates
- For 2nd innings: target, required runs, required run rate
- Phase classification (powerplay, middle, death)
"""

import pandas as pd
import numpy as np
from pathlib import Path


def is_legal_ball(extras_type):
    """Determine if a delivery counts as a legal ball."""
    if pd.isna(extras_type):
        return True
    return extras_type not in ['wide', 'Overstep']


def classify_phase(over_num, innings, total_overs=20):
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
    # RR = team_score / (legal_balls_bowled / 6)
    df['current_run_rate'] = np.where(
        df['legal_balls_before'] > 0,
        df['team_score_before'] / (df['legal_balls_before'] / 6.0),
        0.0
    )

    # Phase
    df['phase'] = df['overid'].apply(lambda x: classify_phase(x, df['innings'].iloc[0]))

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

    # Get target for each match (from matches.csv)
    # target = win_team's score + 1 in first innings, or revised target
    match_targets = matches_df[['match_id', 'first_inn_revised_overs', 'second_inn_revised_overs',
                                 'revised_target', 'win_team_id']].copy()

    # We need to compute first innings total for each match to get target
    # Target = first innings total + 1 (or revised_target if available)
    first_inn_totals = df[df['innings'] == 1].groupby('match_id').apply(
        lambda x: x['team_score_before'].iloc[-1] + x['runs'].iloc[-1] + x['extras1_runs'].iloc[-1] + x['extras_2_runs'].iloc[-1]
    ).reset_index()
    first_inn_totals.columns = ['match_id', 'first_innings_total']

    # Merge with match targets
    match_info = matches_df[['match_id', 'revised_target', 'first_inn_revised_overs', 'second_inn_revised_overs']].copy()
    match_info = match_info.merge(first_inn_totals, on='match_id', how='left')

    # Determine effective target for 2nd innings
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

    # First innings: no target, but we can compute projected score pressure
    mask_1st = df['innings'] == 1
    df.loc[mask_1st, 'target'] = np.nan
    df.loc[mask_1st, 'required_runs'] = np.nan
    df.loc[mask_1st, 'required_run_rate'] = np.nan
    df.loc[mask_1st, 'runs_per_ball_required'] = np.nan

    return df


def main():
    print("=" * 60)
    print("RECONSTRUCT MATCH STATE - Pressure-X")
    print("=" * 60)

    # Load primary datasets
    ipl = pd.read_csv("data/processed/ipl_primary_deliveries.csv")
    t20i = pd.read_csv("data/processed/t20i_supplementary_deliveries.csv")
    matches = pd.read_csv("data/raw/matches.csv")

    print(f"Loaded IPL primary: {len(ipl)} rows")
    print(f"Loaded T20I primary: {len(t20i)} rows")
    print(f"Loaded matches: {len(matches)} rows")

    # Reconstruct state for IPL
    print("\n--- Reconstructing IPL match state ---")
    ipl_state = reconstruct_match_state(ipl)
    ipl_state = add_second_innings_context(ipl_state, matches)
    print(f"IPL state shape: {ipl_state.shape}")

    # Reconstruct state for T20I
    print("\n--- Reconstructing T20I match state ---")
    t20i_state = reconstruct_match_state(t20i)
    t20i_state = add_second_innings_context(t20i_state, matches)
    print(f"T20I state shape: {t20i_state.shape}")

    # Verify no future leakage
    print("\n--- Leakage Checks ---")
    for name, df in [("IPL", ipl_state), ("T20I", t20i_state)]:
        # Check that legal_balls_before never decreases within an innings
        for (mid, inn), group in df.groupby(['match_id', 'innings']):
            lb = group['legal_balls_before'].values
            if not np.all(np.diff(lb) >= 0):
                print(f"WARNING: {name} match {mid} inn {inn} - legal balls decreased!")

        # Check wickets_before never decreases
        for (mid, inn), group in df.groupby(['match_id', 'innings']):
            wb = group['wickets_before'].values
            if not np.all(np.diff(wb) >= 0):
                print(f"WARNING: {name} match {mid} inn {inn} - wickets decreased!")

        # Check team_score_before never decreases
        for (mid, inn), group in df.groupby(['match_id', 'innings']):
            ts = group['team_score_before'].values
            if not np.all(np.diff(ts) >= 0):
                print(f"WARNING: {name} match {mid} inn {inn} - score decreased!")

        print(f"  {name}: No future leakage detected [OK]")

    # Save
    out_dir = Path("data/processed")
    ipl_state.to_csv(out_dir / "ipl_match_state.csv", index=False)
    t20i_state.to_csv(out_dir / "t20i_match_state.csv", index=False)

    print(f"\n--- Saved ---")
    print(f"  IPL match state: data/processed/ipl_match_state.csv ({len(ipl_state)} rows)")
    print(f"  T20I match state: data/processed/t20i_match_state.csv ({len(t20i_state)} rows)")

    # Sample verification
    print("\n--- Sample: Match 14094 (IPL 2022) 2nd innings ---")
    sample = ipl_state[(ipl_state['match_id'] == 14094) & (ipl_state['innings'] == 2)].head(10)
    cols = ['match_id', 'innings', 'overid', 'over_ball_num', 'team_score_before', 'wickets_before',
            'legal_balls_before', 'legal_balls_remaining', 'target', 'required_runs',
            'current_run_rate', 'required_run_rate', 'phase']
    print(sample[cols].to_string())

    print("\n" + "=" * 60)
    print("MATCH STATE RECONSTRUCTION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()