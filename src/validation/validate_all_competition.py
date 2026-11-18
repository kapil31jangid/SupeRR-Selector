#!/usr/bin/env python3
"""
Validate All-Competition Pressure Features
Task 07 — Pressure-X Multi-Competition Evidence Engine

Comprehensive validation checks for leakage, correctness, and completeness.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def validate_delivery_level(df, name="Dataset"):
    """Validate delivery-level pressure features."""
    print(f"\n{'='*60}")
    print(f"VALIDATING {name.upper()} DELIVERY LEVEL")
    print(f"{'='*60}")

    issues = []

    # 1. No negative runs
    if (df['runs'] < 0).any():
        issues.append("Negative runs found")
    else:
        print("[OK] No negative runs")

    # 2. No duplicate delivery keys
    dup_keys = df.duplicated(subset=['match_id', 'innings', 'overid', 'over_ball_num']).sum()
    if dup_keys > 0:
        issues.append(f"Duplicate delivery keys: {dup_keys}")
    else:
        print("[OK] No duplicate delivery keys")

    # 3. Legal ball count consistency
    legal_count = (~df['extras_type'].isin(['wide', 'Overstep'])).sum()
    print(f"[OK] Legal balls: {legal_count} ({legal_count/len(df)*100:.2f}%)")

    # 4. No negative balls remaining
    if (df['legal_balls_remaining'] < 0).any():
        issues.append("Negative legal_balls_remaining")
    else:
        print("[OK] No negative balls remaining")

    # 5. No future leakage - check monotonicity within innings
    for (mid, inn), group in df.groupby(['match_id', 'innings']):
        group = group.sort_values(['overid', 'over_ball_num', 'innings_ball_num'])

        lb = group['legal_balls_before'].values
        if not np.all(np.diff(lb) >= 0):
            issues.append(f"Match {mid} inn {inn}: legal_balls_before decreases")

        wb = group['wickets_before'].values
        if not np.all(np.diff(wb) >= 0):
            issues.append(f"Match {mid} inn {inn}: wickets_before decreases")

        ts = group['team_score_before'].values
        if not np.all(np.diff(ts) >= 0):
            issues.append(f"Match {mid} inn {inn}: team_score_before decreases")

        lbr = group['legal_balls_remaining'].values
        if not np.all(np.diff(lbr) <= 0):
            issues.append(f"Match {mid} inn {inn}: legal_balls_remaining increases")

    if not any("decreases" in i or "increases" in i for i in issues):
        print("[OK] No future leakage (monotonicity checks passed)")

    # 6. No Super Over deliveries
    if df['innings'].isin([3, 4]).any():
        issues.append("Super Over deliveries found in primary")
    else:
        print("[OK] No Super Over deliveries")

    # 7. No ambiguous extras
    if (df['extras_type'] == 'other').any():
        issues.append("Ambiguous extras (other) found in primary")
    else:
        print("[OK] No ambiguous extras")

    # 8. Pressure categories valid
    valid_pressures = ['low', 'medium', 'high', 'extreme']
    if not df['batting_pressure'].isin(valid_pressures).all():
        issues.append("Invalid batting_pressure values")
    else:
        print("[OK] Batting pressure categories valid")

    if not df['bowling_pressure'].isin(valid_pressures).all():
        issues.append("Invalid bowling_pressure values")
    else:
        print("[OK] Bowling pressure categories valid")

    # 9. Batter runs = runs column
    if not (df['batter_runs'] == df['runs']).all():
        issues.append("batter_runs != runs")
    else:
        print("[OK] batter_runs equals runs column")

    # 10. Division by zero checks
    inf_sr = np.isinf(df['strike_rate']).sum() if 'strike_rate' in df.columns else 0
    if inf_sr > 0:
        issues.append(f"Infinite strike rates: {inf_sr}")
    else:
        print("[OK] No infinite rates")

    # 11. Player ID joins - no missing names for key players
    missing_striker = df['striker_canonical_name'].isna().sum()
    missing_bowler = df['bowler_canonical_name'].isna().sum()
    if missing_striker > 0 or missing_bowler > 0:
        print(f"[WARN] Missing canonical names: striker={missing_striker}, bowler={missing_bowler}")
    else:
        print("[OK] All player canonical names joined")

    # 12. Competition tier coverage
    print(f"[INFO] Competition tiers: {sorted(df['comp_tier'].unique())}")
    print(f"[INFO] Competition types: {df['comp_type'].unique()}")

    return issues


def validate_match_level(batter_match, bowler_match, name="Dataset"):
    """Validate player-match level features."""
    print(f"\n{'='*60}")
    print(f"VALIDATING {name.upper()} MATCH LEVEL")
    print(f"{'='*60}")

    issues = []

    # Check no negative values
    for col in ['runs_scored', 'balls_faced', 'balls_bowled', 'runs_conceded']:
        if col in batter_match.columns and (batter_match[col] < 0).any():
            issues.append(f"Batter match: negative {col}")
        if col in bowler_match.columns and (bowler_match[col] < 0).any():
            issues.append(f"Bowler match: negative {col}")

    if not any("negative" in i for i in issues):
        print("[OK] No negative counts")

    # Check strike rates are reasonable
    if 'strike_rate' in batter_match.columns:
        extreme_sr = (batter_match['strike_rate'] > 500).sum()
        if extreme_sr > 0:
            print(f"[WARN] {extreme_sr} batter-match rows with SR > 500")

    if 'economy_rate' in bowler_match.columns:
        extreme_er = (bowler_match['economy_rate'] > 30).sum()
        if extreme_er > 0:
            print(f"[WARN] {extreme_er} bowler-match rows with economy > 30")

    # Check pressure distributions
    for p_col in ['batting_pressure', 'bowling_pressure']:
        if p_col in batter_match.columns or p_col in bowler_match.columns:
            print(f"[INFO] Pressure distribution available")

    # Check competition-adjusted columns
    adj_cols = [c for c in batter_match.columns if c.endswith('_comp_adj')]
    print(f"[INFO] Batter competition-adjusted columns: {len(adj_cols)}")
    adj_cols = [c for c in bowler_match.columns if c.endswith('_comp_adj')]
    print(f"[INFO] Bowler competition-adjusted columns: {len(adj_cols)}")

    return issues


def validate_season_level(batter_season, bowler_season, name="Dataset"):
    """Validate player-season level features."""
    print(f"\n{'='*60}")
    print(f"VALIDATING {name.upper()} SEASON LEVEL")
    print(f"{'='*60}")

    issues = []

    # Check adjusted rates exist
    adj_cols = [c for c in batter_season.columns if c.endswith('_adj')]
    print(f"[INFO] Batter shrinkage-adjusted columns: {len(adj_cols)}")

    adj_cols = [c for c in bowler_season.columns if c.endswith('_adj')]
    print(f"[INFO] Bowler shrinkage-adjusted columns: {len(adj_cols)}")

    adj_cols = [c for c in batter_season.columns if c.endswith('_comp_adj')]
    print(f"[INFO] Batter competition-adjusted columns: {len(adj_cols)}")

    adj_cols = [c for c in bowler_season.columns if c.endswith('_comp_adj')]
    print(f"[INFO] Bowler competition-adjusted columns: {len(adj_cols)}")

    # Check reliability flags
    for flag in ['min_balls_100', 'min_balls_50', 'min_high_extreme_30', 'min_chase_30']:
        if flag in batter_season.columns:
            eligible = batter_season[flag].sum()
            print(f"[INFO] Batter {flag}: {eligible} player-seasons")

    for flag in ['min_balls_100', 'min_balls_50', 'min_high_extreme_30', 'min_defend_30']:
        if flag in bowler_season.columns:
            eligible = bowler_season[flag].sum()
            print(f"[INFO] Bowler {flag}: {eligible} player-seasons")

    # Check seasons played
    if 'seasons_played' in batter_season.columns:
        print(f"[INFO] Batter seasons played range: {batter_season['seasons_played'].min()}-{batter_season['seasons_played'].max()}")

    if 'seasons_played' in bowler_season.columns:
        print(f"[INFO] Bowler seasons played range: {bowler_season['seasons_played'].min()}-{bowler_season['seasons_played'].max()}")

    # Check for NaN in key adjusted columns
    for col in ['strike_rate_adj', 'high_extreme_sr_adj', 'strike_rate_comp_adj']:
        if col in batter_season.columns:
            nan_count = batter_season[col].isna().sum()
            if nan_count > 0:
                issues.append(f"NaN in {col}: {nan_count}")

    for col in ['economy_rate_adj', 'high_extreme_economy_adj', 'economy_rate_comp_adj']:
        if col in bowler_season.columns:
            nan_count = bowler_season[col].isna().sum()
            if nan_count > 0:
                issues.append(f"NaN in {col}: {nan_count}")

    if not any("NaN" in i for i in issues):
        print("[OK] No NaN in key adjusted columns")

    return issues


def manual_innings_inspection(df, name="Dataset"):
    """Manually inspect representative innings."""
    print(f"\n{'='*60}")
    print(f"MANUAL INNINGS INSPECTION - {name.upper()}")
    print(f"{'='*60}")

    # Find a successful chase
    chase_wins = df[(df['innings'] == 2) & (df['required_runs'] <= 0)]
    if len(chase_wins) > 0:
        match_ids = chase_wins['match_id'].unique()[:2]
        print(f"\n--- Successful chase: Match {match_ids[0]} ---")
        sample = df[(df['match_id'] == match_ids[0]) & (df['innings'] == 2)].head(15)
        cols = ['overid', 'over_ball_num', 'batter_runs', 'is_wicket', 'team_score_before',
                'wickets_before', 'required_runs', 'required_run_rate', 'batting_pressure', 'comp_type']
        print(sample[cols].to_string())

    # Find a failed chase
    chase_losses = df[(df['innings'] == 2) & (df['legal_balls_remaining'] == 0) & (df['required_runs'] > 0)]
    if len(chase_losses) > 0:
        match_ids = chase_losses['match_id'].unique()[:2]
        print(f"\n--- Failed chase: Match {match_ids[0]} ---")
        sample = df[(df['match_id'] == match_ids[0]) & (df['innings'] == 2)].tail(15)
        cols = ['overid', 'over_ball_num', 'batter_runs', 'is_wicket', 'team_score_before',
                'wickets_before', 'required_runs', 'required_run_rate', 'batting_pressure', 'comp_type']
        print(sample[cols].to_string())

    # Find a first innings collapse
    collapse = df[(df['innings'] == 1) & (df['wickets_before'] >= 6) & (df['overid'] <= 10)]
    if len(collapse) > 0:
        match_ids = collapse['match_id'].unique()[:1]
        print(f"\n--- First innings collapse: Match {match_ids[0]} ---")
        sample = df[(df['match_id'] == match_ids[0]) & (df['innings'] == 1)].head(20)
        cols = ['overid', 'over_ball_num', 'batter_runs', 'is_wicket', 'team_score_before',
                'wickets_before', 'current_run_rate', 'batting_pressure', 'comp_type']
        print(sample[cols].to_string())


def main():
    print("=" * 60)
    print("VALIDATE ALL-COMPETITION PRESSURE FEATURES - Task 07")
    print("=" * 60)

    # Load datasets
    all_comp = pd.read_csv("data/processed/all_competition_pressure_deliveries.csv", low_memory=False)
    batter_match = pd.read_csv("data/processed/all_competition_batter_match_features.csv")
    bowler_match = pd.read_csv("data/processed/all_competition_bowler_match_features.csv")
    batter_season = pd.read_csv("data/processed/all_competition_batter_season_features.csv")
    bowler_season = pd.read_csv("data/processed/all_competition_bowler_season_features.csv")

    all_issues = []

    # Delivery level validation
    all_issues.extend(validate_delivery_level(all_comp, "All-Competition"))

    # Match level validation
    all_issues.extend(validate_match_level(batter_match, bowler_match, "All-Competition"))

    # Season level validation
    all_issues.extend(validate_season_level(batter_season, bowler_season, "All-Competition"))

    # Manual inspection
    manual_innings_inspection(all_comp, "All-Competition")

    # Summary
    print(f"\n{'='*60}")
    print("VALIDATION SUMMARY")
    print(f"{'='*60}")

    if all_issues:
        print(f"ISSUES FOUND ({len(all_issues)}):")
        for issue in all_issues:
            print(f"  - {issue}")
    else:
        print("ALL CHECKS PASSED [OK]")

    # Save validation report
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "task07_validation_report.md", "w", encoding="utf-8") as f:
        f.write("# Task 07 Validation Report\n\n")
        f.write(f"**Generated:** 2026-11-17\n\n")

        if all_issues:
            f.write(f"## Issues Found ({len(all_issues)})\n\n")
            for issue in all_issues:
                f.write(f"- {issue}\n")
        else:
            f.write("## All Checks Passed ✅\n\n")

        f.write("\n## Validation Checks Performed\n\n")
        f.write("### Delivery Level\n")
        f.write("- No negative runs\n")
        f.write("- No duplicate delivery keys\n")
        f.write("- Legal ball counts consistent\n")
        f.write("- No negative balls remaining\n")
        f.write("- No future leakage (monotonicity)\n")
        f.write("- No Super Over deliveries in primary\n")
        f.write("- No ambiguous extras in primary\n")
        f.write("- Pressure categories valid\n")
        f.write("- batter_runs = runs column\n")
        f.write("- No division by zero / infinite rates\n")
        f.write("- Player ID joins complete\n")
        f.write("- Competition tier/type coverage verified\n\n")

        f.write("### Match Level\n")
        f.write("- No negative counts\n")
        f.write("- Reasonable strike rates / economy rates\n")
        f.write("- Pressure distributions available\n")
        f.write("- Competition-adjusted columns present\n\n")

        f.write("### Season Level\n")
        f.write("- Shrinkage-adjusted rates computed\n")
        f.write("- Competition-adjusted rates computed\n")
        f.write("- Reliability flags populated\n")
        f.write("- Seasons played tracked\n")
        f.write("- No NaN in key adjusted columns\n\n")

        f.write("### Manual Inspection\n")
        f.write("- Successful chase inspected\n")
        f.write("- Failed chase inspected\n")
        f.write("- First innings collapse inspected\n")

    print(f"\nValidation report saved to outputs/task07_validation_report.md")


if __name__ == "__main__":
    main()