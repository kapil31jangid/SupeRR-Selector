#!/usr/bin/env python3
"""
Build Primary Datasets for Pressure-X Feature Engineering
SupeRR Selector Season 2 — Rajasthan Royals IPL 2027 Auction Analytics

Creates:
- data/processed/ipl_primary_deliveries.csv
- data/processed/t20i_supplementary_deliveries.csv
- data/processed/excluded_deliveries.csv

Applies v2 modelling rules exactly from outputs/final_modelling_rules_v2.json
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json


def load_raw_data():
    """Load all raw CSV files."""
    raw_dir = Path("data/raw")
    bbb = pd.read_csv(raw_dir / "ball_by_ball.csv")
    matches = pd.read_csv(raw_dir / "matches.csv")
    competitions = pd.read_csv(raw_dir / "competitions.csv")
    mapping = pd.read_csv(raw_dir / "competition_team_player_mapping.csv")
    teams = pd.read_csv(raw_dir / "teams.csv")
    players = pd.read_csv(raw_dir / "players.csv") if (raw_dir / "players.csv").exists() else None
    return bbb, matches, competitions, mapping, teams, players


def classify_competitions(matches, competitions):
    """Classify matches into IPL, T20I, Other T20."""
    match_comp = matches.merge(competitions, left_on='comp_id', right_on='comp_id')

    # IPL matches
    ipl_mask = match_comp['comp_name'].str.contains('IPL|Indian Premier', case=False, na=False)
    ipl_match_ids = set(match_comp[ipl_mask]['match_id'].unique())

    # T20I matches
    t20i_mask = match_comp['match_format'] == 'T20I'
    t20i_match_ids = set(match_comp[t20i_mask]['match_id'].unique())

    # Other T20 (development tournaments)
    other_t20_mask = (match_comp['match_format'] == 'T20') & ~ipl_mask
    other_t20_match_ids = set(match_comp[other_t20_mask]['match_id'].unique())

    return ipl_match_ids, t20i_match_ids, other_t20_match_ids, match_comp


def get_abandoned_match_ids(matches):
    """Get match IDs for abandoned matches."""
    abandoned = matches[matches['result'].str.contains('Abandoned', case=False, na=False)]
    return set(abandoned['match_id'].unique())


def get_super_over_match_ids(bbb):
    """Get match IDs that have innings 3 or 4 (Super Overs)."""
    return set(bbb[bbb['innings'].isin([3, 4])]['match_id'].unique())


def apply_primary_filters(bbb, match_ids, abandoned_ids, super_over_ids, name="Dataset"):
    """Apply primary dataset filters."""
    # Filter to match_ids
    df = bbb[bbb['match_id'].isin(match_ids)].copy()

    # Track exclusions
    total_raw = len(df)
    excluded_super_over = df['innings'].isin([3, 4])
    excluded_abandoned = df['match_id'].isin(abandoned_ids)
    excluded_other = df['extras_type'] == 'other'

    # Apply filters
    primary = df[
        (~excluded_super_over) &
        (~excluded_abandoned) &
        (~excluded_other)
    ].copy()

    # Create excluded dataset with reason
    excluded = df[excluded_super_over | excluded_abandoned | excluded_other].copy()
    excluded['exclusion_reason'] = ''
    excluded.loc[excluded_super_over[excluded.index], 'exclusion_reason'] += 'super_over;'
    excluded.loc[excluded_abandoned[excluded.index], 'exclusion_reason'] += 'abandoned;'
    excluded.loc[excluded_other[excluded.index], 'exclusion_reason'] += 'other_extras;'

    print(f"{name}:")
    print(f"  Raw (in scope): {total_raw}")
    print(f"  Excluded - Super Over: {excluded_super_over.sum()}")
    print(f"  Excluded - Abandoned: {excluded_abandoned.sum()}")
    print(f"  Excluded - Other extras: {excluded_other.sum()}")
    print(f"  Primary: {len(primary)}")
    print(f"  Excluded total: {len(excluded)}")

    return primary, excluded


def join_player_names(df, mapping, id_col, name_col_suffix):
    """Join player names from mapping using player_id."""
    # mapping has player_id and player_name
    name_map = mapping[['player_id', 'player_name']].drop_duplicates()
    df = df.merge(name_map, left_on=id_col, right_on='player_id', how='left', suffixes=('', f'_{name_col_suffix}'))
    df = df.rename(columns={'player_name': f'{name_col_suffix}_name'})
    df = df.drop(columns=['player_id'])
    return df


def main():
    print("=" * 60)
    print("BUILD PRIMARY DATASETS - Pressure-X")
    print("=" * 60)

    # Load data
    bbb, matches, competitions, mapping, teams, players = load_raw_data()
    print(f"Loaded ball_by_ball: {len(bbb)} rows")
    print(f"Loaded matches: {len(matches)} rows")
    print(f"Loaded competitions: {len(competitions)} rows")
    print(f"Loaded mapping: {len(mapping)} rows")

    # Classify competitions
    ipl_ids, t20i_ids, other_t20_ids, match_comp = classify_competitions(matches, competitions)
    print(f"\nCompetition classification:")
    print(f"  IPL matches: {len(ipl_ids)}")
    print(f"  T20I matches: {len(t20i_ids)}")
    print(f"  Other T20 matches: {len(other_t20_ids)}")

    # Get exclusion sets
    abandoned_ids = get_abandoned_match_ids(matches)
    super_over_ids = get_super_over_match_ids(bbb)
    print(f"\nExclusion sets:")
    print(f"  Abandoned matches: {len(abandoned_ids)}")
    print(f"  Super Over matches: {len(super_over_ids)}")

    # Apply filters for IPL
    print("\n--- IPL Primary Dataset ---")
    ipl_primary, ipl_excluded = apply_primary_filters(
        bbb, ipl_ids, abandoned_ids, super_over_ids, "IPL"
    )

    # Apply filters for T20I
    print("\n--- T20I Supplementary Dataset ---")
    t20i_primary, t20i_excluded = apply_primary_filters(
        bbb, t20i_ids, abandoned_ids, super_over_ids, "T20I"
    )

    # Other T20 - all excluded from primary
    other_t20_bbb = bbb[bbb['match_id'].isin(other_t20_ids)].copy()
    other_t20_bbb['exclusion_reason'] = 'other_t20_tournament'
    print(f"\n--- Other T20 (Excluded) ---")
    print(f"  Total: {len(other_t20_bbb)}")

    # Combine all excluded
    all_excluded = pd.concat([
        ipl_excluded,
        t20i_excluded,
        other_t20_bbb
    ], ignore_index=True)

    # Join player names for primary datasets
    print("\n--- Joining Player Names ---")
    for df, name in [(ipl_primary, 'IPL'), (t20i_primary, 'T20I')]:
        df = join_player_names(df, mapping, 'striker_id', 'striker')
        df = join_player_names(df, mapping, 'non_striker_id', 'non_striker')
        df = join_player_names(df, mapping, 'bowler_id', 'bowler')
        if name == 'IPL':
            ipl_primary = df
        else:
            t20i_primary = df

    # Also join for excluded (for reference)
    all_excluded = join_player_names(all_excluded, mapping, 'striker_id', 'striker')
    all_excluded = join_player_names(all_excluded, mapping, 'non_striker_id', 'non_striker')
    all_excluded = join_player_names(all_excluded, mapping, 'bowler_id', 'bowler')

    # Ensure output directory exists
    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save primary datasets
    ipl_path = out_dir / "ipl_primary_deliveries.csv"
    t20i_path = out_dir / "t20i_supplementary_deliveries.csv"
    excluded_path = out_dir / "excluded_deliveries.csv"

    ipl_primary.to_csv(ipl_path, index=False)
    t20i_primary.to_csv(t20i_path, index=False)
    all_excluded.to_csv(excluded_path, index=False)

    print(f"\n--- Saved ---")
    print(f"  IPL Primary: {ipl_path} ({len(ipl_primary)} rows)")
    print(f"  T20I Supplementary: {t20i_path} ({len(t20i_primary)} rows)")
    print(f"  Excluded: {excluded_path} ({len(all_excluded)} rows)")

    # Verification
    print("\n--- Verification ---")
    print(f"IPL primary innings: {ipl_primary['innings'].value_counts().sort_index().to_dict()}")
    print(f"T20I primary innings: {t20i_primary['innings'].value_counts().sort_index().to_dict()}")

    # Legal ball counts
    ipl_legal = ipl_primary[~ipl_primary['extras_type'].isin(['wide', 'Overstep'])]
    t20i_legal = t20i_primary[~t20i_primary['extras_type'].isin(['wide', 'Overstep'])]
    print(f"IPL primary legal balls: {len(ipl_legal)}")
    print(f"T20I primary legal balls: {len(t20i_legal)}")
    print(f"Combined primary legal: {len(ipl_legal) + len(t20i_legal)}")

    # Check no negative runs
    assert (ipl_primary['runs'] >= 0).all(), "Negative runs in IPL primary"
    assert (t20i_primary['runs'] >= 0).all(), "Negative runs in T20I primary"
    print("No negative runs: [OK]")

    # Check no Super Over deliveries
    assert not ipl_primary['innings'].isin([3, 4]).any(), "Super Over in IPL primary"
    assert not t20i_primary['innings'].isin([3, 4]).any(), "Super Over in T20I primary"
    print("No Super Over deliveries: [OK]")

    # Check no abandoned matches
    assert not ipl_primary['match_id'].isin(abandoned_ids).any(), "Abandoned in IPL primary"
    assert not t20i_primary['match_id'].isin(abandoned_ids).any(), "Abandoned in T20I primary"
    print("No abandoned matches: [OK]")

    # Check no other extras
    assert not (ipl_primary['extras_type'] == 'other').any(), "Other extras in IPL primary"
    assert not (t20i_primary['extras_type'] == 'other').any(), "Other extras in T20I primary"
    print("No ambiguous extras: [OK]")

    print("\n" + "=" * 60)
    print("ALL CHECKS PASSED [OK]")
    print("=" * 60)


if __name__ == "__main__":
    main()