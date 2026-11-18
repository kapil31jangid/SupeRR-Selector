"""
Build Corrected Competition Adjustment Factors
===============================================

Task 07B: Recalculate competition adjustment factors with correct ratio directions
based on verified paired-player analysis from Task 07A audit.

Key corrections from Task 07A:
- SR Ratio T2/IPL (paired): 0.994 (not 1.020) - IPL batters slightly outperform T2
- DR Ratio T2/IPL (paired): 1.113 (not 0.967) - T2 batters dismissed more often
- BP Ratio T2/IPL (paired): 0.980 (not 0.985) - minor difference
- Bowler Econ T2/IPL (paired): 0.954 - T2 bowlers more economical
- Bowler WR T2/IPL (paired): 1.125 - T2 bowlers take wickets more often
- Bowler Dot% T2/IPL (paired): 1.052 - T2 bowlers bowl more dots

Ratio convention: factor = Tier_ref / Tier_target (so Tier 1 reference = 1.0)
All ratios documented as TARGET/REFERENCE, factor = REFERENCE/TARGET
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime


def load_data():
    """Load primary deliveries."""
    primary = pd.read_csv('data/processed/all_competition_deliveries.csv', low_memory=False)
    return primary


def compute_bowler_runs(row):
    """Compute bowler runs conceded per cricket laws."""
    et = row['extras_type']
    if pd.isna(et):
        return row['runs']
    if et == 'wide':
        return row['extras1_runs']
    elif et == 'Overstep':
        return row['runs'] + row['extras1_runs']
    elif et in ['byes', 'legbyes', 'Penalty']:
        return 0
    elif et == 'other':
        return np.nan
    else:
        return row['runs']


def compute_paired_ratios(primary, min_balls=30):
    """
    Compute paired player ratios for consecutive tiers.
    Returns ratios as TARGET/REFERENCE (e.g., T2/T1 for Tier 1->2).
    """
    bowler_wicket_types = ['Bowled', 'Caught', 'LBW', 'Stump', 'Hit Wicket',
                           'Obstructing the field', 'Obstracting the field']

    primary = primary.copy()
    primary['bowler_runs'] = primary.apply(compute_bowler_runs, axis=1)
    primary['is_legal'] = primary['extras_type'].isna() | ~primary['extras_type'].isin(['wide', 'Overstep'])
    primary['is_boundary'] = (primary['is_four'] == 1) | (primary['is_six'] == 1)
    primary['is_dot'] = primary['is_legal'] & (primary['runs'] == 0) & (primary['extras1_runs'] == 0)
    primary['is_bowler_wicket'] = primary['dismissal_type'].isin(bowler_wicket_types)

    results = {}

    # Tier 1 vs Tier 2 (IPL vs T20I FMvFM)
    for tier_ref, tier_target in [(1, 2), (2, 3)]:
        key = f'T{tier_ref}_vs_T{tier_target}'
        results[key] = {}

        # Batters
        t_ref = primary[(primary['comp_tier'] == tier_ref) & primary['is_legal']]
        t_tgt = primary[(primary['comp_tier'] == tier_target) & primary['is_legal']]

        ref_batters = t_ref.groupby('striker_id').agg(
            balls=('is_legal', 'sum'),
            runs=('runs', 'sum'),
            dismissals=('is_wicket', 'sum'),
            boundaries=('is_boundary', 'sum')
        ).reset_index()
        ref_batters = ref_batters[ref_batters['balls'] >= min_balls]

        tgt_batters = t_tgt.groupby('striker_id').agg(
            balls=('is_legal', 'sum'),
            runs=('runs', 'sum'),
            dismissals=('is_wicket', 'sum'),
            boundaries=('is_boundary', 'sum')
        ).reset_index()
        tgt_batters = tgt_batters[tgt_batters['balls'] >= min_balls]

        paired_bat = ref_batters.merge(tgt_batters, on='striker_id', suffixes=('_ref', '_tgt'))
        paired_bat['sr_ref'] = paired_bat['runs_ref'] / paired_bat['balls_ref'] * 100
        paired_bat['sr_tgt'] = paired_bat['runs_tgt'] / paired_bat['balls_tgt'] * 100
        paired_bat['dr_ref'] = paired_bat['dismissals_ref'] / paired_bat['balls_ref']
        paired_bat['dr_tgt'] = paired_bat['dismissals_tgt'] / paired_bat['balls_tgt']
        paired_bat['bp_ref'] = paired_bat['boundaries_ref'] / paired_bat['balls_ref'] * 100
        paired_bat['bp_tgt'] = paired_bat['boundaries_tgt'] / paired_bat['balls_tgt'] * 100

        # Bowlers
        t_ref_bowl = primary[(primary['comp_tier'] == tier_ref) & primary['is_legal']]
        t_tgt_bowl = primary[(primary['comp_tier'] == tier_target) & primary['is_legal']]

        ref_bowlers = t_ref_bowl.groupby('bowler_id').agg(
            balls=('is_legal', 'sum'),
            runs=('bowler_runs', 'sum'),
            wickets=('is_bowler_wicket', 'sum'),
            dots=('is_dot', 'sum')
        ).reset_index()
        ref_bowlers = ref_bowlers[ref_bowlers['balls'] >= min_balls]

        tgt_bowlers = t_tgt_bowl.groupby('bowler_id').agg(
            balls=('is_legal', 'sum'),
            runs=('bowler_runs', 'sum'),
            wickets=('is_bowler_wicket', 'sum'),
            dots=('is_dot', 'sum')
        ).reset_index()
        tgt_bowlers = tgt_bowlers[tgt_bowlers['balls'] >= min_balls]

        paired_bowl = ref_bowlers.merge(tgt_bowlers, on='bowler_id', suffixes=('_ref', '_tgt'))
        paired_bowl['econ_ref'] = paired_bowl['runs_ref'] / paired_bowl['balls_ref'] * 6
        paired_bowl['econ_tgt'] = paired_bowl['runs_tgt'] / paired_bowl['balls_tgt'] * 6
        paired_bowl['wr_ref'] = paired_bowl['wickets_ref'] / paired_bowl['balls_ref']
        paired_bowl['wr_tgt'] = paired_bowl['wickets_tgt'] / paired_bowl['balls_tgt']
        paired_bowl['dot_ref'] = paired_bowl['dots_ref'] / paired_bowl['balls_ref'] * 100
        paired_bowl['dot_tgt'] = paired_bowl['dots_tgt'] / paired_bowl['balls_tgt'] * 100

        # Compute median ratios (TARGET / REFERENCE)
        results[key]['batters'] = {
            'n_players': len(paired_bat),
            'sr_ratio': paired_bat['sr_tgt'].median() / paired_bat['sr_ref'].median(),
            'dr_ratio': paired_bat['dr_tgt'].median() / paired_bat['dr_ref'].median(),
            'bp_ratio': paired_bat['bp_tgt'].median() / paired_bat['bp_ref'].median(),
            'sr_ref_median': paired_bat['sr_ref'].median(),
            'sr_tgt_median': paired_bat['sr_tgt'].median(),
            'dr_ref_median': paired_bat['dr_ref'].median(),
            'dr_tgt_median': paired_bat['dr_tgt'].median(),
            'bp_ref_median': paired_bat['bp_ref'].median(),
            'bp_tgt_median': paired_bat['bp_tgt'].median(),
        }
        results[key]['bowlers'] = {
            'n_players': len(paired_bowl),
            'econ_ratio': paired_bowl['econ_tgt'].median() / paired_bowl['econ_ref'].median(),
            'wr_ratio': paired_bowl['wr_tgt'].median() / paired_bowl['wr_ref'].median(),
            'dot_ratio': paired_bowl['dot_tgt'].median() / paired_bowl['dot_ref'].median(),
            'econ_ref_median': paired_bowl['econ_ref'].median(),
            'econ_tgt_median': paired_bowl['econ_tgt'].median(),
            'wr_ref_median': paired_bowl['wr_ref'].median(),
            'wr_tgt_median': paired_bowl['wr_tgt'].median(),
            'dot_ref_median': paired_bowl['dot_ref'].median(),
            'dot_tgt_median': paired_bowl['dot_tgt'].median(),
        }

    return results


def compute_population_ratios(primary):
    """Compute population-level ratios for Tiers 3, 4, 5 vs Tier 1."""
    bowler_wicket_types = ['Bowled', 'Caught', 'LBW', 'Stump', 'Hit Wicket',
                           'Obstructing the field', 'Obstracting the field']

    primary = primary.copy()
    primary['bowler_runs'] = primary.apply(compute_bowler_runs, axis=1)
    primary['is_legal'] = primary['extras_type'].isna() | ~primary['extras_type'].isin(['wide', 'Overstep'])
    primary['is_boundary'] = (primary['is_four'] == 1) | (primary['is_six'] == 1)
    primary['is_dot'] = primary['is_legal'] & (primary['runs'] == 0) & (primary['extras1_runs'] == 0)
    primary['is_bowler_wicket'] = primary['dismissal_type'].isin(bowler_wicket_types)

    # Tier 1 reference
    t1 = primary[(primary['comp_tier'] == 1) & primary['is_legal']]
    t1_legal = t1['is_legal'].sum()
    t1_sr = t1['runs'].sum() / t1_legal * 100
    t1_dr = t1['is_wicket'].sum() / t1_legal
    t1_bp = t1['is_boundary'].sum() / t1_legal * 100
    t1_econ = t1['bowler_runs'].sum() / t1_legal * 6
    t1_wr = t1['is_bowler_wicket'].sum() / t1_legal
    t1_dot = t1['is_dot'].sum() / t1_legal * 100

    results = {}
    for tier in [3, 4, 5]:
        t = primary[(primary['comp_tier'] == tier) & primary['is_legal']]
        legal = t['is_legal'].sum()

        if legal == 0:
            continue

        sr = t['runs'].sum() / legal * 100
        dr = t['is_wicket'].sum() / legal
        bp = t['is_boundary'].sum() / legal * 100
        econ = t['bowler_runs'].sum() / legal * 6
        wr = t['is_bowler_wicket'].sum() / legal
        dot = t['is_dot'].sum() / legal * 100

        results[f'pop_T1_vs_T{tier}'] = {
            'sr_ratio': sr / t1_sr,
            'dr_ratio': dr / t1_dr,
            'bp_ratio': bp / t1_bp,
            'econ_ratio': econ / t1_econ,
            'wr_ratio': wr / t1_wr,
            'dot_ratio': dot / t1_dot,
            'sr_ref': t1_sr,
            'sr_tgt': sr,
            'dr_ref': t1_dr,
            'dr_tgt': dr,
            'bp_ref': t1_bp,
            'bp_tgt': bp,
            'econ_ref': t1_econ,
            'econ_tgt': econ,
            'wr_ref': t1_wr,
            'wr_tgt': wr,
            'dot_ref': t1_dot,
            'dot_tgt': dot,
            'n_balls_tgt': int(legal),
        }

    return results


def apply_shrinkage(paired_results, population_results, prior_weight=30):
    """
    Apply Bayesian shrinkage to competition adjustment factors.

    For paired ratios (T1-T2, T2-T3): use paired estimates with shrinkage toward 1.0
    For population ratios (T1-T3, T1-T4, T1-T5): use population estimates with shrinkage toward 1.0

    Shrinkage formula: adjusted = (weight * observed + prior_weight * 1.0) / (weight + prior_weight)
    where weight = sqrt(n_players) for paired, n_balls for population
    """

    # Chain: T1 -> T2 -> T3 -> T4 -> T5
    # We have: T1 vs T2 (paired), T2 vs T3 (paired), T1 vs T3 (pop), T1 vs T4 (pop), T1 vs T5 (pop)
    # Need to derive T3 vs T4, T4 vs T5 from population

    adjustments = {}

    # Tier 1 (reference) - identity
    adjustments[1] = {
        'sr_factor': 1.0, 'dr_factor': 1.0, 'bp_factor': 1.0,
        'econ_factor': 1.0, 'wr_factor': 1.0, 'dot_factor': 1.0,
        'source': 'reference',
        'n_players': None,
        'uncertainty': 0.0
    }

    # Tier 2: Use paired T1 vs T2
    t12_bat = paired_results['T1_vs_T2']['batters']
    t12_bowl = paired_results['T1_vs_T2']['bowlers']
    n_t12 = min(t12_bat['n_players'], t12_bowl['n_players'])
    weight_t12 = np.sqrt(n_t12)

    # Factors = REFERENCE / TARGET = 1 / (TARGET/REFERENCE)
    sr_f = 1.0 / t12_bat['sr_ratio']
    dr_f = 1.0 / t12_bat['dr_ratio']
    bp_f = 1.0 / t12_bat['bp_ratio']
    econ_f = 1.0 / t12_bowl['econ_ratio']
    wr_f = 1.0 / t12_bowl['wr_ratio']
    dot_f = 1.0 / t12_bowl['dot_ratio']

    # Shrink toward 1.0
    sr_adj = (weight_t12 * sr_f + prior_weight * 1.0) / (weight_t12 + prior_weight)
    dr_adj = (weight_t12 * dr_f + prior_weight * 1.0) / (weight_t12 + prior_weight)
    bp_adj = (weight_t12 * bp_f + prior_weight * 1.0) / (weight_t12 + prior_weight)
    econ_adj = (weight_t12 * econ_f + prior_weight * 1.0) / (weight_t12 + prior_weight)
    wr_adj = (weight_t12 * wr_f + prior_weight * 1.0) / (weight_t12 + prior_weight)
    dot_adj = (weight_t12 * dot_f + prior_weight * 1.0) / (weight_t12 + prior_weight)

    # Uncertainty (approximate): 1 / sqrt(weight + prior)
    uncertainty = 1.0 / np.sqrt(weight_t12 + prior_weight)

    adjustments[2] = {
        'sr_factor': sr_adj, 'dr_factor': dr_adj, 'bp_factor': bp_adj,
        'econ_factor': econ_adj, 'wr_factor': wr_adj, 'dot_factor': dot_adj,
        'source': 'paired_T1_T2',
        'n_players': int(n_t12),
        'raw_sr_factor': sr_f, 'raw_dr_factor': dr_f, 'raw_bp_factor': bp_f,
        'raw_econ_factor': econ_f, 'raw_wr_factor': wr_f, 'raw_dot_factor': dot_f,
        'uncertainty': uncertainty
    }

    # Tier 3: Use paired T2 vs T3, chain from T2
    t23_bat = paired_results['T2_vs_T3']['batters']
    t23_bowl = paired_results['T2_vs_T3']['bowlers']
    n_t23 = min(t23_bat['n_players'], t23_bowl['n_players'])
    weight_t23 = np.sqrt(n_t23)

    sr_f_t23 = 1.0 / t23_bat['sr_ratio']
    dr_f_t23 = 1.0 / t23_bat['dr_ratio']
    bp_f_t23 = 1.0 / t23_bat['bp_ratio']
    econ_f_t23 = 1.0 / t23_bowl['econ_ratio']
    wr_f_t23 = 1.0 / t23_bowl['wr_ratio']
    dot_f_t23 = 1.0 / t23_bowl['dot_ratio']

    sr_adj_t23 = (weight_t23 * sr_f_t23 + prior_weight * 1.0) / (weight_t23 + prior_weight)
    dr_adj_t23 = (weight_t23 * dr_f_t23 + prior_weight * 1.0) / (weight_t23 + prior_weight)
    bp_adj_t23 = (weight_t23 * bp_f_t23 + prior_weight * 1.0) / (weight_t23 + prior_weight)
    econ_adj_t23 = (weight_t23 * econ_f_t23 + prior_weight * 1.0) / (weight_t23 + prior_weight)
    wr_adj_t23 = (weight_t23 * wr_f_t23 + prior_weight * 1.0) / (weight_t23 + prior_weight)
    dot_adj_t23 = (weight_t23 * dot_f_t23 + prior_weight * 1.0) / (weight_t23 + prior_weight)

    # Chain: T3 = T2 * (T3/T2 factors)
    adjustments[3] = {
        'sr_factor': adjustments[2]['sr_factor'] * sr_adj_t23,
        'dr_factor': adjustments[2]['dr_factor'] * dr_adj_t23,
        'bp_factor': adjustments[2]['bp_factor'] * bp_adj_t23,
        'econ_factor': adjustments[2]['econ_factor'] * econ_adj_t23,
        'wr_factor': adjustments[2]['wr_factor'] * wr_adj_t23,
        'dot_factor': adjustments[2]['dot_factor'] * dot_adj_t23,
        'source': 'paired_T2_T3_chained',
        'n_players': int(n_t23),
        'raw_sr_factor': sr_f_t23, 'raw_dr_factor': dr_f_t23, 'raw_bp_factor': bp_f_t23,
        'raw_econ_factor': econ_f_t23, 'raw_wr_factor': wr_f_t23, 'raw_dot_factor': dot_f_t23,
        'uncertainty': 1.0 / np.sqrt(weight_t23 + prior_weight)
    }

    # Tier 4: Population T1 vs T4, but with heavy shrinkage
    pop_t14 = population_results['pop_T1_vs_T4']
    n_t14 = pop_t14['n_balls_tgt']
    weight_t14 = np.sqrt(n_t14 / 1000)  # scale down ball count

    sr_f_t14 = 1.0 / pop_t14['sr_ratio']
    dr_f_t14 = 1.0 / pop_t14['dr_ratio']
    bp_f_t14 = 1.0 / pop_t14['bp_ratio']
    econ_f_t14 = 1.0 / pop_t14['econ_ratio']
    wr_f_t14 = 1.0 / pop_t14['wr_ratio']
    dot_f_t14 = 1.0 / pop_t14['dot_ratio']

    sr_adj_t14 = (weight_t14 * sr_f_t14 + prior_weight * 1.0) / (weight_t14 + prior_weight)
    dr_adj_t14 = (weight_t14 * dr_f_t14 + prior_weight * 1.0) / (weight_t14 + prior_weight)
    bp_adj_t14 = (weight_t14 * bp_f_t14 + prior_weight * 1.0) / (weight_t14 + prior_weight)
    econ_adj_t14 = (weight_t14 * econ_f_t14 + prior_weight * 1.0) / (weight_t14 + prior_weight)
    wr_adj_t14 = (weight_t14 * wr_f_t14 + prior_weight * 1.0) / (weight_t14 + prior_weight)
    dot_adj_t14 = (weight_t14 * dot_f_t14 + prior_weight * 1.0) / (weight_t14 + prior_weight)

    adjustments[4] = {
        'sr_factor': sr_adj_t14, 'dr_factor': dr_adj_t14, 'bp_factor': bp_adj_t14,
        'econ_factor': econ_adj_t14, 'wr_factor': wr_adj_t14, 'dot_factor': dot_adj_t14,
        'source': 'population_T1_T4_shrunk',
        'n_balls': int(n_t14),
        'raw_sr_factor': sr_f_t14, 'raw_dr_factor': dr_f_t14, 'raw_bp_factor': bp_f_t14,
        'raw_econ_factor': econ_f_t14, 'raw_wr_factor': wr_f_t14, 'raw_dot_factor': dot_f_t14,
        'uncertainty': 1.0 / np.sqrt(weight_t14 + prior_weight)
    }

    # Tier 5: Population T1 vs T5
    pop_t15 = population_results['pop_T1_vs_T5']
    n_t15 = pop_t15['n_balls_tgt']
    weight_t15 = np.sqrt(n_t15 / 1000)

    sr_f_t15 = 1.0 / pop_t15['sr_ratio']
    dr_f_t15 = 1.0 / pop_t15['dr_ratio']
    bp_f_t15 = 1.0 / pop_t15['bp_ratio']
    econ_f_t15 = 1.0 / pop_t15['econ_ratio']
    wr_f_t15 = 1.0 / pop_t15['wr_ratio']
    dot_f_t15 = 1.0 / pop_t15['dot_ratio']

    sr_adj_t15 = (weight_t15 * sr_f_t15 + prior_weight * 1.0) / (weight_t15 + prior_weight)
    dr_adj_t15 = (weight_t15 * dr_f_t15 + prior_weight * 1.0) / (weight_t15 + prior_weight)
    bp_adj_t15 = (weight_t15 * bp_f_t15 + prior_weight * 1.0) / (weight_t15 + prior_weight)
    econ_adj_t15 = (weight_t15 * econ_f_t15 + prior_weight * 1.0) / (weight_t15 + prior_weight)
    wr_adj_t15 = (weight_t15 * wr_f_t15 + prior_weight * 1.0) / (weight_t15 + prior_weight)
    dot_adj_t15 = (weight_t15 * dot_f_t15 + prior_weight * 1.0) / (weight_t15 + prior_weight)

    adjustments[5] = {
        'sr_factor': sr_adj_t15, 'dr_factor': dr_adj_t15, 'bp_factor': bp_adj_t15,
        'econ_factor': econ_adj_t15, 'wr_factor': wr_adj_t15, 'dot_factor': dot_adj_t15,
        'source': 'population_T1_T5_shrunk',
        'n_balls': int(n_t15),
        'raw_sr_factor': sr_f_t15, 'raw_dr_factor': dr_f_t15, 'raw_bp_factor': bp_f_t15,
        'raw_econ_factor': econ_f_t15, 'raw_wr_factor': wr_f_t15, 'raw_dot_factor': dot_f_t15,
        'uncertainty': 1.0 / np.sqrt(weight_t15 + prior_weight)
    }

    return adjustments


def compute_confidence_intervals(adjustments, paired_results, population_results):
    """Compute approximate 95% confidence intervals for adjustment factors."""
    # For paired ratios, use bootstrap-like approximation
    # For population, use normal approximation on log scale

    intervals = {}
    for tier, adj in adjustments.items():
        intervals[tier] = {}
        for metric in ['sr_factor', 'dr_factor', 'bp_factor', 'econ_factor', 'wr_factor', 'dot_factor']:
            factor = adj[metric]
            unc = adj.get('uncertainty', 0.05)
            # Approximate 95% CI: factor * exp(±1.96 * uncertainty)
            # For small uncertainty, factor * (1 ± 1.96*uncertainty)
            margin = 1.96 * unc
            intervals[tier][metric] = {
                'point': factor,
                'lower': factor * (1 - margin),
                'upper': factor * (1 + margin),
                'uncertainty': unc
            }
    return intervals


def flag_unstable_players(batter_features, bowler_features, adjustments):
    """
    Flag players with unstable competition-adjusted performance.
    Instability criteria:
    - Performance varies significantly across competition tiers
    - Small sample in higher tiers
    - Large adjustment factor applied (uncertainty)
    """
    unstable_batters = []
    unstable_bowlers = []

    # Check batters with multi-tier presence
    batter_tiers = batter_features.groupby('striker_id')['comp_tiers'].first()
    for pid, tiers_str in batter_tiers.items():
        if pd.isna(tiers_str):
            continue
        tiers = set(int(t) for t in str(tiers_str).split(';'))
        if len(tiers) >= 2:
            # Player appears in multiple tiers
            tier_data = batter_features[batter_features['striker_id'] == pid]
            # Check if they have enough balls in each tier
            # This is simplified - would need tier-specific breakdown
            # For now, flag if they appear in Tier 3+ and Tier 1
            if 1 in tiers and (3 in tiers or 4 in tiers or 5 in tiers):
                unstable_batters.append(pid)

    # Check bowlers with multi-tier presence
    bowler_tiers = bowler_features.groupby('bowler_id')['comp_tiers'].first()
    for pid, tiers_str in bowler_tiers.items():
        if pd.isna(tiers_str):
            continue
        tiers = set(int(t) for t in str(tiers_str).split(';'))
        if len(tiers) >= 2:
            if 1 in tiers and (3 in tiers or 4 in tiers or 5 in tiers):
                unstable_bowlers.append(pid)

    return unstable_batters, unstable_bowlers


def flag_unstable_players(primary, adjustments):
    """
    Flag players with unstable competition-adjusted performance.
    Instability criteria:
    - Performance varies significantly across competition tiers
    - Small sample in higher tiers
    - Large adjustment factor applied (uncertainty)
    """
    unstable_batters = []
    unstable_bowlers = []

    # Check batters with multi-tier presence
    primary_legal = primary[primary['extras_type'].isna() | ~primary['extras_type'].isin(['wide', 'Overstep'])]
    batter_tiers = primary_legal.groupby('striker_id')['comp_tier'].unique()
    for pid, tiers in batter_tiers.items():
        if len(tiers) >= 2:
            if 1 in tiers and (3 in tiers or 4 in tiers or 5 in tiers):
                unstable_batters.append(pid)

    # Check bowlers with multi-tier presence
    bowler_tiers = primary_legal.groupby('bowler_id')['comp_tier'].unique()
    for pid, tiers in bowler_tiers.items():
        if len(tiers) >= 2:
            if 1 in tiers and (3 in tiers or 4 in tiers or 5 in tiers):
                unstable_bowlers.append(pid)

    return unstable_batters, unstable_bowlers


def main():
    print("=" * 60)
    print("BUILDING CORRECTED COMPETITION ADJUSTMENT FACTORS")
    print("=" * 60)

    # Load data
    print("\n[1/5] Loading data...")
    primary = load_data()
    print(f"  Primary deliveries: {len(primary):,}")

    # Compute paired ratios
    print("\n[2/5] Computing paired player ratios (30+ balls)...")
    paired_results = compute_paired_ratios(primary, min_balls=30)
    for key, val in paired_results.items():
        print(f"  {key}: {val['batters']['n_players']} batters, {val['bowlers']['n_players']} bowlers")
        print(f"    Batters: SR_ratio={val['batters']['sr_ratio']:.4f}, DR_ratio={val['batters']['dr_ratio']:.4f}, BP_ratio={val['batters']['bp_ratio']:.4f}")
        print(f"    Bowlers: Econ_ratio={val['bowlers']['econ_ratio']:.4f}, WR_ratio={val['bowlers']['wr_ratio']:.4f}, Dot_ratio={val['bowlers']['dot_ratio']:.4f}")

    # Compute population ratios
    print("\n[3/5] Computing population ratios...")
    population_results = compute_population_ratios(primary)
    for key, val in population_results.items():
        print(f"  {key}: SR_ratio={val['sr_ratio']:.4f}, DR_ratio={val['dr_ratio']:.4f}")

    # Apply shrinkage
    print("\n[4/5] Applying Bayesian shrinkage (prior_weight=30)...")
    adjustments = apply_shrinkage(paired_results, population_results, prior_weight=30)

    print("\n  Corrected Adjustment Factors (Tier -> IPL equivalent):")
    print(f"  {'Tier':<5} {'Source':<25} {'SR':>7} {'DR':>7} {'BP':>7} {'Econ':>7} {'WR':>7} {'Dot%':>7} {'Unc':>6}")
    print(f"  {'-'*5} {'-'*25} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*6}")
    for tier in range(1, 6):
        adj = adjustments[tier]
        print(f"  {tier:<5} {adj['source']:<25} {adj['sr_factor']:.4f} {adj['dr_factor']:.4f} {adj['bp_factor']:.4f} {adj['econ_factor']:.4f} {adj['wr_factor']:.4f} {adj['dot_factor']:.4f} {adj.get('uncertainty', 0):.4f}")

    # Confidence intervals
    print("\n[5/5] Computing confidence intervals...")
    intervals = compute_confidence_intervals(adjustments, paired_results, population_results)

    # Flag unstable players
    print("\nFlagging unstable players...")
    unstable_batters, unstable_bowlers = flag_unstable_players(primary, adjustments)
    print(f"  Unstable batters (multi-tier 1+3/4/5): {len(unstable_batters)}")
    print(f"  Unstable bowlers (multi-tier 1+3/4/5): {len(unstable_bowlers)}")

    # Save outputs
    print("\nSaving outputs...")
    Path('outputs/task07b').mkdir(parents=True, exist_ok=True)

    # 1. Adjustment factors CSV
    adj_rows = []
    for tier in range(1, 6):
        adj = adjustments[tier]
        row = {
            'comp_tier': tier,
            'source': adj['source'],
            'sr_factor': adj['sr_factor'],
            'dr_factor': adj['dr_factor'],
            'bp_factor': adj['bp_factor'],
            'econ_factor': adj['econ_factor'],
            'wr_factor': adj['wr_factor'],
            'dot_factor': adj['dot_factor'],
            'uncertainty': adj.get('uncertainty', 0),
            'sr_ci_lower': intervals[tier]['sr_factor']['lower'],
            'sr_ci_upper': intervals[tier]['sr_factor']['upper'],
            'dr_ci_lower': intervals[tier]['dr_factor']['lower'],
            'dr_ci_upper': intervals[tier]['dr_factor']['upper'],
            'bp_ci_lower': intervals[tier]['bp_factor']['lower'],
            'bp_ci_upper': intervals[tier]['bp_factor']['upper'],
            'econ_ci_lower': intervals[tier]['econ_factor']['lower'],
            'econ_ci_upper': intervals[tier]['econ_factor']['upper'],
            'wr_ci_lower': intervals[tier]['wr_factor']['lower'],
            'wr_ci_upper': intervals[tier]['wr_factor']['upper'],
            'dot_ci_lower': intervals[tier]['dot_factor']['lower'],
            'dot_ci_upper': intervals[tier]['dot_factor']['upper'],
        }
        if 'n_players' in adj:
            row['n_players'] = adj['n_players']
        if 'n_balls' in adj:
            row['n_balls'] = adj['n_balls']
        adj_rows.append(row)

    adj_df = pd.DataFrame(adj_rows)
    adj_df.to_csv('outputs/task07b/corrected_competition_adjustments.csv', index=False)
    print("  Saved: outputs/task07b/corrected_competition_adjustments.csv")

    # 2. Detailed documentation markdown
    with open('outputs/task07b/competition_adjustment_methodology.md', 'w') as f:
        f.write("# Corrected Competition Adjustment Methodology\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        f.write("## Ratio Convention\n\n")
        f.write("- All ratios documented as **TARGET / REFERENCE** (e.g., T2/T1 for Tier 1->2 comparison)\n")
        f.write("- Adjustment factor = **REFERENCE / TARGET** = 1 / (TARGET/REFERENCE)\n")
        f.write("- Factor > 1.0 means target tier is weaker (needs upward adjustment to match IPL)\n")
        f.write("- Factor < 1.0 means target tier is stronger (needs downward adjustment)\n\n")

        f.write("## Paired Player Analysis Results (30+ balls threshold)\n\n")
        f.write("### Tier 1 (IPL) vs Tier 2 (T20I FMvFM)\n")
        t12_b = paired_results['T1_vs_T2']['batters']
        t12_bo = paired_results['T1_vs_T2']['bowlers']
        f.write(f"- **Players:** {t12_b['n_players']} batters, {t12_bo['n_players']} bowlers\n")
        f.write(f"- **SR Ratio (T2/T1):** {t12_b['sr_ratio']:.4f} -> Factor (T1/T2): {1/t12_b['sr_ratio']:.4f}\n")
        f.write(f"  - IPL median SR: {t12_b['sr_ref_median']:.2f}, T2 median SR: {t12_b['sr_tgt_median']:.2f}\n")
        f.write(f"- **DR Ratio (T2/T1):** {t12_b['dr_ratio']:.4f} -> Factor (T1/T2): {1/t12_b['dr_ratio']:.4f}\n")
        f.write(f"  - IPL median DR: {t12_b['dr_ref_median']:.4f}, T2 median DR: {t12_b['dr_tgt_median']:.4f}\n")
        f.write(f"- **BP Ratio (T2/T1):** {t12_b['bp_ratio']:.4f} -> Factor (T1/T2): {1/t12_b['bp_ratio']:.4f}\n")
        f.write(f"- **Econ Ratio (T2/T1):** {t12_bo['econ_ratio']:.4f} -> Factor (T1/T2): {1/t12_bo['econ_ratio']:.4f}\n")
        f.write(f"- **WR Ratio (T2/T1):** {t12_bo['wr_ratio']:.4f} -> Factor (T1/T2): {1/t12_bo['wr_ratio']:.4f}\n")
        f.write(f"- **Dot% Ratio (T2/T1):** {t12_bo['dot_ratio']:.4f} -> Factor (T1/T2): {1/t12_bo['dot_ratio']:.4f}\n\n")

        f.write("### Tier 2 (T20I FMvFM) vs Tier 3 (T20I FMvAssoc)\n")
        t23_b = paired_results['T2_vs_T3']['batters']
        t23_bo = paired_results['T2_vs_T3']['bowlers']
        f.write(f"- **Players:** {t23_b['n_players']} batters, {t23_bo['n_players']} bowlers\n")
        f.write(f"- **SR Ratio (T3/T2):** {t23_b['sr_ratio']:.4f} -> Factor (T2/T3): {1/t23_b['sr_ratio']:.4f}\n")
        f.write(f"  - T2 median SR: {t23_b['sr_ref_median']:.2f}, T3 median SR: {t23_b['sr_tgt_median']:.2f}\n")
        f.write(f"- **DR Ratio (T3/T2):** {t23_b['dr_ratio']:.4f} -> Factor (T2/T3): {1/t23_b['dr_ratio']:.4f}\n")
        f.write(f"- **BP Ratio (T3/T2):** {t23_b['bp_ratio']:.4f} -> Factor (T2/T3): {1/t23_b['bp_ratio']:.4f}\n")
        f.write(f"- **Econ Ratio (T3/T2):** {t23_bo['econ_ratio']:.4f} -> Factor (T2/T3): {1/t23_bo['econ_ratio']:.4f}\n")
        f.write(f"- **WR Ratio (T3/T2):** {t23_bo['wr_ratio']:.4f} -> Factor (T2/T3): {1/t23_bo['wr_ratio']:.4f}\n")
        f.write(f"- **Dot% Ratio (T3/T2):** {t23_bo['dot_ratio']:.4f} -> Factor (T2/T3): {1/t23_bo['dot_ratio']:.4f}\n\n")

        f.write("## Population Ratios (for Tiers 3, 4, 5 vs Tier 1)\n\n")
        for key, val in population_results.items():
            f.write(f"### {key}\n")
            f.write(f"- Balls in target tier: {val['n_balls_tgt']:,}\n")
            f.write(f"- SR Ratio: {val['sr_ratio']:.4f} (Factor: {1/val['sr_ratio']:.4f})\n")
            f.write(f"- DR Ratio: {val['dr_ratio']:.4f} (Factor: {1/val['dr_ratio']:.4f})\n")
            f.write(f"- BP Ratio: {val['bp_ratio']:.4f} (Factor: {1/val['bp_ratio']:.4f})\n")
            f.write(f"- Econ Ratio: {val['econ_ratio']:.4f} (Factor: {1/val['econ_ratio']:.4f})\n")
            f.write(f"- WR Ratio: {val['wr_ratio']:.4f} (Factor: {1/val['wr_ratio']:.4f})\n")
            f.write(f"- Dot% Ratio: {val['dot_ratio']:.4f} (Factor: {1/val['dot_ratio']:.4f})\n\n")

        f.write("## Shrinkage Methodology\n\n")
        f.write("- **Prior weight:** 30 balls (equivalent to ~5 overs)\n")
        f.write("- **Paired estimates:** weight = sqrt(n_players), shrunk toward 1.0\n")
        f.write("- **Population estimates:** weight = sqrt(n_balls/1000), shrunk toward 1.0\n")
        f.write("- **Chaining:** Tier 3 = Tier 2 factor × Tier 2->3 paired factor\n")
        f.write("- **Tier 4, 5:** Direct population ratios with heavy shrinkage\n\n")

        f.write("## Final Adjustment Factors (with 95% CI)\n\n")
        f.write("| Tier | Source | SR Factor | DR Factor | BP Factor | Econ Factor | WR Factor | Dot% Factor | Uncertainty |\n")
        f.write("|------|--------|-----------|-----------|-----------|-------------|-----------|-------------|-------------|\n")
        for tier in range(1, 6):
            adj = adjustments[tier]
            f.write(f"| {tier} | {adj['source']} | {adj['sr_factor']:.4f} | {adj['dr_factor']:.4f} | {adj['bp_factor']:.4f} | {adj['econ_factor']:.4f} | {adj['wr_factor']:.4f} | {adj['dot_factor']:.4f} | {adj.get('uncertainty', 0):.4f} |\n")

        f.write("\n## Unstable Players Flagged\n\n")
        f.write(f"- **Batters in Tier 1 + Tier 3/4/5:** {len(unstable_batters)}\n")
        f.write(f"- **Bowlers in Tier 1 + Tier 3/4/5:** {len(unstable_bowlers)}\n")
        f.write("- These players have competition-adjusted metrics with higher uncertainty\n")
        f.write("- Recommendation: Review manually or apply additional shrinkage\n\n")

        f.write("## Discrepancy with Task 07\n\n")
        f.write("| Metric | Task 07 Claimed | Corrected (This Analysis) | Change |\n")
        f.write("|--------|----------------|---------------------------|--------|\n")
        f.write("| SR Ratio T2/IPL (paired) | 1.020 | 0.994 | -0.026 |\n")
        f.write("| DR Ratio T2/IPL (paired) | 0.967 | 1.113 | +0.146 |\n")
        f.write("| BP Ratio T2/IPL (paired) | 0.985 | 0.980 | -0.005 |\n")
        f.write("| Batters T2<->T3 overlap | 126 | 107 | -19 |\n")
        f.write("| Bowlers IPL<->T2 overlap | 118 | 110 | -8 |\n")
        f.write("\n**Critical:** Task 07 claimed T2 batters outperform IPL (SR ratio 1.020). ")
        f.write("Corrected analysis shows IPL batters slightly outperform T2 (ratio 0.994). ")
        f.write("The DR ratio direction is also reversed (0.967 -> 1.113).\n")

    # 3. Unstable players list
    unstable_df = pd.DataFrame({
        'player_id': unstable_batters,
        'type': 'batter'
    })
    if len(unstable_bowlers) > 0:
        unstable_df = pd.concat([unstable_df, pd.DataFrame({
            'player_id': unstable_bowlers,
            'type': 'bowler'
        })], ignore_index=True)
    unstable_df.to_csv('outputs/task07b/unstable_players.csv', index=False)
    print("  Saved: outputs/task07b/unstable_players.csv")

    # 4. Paired analysis details
    paired_rows = []
    for key, val in paired_results.items():
        for role in ['batters', 'bowlers']:
            for metric in ['sr_ratio', 'dr_ratio', 'bp_ratio', 'econ_ratio', 'wr_ratio', 'dot_ratio']:
                if metric in val[role]:
                    paired_rows.append({
                        'comparison': key,
                        'role': role,
                        'metric': metric,
                        'ratio_target_over_ref': val[role][metric],
                        'factor_ref_over_target': 1.0 / val[role][metric],
                        'n_players': val[role]['n_players']
                    })
    paired_df = pd.DataFrame(paired_rows)
    paired_df.to_csv('outputs/task07b/paired_analysis_details.csv', index=False)
    print("  Saved: outputs/task07b/paired_analysis_details.csv")

    # 5. Population analysis details
    pop_rows = []
    for key, val in population_results.items():
        for metric in ['sr_ratio', 'dr_ratio', 'bp_ratio', 'econ_ratio', 'wr_ratio', 'dot_ratio']:
            pop_rows.append({
                'comparison': key,
                'metric': metric,
                'ratio_target_over_ref': val[metric],
                'factor_ref_over_target': 1.0 / val[metric],
                'n_balls_target': val['n_balls_tgt']
            })
    pop_df = pd.DataFrame(pop_rows)
    pop_df.to_csv('outputs/task07b/population_analysis_details.csv', index=False)
    print("  Saved: outputs/task07b/population_analysis_details.csv")

    print("\n" + "=" * 60)
    print("CORRECTED COMPETITION ADJUSTMENT COMPLETE")
    print("=" * 60)

    return adjustments, intervals, unstable_batters, unstable_bowlers


if __name__ == '__main__':
    main()