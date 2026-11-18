#!/usr/bin/env python3
"""
Identify specific missing player IDs from eligible pool in key datasets
"""

import pandas as pd
from pathlib import Path

SUPPORTING = Path("outputs/supporting_evidence")
PROCESSED = Path("data/processed")
OFFICIAL = Path("outputs/official_reference")
AUDIT_DIR = Path("outputs/audit")

# Load eligible pool
eligible_df = pd.read_csv(SUPPORTING / "ipl_eligibility_audit.csv")
eligible_ids = set(eligible_df[eligible_df['eligibility_status'] == 'ELIGIBLE']['player_id'].astype(int).tolist())
eligible_names = dict(zip(eligible_df['player_id'].astype(int), eligible_df['player_name']))

print(f"Total eligible: {len(eligible_ids)}")

# Load key datasets
datasets = {
    'comp_batter': PROCESSED / "player_performance_by_competition_batter.csv",
    'comp_bowler': PROCESSED / "player_performance_by_competition_bowler.csv",
    'season_batter': PROCESSED / "player_performance_by_season_batter.csv",
    'season_bowler': PROCESSED / "player_performance_by_season_bowler.csv",
    'pressure_batter': PROCESSED / "player_pressure_metrics_batter.csv",
    'pressure_bowler': PROCESSED / "player_pressure_metrics_bowler.csv",
    'domestic_batter': PROCESSED / "player_domestic_metrics_batter.csv",
    'domestic_bowler': PROCESSED / "player_domestic_metrics_bowler.csv",
    'form': PROCESSED / "player_current_form.csv",
    'phase': PROCESSED / "player_bowling_phase_metrics.csv",
}

id_cols = {
    'comp_batter': 'striker_id',
    'comp_bowler': 'bowler_id',
    'season_batter': 'striker_id',
    'season_bowler': 'bowler_id',
    'pressure_batter': 'player_id',
    'pressure_bowler': 'player_id',
    'domestic_batter': 'striker_id',
    'domestic_bowler': 'bowler_id',
    'form': 'player_id',
    'phase': 'bowler_id',
}

missing_report = []

for name, path in datasets.items():
    df = pd.read_csv(path)
    id_col = id_cols[name]
    present_ids = set(df[id_col].astype(int).unique())
    missing = eligible_ids - present_ids
    missing_report.append({
        'dataset': name,
        'id_column': id_col,
        'eligible_count': len(eligible_ids),
        'present_count': len(present_ids & eligible_ids),
        'missing_count': len(missing),
        'missing_ids': ','.join(str(m) for m in sorted(missing)),
        'missing_names': ','.join(eligible_names.get(m, 'UNKNOWN') for m in sorted(missing))
    })
    print(f"{name}: {len(present_ids & eligible_ids)}/{len(eligible_ids)} present, {len(missing)} missing")

# Save detailed missing report
report_df = pd.DataFrame(missing_report)
report_df.to_csv(AUDIT_DIR / "missing_ids_detail.csv", index=False)
print(f"\nSaved missing IDs detail to {AUDIT_DIR / 'missing_ids_detail.csv'}")

# Focus on bowler gap
bowler_missing = eligible_ids - set(pd.read_csv(PROCESSED / "player_performance_by_competition_bowler.csv")['bowler_id'].astype(int).unique())
print(f"\n=== {len(bowler_missing)} ELIGIBLE PLAYERS MISSING BOWLING DATA ===")
for pid in sorted(bowler_missing):
    print(f"  {pid}: {eligible_names.get(pid, 'UNKNOWN')}")

# Check if these are in batter data
batter_present = set(pd.read_csv(PROCESSED / "player_performance_by_competition_batter.csv")['striker_id'].astype(int).unique())
pure_batters = bowler_missing & batter_present
pure_bowlers = bowler_missing - batter_present
print(f"\n  Pure batters (no bowling data): {len(pure_batters)}")
for pid in sorted(pure_batters):
    print(f"    {pid}: {eligible_names.get(pid, 'UNKNOWN')}")
print(f"  Neither batting nor bowling: {len(pure_bowlers)}")
for pid in sorted(pure_bowlers):
    print(f"    {pid}: {eligible_names.get(pid, 'UNKNOWN')}")

# Domestic missing
dom_bat_missing = eligible_ids - set(pd.read_csv(PROCESSED / "player_domestic_metrics_batter.csv")['striker_id'].astype(int).unique())
dom_bowl_missing = eligible_ids - set(pd.read_csv(PROCESSED / "player_domestic_metrics_bowler.csv")['bowler_id'].astype(int).unique())
print(f"\n=== DOMESTIC MISSING ===")
print(f"  Batters missing domestic: {len(dom_bat_missing)}")
print(f"  Bowlers missing domestic: {len(dom_bowl_missing)}")

# Shortlist domestic coverage
shortlist_ids = set()
for f in ['final_combined_top10_batters.csv', 'final_combined_top10_bowlers.csv', 'final_combined_reserves.csv']:
    df = pd.read_csv(OFFICIAL / f)
    if 'player_id' in df.columns:
        shortlist_ids.update(df['player_id'].astype(int).unique())

shortlist_dom_bat = shortlist_ids & set(pd.read_csv(PROCESSED / "player_domestic_metrics_batter.csv")['striker_id'].astype(int).unique())
shortlist_dom_bowl = shortlist_ids & set(pd.read_csv(PROCESSED / "player_domestic_metrics_bowler.csv")['bowler_id'].astype(int).unique())
print(f"\n=== SHORTLIST DOMESTIC COVERAGE ===")
print(f"  Shortlist: {len(shortlist_ids)} players")
print(f"  With domestic batting: {len(shortlist_dom_bat)}")
print(f"  With domestic bowling: {len(shortlist_dom_bowl)}")
print(f"  Shortlist missing domestic: {shortlist_ids - shortlist_dom_bat - shortlist_dom_bowl}")

# Create summary of missing bowlers who are in shortlist
shortlist_missing_bowl = shortlist_ids - set(pd.read_csv(PROCESSED / "player_performance_by_competition_bowler.csv")['bowler_id'].astype(int).unique())
print(f"\n=== SHORTLIST PLAYERS MISSING BOWLING DATA ===")
for pid in sorted(shortlist_missing_bowl):
    print(f"  {pid}: {eligible_names.get(pid, 'UNKNOWN')}")