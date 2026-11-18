#!/usr/bin/env python3
"""
Aggregate Player Features Across All Competitions
Task 07 — Pressure-X Multi-Competition Evidence Engine

Builds player-season and player-match features from all-competition pressure deliveries,
with competition strength adjustment and reliability tracking.
"""

import pandas as pd
import numpy as np
from pathlib import Path


# Competition adjustment factors (from methodology)
BATTER_ADJ = {
    1: {'sr': 1.000, 'dr': 1.000, 'bp': 1.000},
    2: {'sr': 1.020, 'dr': 0.967, 'bp': 0.985},
    3: {'sr': 0.925, 'dr': 0.825, 'bp': 0.890},
    4: {'sr': 0.855, 'dr': 0.925, 'bp': 0.765},
    5: {'sr': 0.890, 'dr': 0.925, 'bp': 0.825},
}

BOWLER_ADJ = {
    1: {'econ': 1.000, 'wr': 1.000, 'dot': 1.000, 'bp': 1.000},
    2: {'econ': 0.910, 'wr': 1.195, 'dot': 1.128, 'bp': 0.895},
    3: {'econ': 0.870, 'wr': 1.095, 'dot': 1.105, 'bp': 0.895},
    4: {'econ': 0.815, 'wr': 1.175, 'dot': 1.120, 'bp': 0.895},
    5: {'econ': 0.850, 'wr': 1.075, 'dot': 1.130, 'bp': 0.895},
}

PRIOR_WEIGHT = 30  # Bayesian shrinkage prior weight


def apply_shrinkage(observed_rate, n_obs, prior_rate, prior_weight=PRIOR_WEIGHT):
    """Bayesian shrinkage: (obs * n + prior * weight) / (n + weight)"""
    if n_obs <= 0:
        return prior_rate
    return (observed_rate * n_obs + prior_rate * prior_weight) / (n_obs + prior_weight)


def aggregate_batter_match(pressure_df):
    """Aggregate batter features at match level."""
    pressure_cats = ['low', 'medium', 'high', 'extreme']

    # Base aggregation (excluding grouping columns)
    base_agg = pressure_df.groupby(['match_id', 'innings', 'striker_id']).agg(
        season=('season', 'first'),
        comp_id=('comp_id', 'first'),
        comp_type=('comp_type', 'first'),
        comp_tier=('comp_tier', 'first'),
        striker_name=('striker_canonical_name', 'first'),
        batting_team_id=('batting_team_id', 'first'),
        balls_faced=('balls_faced', 'sum'),
        runs_scored=('batter_runs', 'sum'),
        fours=('is_four', 'sum'),
        sixes=('is_six', 'sum'),
        boundaries=('is_boundary', 'sum'),
        dismissed=('is_dismissed', 'sum'),
        name_mismatch=('striker_name_mismatch', 'max'),
    ).reset_index()

    # Pressure-specific
    for p in pressure_cats:
        mask = pressure_df['batting_pressure'] == p
        p_data = pressure_df[mask].groupby(['match_id', 'innings', 'striker_id']).agg(
            **{
                f'{p}_pressure_balls': ('balls_faced', 'sum'),
                f'{p}_pressure_runs': ('batter_runs', 'sum'),
                f'{p}_pressure_dismissals': ('is_dismissed', 'sum'),
                f'{p}_pressure_boundaries': ('is_boundary', 'sum'),
            }
        ).reset_index()
        base_agg = base_agg.merge(p_data, on=['match_id', 'innings', 'striker_id'], how='left')

    # High+extreme
    he_mask = pressure_df['batting_pressure'].isin(['high', 'extreme'])
    he_data = pressure_df[he_mask].groupby(['match_id', 'innings', 'striker_id']).agg(
        high_extreme_balls=('balls_faced', 'sum'),
        high_extreme_runs=('batter_runs', 'sum'),
        high_extreme_dismissals=('is_dismissed', 'sum'),
        high_extreme_boundaries=('is_boundary', 'sum'),
    ).reset_index()
    base_agg = base_agg.merge(he_data, on=['match_id', 'innings', 'striker_id'], how='left')

    # Chase
    chase_mask = pressure_df['innings'] == 2
    chase_data = pressure_df[chase_mask].groupby(['match_id', 'innings', 'striker_id']).agg(
        chase_balls=('balls_faced', 'sum'),
        chase_runs=('batter_runs', 'sum'),
        chase_dismissals=('is_dismissed', 'sum'),
        chase_boundaries=('is_boundary', 'sum'),
    ).reset_index()
    base_agg = base_agg.merge(chase_data, on=['match_id', 'innings', 'striker_id'], how='left')

    # Phase
    for phase in ['powerplay', 'middle', 'death']:
        if phase == 'powerplay':
            phase_mask = pressure_df['is_powerplay']
        elif phase == 'middle':
            phase_mask = pressure_df['is_middle_over']
        else:
            phase_mask = pressure_df['is_death_over']
        phase_data = pressure_df[phase_mask].groupby(['match_id', 'innings', 'striker_id']).agg(
            **{
                f'{phase}_balls': ('balls_faced', 'sum'),
                f'{phase}_runs': ('batter_runs', 'sum'),
            }
        ).reset_index()
        base_agg = base_agg.merge(phase_data, on=['match_id', 'innings', 'striker_id'], how='left')

    # Fill NaN with 0
    fill_cols = []
    for p in pressure_cats:
        fill_cols.extend([f'{p}_pressure_balls', f'{p}_pressure_runs', f'{p}_pressure_dismissals', f'{p}_pressure_boundaries'])
    fill_cols.extend(['high_extreme_balls', 'high_extreme_runs', 'high_extreme_dismissals', 'high_extreme_boundaries'])
    fill_cols.extend(['chase_balls', 'chase_runs', 'chase_dismissals', 'chase_boundaries'])
    for phase in ['powerplay', 'middle', 'death']:
        fill_cols.extend([f'{phase}_balls', f'{phase}_runs'])

    for c in fill_cols:
        if c in base_agg.columns:
            base_agg[c] = base_agg[c].fillna(0).astype(int if 'balls' in c or 'runs' in c or 'dismissals' in c or 'boundaries' in c else float)

    # Compute rates
    base_agg['strike_rate'] = np.where(base_agg['balls_faced'] > 0,
                                       base_agg['runs_scored'] / base_agg['balls_faced'] * 100, 0)
    base_agg['dismissal_rate'] = np.where(base_agg['balls_faced'] > 0,
                                          base_agg['dismissed'] / base_agg['balls_faced'], 0)
    base_agg['boundary_pct'] = np.where(base_agg['balls_faced'] > 0,
                                        base_agg['boundaries'] / base_agg['balls_faced'] * 100, 0)

    for p in pressure_cats:
        b_col = f'{p}_pressure_balls'
        if b_col in base_agg.columns:
            base_agg[f'{p}_pressure_sr'] = np.where(base_agg[b_col] > 0,
                                                    base_agg[f'{p}_pressure_runs'] / base_agg[b_col] * 100, 0)
            base_agg[f'{p}_pressure_dismissal_rate'] = np.where(base_agg[b_col] > 0,
                                                                base_agg[f'{p}_pressure_dismissals'] / base_agg[b_col], 0)
            base_agg[f'{p}_pressure_boundary_pct'] = np.where(base_agg[b_col] > 0,
                                                              base_agg[f'{p}_pressure_boundaries'] / base_agg[b_col] * 100, 0)

    if 'high_extreme_balls' in base_agg.columns:
        base_agg['high_extreme_sr'] = np.where(base_agg['high_extreme_balls'] > 0,
                                               base_agg['high_extreme_runs'] / base_agg['high_extreme_balls'] * 100, 0)
        base_agg['high_extreme_dismissal_rate'] = np.where(base_agg['high_extreme_balls'] > 0,
                                                           base_agg['high_extreme_dismissals'] / base_agg['high_extreme_balls'], 0)
        base_agg['high_extreme_boundary_pct'] = np.where(base_agg['high_extreme_balls'] > 0,
                                                         base_agg['high_extreme_boundaries'] / base_agg['high_extreme_balls'] * 100, 0)

    if 'chase_balls' in base_agg.columns:
        base_agg['chase_strike_rate'] = np.where(base_agg['chase_balls'] > 0,
                                                 base_agg['chase_runs'] / base_agg['chase_balls'] * 100, 0)
        base_agg['chase_dismissal_rate'] = np.where(base_agg['chase_balls'] > 0,
                                                    base_agg['chase_dismissals'] / base_agg['chase_balls'], 0)
        base_agg['chase_boundary_pct'] = np.where(base_agg['chase_balls'] > 0,
                                                  base_agg['chase_boundaries'] / base_agg['chase_balls'] * 100, 0)

    for phase in ['powerplay', 'middle', 'death']:
        b_col = f'{phase}_balls'
        if b_col in base_agg.columns:
            base_agg[f'{phase}_sr'] = np.where(base_agg[b_col] > 0,
                                               base_agg[f'{phase}_runs'] / base_agg[b_col] * 100, 0)

    return base_agg


def aggregate_bowler_match(pressure_df):
    """Aggregate bowler features at match level."""
    pressure_cats = ['low', 'medium', 'high', 'extreme']

    base_agg = pressure_df.groupby(['match_id', 'innings', 'bowler_id']).agg(
        season=('season', 'first'),
        comp_id=('comp_id', 'first'),
        comp_type=('comp_type', 'first'),
        comp_tier=('comp_tier', 'first'),
        bowler_name=('bowler_canonical_name', 'first'),
        bowling_team_id=('bowling_team_id', 'first'),
        balls_bowled=('legal_ball_bowled', 'sum'),
        runs_conceded=('bowler_runs_conceded', 'sum'),
        wickets=('bowler_wicket', 'sum'),
        dots=('is_dot', 'sum'),
        boundaries_conceded=('boundary_conceded', 'sum'),
        name_mismatch=('bowler_name_mismatch', 'max'),
    ).reset_index()

    for p in pressure_cats:
        mask = pressure_df['bowling_pressure'] == p
        p_data = pressure_df[mask].groupby(['match_id', 'innings', 'bowler_id']).agg(
            **{
                f'{p}_pressure_balls': ('legal_ball_bowled', 'sum'),
                f'{p}_pressure_runs': ('bowler_runs_conceded', 'sum'),
                f'{p}_pressure_wickets': ('bowler_wicket', 'sum'),
                f'{p}_pressure_dots': ('is_dot', 'sum'),
                f'{p}_pressure_boundaries': ('boundary_conceded', 'sum'),
            }
        ).reset_index()
        base_agg = base_agg.merge(p_data, on=['match_id', 'innings', 'bowler_id'], how='left')

    he_mask = pressure_df['bowling_pressure'].isin(['high', 'extreme'])
    he_data = pressure_df[he_mask].groupby(['match_id', 'innings', 'bowler_id']).agg(
        high_extreme_balls=('legal_ball_bowled', 'sum'),
        high_extreme_runs=('bowler_runs_conceded', 'sum'),
        high_extreme_wickets=('bowler_wicket', 'sum'),
        high_extreme_dots=('is_dot', 'sum'),
        high_extreme_boundaries=('boundary_conceded', 'sum'),
    ).reset_index()
    base_agg = base_agg.merge(he_data, on=['match_id', 'innings', 'bowler_id'], how='left')

    def_mask = pressure_df['innings'] == 2
    def_data = pressure_df[def_mask].groupby(['match_id', 'innings', 'bowler_id']).agg(
        defend_balls=('legal_ball_bowled', 'sum'),
        defend_runs=('bowler_runs_conceded', 'sum'),
        defend_wickets=('bowler_wicket', 'sum'),
        defend_dots=('is_dot', 'sum'),
    ).reset_index()
    base_agg = base_agg.merge(def_data, on=['match_id', 'innings', 'bowler_id'], how='left')

    for phase in ['powerplay', 'middle', 'death']:
        if phase == 'powerplay':
            phase_mask = pressure_df['is_powerplay']
        elif phase == 'middle':
            phase_mask = pressure_df['is_middle_over']
        else:
            phase_mask = pressure_df['is_death_over']
        phase_data = pressure_df[phase_mask].groupby(['match_id', 'innings', 'bowler_id']).agg(
            **{
                f'{phase}_balls': ('legal_ball_bowled', 'sum'),
                f'{phase}_runs': ('bowler_runs_conceded', 'sum'),
                f'{phase}_wickets': ('bowler_wicket', 'sum'),
            }
        ).reset_index()
        base_agg = base_agg.merge(phase_data, on=['match_id', 'innings', 'bowler_id'], how='left')

    # Fill NaN
    fill_cols = []
    for p in pressure_cats:
        fill_cols.extend([f'{p}_pressure_balls', f'{p}_pressure_runs', f'{p}_pressure_wickets',
                          f'{p}_pressure_dots', f'{p}_pressure_boundaries'])
    fill_cols.extend(['high_extreme_balls', 'high_extreme_runs', 'high_extreme_wickets',
                      'high_extreme_dots', 'high_extreme_boundaries'])
    fill_cols.extend(['defend_balls', 'defend_runs', 'defend_wickets', 'defend_dots'])
    for phase in ['powerplay', 'middle', 'death']:
        fill_cols.extend([f'{phase}_balls', f'{phase}_runs', f'{phase}_wickets'])

    for c in fill_cols:
        if c in base_agg.columns:
            base_agg[c] = base_agg[c].fillna(0)

    # Rates
    base_agg['economy_rate'] = np.where(base_agg['balls_bowled'] > 0,
                                        base_agg['runs_conceded'] / base_agg['balls_bowled'] * 6, 0)
    base_agg['wicket_rate'] = np.where(base_agg['balls_bowled'] > 0,
                                       base_agg['wickets'] / base_agg['balls_bowled'], 0)
    base_agg['dot_ball_pct'] = np.where(base_agg['balls_bowled'] > 0,
                                        base_agg['dots'] / base_agg['balls_bowled'] * 100, 0)
    base_agg['boundary_concession_pct'] = np.where(base_agg['balls_bowled'] > 0,
                                                   base_agg['boundaries_conceded'] / base_agg['balls_bowled'] * 100, 0)
    base_agg['wickets_per_over'] = np.where(base_agg['balls_bowled'] > 0,
                                            base_agg['wickets'] / base_agg['balls_bowled'] * 6, 0)

    for p in pressure_cats:
        b_col = f'{p}_pressure_balls'
        if b_col in base_agg.columns:
            base_agg[f'{p}_pressure_economy'] = np.where(base_agg[b_col] > 0,
                                                         base_agg[f'{p}_pressure_runs'] / base_agg[b_col] * 6, 0)
            base_agg[f'{p}_pressure_wicket_rate'] = np.where(base_agg[b_col] > 0,
                                                             base_agg[f'{p}_pressure_wickets'] / base_agg[b_col], 0)
            base_agg[f'{p}_pressure_dot_pct'] = np.where(base_agg[b_col] > 0,
                                                         base_agg[f'{p}_pressure_dots'] / base_agg[b_col] * 100, 0)
            base_agg[f'{p}_pressure_boundary_pct'] = np.where(base_agg[b_col] > 0,
                                                              base_agg[f'{p}_pressure_boundaries'] / base_agg[b_col] * 100, 0)
            base_agg[f'{p}_pressure_wickets_per_over'] = np.where(base_agg[b_col] > 0,
                                                                  base_agg[f'{p}_pressure_wickets'] / base_agg[b_col] * 6, 0)

    if 'high_extreme_balls' in base_agg.columns:
        base_agg['high_extreme_economy'] = np.where(base_agg['high_extreme_balls'] > 0,
                                                    base_agg['high_extreme_runs'] / base_agg['high_extreme_balls'] * 6, 0)
        base_agg['high_extreme_wicket_rate'] = np.where(base_agg['high_extreme_balls'] > 0,
                                                        base_agg['high_extreme_wickets'] / base_agg['high_extreme_balls'], 0)
        base_agg['high_extreme_dot_pct'] = np.where(base_agg['high_extreme_balls'] > 0,
                                                    base_agg['high_extreme_dots'] / base_agg['high_extreme_balls'] * 100, 0)
        base_agg['high_extreme_boundary_pct'] = np.where(base_agg['high_extreme_balls'] > 0,
                                                         base_agg['high_extreme_boundaries'] / base_agg['high_extreme_balls'] * 100, 0)
        base_agg['high_extreme_wickets_per_over'] = np.where(base_agg['high_extreme_balls'] > 0,
                                                             base_agg['high_extreme_wickets'] / base_agg['high_extreme_balls'] * 6, 0)

    if 'defend_balls' in base_agg.columns:
        base_agg['defend_economy'] = np.where(base_agg['defend_balls'] > 0,
                                              base_agg['defend_runs'] / base_agg['defend_balls'] * 6, 0)
        base_agg['defend_wicket_rate'] = np.where(base_agg['defend_balls'] > 0,
                                                  base_agg['defend_wickets'] / base_agg['defend_balls'], 0)
        base_agg['defend_dot_pct'] = np.where(base_agg['defend_balls'] > 0,
                                              base_agg['defend_dots'] / base_agg['defend_balls'] * 100, 0)
        base_agg['defend_wickets_per_over'] = np.where(base_agg['defend_balls'] > 0,
                                                       base_agg['defend_wickets'] / base_agg['defend_balls'] * 6, 0)

    for phase in ['powerplay', 'middle', 'death']:
        b_col = f'{phase}_balls'
        if b_col in base_agg.columns:
            base_agg[f'{phase}_economy'] = np.where(base_agg[b_col] > 0,
                                                    base_agg[f'{phase}_runs'] / base_agg[b_col] * 6, 0)
            base_agg[f'{phase}_wickets_per_over'] = np.where(base_agg[b_col] > 0,
                                                             base_agg[f'{phase}_wickets'] / base_agg[b_col] * 6, 0)

    return base_agg


def aggregate_batter_season(batter_match):
    """Aggregate batter match features to season level with shrinkage and competition adjustment."""
    grouped = batter_match.groupby(['striker_id', 'striker_name', 'season'])

    counts = grouped.agg(
        matches=('match_id', 'nunique'),
        innings=('innings', 'count'),
        total_balls=('balls_faced', 'sum'),
        total_runs=('runs_scored', 'sum'),
        total_fours=('fours', 'sum'),
        total_sixes=('sixes', 'sum'),
        total_boundaries=('boundaries', 'sum'),
        total_dismissals=('dismissed', 'sum'),
        name_mismatch=('name_mismatch', 'max'),
        comp_types=('comp_type', lambda x: list(x.unique())),
        comp_tiers=('comp_tier', lambda x: list(x.unique())),
    ).reset_index()

    pressure_cats = ['low', 'medium', 'high', 'extreme']
    for p in pressure_cats:
        for metric in ['balls', 'runs', 'dismissals', 'boundaries']:
            col = f'{p}_pressure_{metric}'
            if col in batter_match.columns:
                counts[f'{p}_{metric}'] = grouped[col].sum().values

    for metric in ['balls', 'runs', 'dismissals', 'boundaries']:
        col = f'high_extreme_{metric}'
        if col in batter_match.columns:
            counts[f'high_extreme_{metric}'] = grouped[col].sum().values

    for metric in ['balls', 'runs', 'dismissals', 'boundaries']:
        col = f'chase_{metric}'
        if col in batter_match.columns:
            counts[f'chase_{metric}'] = grouped[col].sum().values

    for phase in ['powerplay', 'middle', 'death']:
        for metric in ['balls', 'runs']:
            col = f'{phase}_{metric}'
            if col in batter_match.columns:
                counts[f'{phase}_{metric}'] = grouped[col].sum().values

    # Raw rates
    counts['strike_rate'] = np.where(counts['total_balls'] > 0,
                                     counts['total_runs'] / counts['total_balls'] * 100, 0)
    counts['dismissal_rate'] = np.where(counts['total_balls'] > 0,
                                        counts['total_dismissals'] / counts['total_balls'], 0)
    counts['boundary_pct'] = np.where(counts['total_balls'] > 0,
                                      counts['total_boundaries'] / counts['total_balls'] * 100, 0)

    for p in pressure_cats:
        b_col = f'{p}_balls'
        if b_col in counts.columns:
            counts[f'{p}_pressure_sr'] = np.where(counts[b_col] > 0,
                                                  counts[f'{p}_runs'] / counts[b_col] * 100, 0)
            counts[f'{p}_pressure_dismissal_rate'] = np.where(counts[b_col] > 0,
                                                              counts[f'{p}_dismissals'] / counts[b_col], 0)
            counts[f'{p}_pressure_boundary_pct'] = np.where(counts[b_col] > 0,
                                                            counts[f'{p}_boundaries'] / counts[b_col] * 100, 0)

    if 'high_extreme_balls' in counts.columns:
        counts['high_extreme_sr'] = np.where(counts['high_extreme_balls'] > 0,
                                             counts['high_extreme_runs'] / counts['high_extreme_balls'] * 100, 0)
        counts['high_extreme_dismissal_rate'] = np.where(counts['high_extreme_balls'] > 0,
                                                         counts['high_extreme_dismissals'] / counts['high_extreme_balls'], 0)
        counts['high_extreme_boundary_pct'] = np.where(counts['high_extreme_balls'] > 0,
                                                       counts['high_extreme_boundaries'] / counts['high_extreme_balls'] * 100, 0)

    if 'chase_balls' in counts.columns:
        counts['chase_strike_rate'] = np.where(counts['chase_balls'] > 0,
                                               counts['chase_runs'] / counts['chase_balls'] * 100, 0)
        counts['chase_dismissal_rate'] = np.where(counts['chase_balls'] > 0,
                                                  counts['chase_dismissals'] / counts['chase_balls'], 0)
        counts['chase_boundary_pct'] = np.where(counts['chase_balls'] > 0,
                                                counts['chase_boundaries'] / counts['chase_balls'] * 100, 0)

    for phase in ['powerplay', 'middle', 'death']:
        b_col = f'{phase}_balls'
        if b_col in counts.columns:
            counts[f'{phase}_sr'] = np.where(counts[b_col] > 0,
                                             counts[f'{phase}_runs'] / counts[b_col] * 100, 0)

    # Competition-adjusted rates
    adj_metrics = ['strike_rate', 'dismissal_rate', 'boundary_pct']
    for metric in adj_metrics:
        tier_data = batter_match.groupby(['striker_id', 'season', 'comp_tier']).agg(
            balls=('balls_faced', 'sum'),
            runs=('runs_scored', 'sum'),
            dismissals=('dismissed', 'sum'),
            boundaries=('boundaries', 'sum'),
        ).reset_index()

        if metric == 'strike_rate':
            tier_data['raw'] = np.where(tier_data['balls'] > 0, tier_data['runs'] / tier_data['balls'] * 100, 0)
            adj_key = 'sr'
        elif metric == 'dismissal_rate':
            tier_data['raw'] = np.where(tier_data['balls'] > 0, tier_data['dismissals'] / tier_data['balls'], 0)
            adj_key = 'dr'
        elif metric == 'boundary_pct':
            tier_data['raw'] = np.where(tier_data['balls'] > 0, tier_data['boundaries'] / tier_data['balls'] * 100, 0)
            adj_key = 'bp'

        tier_data['adj'] = tier_data.apply(
            lambda r: r['raw'] * BATTER_ADJ.get(int(r['comp_tier']), {}).get(adj_key, 1.0), axis=1
        )

        weighted = tier_data.groupby(['striker_id', 'season']).apply(
            lambda g: np.average(g['adj'], weights=g['balls']) if g['balls'].sum() > 0 else 0
        ).reset_index()
        weighted.columns = ['striker_id', 'season', f'{metric}_comp_adj']
        counts = counts.merge(weighted, on=['striker_id', 'season'], how='left')

    # Shrinkage priors
    priors = {}
    rate_cols = ['strike_rate', 'dismissal_rate', 'boundary_pct'] + \
                [f'{p}_pressure_sr' for p in pressure_cats] + \
                [f'{p}_pressure_dismissal_rate' for p in pressure_cats] + \
                [f'{p}_pressure_boundary_pct' for p in pressure_cats] + \
                ['high_extreme_sr', 'high_extreme_dismissal_rate', 'high_extreme_boundary_pct'] + \
                ['chase_strike_rate', 'chase_dismissal_rate', 'chase_boundary_pct'] + \
                [f'{phase}_sr' for phase in ['powerplay', 'middle', 'death']]

    for col in rate_cols:
        if col in counts.columns:
            if 'strike_rate' in col or '_sr' in col:
                priors[col] = (batter_match.groupby('season')['runs_scored'].sum() /
                               batter_match.groupby('season')['balls_faced'].sum() * 100).to_dict()
            elif 'dismissal_rate' in col:
                priors[col] = (batter_match.groupby('season')['dismissed'].sum() /
                               batter_match.groupby('season')['balls_faced'].sum()).to_dict()
            elif 'boundary_pct' in col:
                priors[col] = (batter_match.groupby('season')['boundaries'].sum() /
                               batter_match.groupby('season')['balls_faced'].sum() * 100).to_dict()

    for col in rate_cols:
        if col in counts.columns:
            prior_col = priors.get(col, {})
            counts[f'{col}_adj'] = counts.apply(
                lambda r: apply_shrinkage(r[col], r['total_balls'], prior_col.get(r['season'], 0)), axis=1
            )

    # Reliability
    counts['min_balls_100'] = counts['total_balls'] >= 100
    counts['min_balls_50'] = counts['total_balls'] >= 50
    counts['min_high_extreme_30'] = counts.get('high_extreme_balls', 0) >= 30
    counts['min_chase_30'] = counts.get('chase_balls', 0) >= 30

    return counts


def aggregate_bowler_season(bowler_match):
    """Aggregate bowler match features to season level with shrinkage and competition adjustment."""
    grouped = bowler_match.groupby(['bowler_id', 'bowler_name', 'season'])

    counts = grouped.agg(
        matches=('match_id', 'nunique'),
        innings=('innings', 'count'),
        total_balls=('balls_bowled', 'sum'),
        total_runs=('runs_conceded', 'sum'),
        total_wickets=('wickets', 'sum'),
        total_dots=('dots', 'sum'),
        total_boundaries=('boundaries_conceded', 'sum'),
        name_mismatch=('name_mismatch', 'max'),
        comp_types=('comp_type', lambda x: list(x.unique())),
        comp_tiers=('comp_tier', lambda x: list(x.unique())),
    ).reset_index()

    pressure_cats = ['low', 'medium', 'high', 'extreme']
    for p in pressure_cats:
        for metric in ['balls', 'runs', 'wickets', 'dots', 'boundaries']:
            col = f'{p}_pressure_{metric}'
            if col in bowler_match.columns:
                counts[f'{p}_{metric}'] = grouped[col].sum().values

    for metric in ['balls', 'runs', 'wickets', 'dots', 'boundaries']:
        col = f'high_extreme_{metric}'
        if col in bowler_match.columns:
            counts[f'high_extreme_{metric}'] = grouped[col].sum().values

    for metric in ['balls', 'runs', 'wickets', 'dots']:
        col = f'defend_{metric}'
        if col in bowler_match.columns:
            counts[f'defend_{metric}'] = grouped[col].sum().values

    for phase in ['powerplay', 'middle', 'death']:
        for metric in ['balls', 'runs', 'wickets']:
            col = f'{phase}_{metric}'
            if col in bowler_match.columns:
                counts[f'{phase}_{metric}'] = grouped[col].sum().values

    # Raw rates
    counts['economy_rate'] = np.where(counts['total_balls'] > 0,
                                      counts['total_runs'] / counts['total_balls'] * 6, 0)
    counts['wicket_rate'] = np.where(counts['total_balls'] > 0,
                                     counts['total_wickets'] / counts['total_balls'], 0)
    counts['dot_ball_pct'] = np.where(counts['total_balls'] > 0,
                                      counts['total_dots'] / counts['total_balls'] * 100, 0)
    counts['boundary_concession_pct'] = np.where(counts['total_balls'] > 0,
                                                 counts['total_boundaries'] / counts['total_balls'] * 100, 0)
    counts['wickets_per_over'] = np.where(counts['total_balls'] > 0,
                                          counts['total_wickets'] / counts['total_balls'] * 6, 0)

    for p in pressure_cats:
        b_col = f'{p}_balls'
        if b_col in counts.columns:
            counts[f'{p}_pressure_economy'] = np.where(counts[b_col] > 0,
                                                       counts[f'{p}_runs'] / counts[b_col] * 6, 0)
            counts[f'{p}_pressure_wicket_rate'] = np.where(counts[b_col] > 0,
                                                           counts[f'{p}_wickets'] / counts[b_col], 0)
            counts[f'{p}_pressure_dot_pct'] = np.where(counts[b_col] > 0,
                                                       counts[f'{p}_dots'] / counts[b_col] * 100, 0)
            counts[f'{p}_pressure_boundary_pct'] = np.where(counts[b_col] > 0,
                                                            counts[f'{p}_boundaries'] / counts[b_col] * 100, 0)
            counts[f'{p}_pressure_wickets_per_over'] = np.where(counts[b_col] > 0,
                                                                counts[f'{p}_wickets'] / counts[b_col] * 6, 0)

    if 'high_extreme_balls' in counts.columns:
        counts['high_extreme_economy'] = np.where(counts['high_extreme_balls'] > 0,
                                                  counts['high_extreme_runs'] / counts['high_extreme_balls'] * 6, 0)
        counts['high_extreme_wicket_rate'] = np.where(counts['high_extreme_balls'] > 0,
                                                      counts['high_extreme_wickets'] / counts['high_extreme_balls'], 0)
        counts['high_extreme_dot_pct'] = np.where(counts['high_extreme_balls'] > 0,
                                                  counts['high_extreme_dots'] / counts['high_extreme_balls'] * 100, 0)
        counts['high_extreme_boundary_pct'] = np.where(counts['high_extreme_balls'] > 0,
                                                       counts['high_extreme_boundaries'] / counts['high_extreme_balls'] * 100, 0)
        counts['high_extreme_wickets_per_over'] = np.where(counts['high_extreme_balls'] > 0,
                                                           counts['high_extreme_wickets'] / counts['high_extreme_balls'] * 6, 0)

    if 'defend_balls' in counts.columns:
        counts['defend_economy'] = np.where(counts['defend_balls'] > 0,
                                            counts['defend_runs'] / counts['defend_balls'] * 6, 0)
        counts['defend_wicket_rate'] = np.where(counts['defend_balls'] > 0,
                                                counts['defend_wickets'] / counts['defend_balls'], 0)
        counts['defend_dot_pct'] = np.where(counts['defend_balls'] > 0,
                                            counts['defend_dots'] / counts['defend_balls'] * 100, 0)
        counts['defend_wickets_per_over'] = np.where(counts['defend_balls'] > 0,
                                                     counts['defend_wickets'] / counts['defend_balls'] * 6, 0)

    for phase in ['powerplay', 'middle', 'death']:
        b_col = f'{phase}_balls'
        if b_col in counts.columns:
            counts[f'{phase}_economy'] = np.where(counts[b_col] > 0,
                                                  counts[f'{phase}_runs'] / counts[b_col] * 6, 0)
            counts[f'{phase}_wickets_per_over'] = np.where(counts[b_col] > 0,
                                                           counts[f'{phase}_wickets'] / counts[b_col] * 6, 0)

    # Competition adjustment
    adj_metrics = ['economy_rate', 'wicket_rate', 'dot_ball_pct', 'boundary_concession_pct']
    for metric in adj_metrics:
        tier_data = bowler_match.groupby(['bowler_id', 'season', 'comp_tier']).agg(
            balls=('balls_bowled', 'sum'),
            runs=('runs_conceded', 'sum'),
            wickets=('wickets', 'sum'),
            dots=('dots', 'sum'),
            boundaries=('boundaries_conceded', 'sum'),
        ).reset_index()

        if metric == 'economy_rate':
            tier_data['raw'] = np.where(tier_data['balls'] > 0, tier_data['runs'] / tier_data['balls'] * 6, 0)
            adj_key = 'econ'
        elif metric == 'wicket_rate':
            tier_data['raw'] = np.where(tier_data['balls'] > 0, tier_data['wickets'] / tier_data['balls'], 0)
            adj_key = 'wr'
        elif metric == 'dot_ball_pct':
            tier_data['raw'] = np.where(tier_data['balls'] > 0, tier_data['dots'] / tier_data['balls'] * 100, 0)
            adj_key = 'dot'
        elif metric == 'boundary_concession_pct':
            tier_data['raw'] = np.where(tier_data['balls'] > 0, tier_data['boundaries'] / tier_data['balls'] * 100, 0)
            adj_key = 'bp'

        tier_data['adj'] = tier_data.apply(
            lambda r: r['raw'] * BOWLER_ADJ.get(int(r['comp_tier']), {}).get(adj_key, 1.0), axis=1
        )

        weighted = tier_data.groupby(['bowler_id', 'season']).apply(
            lambda g: np.average(g['adj'], weights=g['balls']) if g['balls'].sum() > 0 else 0
        ).reset_index()
        weighted.columns = ['bowler_id', 'season', f'{metric}_comp_adj']
        counts = counts.merge(weighted, on=['bowler_id', 'season'], how='left')

    # Shrinkage
    priors = {}
    rate_cols = ['economy_rate', 'wicket_rate', 'dot_ball_pct', 'boundary_concession_pct',
                 'wickets_per_over'] + \
                [f'{p}_pressure_economy' for p in pressure_cats] + \
                [f'{p}_pressure_wicket_rate' for p in pressure_cats] + \
                [f'{p}_pressure_dot_pct' for p in pressure_cats] + \
                [f'{p}_pressure_boundary_pct' for p in pressure_cats] + \
                ['high_extreme_economy', 'high_extreme_wicket_rate', 'high_extreme_dot_pct',
                 'high_extreme_boundary_pct', 'high_extreme_wickets_per_over'] + \
                ['defend_economy', 'defend_wicket_rate', 'defend_dot_pct', 'defend_wickets_per_over'] + \
                [f'{phase}_economy' for phase in ['powerplay', 'middle', 'death']] + \
                [f'{phase}_wickets_per_over' for phase in ['powerplay', 'middle', 'death']]

    for col in rate_cols:
        if col in counts.columns:
            if 'economy' in col:
                priors[col] = (bowler_match.groupby('season')['runs_conceded'].sum() /
                               bowler_match.groupby('season')['balls_bowled'].sum() * 6).to_dict()
            elif 'wicket_rate' in col or 'wickets_per_over' in col:
                priors[col] = (bowler_match.groupby('season')['wickets'].sum() /
                               bowler_match.groupby('season')['balls_bowled'].sum() * 6).to_dict()
            elif 'dot_pct' in col:
                priors[col] = (bowler_match.groupby('season')['dots'].sum() /
                               bowler_match.groupby('season')['balls_bowled'].sum() * 100).to_dict()
            elif 'boundary' in col:
                priors[col] = (bowler_match.groupby('season')['boundaries_conceded'].sum() /
                               bowler_match.groupby('season')['balls_bowled'].sum() * 100).to_dict()

    for col in rate_cols:
        if col in counts.columns:
            prior_col = priors.get(col, {})
            counts[f'{col}_adj'] = counts.apply(
                lambda r: apply_shrinkage(r[col], r['total_balls'], prior_col.get(r['season'], 0)), axis=1
            )

    # Reliability
    counts['min_balls_100'] = counts['total_balls'] >= 100
    counts['min_balls_50'] = counts['total_balls'] >= 50
    counts['min_high_extreme_30'] = counts.get('high_extreme_balls', 0) >= 30
    counts['min_defend_30'] = counts.get('defend_balls', 0) >= 30

    return counts


def add_seasons_played(batter_season, bowler_season):
    """Add seasons_played count per player."""
    batter_seasons = batter_season.groupby('striker_id')['season'].nunique().reset_index()
    batter_seasons.columns = ['striker_id', 'seasons_played']
    batter_season = batter_season.merge(batter_seasons, on='striker_id', how='left')

    bowler_seasons = bowler_season.groupby('bowler_id')['season'].nunique().reset_index()
    bowler_seasons.columns = ['bowler_id', 'seasons_played']
    bowler_season = bowler_season.merge(bowler_seasons, on='bowler_id', how='left')

    return batter_season, bowler_season


def main():
    print("=" * 70)
    print("AGGREGATE ALL-COMPETITION PLAYER FEATURES — Task 07")
    print("=" * 70)

    # Load pressure deliveries
    pressure = pd.read_csv("data/processed/all_competition_pressure_deliveries.csv", low_memory=False)
    print(f"Loaded pressure deliveries: {len(pressure)} rows")

    # Aggregate batter match features
    print("\n--- Aggregating batter match features ---")
    batter_match = aggregate_batter_match(pressure)
    print(f"Batter match features: {len(batter_match)} rows")

    # Aggregate bowler match features
    print("\n--- Aggregating bowler match features ---")
    bowler_match = aggregate_bowler_match(pressure)
    print(f"Bowler match features: {len(bowler_match)} rows")

    # Aggregate to season level
    print("\n--- Aggregating batter season features ---")
    batter_season = aggregate_batter_season(batter_match)
    print(f"Batter season features: {len(batter_season)} rows")

    print("\n--- Aggregating bowler season features ---")
    bowler_season = aggregate_bowler_season(bowler_match)
    print(f"Bowler season features: {len(bowler_season)} rows")

    # Add seasons played
    print("\n--- Adding seasons played ---")
    batter_season, bowler_season = add_seasons_played(batter_season, bowler_season)

    # Save
    out_dir = Path("data/processed")
    batter_match.to_csv(out_dir / "all_competition_batter_match_features.csv", index=False)
    bowler_match.to_csv(out_dir / "all_competition_bowler_match_features.csv", index=False)
    batter_season.to_csv(out_dir / "all_competition_batter_season_features.csv", index=False)
    bowler_season.to_csv(out_dir / "all_competition_bowler_season_features.csv", index=False)

    print(f"\n--- Saved ---")
    print(f"  Batter match: {out_dir}/all_competition_batter_match_features.csv ({len(batter_match)} rows)")
    print(f"  Bowler match: {out_dir}/all_competition_bowler_match_features.csv ({len(bowler_match)} rows)")
    print(f"  Batter season: {out_dir}/all_competition_batter_season_features.csv ({len(batter_season)} rows)")
    print(f"  Bowler season: {out_dir}/all_competition_bowler_season_features.csv ({len(bowler_season)} rows)")

    # Summary stats
    print(f"\n--- Summary ---")
    print(f"Unique batters: {batter_season['striker_id'].nunique()}")
    print(f"Unique bowlers: {bowler_season['bowler_id'].nunique()}")
    print(f"Seasons covered: {sorted(batter_season['season'].unique())}")

    # Competition type breakdown
    print(f"\nBatter match by comp_type:")
    print(batter_match['comp_type'].value_counts())
    print(f"\nBowler match by comp_type:")
    print(bowler_match['comp_type'].value_counts())

    print("\n" + "=" * 70)
    print("ALL-COMPETITION PLAYER FEATURES AGGREGATED")
    print("=" * 70)


if __name__ == "__main__":
    main()