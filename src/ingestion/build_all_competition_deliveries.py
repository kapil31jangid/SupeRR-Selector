#!/usr/bin/env python3
"""
Build All-Competition Deliveries Dataset
Task 07 — Pressure-X Multi-Competition Evidence Engine

Processes ALL valid T20 competitions from raw data:
- IPL 2022-2026 (primary)
- T20I 2022-2026 (supplementary)
- Other T20 tournaments (Emerging Teams, Rising Stars)

Creates unified delivery dataset with competition metadata,
and separate datasets for Super Overs, abandoned matches, ambiguous extras.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_raw_data():
    """Load all raw CSV files."""
    print("Loading raw data...")
    balls = pd.read_csv("data/raw/ball_by_ball.csv")
    matches = pd.read_csv("data/raw/matches.csv")
    comps = pd.read_csv("data/raw/competitions.csv")
    mapping = pd.read_csv("data/raw/competition_team_player_mapping.csv")
    playing = pd.read_csv("data/raw/playing_eleven.csv")
    teams = pd.read_csv("data/raw/teams.csv")

    print(f"  ball_by_ball: {len(balls)} rows")
    print(f"  matches: {len(matches)} rows")
    print(f"  competitions: {len(comps)} rows")
    print(f"  player mapping: {len(mapping)} rows")
    print(f"  playing eleven: {len(playing)} rows")
    print(f"  teams: {len(teams)} rows")

    return balls, matches, comps, mapping, playing, teams


def classify_competitions(comps):
    """Classify competitions into tiers and types."""
    comp_info = comps.copy()

    # Determine competition type
    def comp_type(row):
        name = row['comp_name'].lower()
        fmt = row['match_format']
        if 'ipl' in name:
            return 'IPL'
        elif fmt == 'T20I' or 't20i' in name:
            return 'T20I'
        elif fmt == 'T20':
            # Check if it's an Asia Cup or similar multi-team tournament
            if 'asia cup' in name or 'emerging' in name or 'rising stars' in name:
                return 'Other_T20'  # Multi-team T20 tournaments
            return 'Other_T20'
        else:
            return 'Unknown'

    comp_info['comp_type'] = comp_info.apply(comp_type, axis=1)

    # Determine tier for strength adjustment
    def comp_tier(row):
        ctype = row['comp_type']
        name = row['comp_name'].lower()
        if ctype == 'IPL':
            return 1
        elif ctype == 'T20I':
            # Full member vs full member = tier 2
            # Check if associate nations involved
            associate_keywords = ['nepal', 'uae', 'united arab emirates', 'netherlands', 'scotland',
                                  'ireland', 'zimbabwe', 'namibia', 'oman', 'papua new guinea',
                                  'hong kong', 'singapore', 'malaysia', 'kuwait', 'qatar',
                                  'bahrain', 'saudi arabia', 'cayman islands', 'bermuda',
                                  'canada', 'usa', 'americas', 'europe', 'africa qualifier',
                                  'asia qualifier', 'emerging', 'rising stars', 'tri-nation',
                                  'tri-series', 'tri series']
            if any(kw in name for kw in associate_keywords):
                # Could be tier 3 or 4 depending on opponents
                # Simple heuristic: if "india", "england", "australia", "south africa",
                # "pakistan", "new zealand", "sri lanka", "west indies", "bangladesh", "afghanistan"
                # are in name -> tier 3 (full member vs associate)
                # else tier 4 (associate vs associate)
                full_members = ['india', 'england', 'australia', 'south africa', 'pakistan',
                                'new zealand', 'sri lanka', 'west indies', 'bangladesh', 'afghanistan']
                if any(fm in name for fm in full_members):
                    return 3
                else:
                    return 4
            else:
                return 2  # Full member vs full member
        elif ctype == 'Other_T20':
            return 5  # Development/emerging tournaments
        return 5

    comp_info['comp_tier'] = comp_info.apply(comp_tier, axis=1)

    return comp_info


def identify_special_matches(matches, balls):
    """Identify Super Over matches, abandoned matches, etc."""
    # Super Over matches: have innings 3 or 4
    super_over_match_ids = balls[balls['innings'].isin([3, 4])]['match_id'].unique()

    # Abandoned / No Result matches
    abandoned_mask = matches['result'].str.contains('Abandoned|No Result', case=False, na=False)
    abandoned_match_ids = matches[abandoned_mask]['match_id'].unique()

    # Matches with ball-by-ball data
    matches_with_balls = balls['match_id'].unique()

    return super_over_match_ids, abandoned_match_ids, matches_with_balls


def filter_primary_deliveries(balls, matches, comps, super_over_ids, abandoned_ids):
    """Filter to primary dataset: regular innings (1,2) from completed matches."""
    # Merge balls with match and competition info
    balls_merged = balls.merge(matches[['match_id', 'comp_id', 'result']], on='match_id', how='left')
    balls_merged = balls_merged.merge(comps[['comp_id', 'comp_name', 'match_format', 'season']], on='comp_id', how='left')

    # Identify excluded deliveries
    # 1. Super Over innings (3, 4)
    is_super_over = balls_merged['innings'].isin([3, 4])

    # 2. Abandoned/No Result matches
    is_abandoned = balls_merged['match_id'].isin(abandoned_ids)

    # 3. Ambiguous extras
    is_ambiguous_extras = balls_merged['extras_type'] == 'other'

    # 4. Non-T20 competitions (shouldn't exist but safety check)
    is_non_t20 = ~balls_merged['match_format'].isin(['T20', 'T20I'])

    # Primary: innings 1&2, not abandoned, not ambiguous extras, T20 format
    is_primary = (
        balls_merged['innings'].isin([1, 2]) &
        ~is_abandoned &
        ~is_ambiguous_extras &
        ~is_non_t20
    )

    # Create exclusion reason
    def exclusion_reason(row):
        if row['innings'] in [3, 4]:
            return 'super_over'
        elif row['match_id'] in abandoned_ids:
            return 'abandoned'
        elif row['extras_type'] == 'other':
            return 'other_extras'
        elif row['match_format'] not in ['T20', 'T20I']:
            return 'non_t20_format'
        else:
            return 'included'

    balls_merged['exclusion_reason'] = balls_merged.apply(exclusion_reason, axis=1)

    primary = balls_merged[is_primary].copy()
    excluded = balls_merged[~is_primary].copy()

    print(f"\nDelivery filtering:")
    print(f"  Total raw deliveries: {len(balls_merged)}")
    print(f"  Primary (innings 1&2, completed, clear extras): {len(primary)}")
    print(f"  Excluded: {len(excluded)}")
    print(f"    Super Over: {(excluded['exclusion_reason']=='super_over').sum()}")
    print(f"    Abandoned: {(excluded['exclusion_reason']=='abandoned').sum()}")
    print(f"    Other extras: {(excluded['exclusion_reason']=='other_extras').sum()}")
    print(f"    Non-T20: {(excluded['exclusion_reason']=='non_t20_format').sum()}")

    return primary, excluded, balls_merged


def add_canonical_names(primary, mapping):
    """Add canonical player names from competition_team_player_mapping."""
    # Create mapping dictionaries keyed by (comp_id, player_id)
    name_map = mapping.drop_duplicates(subset=['comp_id', 'player_id']).set_index(['comp_id', 'player_id'])['player_name']

    # Map striker names
    primary['striker_canonical_name'] = primary.apply(
        lambda r: name_map.get((r['comp_id'], r['striker_id']), r['striker_name']), axis=1
    )

    # Map non-striker names
    primary['non_striker_canonical_name'] = primary.apply(
        lambda r: name_map.get((r['comp_id'], r['non_striker_id']), r['non_striker_name']), axis=1
    )

    # Map bowler names
    primary['bowler_canonical_name'] = primary.apply(
        lambda r: name_map.get((r['comp_id'], r['bowler_id']), r['bowler_name']), axis=1
    )

    # Flag name mismatches
    primary['striker_name_mismatch'] = primary['striker_name'] != primary['striker_canonical_name']
    primary['bowler_name_mismatch'] = primary['bowler_name'] != primary['bowler_canonical_name']

    mismatch_count = primary['striker_name_mismatch'].sum() + primary['bowler_name_mismatch'].sum()
    print(f"  Name mismatches flagged: {mismatch_count}")

    return primary


def add_competition_tier(primary, comp_info):
    """Add competition tier and type to deliveries."""
    tier_map = comp_info.set_index('comp_id')['comp_tier']
    type_map = comp_info.set_index('comp_id')['comp_type']

    primary['comp_tier'] = primary['comp_id'].map(tier_map)
    primary['comp_type'] = primary['comp_id'].map(type_map)

    return primary


def identify_valid_abandoned_partials(balls, matches, abandoned_ids):
    """Identify abandoned matches with valid partial ball-by-ball data."""
    abandoned_balls = balls[balls['match_id'].isin(abandoned_ids)].copy()
    if len(abandoned_balls) == 0:
        return pd.DataFrame()

    # For each abandoned match, check if we have valid state reconstruction
    # Valid if: innings 1 or 2, and at least some deliveries
    valid_partials = abandoned_balls[abandoned_balls['innings'].isin([1, 2])].copy()

    # Add match result info
    match_result = matches[['match_id', 'result']].drop_duplicates()
    valid_partials = valid_partials.merge(match_result, on='match_id', how='left')

    print(f"  Abandoned matches with partial data: {valid_partials['match_id'].nunique()}")
    print(f"  Partial deliveries: {len(valid_partials)}")

    return valid_partials


def main():
    print("=" * 70)
    print("BUILD ALL-COMPETITION DELIVERIES — Task 07")
    print("=" * 70)

    # Load raw data
    balls, matches, comps, mapping, playing, teams = load_raw_data()

    # Classify competitions
    comp_info = classify_competitions(comps)
    print(f"\nCompetition classification:")
    print(comp_info.groupby(['comp_type', 'comp_tier']).size().reset_index(name='count').to_string())

    # Identify special matches
    super_over_ids, abandoned_ids, matches_with_balls = identify_special_matches(matches, balls)
    print(f"\nSpecial matches:")
    print(f"  Super Over matches: {len(super_over_ids)}")
    print(f"  Abandoned/No Result matches: {len(abandoned_ids)}")
    print(f"  Matches with ball-by-ball data: {len(matches_with_balls)}")

    # Filter primary deliveries
    primary, excluded, all_merged = filter_primary_deliveries(
        balls, matches, comps, super_over_ids, abandoned_ids
    )

    # Add canonical names
    primary = add_canonical_names(primary, mapping)

    # Add competition tier/type
    primary = add_competition_tier(primary, comp_info)

    # Identify valid abandoned partials
    abandoned_partials = identify_valid_abandoned_partials(balls, matches, abandoned_ids)

    # Super Over deliveries
    super_over_deliveries = all_merged[all_merged['innings'].isin([3, 4])].copy()
    super_over_deliveries = add_canonical_names(super_over_deliveries, mapping)
    super_over_deliveries = add_competition_tier(super_over_deliveries, comp_info)

    # Ambiguous extras
    ambiguous_extras = all_merged[all_merged['extras_type'] == 'other'].copy()
    ambiguous_extras = add_canonical_names(ambiguous_extras, mapping)
    ambiguous_extras = add_competition_tier(ambiguous_extras, comp_info)

    # Save outputs
    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("\n--- Saving datasets ---")

    # Primary all-competition deliveries
    primary_path = out_dir / "all_competition_deliveries.csv"
    primary.to_csv(primary_path, index=False)
    print(f"  Primary: {primary_path} ({len(primary)} rows)")

    # Excluded deliveries with reasons
    excluded_path = out_dir / "all_competition_excluded_deliveries.csv"
    excluded.to_csv(excluded_path, index=False)
    print(f"  Excluded: {excluded_path} ({len(excluded)} rows)")

    # Super Over deliveries
    so_path = out_dir / "super_over_deliveries.csv"
    super_over_deliveries.to_csv(so_path, index=False)
    print(f"  Super Over: {so_path} ({len(super_over_deliveries)} rows)")

    # Abandoned partials
    if len(abandoned_partials) > 0:
        ap_path = out_dir / "abandoned_partial_deliveries.csv"
        abandoned_partials.to_csv(ap_path, index=False)
        print(f"  Abandoned partials: {ap_path} ({len(abandoned_partials)} rows)")

    # Ambiguous extras
    ae_path = out_dir / "ambiguous_extras_deliveries.csv"
    ambiguous_extras.to_csv(ae_path, index=False)
    print(f"  Ambiguous extras: {ae_path} ({len(ambiguous_extras)} rows)")

    # Competition info reference
    comp_info_path = out_dir / "competition_info.csv"
    comp_info.to_csv(comp_info_path, index=False)
    print(f"  Competition info: {comp_info_path} ({len(comp_info)} rows)")

    # Summary by competition type
    print("\n--- Primary deliveries by competition type ---")
    type_summary = primary.groupby('comp_type').agg(
        deliveries=('match_id', 'count'),
        matches=('match_id', 'nunique'),
        comps=('comp_id', 'nunique'),
        players=('striker_id', 'nunique')
    ).reset_index()
    print(type_summary.to_string())

    # Summary by tier
    print("\n--- Primary deliveries by competition tier ---")
    tier_summary = primary.groupby('comp_tier').agg(
        deliveries=('match_id', 'count'),
        matches=('match_id', 'nunique'),
        comps=('comp_id', 'nunique')
    ).reset_index().sort_values('comp_tier')
    print(tier_summary.to_string())

    # Summary by season
    print("\n--- Primary deliveries by season ---")
    season_summary = primary.groupby('season').agg(
        deliveries=('match_id', 'count'),
        matches=('match_id', 'nunique'),
        comps=('comp_id', 'nunique')
    ).reset_index().sort_values('season')
    print(season_summary.to_string())

    print("\n" + "=" * 70)
    print("ALL-COMPETITION DELIVERIES BUILT")
    print("=" * 70)


if __name__ == "__main__":
    main()