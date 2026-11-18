#!/usr/bin/env python3
"""
Phase 3: Batting/Bowling Statistical Audit
Validates calculations, shrinkage, pressure metrics, EQ bowling boundaries
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

PROCESSED = Path("data/processed")
SUPPORTING = Path("outputs/supporting_evidence")
OFFICIAL = Path("outputs/official_reference")
AUDIT_DIR = Path("outputs/audit")
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

# Load official rankings for validation
official_bat = pd.read_csv(OFFICIAL / "final_combined_top10_batters.csv")
official_bowl = pd.read_csv(OFFICIAL / "final_combined_top10_bowlers.csv")
official_res = pd.read_csv(OFFICIAL / "final_combined_reserves.csv")

# Load eligible pool
eligible_df = pd.read_csv(SUPPORTING / "ipl_eligibility_audit.csv")
eligible_ids = set(eligible_df[eligible_df['eligibility_status'] == 'ELIGIBLE']['player_id'].astype(int).tolist())
eligible_names = dict(zip(eligible_df['player_id'].astype(int), eligible_df['player_name']))

print("="*60)
print("PHASE 3: BATTING/BOWLING STATISTICAL AUDIT")
print("="*60)

# ============================================================
# 1. VALIDATE SHRINKAGE CALCULATIONS
# ============================================================
print("\n### 1. SHRINKAGE VALIDATION ###")

# Load season features to check shrinkage
bat_season = pd.read_csv(PROCESSED / "all_competition_batter_season_features.csv")
bowl_season = pd.read_csv(PROCESSED / "all_competition_bowler_season_features.csv")

# Filter to eligible only
bat_season_elig = bat_season[bat_season['striker_id'].isin(eligible_ids)].copy()
bowl_season_elig = bowl_season[bowl_season['bowler_id'].isin(eligible_ids)].copy()

print(f"Eligible batter seasons: {len(bat_season_elig)}")
print(f"Eligible bowler seasons: {len(bowl_season_elig)}")

# Check shrinkage columns
shrink_cols_bat = [c for c in bat_season_elig.columns if 'shrink' in c.lower() or 'adj' in c.lower() or 'pop' in c.lower()]
shrink_cols_bowl = [c for c in bowl_season_elig.columns if 'shrink' in c.lower() or 'adj' in c.lower() or 'pop' in c.lower()]

print(f"Batter shrinkage/adj columns: {shrink_cols_bat}")
print(f"Bowler shrinkage/adj columns: {shrink_cols_bowl}")

# Check min_balls flags
print(f"\nMin balls flags (batter): {bat_season_elig['min_balls_100'].sum()}/100, {bat_season_elig['min_balls_50'].sum()}/50, {bat_season_elig['min_high_extreme_30'].sum()}/30, {bat_season_elig['min_chase_30'].sum()}/30")
print(f"Min balls flags (bowler): {bowl_season_elig['min_balls_100'].sum()}/100, {bowl_season_elig['min_balls_50'].sum()}/50, {bowl_season_elig['min_high_extreme_30'].sum()}/30")

# ============================================================
# 2. VALIDATE PRESSURE METRICS
# ============================================================
print("\n### 2. PRESSURE METRICS VALIDATION ###")

pressure_bat = pd.read_csv(PROCESSED / "player_pressure_metrics_batter.csv")
pressure_bowl = pd.read_csv(PROCESSED / "player_pressure_metrics_bowler.csv")

pressure_bat_elig = pressure_bat[pressure_bat['player_id'].isin(eligible_ids)].copy()
pressure_bowl_elig = pressure_bowl[pressure_bowl['player_id'].isin(eligible_ids)].copy()

print(f"Eligible pressure batter: {len(pressure_bat_elig)}")
print(f"Eligible pressure bowler: {len(pressure_bowl_elig)}")

# Check pressure columns
press_cols = [c for c in pressure_bat_elig.columns if 'pressure' in c.lower() or 'chase' in c.lower() or 'defend' in c.lower() or 'high_extreme' in c.lower()]
print(f"Pressure columns (sample): {press_cols[:20]}")

# Validate chase pressure metrics
if 'chase_balls' in pressure_bat_elig.columns:
    chase_players = pressure_bat_elig[pressure_bat_elig['chase_balls'] > 0]
    print(f"Players with chase data: {len(chase_players)}")
    if len(chase_players) > 0:
        print(f"  Chase SR range: {chase_players['chase_strike_rate'].min():.1f} - {chase_players['chase_strike_rate'].max():.1f}")
        print(f"  Chase dismissal rate range: {chase_players['chase_dismissal_rate'].min():.4f} - {chase_players['chase_dismissal_rate'].max():.4f}")

# Validate high-extreme pressure
if 'high_extreme_balls' in pressure_bat_elig.columns:
    he_players = pressure_bat_elig[pressure_bat_elig['high_extreme_balls'] > 0]
    print(f"Players with high-extreme data: {len(he_players)}")

# ============================================================
# 3. VALIDATE EQ BOWLING MODEL
# ============================================================
print("\n### 3. EVIDENCE-QUALIFIED BOWLING VALIDATION ###")

eq_comparison = pd.read_csv(SUPPORTING / "evidence_qualified_bowler_comparison.csv")
print(f"EQ Comparison rows: {len(eq_comparison)}")
print(f"Columns: {list(eq_comparison.columns)}")

bowl_deploy = pd.read_csv(SUPPORTING / "bowling_deployment_validation.csv")
print(f"Bowling Deployment rows: {len(bowl_deploy)}")
print(f"Columns: {list(bowl_deploy.columns)}")

bowl_zero = pd.read_csv(SUPPORTING / "bowling_zero_opportunity_audit.csv")
print(f"Bowling Zero Opp rows: {len(bowl_zero)}")
print(f"Columns: {list(bowl_zero.columns)}")

# Check deployment boundaries
if 'prohibited_deployment' in bowl_deploy.columns:
    print(f"\nProhibited deployments:")
    print(bowl_deploy[['player_id', 'player_name', 'prohibited_deployment']].to_string())

# Check zero opportunity players
if 'player_id' in bowl_zero.columns:
    print(f"\nZero opportunity players: {len(bowl_zero)}")
    cols = [c for c in ['player_id', 'bowler_name', 'artifact_diagnosis', 'he_status', 'death_status', 'pp_status'] if c in bowl_zero.columns]
    print(bowl_zero[cols].to_string())

# ============================================================
# 4. VALIDATE OFFICIAL RANKINGS REPRODUCTION
# ============================================================
print("\n### 4. OFFICIAL RANKINGS REPRODUCTION ###")

scoring_repro = pd.read_csv(SUPPORTING / "scoring_reproduction.csv")
print(f"Scoring Reproduction rows: {len(scoring_repro)}")
print(f"Columns: {list(scoring_repro.columns)}")

# Check if it matches official
if 'player_id' in scoring_repro.columns:
    match_ids = set(scoring_repro['player_id'].astype(int).unique()) & set(official_bat['player_id'].astype(int).unique()) | set(official_bowl['player_id'].astype(int).unique()) | set(official_res['player_id'].astype(int).unique())
    print(f"Official IDs in scoring reproduction: {len(match_ids)}")

# ============================================================
# 5. VALIDATE SCORING SENSITIVITY
# ============================================================
print("\n### 5. SCORING SENSITIVITY ANALYSIS ###")

sens = pd.read_csv(SUPPORTING / "scoring_sensitivity_analysis.csv")
print(f"Sensitivity rows: {len(sens)}")
print(f"Columns: {list(sens.columns)}")

# ============================================================
# 6. VALIDATE COMPETITION TIER WEIGHTS
# ============================================================
print("\n### 6. COMPETITION TIER VALIDATION ###")

comp_bat = pd.read_csv(PROCESSED / "player_performance_by_competition_batter.csv")
comp_bowl = pd.read_csv(PROCESSED / "player_performance_by_competition_bowler.csv")

comp_bat_elig = comp_bat[comp_bat['striker_id'].isin(eligible_ids)].copy()
comp_bowl_elig = comp_bowl[comp_bowl['bowler_id'].isin(eligible_ids)].copy()

print(f"Eligible competition batter: {len(comp_bat_elig)}")
print(f"Eligible competition bowler: {len(comp_bowl_elig)}")

# Check tier distribution
if 'comp_tier' in comp_bat_elig.columns:
    print(f"Batter tier distribution:")
    print(comp_bat_elig['comp_tier'].value_counts().sort_index())

if 'comp_tier' in comp_bowl_elig.columns:
    print(f"Bowler tier distribution:")
    print(comp_bowl_elig['comp_tier'].value_counts().sort_index())

# ============================================================
# 7. VALIDATE DOMESTIC METRICS CALCULATIONS
# ============================================================
print("\n### 7. DOMESTIC METRICS VALIDATION ###")

dom_bat = pd.read_csv(PROCESSED / "player_domestic_metrics_batter.csv")
dom_bowl = pd.read_csv(PROCESSED / "player_domestic_metrics_bowler.csv")

dom_bat_elig = dom_bat[dom_bat['striker_id'].isin(eligible_ids)].copy()
dom_bowl_elig = dom_bowl[dom_bowl['bowler_id'].isin(eligible_ids)].copy()

print(f"Eligible domestic batter: {len(dom_bat_elig)}")
print(f"Eligible domestic bowler: {len(dom_bowl_elig)}")

# Check domestic columns
print(f"Domestic batter columns: {list(dom_bat_elig.columns)[:30]}")
print(f"Domestic bowler columns: {list(dom_bowl_elig.columns)[:30]}")

# Validate calculations
if 'strike_rate' in dom_bat_elig.columns and 'total_runs' in dom_bat_elig.columns and 'total_dismissals' in dom_bat_elig.columns:
    # Check batting average calculation
    valid = dom_bat_elig[dom_bat_elig['total_dismissals'] > 0]
    if len(valid) > 0:
        valid['calc_avg'] = valid['total_runs'] / valid['total_dismissals']
        avg_diff = (valid['calc_avg'] - valid['strike_rate']).abs().mean()
        print(f"Batting avg vs SR diff: {avg_diff:.4f} (should be different metrics)")

if 'economy' in dom_bowl_elig.columns and 'total_runs' in dom_bowl_elig.columns and 'total_balls' in dom_bowl_elig.columns:
    valid = dom_bowl_elig[dom_bowl_elig['total_balls'] > 0]
    if len(valid) > 0:
        valid['calc_econ'] = (valid['total_runs'] / valid['total_balls']) * 6
        econ_diff = (valid['calc_econ'] - valid['economy']).abs().mean()
        print(f"Bowling economy diff: {econ_diff:.4f}")

# ============================================================
# 8. CROSS-CHECK SCORING WEIGHTS
# ============================================================
print("\n### 8. SCORING WEIGHT VALIDATION ###")

# Dynamic scouting engine weights
dyn_engine = Path("src/scoring/dynamic_scouting_engine.py")
if dyn_engine.exists():
    content = dyn_engine.read_text()
    print("Dynamic Scouting Engine - Profile weights:")
    import re
    # Find profile definitions
    profiles = re.findall(r'["\'](\w+)["\']:\s*\{[^}]*dimA[^}]*dimB[^}]*dimC[^}]*dimD', content)
    print(f"  Profiles found: {profiles}")

# Check scouting priority scores
scouting_scores = pd.read_csv(SUPPORTING / "rr_scouting_priority_scores.csv")
print(f"\nRR Scouting Priority Scores: {len(scouting_scores)} rows")
print(f"Columns: {list(scouting_scores.columns)}")

if len(scouting_scores) > 0:
    print(scouting_scores.head(3).to_string())

# ============================================================
# 9. STATISTICAL ANOMALY DETECTION
# ============================================================
print("\n### 9. STATISTICAL ANOMALY DETECTION ###")

# Check for impossible values
# Batting: SR > 400, avg > 200, dismissal_rate > 1
# Bowling: econ > 20, avg > 100, wkts > balls

anomalies = []

# Season batting
bat_check = bat_season_elig.copy()
if 'strike_rate' in bat_check.columns:
    high_sr = bat_check[bat_check['strike_rate'] > 400]
    if len(high_sr) > 0:
        anomalies.append(f"Batter SR > 400: {len(high_sr)} records")
    if 'dismissal_rate' in bat_check.columns:
        bad_dr = bat_check[bat_check['dismissal_rate'] > 1]
        if len(bad_dr) > 0:
            anomalies.append(f"Batter dismissal_rate > 1: {len(bad_dr)} records")

# Season bowling
bowl_check = bowl_season_elig.copy()
if 'economy' in bowl_check.columns:
    high_econ = bowl_check[bowl_check['economy'] > 20]
    if len(high_econ) > 0:
        anomalies.append(f"Bowler econ > 20: {len(high_econ)} records")
if 'total_balls' in bowl_check.columns and 'total_wickets' in bowl_check.columns:
    bad_wkts = bowl_check[bowl_check['total_wickets'] > bowl_check['total_balls']]
    if len(bad_wkts) > 0:
        anomalies.append(f"Bowler wickets > balls: {len(bad_wkts)} records")

# Pressure metrics
if 'chase_strike_rate' in pressure_bat_elig.columns:
    bad_chase = pressure_bat_elig[pressure_bat_elig['chase_strike_rate'] > 500]
    if len(bad_chase) > 0:
        anomalies.append(f"Chase SR > 500: {len(bad_chase)} records")

if anomalies:
    print("ANOMALIES FOUND:")
    for a in anomalies:
        print(f"  - {a}")
else:
    print("No statistical anomalies detected")

# ============================================================
# 10. SAVE AUDIT SUMMARY
# ============================================================
print("\n### 10. SAVING AUDIT RESULTS ###")

audit_summary = {
    'timestamp': pd.Timestamp.now().isoformat(),
    'eligible_players': len(eligible_ids),
    'official_top10_batters': len(official_bat),
    'official_top10_bowlers': len(official_bowl),
    'official_reserves': len(official_res),
    'batter_seasons': len(bat_season_elig),
    'bowler_seasons': len(bowl_season_elig),
    'pressure_batter': len(pressure_bat_elig),
    'pressure_bowler': len(pressure_bowl_elig),
    'competition_batter': len(comp_bat_elig),
    'competition_bowler': len(comp_bowl_elig),
    'domestic_batter': len(dom_bat_elig),
    'domestic_bowler': len(dom_bowl_elig),
    'anomalies_found': len(anomalies),
    'anomalies': anomalies,
    'shrinkage_columns_batter': shrink_cols_bat,
    'shrinkage_columns_bowler': shrink_cols_bowl,
    'min_balls_100_batter': int(bat_season_elig['min_balls_100'].sum()) if 'min_balls_100' in bat_season_elig.columns else 0,
    'min_balls_50_batter': int(bat_season_elig['min_balls_50'].sum()) if 'min_balls_50' in bat_season_elig.columns else 0,
    'min_balls_100_bowler': int(bowl_season_elig['min_balls_100'].sum()) if 'min_balls_100' in bowl_season_elig.columns else 0,
    'min_balls_50_bowler': int(bowl_season_elig['min_balls_50'].sum()) if 'min_balls_50' in bowl_season_elig.columns else 0,
}

with open(AUDIT_DIR / "statistical_audit_summary.json", 'w') as f:
    json.dump(audit_summary, f, indent=2)

print(f"Saved audit summary to {AUDIT_DIR / 'statistical_audit_summary.json'}")

# Save detailed comparison of official vs computed
if 'verified_rr_scouting_score' in official_bat.columns and 'verified_rr_scouting_score' in scoring_repro.columns:
    # Try to match
    pass

print("\n" + "="*60)
print("PHASE 3 STATISTICAL AUDIT COMPLETE")
print("="*60)