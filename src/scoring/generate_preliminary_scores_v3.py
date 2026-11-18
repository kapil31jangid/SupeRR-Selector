#!/usr/bin/env python3
"""
Generate Preliminary Evaluation Tables v3 — Task 07D
CORRECTED SCENARIO IMPLEMENTATIONS

Scenario Definitions (matching documentation):
- Conservative: ALL competitions, NO competition adjustment, shrinkage applied (_adj columns)
- Evidence-Based: ALL competitions, PAIRED competition adjustment (_comp_adj for overall, _adj for components)
- Aggressive: ALL competitions, POPULATION competition adjustment (_pop_adj for overall, _adj for components)
- IPL-Only: IPL 2022-2026 only, NO competition adjustment, shrinkage applied

Evidence-Based implementation is PRESERVED from validated v2.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def compute_batter_composite_score(df, scenario='evidence'):
    """
    Compute composite batter score.

    Components (weighted):
    - Overall SR (30%)
    - High/Extreme SR (25%) - pressure performance
    - Chase SR (20%) - chasing ability
    - Powerplay SR (10%) - intent
    - Death SR (10%) - finishing
    - Boundary % (5%) - boundary hitting
    """
    # Select scenario columns
    if scenario == 'conservative':
        # Shrinkage-adjusted raw rates (no competition adjustment)
        sr_col = 'strike_rate_adj'
        he_sr_col = 'high_extreme_sr_adj'
        chase_sr_col = 'chase_strike_rate_adj'
        pp_sr_col = 'powerplay_sr_adj'
        death_sr_col = 'death_sr_adj'
        bp_col = 'boundary_pct_adj'
    elif scenario == 'evidence':
        # Paired competition adjustment for overall rates, shrinkage for components
        sr_col = 'strike_rate_comp_adj'
        he_sr_col = 'high_extreme_sr_adj'  # Component: shrinkage only
        chase_sr_col = 'chase_strike_rate_adj'  # Component: shrinkage only
        pp_sr_col = 'powerplay_sr_adj'  # Component: shrinkage only
        death_sr_col = 'death_sr_adj'  # Component: shrinkage only
        bp_col = 'boundary_pct_comp_adj'
    elif scenario == 'aggressive':
        # Population competition adjustment for overall rates, shrinkage for components
        sr_col = 'strike_rate_pop_adj_shrunk'
        he_sr_col = 'high_extreme_sr_adj'  # Component: shrinkage only
        chase_sr_col = 'chase_strike_rate_adj'  # Component: shrinkage only
        pp_sr_col = 'powerplay_sr_adj'  # Component: shrinkage only
        death_sr_col = 'death_sr_adj'  # Component: shrinkage only
        bp_col = 'boundary_pct_pop_adj_shrunk'
    elif scenario == 'ipl_only':
        # IPL only, shrinkage-adjusted (same column names as conservative but IPL-only data)
        sr_col = 'strike_rate_adj'
        he_sr_col = 'high_extreme_sr_adj'
        chase_sr_col = 'chase_strike_rate_adj'
        pp_sr_col = 'powerplay_sr_adj'
        death_sr_col = 'death_sr_adj'
        bp_col = 'boundary_pct_adj'
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    # Normalize each component to 0-100 scale (relative to population)
    def normalize(series, higher_better=True):
        p5 = series.quantile(0.05)
        p95 = series.quantile(0.95)
        if p95 == p5:
            return pd.Series(50, index=series.index)
        if higher_better:
            return np.clip((series - p5) / (p95 - p5) * 100, 0, 100)
        else:
            return np.clip((p95 - series) / (p95 - p5) * 100, 0, 100)

    # Only compute for rows with minimum balls
    mask = df['min_balls_100'] | df['min_balls_50']

    scores = pd.DataFrame(index=df.index)
    scores['sr_score'] = normalize(df[sr_col])
    scores['he_sr_score'] = normalize(df[he_sr_col]) if he_sr_col in df.columns else 50
    scores['chase_sr_score'] = normalize(df[chase_sr_col]) if chase_sr_col in df.columns else 50
    scores['pp_sr_score'] = normalize(df[pp_sr_col]) if pp_sr_col in df.columns else 50
    scores['death_sr_score'] = normalize(df[death_sr_col]) if death_sr_col in df.columns else 50
    scores['bp_score'] = normalize(df[bp_col]) if bp_col in df.columns else 50

    # Weighted composite
    composite = (
        0.30 * scores['sr_score'] +
        0.25 * scores['he_sr_score'] +
        0.20 * scores['chase_sr_score'] +
        0.10 * scores['pp_sr_score'] +
        0.10 * scores['death_sr_score'] +
        0.05 * scores['bp_score']
    )

    return composite, scores


def compute_bowler_composite_score(df, scenario='evidence'):
    """
    Compute composite bowler score.

    Components (weighted, lower is better for economy):
    - Overall Economy (30%)
    - High/Extreme Economy (25%) - pressure performance
    - Death Economy (20%) - death bowling
    - Powerplay Economy (10%) - new ball
    - Wicket Rate (10%) - wicket taking
    - Dot Ball % (5%) - control
    """
    if scenario == 'conservative':
        # Shrinkage-adjusted raw rates (no competition adjustment)
        econ_col = 'economy_rate_adj'
        he_econ_col = 'high_extreme_economy_adj'
        death_econ_col = 'death_economy_adj'
        pp_econ_col = 'powerplay_economy_adj'
        wr_col = 'wicket_rate_adj'
        dot_col = 'dot_ball_pct_adj'
    elif scenario == 'evidence':
        # Paired competition adjustment for overall rates, shrinkage for components
        econ_col = 'economy_rate_comp_adj'
        he_econ_col = 'high_extreme_economy_adj'  # Component: shrinkage only
        death_econ_col = 'death_economy_adj'  # Component: shrinkage only
        pp_econ_col = 'powerplay_economy_adj'  # Component: shrinkage only
        wr_col = 'wicket_rate_comp_adj'
        dot_col = 'dot_ball_pct_comp_adj'
    elif scenario == 'aggressive':
        # Population competition adjustment for overall rates, shrinkage for components
        econ_col = 'economy_rate_pop_adj_shrunk'
        he_econ_col = 'high_extreme_economy_adj'  # Component: shrinkage only
        death_econ_col = 'death_economy_adj'  # Component: shrinkage only
        pp_econ_col = 'powerplay_economy_adj'  # Component: shrinkage only
        wr_col = 'wicket_rate_pop_adj_shrunk'
        dot_col = 'dot_ball_pct_pop_adj_shrunk'
    elif scenario == 'ipl_only':
        # IPL only, shrinkage-adjusted (same column names as conservative but IPL-only data)
        econ_col = 'economy_rate_adj'
        he_econ_col = 'high_extreme_economy_adj'
        death_econ_col = 'death_economy_adj'
        pp_econ_col = 'powerplay_economy_adj'
        wr_col = 'wicket_rate_adj'
        dot_col = 'dot_ball_pct_adj'
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    def normalize(series, higher_better=True):
        p5 = series.quantile(0.05)
        p95 = series.quantile(0.95)
        if p95 == p5:
            return pd.Series(50, index=series.index)
        if higher_better:
            return np.clip((series - p5) / (p95 - p5) * 100, 0, 100)
        else:
            return np.clip((p95 - series) / (p95 - p5) * 100, 0, 100)

    mask = df['min_balls_100'] | df['min_balls_50']

    scores = pd.DataFrame(index=df.index)
    scores['econ_score'] = normalize(df[econ_col], higher_better=False)
    scores['he_econ_score'] = normalize(df[he_econ_col], higher_better=False) if he_econ_col in df.columns else 50
    scores['death_econ_score'] = normalize(df[death_econ_col], higher_better=False) if death_econ_col in df.columns else 50
    scores['pp_econ_score'] = normalize(df[pp_econ_col], higher_better=False) if pp_econ_col in df.columns else 50
    scores['wr_score'] = normalize(df[wr_col], higher_better=True) if wr_col in df.columns else 50
    scores['dot_score'] = normalize(df[dot_col], higher_better=True) if dot_col in df.columns else 50

    composite = (
        0.30 * scores['econ_score'] +
        0.25 * scores['he_econ_score'] +
        0.20 * scores['death_econ_score'] +
        0.10 * scores['pp_econ_score'] +
        0.10 * scores['wr_score'] +
        0.05 * scores['dot_score']
    )

    return composite, scores


def main():
    print("=" * 70)
    print("GENERATE PRELIMINARY EVALUATION TABLES v3 — Task 07D (CORRECTED)")
    print("=" * 70)

    # Load v3 season features (with population-adjusted columns)
    batter_season = pd.read_csv('data/processed_v3/all_competition_batter_season_features.csv', low_memory=False)
    bowler_season = pd.read_csv('data/processed_v3/all_competition_bowler_season_features.csv', low_memory=False)

    # Load IPL-only season features
    batter_season_ipl = pd.read_csv('data/processed_v3/ipl_only_batter_season_features.csv', low_memory=False)
    bowler_season_ipl = pd.read_csv('data/processed_v3/ipl_only_bowler_season_features.csv', low_memory=False)

    print(f"Loaded all-competition batter seasons: {len(batter_season)}")
    print(f"Loaded all-competition bowler seasons: {len(bowler_season)}")
    print(f"Loaded IPL-only batter seasons: {len(batter_season_ipl)}")
    print(f"Loaded IPL-only bowler seasons: {len(bowler_season_ipl)}")

    # Ensure output directory
    out_dir = Path("outputs/rankings_v3")
    out_dir.mkdir(parents=True, exist_ok=True)

    # === BATTER SCORES ===
    print("\n--- Computing Batter Scores ---")

    batter_results = []

    for scenario in ['conservative', 'evidence', 'aggressive', 'ipl_only']:
        print(f"  Scenario: {scenario}")

        # Use IPL-only data for IPL-only scenario
        if scenario == 'ipl_only':
            df = batter_season_ipl.copy()
        else:
            df = batter_season

        composite, components = compute_batter_composite_score(df, scenario)

        # Create result dataframe - select columns that exist in the dataframe
        base_cols = ['striker_id', 'striker_name', 'season', 'comp_types', 'comp_tiers',
                     'total_runs', 'total_balls', 'matches', 'innings',
                     'strike_rate', 'dismissal_rate', 'boundary_pct',
                     'high_extreme_sr', 'high_extreme_dismissal_rate',
                     'chase_strike_rate', 'powerplay_sr', 'death_sr',
                     'strike_rate_adj', 'high_extreme_sr_adj', 'chase_strike_rate_adj',
                     'powerplay_sr_adj', 'death_sr_adj', 'boundary_pct_adj',
                     'min_balls_100', 'min_balls_50', 'min_high_extreme_30', 'min_chase_30',
                     'seasons_played']

        # Add comp_adj columns if they exist (for evidence)
        comp_cols = ['strike_rate_comp_adj', 'dismissal_rate_comp_adj', 'boundary_pct_comp_adj']
        for pc in comp_cols:
            if pc in df.columns:
                base_cols.append(pc)

        # Add pop_adj columns if they exist (for aggressive)
        pop_cols = ['strike_rate_pop_adj_shrunk', 'boundary_pct_pop_adj_shrunk']
        for pc in pop_cols:
            if pc in df.columns:
                base_cols.append(pc)

        res = df[base_cols].copy()

        res['scenario'] = scenario
        res['composite_score'] = composite
        res['sr_score'] = components['sr_score']
        res['he_sr_score'] = components['he_sr_score']
        res['chase_sr_score'] = components['chase_sr_score']
        res['pp_sr_score'] = components['pp_sr_score']
        res['death_sr_score'] = components['death_sr_score']
        res['bp_score'] = components['bp_score']

        batter_results.append(res)

    batter_scores = pd.concat(batter_results, ignore_index=True)

    # Add rank within each scenario for eligible players (min 100 balls)
    for scenario in ['conservative', 'evidence', 'aggressive', 'ipl_only']:
        mask = (batter_scores['scenario'] == scenario) & batter_scores['min_balls_100']
        batter_scores.loc[mask, f'rank_{scenario}'] = batter_scores.loc[mask, 'composite_score'].rank(ascending=False, method='min').astype(int)

    # Save batter scores
    batter_path = out_dir / "preliminary_all_competition_batter_scores_v3.csv"
    batter_scores.to_csv(batter_path, index=False)
    print(f"  Saved: {batter_path} ({len(batter_scores)} rows)")

    # === BOWLER SCORES ===
    print("\n--- Computing Bowler Scores ---")

    bowler_results = []

    for scenario in ['conservative', 'evidence', 'aggressive', 'ipl_only']:
        print(f"  Scenario: {scenario}")

        if scenario == 'ipl_only':
            df = bowler_season_ipl.copy()
        else:
            df = bowler_season

        composite, components = compute_bowler_composite_score(df, scenario)

        base_cols = ['bowler_id', 'bowler_name', 'season', 'comp_types', 'comp_tiers',
                     'total_balls', 'total_runs', 'total_wickets', 'matches',
                     'economy_rate', 'wicket_rate', 'dot_ball_pct', 'boundary_concession_pct',
                     'high_extreme_economy', 'high_extreme_wicket_rate',
                     'death_economy', 'powerplay_economy',
                     'economy_rate_adj', 'high_extreme_economy_adj',
                     'death_economy_adj', 'powerplay_economy_adj',
                     'wicket_rate_adj', 'dot_ball_pct_adj',
                     'min_balls_100', 'min_balls_50', 'min_high_extreme_30', 'min_defend_30',
                     'seasons_played']

        # Add comp_adj columns if they exist (for evidence)
        comp_cols = ['economy_rate_comp_adj', 'wicket_rate_comp_adj', 'dot_ball_pct_comp_adj']
        for pc in comp_cols:
            if pc in df.columns:
                base_cols.append(pc)

        # Add pop_adj columns if they exist (for aggressive)
        pop_cols = ['economy_rate_pop_adj_shrunk', 'wicket_rate_pop_adj_shrunk', 'dot_ball_pct_pop_adj_shrunk']
        for pc in pop_cols:
            if pc in df.columns:
                base_cols.append(pc)

        res = df[base_cols].copy()

        res['scenario'] = scenario
        res['composite_score'] = composite
        res['econ_score'] = components['econ_score']
        res['he_econ_score'] = components['he_econ_score']
        res['death_econ_score'] = components['death_econ_score']
        res['pp_econ_score'] = components['pp_econ_score']
        res['wr_score'] = components['wr_score']
        res['dot_score'] = components['dot_score']

        bowler_results.append(res)

    bowler_scores = pd.concat(bowler_results, ignore_index=True)

    # Add rank within each scenario
    for scenario in ['conservative', 'evidence', 'aggressive', 'ipl_only']:
        mask = (bowler_scores['scenario'] == scenario) & bowler_scores['min_balls_100']
        bowler_scores.loc[mask, f'rank_{scenario}'] = bowler_scores.loc[mask, 'composite_score'].rank(ascending=False, method='min').astype(int)

    # Save bowler scores
    bowler_path = out_dir / "preliminary_all_competition_bowler_scores_v3.csv"
    bowler_scores.to_csv(bowler_path, index=False)
    print(f"  Saved: {bowler_path} ({len(bowler_scores)} rows)")

    # === SUMMARY STATS ===
    print("\n--- Summary (v3 - Corrected Scenario Implementations) ---")
    for scenario in ['conservative', 'evidence', 'aggressive', 'ipl_only']:
        b_mask = (batter_scores['scenario'] == scenario) & batter_scores['min_balls_100']
        bw_mask = (bowler_scores['scenario'] == scenario) & bowler_scores['min_balls_100']
        print(f"  {scenario}: {b_mask.sum()} eligible batters, {bw_mask.sum()} eligible bowlers")

        if b_mask.sum() > 0:
            top10 = batter_scores[b_mask].nsmallest(10, f'rank_{scenario}')
            print(f"    Top 5 batters:")
            for _, row in top10.head(5).iterrows():
                print(f"      Rank {int(row[f'rank_{scenario}'])}: {row['striker_name']} ({row['season']}) - Score: {row['composite_score']:.1f}")

        if bw_mask.sum() > 0:
            top10 = bowler_scores[bw_mask].nsmallest(10, f'rank_{scenario}')
            print(f"    Top 5 bowlers:")
            for _, row in top10.head(5).iterrows():
                print(f"      Rank {int(row[f'rank_{scenario}'])}: {row['bowler_name']} ({row['season']}) - Score: {row['composite_score']:.1f}")

    print("\n" + "=" * 70)
    print("PRELIMINARY EVALUATION TABLES v3 GENERATED")
    print("=" * 70)
    print(f"\nFiles created:")
    print(f"  {batter_path}")
    print(f"  {bowler_path}")
    print("\nScenario Definitions:")
    print("  Conservative: All comps, NO comp adj, shrinkage (_adj)")
    print("  Evidence-Based: All comps, PAIRED comp adj (_comp_adj overall, _adj components)")
    print("  Aggressive: All comps, POPULATION comp adj (_pop_adj overall, _adj components)")
    print("  IPL-Only: IPL 2022-2026 only, NO comp adj, shrinkage (_adj)")
    print("\nEvidence-Based scores preserved from validated v2.")
    print("Aggressive Tier 2 RESOLVED: now uses TRUE population T1-vs-T2 factors (154,631 legal balls).")


if __name__ == "__main__":
    main()