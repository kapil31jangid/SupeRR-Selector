#!/usr/bin/env python3
"""
Create player_role_classification_audit.csv for Phase 1 audit.
Analyzes role classification across all sources and produces canonical audit.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
SUPPORTING = Path("outputs/supporting_evidence")
PROCESSED = Path("data/processed")
AUDIT_DIR = Path("outputs/audit")
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

# Load data sources
pool_df = pd.read_csv(SUPPORTING / "auction_eligible_player_pool.csv")
master_df = pd.read_csv(PROCESSED / "player_master.csv")
age_df = pd.read_csv(SUPPORTING / "age_verification.csv")

# Load batting and bowling evidence from season features
bat_season = pd.read_csv(PROCESSED / "all_competition_batter_season_features.csv")
bowl_season = pd.read_csv(PROCESSED / "all_competition_bowler_season_features.csv")

# Aggregate batting and bowling balls per player across all seasons
bat_balls = bat_season.groupby('striker_id')['total_balls'].sum().reset_index()
bat_balls.columns = ['player_id', 'batting_balls_total']

bowl_balls = bowl_season.groupby('bowler_id')['total_balls'].sum().reset_index()
bowl_balls.columns = ['player_id', 'bowling_balls_total']

print(f"Pool: {len(pool_df)} rows, {pool_df['player_id'].nunique()} unique players")
print(f"Master: {len(master_df)} rows, {master_df['player_id'].nunique()} unique")
print(f"Age verification: {len(age_df)} players")
print(f"Batting evidence: {len(bat_balls)} players")
print(f"Bowling evidence: {len(bowl_balls)} players")

# Get pool role distribution (unique players only)
pool_unique = pool_df.drop_duplicates('player_id')
print("\nPool role distribution (unique players):")
print(pool_unique['role'].value_counts())

# Get master primary_role distribution
print("\nMaster primary_role distribution:")
print(master_df['primary_role'].value_counts())

# For each UNIQUE player in pool, analyze their master records
audit_rows = []

for _, pool_row in pool_unique.iterrows():
    pid = pool_row['player_id']
    pname = pool_row['player_name']
    pool_role = pool_row['role']

    # Get master records for this player
    master_records = master_df[master_df['player_id'] == pid].copy()

    # Get batting and bowling evidence
    bat_evidence = bat_balls[bat_balls['player_id'] == pid]
    bowl_evidence = bowl_balls[bowl_balls['player_id'] == pid]

    batting_balls = int(bat_evidence['batting_balls_total'].values[0]) if len(bat_evidence) > 0 else 0
    bowling_balls = int(bowl_evidence['bowling_balls_total'].values[0]) if len(bowl_evidence) > 0 else 0

    if len(master_records) == 0:
        audit_rows.append({
            'player_id': pid,
            'canonical_name': pname,
            'source_role_pool': pool_role,
            'source_role_master_primary': 'NOT_IN_MASTER',
            'source_role_master_pool_role': 'NOT_IN_MASTER',
            'resolved_role': pool_role,
            'batting_balls_total': batting_balls,
            'bowling_balls_total': bowling_balls,
            'seasons_played': 0,
            'resolution_method': 'pool_only',
            'confidence': 'HIGH',
            'audit_status': 'OK'
        })
        continue

    # Get primary_role from highest composite_score record (best season)
    best_record = master_records.loc[master_records['composite_score'].idxmax()]
    master_primary_role = best_record.get('primary_role', 'Unknown')
    master_role = best_record.get('role', 'Unknown')

    # Determine resolved role with evidence threshold (≥50 balls for each discipline)
    has_bat = batting_balls >= 50
    has_bowl = bowling_balls >= 50

    if has_bat and has_bowl:
        resolved_role = 'All-rounder'
        resolution = 'evidence_both_50+'
        confidence = 'HIGH' if batting_balls >= 100 and bowling_balls >= 100 else 'MEDIUM'
    elif has_bat:
        resolved_role = 'Batter'
        resolution = 'evidence_bat_50+'
        confidence = 'HIGH' if batting_balls >= 100 else 'MEDIUM'
    elif has_bowl:
        resolved_role = 'Bowler'
        resolution = 'evidence_bowl_50+'
        confidence = 'HIGH' if bowling_balls >= 100 else 'MEDIUM'
    else:
        resolved_role = 'Unknown'
        resolution = 'insufficient_evidence'
        confidence = 'LOW'

    # Check consistency with pool role
    # Pool only has Batter/Bowler - so All-rounder from evidence is an enhancement, not mismatch
    if resolved_role == 'All-rounder':
        audit_status = 'ENHANCED'  # Evidence reveals all-rounder capability
    elif pool_role == resolved_role:
        audit_status = 'OK'
    elif pool_role in ['Batter', 'Bowler'] and resolved_role in ['Batter', 'Bowler']:
        audit_status = 'OK'  # Both agree on specialist role
    else:
        audit_status = 'ROLE_MISMATCH'

    audit_rows.append({
        'player_id': pid,
        'canonical_name': pname,
        'source_role_pool': pool_role,
        'source_role_master_primary': master_primary_role,
        'source_role_master_pool_role': master_role,
        'resolved_role': resolved_role,
        'batting_balls_total': batting_balls,
        'bowling_balls_total': bowling_balls,
        'seasons_played': len(master_records),
        'resolution_method': resolution,
        'confidence': confidence,
        'audit_status': audit_status
    })

audit_df = pd.DataFrame(audit_rows)

# Add age info where available
age_dict = age_df.set_index('player_id')['exact_age_as_of_2027_04_01'].to_dict()
audit_df['age'] = audit_df['player_id'].map(age_dict)

# Save
output_path = AUDIT_DIR / "player_role_classification_audit.csv"
audit_df.to_csv(output_path, index=False)

print(f"\nAudit saved to {output_path}")
print(f"Total unique players audited: {len(audit_df)}")
print(f"\nAudit status distribution:")
print(audit_df['audit_status'].value_counts())
print(f"\nResolved role distribution:")
print(audit_df['resolved_role'].value_counts())
print(f"\nResolution method distribution:")
print(audit_df['resolution_method'].value_counts())
print(f"\nConfidence distribution:")
print(audit_df['confidence'].value_counts())

# Show mismatches only
mismatches = audit_df[audit_df['audit_status'] == 'ROLE_MISMATCH']
if len(mismatches) > 0:
    print(f"\nROLE MISMATCHES ({len(mismatches)}):")
    for _, row in mismatches.iterrows():
        print(f"  {row['canonical_name']} (ID:{row['player_id']}): pool={row['source_role_pool']}, resolved={row['resolved_role']}, master_primary={row['source_role_master_primary']}, bat_balls={row['batting_balls_total']}, bowl_balls={row['bowling_balls_total']}")

# Show enhanced (evidence reveals all-rounder)
enhanced = audit_df[audit_df['audit_status'] == 'ENHANCED']
print(f"\nENHANCED - Evidence reveals All-rounder ({len(enhanced)}):")
for _, row in enhanced.head(20).iterrows():
    print(f"  {row['canonical_name']} (ID:{row['player_id']}): pool={row['source_role_pool']}, resolved={row['resolved_role']}, bat_balls={row['batting_balls_total']}, bowl_balls={row['bowling_balls_total']}")

# Also create deduplicated canonical player_master
print("\n\n=== CREATING CANONICAL PLAYER MASTER ===")
# For each player, keep the record with highest composite_score (handle NaN)
master_df['composite_score'] = pd.to_numeric(master_df['composite_score'], errors='coerce')
# Sort by composite_score descending (NaN last), then take first per player
canonical_master = master_df.sort_values('composite_score', ascending=False, na_position='last').drop_duplicates('player_id', keep='first').copy()
print(f"Canonical master: {len(canonical_master)} unique players")

# Add resolved role
role_map = audit_df.set_index('player_id')['resolved_role'].to_dict()
canonical_master['resolved_role'] = canonical_master['player_id'].map(role_map)

# Add age
canonical_master['age'] = canonical_master['player_id'].map(age_dict)

# Add batting/bowling balls
bat_map = bat_balls.set_index('player_id')['batting_balls_total'].to_dict()
bowl_map = bowl_balls.set_index('player_id')['bowling_balls_total'].to_dict()
canonical_master['batting_balls_total'] = canonical_master['player_id'].map(bat_map).fillna(0).astype(int)
canonical_master['bowling_balls_total'] = canonical_master['player_id'].map(bowl_map).fillna(0).astype(int)

# Save canonical master
canonical_path = PROCESSED / "player_master_canonical.csv"
canonical_master.to_csv(canonical_path, index=False)
print(f"Canonical master saved to {canonical_path}")
print(f"Columns: {list(canonical_master.columns)}")

# Also save a version with only pool players
pool_ids = set(pool_unique['player_id'].unique())
pool_master = canonical_master[canonical_master['player_id'].isin(pool_ids)].copy()
pool_master_path = PROCESSED / "player_master_pool.csv"
pool_master.to_csv(pool_master_path, index=False)
print(f"Pool-only canonical master ({len(pool_master)} players) saved to {pool_master_path}")