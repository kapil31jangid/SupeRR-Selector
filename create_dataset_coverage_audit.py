#!/usr/bin/env python3
"""
Phase 2: Dataset Coverage Reconciliation
Creates dataset_coverage_audit.csv and reconciliation_matrix.csv
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

# All datasets to audit
datasets = {
    # Performance Database (15 files)
    "all_competition_batter_match_features": PROCESSED / "all_competition_batter_match_features.csv",
    "all_competition_batter_season_features": PROCESSED / "all_competition_batter_season_features.csv",
    "all_competition_bowler_match_features": PROCESSED / "all_competition_bowler_match_features.csv",
    "all_competition_bowler_season_features": PROCESSED / "all_competition_bowler_season_features.csv",
    "ipl_only_batter_match_features": PROCESSED / "ipl_only_batter_match_features.csv",
    "ipl_only_batter_season_features": PROCESSED / "ipl_only_batter_season_features.csv",
    "ipl_only_bowler_match_features": PROCESSED / "ipl_only_bowler_match_features.csv",
    "ipl_only_bowler_season_features": PROCESSED / "ipl_only_bowler_season_features.csv",
    "player_bowling_phase_metrics": PROCESSED / "player_bowling_phase_metrics.csv",
    "player_current_form": PROCESSED / "player_current_form.csv",
    "player_domestic_metrics_batter": PROCESSED / "player_domestic_metrics_batter.csv",
    "player_domestic_metrics_bowler": PROCESSED / "player_domestic_metrics_bowler.csv",
    "player_performance_by_competition_batter": PROCESSED / "player_performance_by_competition_batter.csv",
    "player_performance_by_competition_bowler": PROCESSED / "player_performance_by_competition_bowler.csv",
    "player_performance_by_season_batter": PROCESSED / "player_performance_by_season_batter.csv",
    "player_performance_by_season_bowler": PROCESSED / "player_performance_by_season_bowler.csv",
    "player_pressure_metrics_batter": PROCESSED / "player_pressure_metrics_batter.csv",
    "player_pressure_metrics_bowler": PROCESSED / "player_pressure_metrics_bowler.csv",

    # Master files
    "player_master": PROCESSED / "player_master.csv",
    "player_master_canonical": PROCESSED / "player_master_canonical.csv",
    "player_master_pool": PROCESSED / "player_master_pool.csv",

    # Official reference (3 files)
    "final_combined_top10_batters": OFFICIAL / "final_combined_top10_batters.csv",
    "final_combined_top10_bowlers": OFFICIAL / "final_combined_top10_bowlers.csv",
    "final_combined_reserves": OFFICIAL / "final_combined_reserves.csv",

    # Supporting evidence
    "auction_eligible_player_pool": SUPPORTING / "auction_eligible_player_pool.csv",
    "ipl_eligibility_audit": SUPPORTING / "ipl_eligibility_audit.csv",
    "age_verification": SUPPORTING / "age_verification.csv",
    "retained_players": SUPPORTING / "retained_players.csv",
    "retained_player_matching_audit": SUPPORTING / "retained_player_matching_audit.csv",
    "bowling_zero_opportunity_audit": SUPPORTING / "bowling_zero_opportunity_audit.csv",
    "current_form_source_verification": SUPPORTING / "current_form_source_verification.csv",
    "evidence_qualified_bowler_comparison": SUPPORTING / "evidence_qualified_bowler_comparison.csv",
    "final_eligibility_audit": SUPPORTING / "final_eligibility_audit.csv",
    "final_shortlist_corrections": SUPPORTING / "final_shortlist_corrections.csv",
    "player_identity_traceability": SUPPORTING / "player_identity_traceability.csv",
    "rr_scouting_priority_scores": SUPPORTING / "rr_scouting_priority_scores.csv",
    "rr_scouting_selection_audit": SUPPORTING / "rr_scouting_selection_audit.csv",
    "scoring_reproduction": SUPPORTING / "scoring_reproduction.csv",
    "scoring_sensitivity_analysis": SUPPORTING / "scoring_sensitivity_analysis.csv",
    "bowling_deployment_validation": SUPPORTING / "bowling_deployment_validation.csv",
}

# Pool of eligible players (303)
eligible_df = pd.read_csv(SUPPORTING / "ipl_eligibility_audit.csv")
eligible_ids = set(eligible_df[eligible_df['eligibility_status'] == 'ELIGIBLE']['player_id'].astype(int).tolist())
print(f"Eligible player IDs: {len(eligible_ids)}")

# Official shortlist (28) - from final combined CSVs
official_bat = pd.read_csv(OFFICIAL / "final_combined_top10_batters.csv")
official_bowl = pd.read_csv(OFFICIAL / "final_combined_top10_bowlers.csv")
official_res = pd.read_csv(OFFICIAL / "final_combined_reserves.csv")
shortlist_ids = set()
for df in [official_bat, official_bowl, official_res]:
    if 'player_id' in df.columns:
        shortlist_ids.update(df['player_id'].astype(int).tolist())
print(f"Shortlist player IDs: {len(shortlist_ids)}")

# RR squad (19)
rr_df = pd.read_csv(Path("data/reference/rr_current_squad.csv"))
rr_ids = set(rr_df['player_id'].astype(int).tolist())
print(f"RR Squad player IDs: {len(rr_ids)}")

# Audit results
coverage_rows = []
reconciliation_rows = []

for name, path in datasets.items():
    if not path.exists():
        print(f"MISSING: {name} at {path}")
        continue

    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"ERROR reading {name}: {e}")
        continue

    # Basic metadata
    row_count = len(df)
    col_count = len(df.columns)
    cols = list(df.columns)

    # Find ID column
    id_col = None
    for c in ['player_id', 'striker_id', 'bowler_id', 'batsman_id', 'bowlerId']:
        if c in df.columns:
            id_col = c
            break

    unique_ids = df[id_col].nunique() if id_col else 0
    unique_id_set = set(df[id_col].astype(int).tolist()) if id_col else set()

    # Null rates
    null_rates = df.isnull().mean().to_dict()
    avg_null_rate = np.mean(list(null_rates.values()))
    max_null_rate = max(null_rates.values()) if null_rates else 0

    # Date/season range
    season_cols = [c for c in df.columns if 'season' in c.lower() or 'year' in c.lower() or 'date' in c.lower()]
    season_range = ""
    if season_cols:
        for sc in season_cols:
            try:
                vals = pd.to_numeric(df[sc], errors='coerce').dropna()
                if len(vals) > 0:
                    season_range = f"{int(vals.min())}-{int(vals.max())}"
                    break
            except:
                pass

    # Competition tiers covered
    comp_cols = [c for c in df.columns if 'comp' in c.lower() or 'tier' in c.lower() or 'competition' in c.lower()]
    tiers = []
    for cc in comp_cols:
        try:
            unique_tiers = df[cc].dropna().unique()
            tiers.extend([str(t) for t in unique_tiers])
        except:
            pass
    tiers = sorted(set(tiers))

    # Coverage against eligible pool
    if id_col:
        in_eligible = len(unique_id_set & eligible_ids)
        in_shortlist = len(unique_id_set & shortlist_ids)
        in_rr = len(unique_id_set & rr_ids)
        orphans = len(unique_id_set - eligible_ids)
        missing_from_eligible = len(eligible_ids - unique_id_set)
    else:
        in_eligible = in_shortlist = in_rr = orphans = missing_from_eligible = 0

    # Duplicates
    dup_count = row_count - unique_ids if id_col else 0

    coverage_rows.append({
        'dataset': name,
        'path': str(path),
        'rows': row_count,
        'columns': col_count,
        'id_column': id_col or 'NONE',
        'unique_ids': unique_ids,
        'duplicates': dup_count,
        'avg_null_rate': round(avg_null_rate, 4),
        'max_null_rate': round(max_null_rate, 4),
        'season_range': season_range,
        'competition_tiers': '|'.join(tiers) if tiers else 'NONE',
        'in_eligible_pool': in_eligible,
        'in_shortlist': in_shortlist,
        'in_rr_squad': in_rr,
        'orphans_outside_eligible': orphans,
        'missing_from_eligible': missing_from_eligible,
        'column_names': '|'.join(cols[:50])  # First 50 cols
    })

    # Reconciliation details for key datasets
    if name in ['auction_eligible_player_pool', 'player_master', 'player_master_canonical',
                'all_competition_batter_season_features', 'all_competition_bowler_season_features',
                'player_performance_by_competition_batter', 'player_performance_by_competition_bowler',
                'player_performance_by_season_batter', 'player_performance_by_season_bowler',
                'player_pressure_metrics_batter', 'player_pressure_metrics_bowler',
                'player_domestic_metrics_batter', 'player_domestic_metrics_bowler']:
        reconciliation_rows.append({
            'dataset': name,
            'id_column': id_col,
            'total_unique_ids': unique_ids,
            'eligible_ids_covered': in_eligible,
            'shortlist_ids_covered': in_shortlist,
            'rr_ids_covered': in_rr,
            'orphan_ids': orphans,
            'missing_eligible_ids': missing_from_eligible,
            'coverage_pct_eligible': round(in_eligible / len(eligible_ids) * 100, 1) if eligible_ids else 0
        })

coverage_df = pd.DataFrame(coverage_rows)
recon_df = pd.DataFrame(reconciliation_rows)

# Save
coverage_path = AUDIT_DIR / "dataset_coverage_audit.csv"
recon_path = AUDIT_DIR / "reconciliation_matrix.csv"

coverage_df.to_csv(coverage_path, index=False)
recon_df.to_csv(recon_path, index=False)

print(f"\nSaved: {coverage_path} ({len(coverage_df)} datasets)")
print(f"Saved: {recon_path} ({len(recon_df)} key datasets)")

# Summary
print("\n=== COVERAGE SUMMARY ===")
for _, row in coverage_df.iterrows():
    print(f"  {row['dataset']}: {row['rows']} rows, {row['unique_ids']} unique {row['id_column']}, "
          f"eligible={row['in_eligible_pool']}, shortlist={row['in_shortlist']}, "
          f"RR={row['in_rr_squad']}, orphans={row['orphans_outside_eligible']}, "
          f"missing={row['missing_from_eligible']}, nulls={row['avg_null_rate']:.1%}")

print("\n=== RECONCILIATION MATRIX ===")
for _, row in recon_df.iterrows():
    print(f"  {row['dataset']}: {row['coverage_pct_eligible']}% of eligible pool covered")

# Check for critical issues
print("\n=== CRITICAL ISSUES ===")
for _, row in coverage_df.iterrows():
    if row['orphans_outside_eligible'] > 0:
        print(f"  ORPHANS: {row['dataset']} has {row['orphans_outside_eligible']} IDs outside eligible pool")
    if row['missing_from_eligible'] > 0 and row['dataset'] in ['player_master', 'auction_eligible_player_pool']:
        print(f"  MISSING: {row['dataset']} missing {row['missing_from_eligible']} eligible players")
    if row['duplicates'] > 0 and row['dataset'] not in ['auction_eligible_player_pool', 'player_master']:
        print(f"  DUPLICATES: {row['dataset']} has {row['duplicates']} duplicate rows")
    if row['avg_null_rate'] > 0.5:
        print(f"  HIGH NULLS: {row['dataset']} has {row['avg_null_rate']:.1%} avg null rate")

# Cross-reference: pool vs master vs official CSVs
print("\n=== CROSS-REFERENCE: POOL VS MASTER VS OFFICIAL ===")
pool_df = pd.read_csv(SUPPORTING / "auction_eligible_player_pool.csv")
pool_unique = set(pool_df['player_id'].astype(int).unique())
master_df = pd.read_csv(PROCESSED / "player_master.csv")
master_ids = set(master_df['player_id'].astype(int).unique())
canon_df = pd.read_csv(PROCESSED / "player_master_canonical.csv")
canon_ids = set(canon_df['player_id'].astype(int).unique())

official_bat = pd.read_csv(OFFICIAL / "final_combined_top10_batters.csv")
official_bowl = pd.read_csv(OFFICIAL / "final_combined_top10_bowlers.csv")
official_res = pd.read_csv(OFFICIAL / "final_combined_reserves.csv")

for name, df_off in [('official_batters', official_bat), ('official_bowlers', official_bowl), ('official_reserves', official_res)]:
    id_col_off = 'player_id' if 'player_id' in df_off.columns else None
    if id_col_off:
        off_ids = set(df_off[id_col_off].astype(int).unique())
        print(f"  {name}: {len(off_ids)} IDs, in_eligible={len(off_ids & eligible_ids)}, in_pool={len(off_ids & pool_unique)}, in_master={len(off_ids & master_ids)}")

# Check performance DB coverage
print("\n=== PERFORMANCE DB COVERAGE ===")
perf_datasets = {
    'comp_batter': 'player_performance_by_competition_batter',
    'comp_bowler': 'player_performance_by_competition_bowler',
    'season_batter': 'player_performance_by_season_batter',
    'season_bowler': 'player_performance_by_season_bowler',
    'pressure_batter': 'player_pressure_metrics_batter',
    'pressure_bowler': 'player_pressure_metrics_bowler',
    'domestic_batter': 'player_domestic_metrics_batter',
    'domestic_bowler': 'player_domestic_metrics_bowler',
}

for label, dname in perf_datasets.items():
    row = coverage_df[coverage_df['dataset'] == dname]
    if len(row) > 0:
        r = row.iloc[0]
        print(f"  {label}: {r['unique_ids']} unique, eligible={r['in_eligible_pool']}, missing={r['missing_from_eligible']}")