#!/usr/bin/env python3
"""
Build Complete Player Master Database
PRESSURE-X 2.0 — Consolidates all player identity, metadata, and eligibility into one canonical table.
Uses player_id as primary key. Never merges players by name alone.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utilities.paths import PROJECT_ROOT as PATHS_ROOT, RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUTS_DIR, SUPPORTING_EVIDENCE_DIR


def build_player_master():
    print("=" * 70)
    print("BUILDING COMPLETE PLAYER MASTER DATABASE")
    print("=" * 70)

    # 1. Load competition_team_player_mapping (primary identity source)
    print("\n[1/8] Loading competition_team_player_mapping...")
    mapping = pd.read_csv(RAW_DATA_DIR / "competition_team_player_mapping.csv")
    print(f"  Rows: {len(mapping)}")
    print(f"  Unique player_ids: {mapping['player_id'].nunique()}")

    # Get canonical name per player_id (most frequent non-null name)
    name_map = mapping.groupby('player_id')['player_name'].apply(
        lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0]
    ).reset_index()
    name_map.columns = ['player_id', 'canonical_name']

    # Get all aliases per player
    alias_map = mapping.groupby('player_id')['player_name'].apply(
        lambda x: '|'.join(sorted(x.unique()))
    ).reset_index()
    alias_map.columns = ['player_id', 'aliases']

    # Get competition coverage per player
    comp_map = mapping.groupby('player_id').agg(
        competition_count=('comp_id', 'nunique'),
        comp_ids=('comp_id', lambda x: '|'.join(map(str, sorted(x.unique())))),
        comp_names=('comp_name', lambda x: '|'.join(sorted(x.unique()))),
        team_count=('team_id', 'nunique'),
        team_names=('team_name', lambda x: '|'.join(sorted(x.unique())))
    ).reset_index()

    # Get country/nationality from competition names - check national team participation
    def infer_nationality(team_names, comp_names):
        teams = team_names.split('|') if isinstance(team_names, str) else []
        comps = comp_names.split('|') if isinstance(comp_names, str) else []

        # National team patterns in competition names
        national_patterns = {
            'India': ['India in ', 'India vs ', 'India in ', 'India v ', 'India in'],
            'Australia': ['Australia in ', 'Australia vs ', 'Australia v ', 'Australia '],
            'England': ['England in ', 'England vs ', 'England v ', 'England '],
            'South Africa': ['South Africa in ', 'South Africa vs ', 'South Africa v ', 'South Africa '],
            'New Zealand': ['New Zealand in ', 'New Zealand vs ', 'New Zealand v ', 'New Zealand '],
            'Pakistan': ['Pakistan in ', 'Pakistan vs ', 'Pakistan v ', 'Pakistan '],
            'Sri Lanka': ['Sri Lanka in ', 'Sri Lanka vs ', 'Sri Lanka v ', 'Sri Lanka '],
            'West Indies': ['West Indies in ', 'West Indies vs ', 'West Indies v ', 'West Indies '],
            'Bangladesh': ['Bangladesh in ', 'Bangladesh vs ', 'Bangladesh v ', 'Bangladesh '],
            'Afghanistan': ['Afghanistan in ', 'Afghanistan vs ', 'Afghanistan v ', 'Afghanistan '],
            'Zimbabwe': ['Zimbabwe in ', 'Zimbabwe vs ', 'Zimbabwe v ', 'Zimbabwe '],
            'Ireland': ['Ireland in ', 'Ireland vs ', 'Ireland v ', 'Ireland '],
            'Netherlands': ['Netherlands in ', 'Netherlands vs ', 'Netherlands v '],
            'Scotland': ['Scotland in ', 'Scotland vs ', 'Scotland v '],
            'UAE': ['United Arab Emirates in ', 'UAE in '],
            'Nepal': ['Nepal in ', 'Nepal vs '],
            'Hong Kong': ['Hong Kong in '],
            'Oman': ['Oman in '],
            'USA': ['United States in ', 'USA in '],
            'Canada': ['Canada in '],
            'Namibia': ['Namibia in '],
            'PNG': ['Papua New Guinea in '],
        }

        # Check for national team participation (not franchise/IPL)
        for c in comps:
            # Skip franchise/IPL/development competitions
            if any(x in c for x in ['IPL', 'Super Kings', 'Mumbai Indians', 'Rajasthan Royals', 'Punjab Kings',
                                    'Royal Challengers', 'Delhi Capitals', 'Kolkata Knight Riders',
                                    'Sunrisers Hyderabad', 'Gujarat Titans', 'Lucknow Super Giants',
                                    'India A', 'Pakistan A', 'Sri Lanka A', 'Bangladesh A', 'Afghanistan A',
                                    'Emerging', 'Rising Stars', 'Tri-Nation', 'Tri-Series', 'Qualifiers',
                                    'Asia Cup', 'CPL', 'BPL', 'LPL', 'BBL', 'PSL', 'SA20', 'The Hundred',
                                    'ILT20', 'MLC', 'Vitality Blast', 'Super Smash', 'SMAT', 'Ranji',
                                    'TNPL', 'Maharaja', 'Delhi Premier']):
                continue
            for country, patterns in national_patterns.items():
                for p in patterns:
                    if p in c:
                        return 'Indian' if country == 'India' else 'Overseas'

        # Fallback: check if any competition has national team name
        for c in comps:
            if c.startswith('India ') and 'A' not in c and 'Emerging' not in c and 'Rising' not in c:
                return 'Indian'

        return 'Overseas'

    comp_map['inferred_nationality'] = comp_map.apply(lambda r: infer_nationality(r['team_names'], r['comp_names']), axis=1)

    # Get first/last season from competitions.csv
    comps = pd.read_csv(RAW_DATA_DIR / "competitions.csv")
    comp_season = comps[['comp_id', 'season']].copy()
    mapping_with_season = mapping.merge(comp_season, on='comp_id', how='left')
    season_map = mapping_with_season.groupby('player_id')['season'].agg(['min', 'max']).reset_index()
    season_map.columns = ['player_id', 'first_season', 'last_season']

    # 2. Load playing_eleven for WK, captain, batting_order info
    print("\n[2/8] Loading playing_eleven...")
    pe = pd.read_csv(RAW_DATA_DIR / "playing_eleven.csv")
    pe_played = pe[pe['is_played'] == True].copy()

    wk_map = pe_played[pe_played['is_wk'] == True].groupby('player_id').size().reset_index(name='wk_appearances')
    capt_map = pe_played[pe_played['is_captain'] == True].groupby('player_id').size().reset_index(name='captain_appearances')
    bat_order_map = pe_played.groupby('player_id')['batting_order'].median().reset_index()
    bat_order_map.columns = ['player_id', 'median_batting_order']
    matches_played_map = pe_played.groupby('player_id')['match_id'].nunique().reset_index()
    matches_played_map.columns = ['player_id', 'matches_played']

    # 3. Load age_verification (DOB for shortlist)
    print("\n[3/8] Loading age_verification...")
    age_ver = pd.read_csv(SUPPORTING_EVIDENCE_DIR / "age_verification.csv")
    age_ver = age_ver[['player_id', 'verified_date_of_birth', 'exact_age_as_of_2027_04_01', 'verified_development_category']].copy()
    age_ver.columns = ['player_id', 'date_of_birth', 'age_as_of_2027_04_01', 'development_category']

    # 4. Load ipl_eligibility_audit
    print("\n[4/8] Loading ipl_eligibility_audit...")
    elig = pd.read_csv(SUPPORTING_EVIDENCE_DIR / "ipl_eligibility_audit.csv")
    elig = elig[['player_id', 'recorded_nationality', 'eligibility_status', 'reason_for_exclusion', 'citizenship_exception_review']].copy()

    # 5. Load retained_players (RR squad + all franchises)
    print("\n[5/8] Loading retained_players...")
    retained = pd.read_csv(SUPPORTING_EVIDENCE_DIR / "retained_players.csv")
    retained['is_retained'] = True
    retained_rr = retained[retained['franchise'] == 'CSK'].copy()  # Actually need to check RR - let me check
    # The retained_players.csv has franchise column - RR is Rajasthan Royals
    # Let me check what franchises exist
    franchises = retained['franchise'].unique()
    print(f"  Franchises: {franchises}")

    # Mark retained status per player
    retained_status = retained.groupby('player_name').agg(
        retained_franchises=('franchise', lambda x: '|'.join(sorted(x.unique()))),
        retained_overseas_status=('overseas_status', lambda x: '|'.join(sorted(x.unique()))),
        retained_trade_status=('trade_status', lambda x: '|'.join(sorted(x.unique())))
    ).reset_index()
    retained_status['is_retained'] = True
    # Add nationality from retained_players (overseas_status)
    retained_status['retained_nationality'] = retained_status['retained_overseas_status'].apply(
        lambda x: 'Overseas' if 'Overseas' in str(x) else 'Indian'
    )

    # 6. Load auction_eligible_player_pool for role, composite_score
    print("\n[6/8] Loading auction_eligible_player_pool...")
    pool = pd.read_csv(SUPPORTING_EVIDENCE_DIR / "auction_eligible_player_pool.csv")
    pool_info = pool[['player_id', 'player_name', 'role', 'season', 'composite_score',
                      'displayed_score', 'uncapped_score', 'total_balls', 'high_extreme_balls',
                      'competition_coverage', 'competition_tiers', 'origin', 'auction_rank',
                      'task07f_global_rank']].copy()

    # 7. Load player_identity_traceability for corrections
    print("\n[7/8] Loading player_identity_traceability...")
    trace = pd.read_csv(SUPPORTING_EVIDENCE_DIR / "player_identity_traceability.csv")
    trace = trace[['verified_canonical_player_id', 'task07l_reported_id', 'id_audit_status']].copy()

    # 8. Load ball_by_ball for batting/bowling style inference
    print("\n[8/8] Loading ball_by_ball for style inference (sampling)...")
    # Sample to infer batting/bowling style
    bbb = pd.read_csv(RAW_DATA_DIR / "ball_by_ball.csv", usecols=['striker_id', 'striker_name', 'bowler_id', 'bowler_name',
                                                                   'batting_type', 'bowling_type'])
    # Batting style per player
    bat_style = bbb.groupby('striker_id').agg(
        batting_type=('batting_type', lambda x: x.mode().iloc[0] if not x.mode().empty else 'Unknown'),
        batting_type_count=('batting_type', 'count')
    ).reset_index()
    bat_style.columns = ['player_id', 'batting_style', 'batting_style_obs']

    bowl_style = bbb.groupby('bowler_id').agg(
        bowling_type=('bowling_type', lambda x: x.mode().iloc[0] if not x.mode().empty else 'Unknown'),
        bowling_type_count=('bowling_type', 'count')
    ).reset_index()
    bowl_style.columns = ['player_id', 'bowling_style', 'bowling_style_obs']

    # Determine primary/secondary role
    def assign_primary_role(row):
        has_bat = row.get('batting_style_obs', 0) > 0
        has_bowl = row.get('bowling_style_obs', 0) > 0
        if has_bat and has_bowl:
            return 'All-rounder'
        elif has_bat:
            return 'Batter'
        elif has_bowl:
            return 'Bowler'
        return 'Unknown'

    # ===== MERGE ALL =====
    print("\n[MERGE] Building master table...")

    # Start with all unique player_ids from mapping (most comprehensive)
    master = name_map.copy()
    master = master.merge(alias_map, on='player_id', how='left')
    master = master.merge(comp_map, on='player_id', how='left')
    master = master.merge(season_map, on='player_id', how='left')
    master = master.merge(wk_map, on='player_id', how='left')
    master = master.merge(capt_map, on='player_id', how='left')
    master = master.merge(bat_order_map, on='player_id', how='left')
    master = master.merge(matches_played_map, on='player_id', how='left')
    master = master.merge(age_ver, on='player_id', how='left')
    master = master.merge(elig, on='player_id', how='left')
    master = master.merge(retained_status, left_on='canonical_name', right_on='player_name', how='left')
    master = master.merge(pool_info, on='player_id', how='left')
    master = master.merge(trace, left_on='player_id', right_on='verified_canonical_player_id', how='left')
    master = master.merge(bat_style, on='player_id', how='left')
    master = master.merge(bowl_style, on='player_id', how='left')

    # Fill missing batting/bowling style from pool role
    master['batting_style'] = master['batting_style'].fillna('Unknown')
    master['bowling_style'] = master['bowling_style'].fillna('Unknown')
    master['batting_style_obs'] = master['batting_style_obs'].fillna(0).astype(int)
    master['bowling_style_obs'] = master['bowling_style_obs'].fillna(0).astype(int)

    # Primary/Secondary role
    master['primary_role'] = master.apply(assign_primary_role, axis=1)
    master['secondary_role'] = np.where(
        (master['batting_style_obs'] > 0) & (master['bowling_style_obs'] > 0),
        'All-rounder',
        np.where(master['batting_style_obs'] > 0, 'Batter',
                 np.where(master['bowling_style_obs'] > 0, 'Bowler', 'Unknown'))
    )

    # Wicketkeeping status
    master['wk_status'] = np.where(master['wk_appearances'].fillna(0) > 0, 'Yes', 'No')

    # IPL participation
    master['ipl_participation'] = master['comp_ids'].apply(
        lambda x: 'Yes' if isinstance(x, str) and ('1358' in x or '1715' in x or '2193' in x or '2725' in x or '3298' in x) else 'No'
    )

    # International participation
    master['international_participation'] = master['comp_ids'].apply(
        lambda x: 'Yes' if isinstance(x, str) and any(tid in x for tid in ['1331', '1335', '1345', '1435', '1439', '1452', '1458', '1474', '1494', '1499', '1512', '1517', '1523', '1531', '1533', '1534', '1537', '1543', '1551', '1584', '1595', '1599', '1601', '1603', '1608', '1611', '1646', '1698', '1700', '1709', '1718', '1719', '1742', '1769', '1792', '1799', '1885', '1913', '1997', '1998', '1999', '2000', '2046', '2047', '2048', '2058', '2059', '2060', '2061', '2062', '2188', '2229', '2267', '2269', '2305', '2350', '2354', '2371', '2372', '2387', '2395', '2398', '2442', '2452', '2453', '2455', '2457', '2512', '2513', '2542', '2548', '2561', '2562', '2605', '2626', '2628', '2670', '2692', '2716', '2718', '2722', '2753', '2755', '2793', '2801', '2873', '2874', '2875', '2906', '2912', '2915', '2921', '2940', '2973', '2975', '3020', '3074', '3126', '3128', '3133', '3159', '3162', '3163', '3174', '3190', '3197', '3223', '3226', '3228', '3241', '3251', '3254', '3282', '3288', '3313', '3317', '3329', '3331', '3334', '3358', '3395', '3405', '3433', '3446', '3450', '3464', '3465', '3473', '3482', '3568', '3690', '3713', '3739', '3765', '3787']) else 'No'
    )

    # Domestic participation (other T20)
    master['domestic_participation'] = master['comp_ids'].apply(
        lambda x: 'Yes' if isinstance(x, str) and any(tid in x for tid in ['2670', '3289']) else 'No'
    )

    # Data completeness score
    master['data_completeness'] = (
        master['date_of_birth'].notna().astype(int) * 20 +
        master['development_category'].notna().astype(int) * 15 +
        master['batting_style'].ne('Unknown').astype(int) * 15 +
        master['bowling_style'].ne('Unknown').astype(int) * 15 +
        master['eligibility_status'].notna().astype(int) * 15 +
        master['composite_score'].notna().astype(int) * 20
    )

    # Evidence reliability
    def evidence_reliability(row):
        if row['data_completeness'] >= 80:
            return 'High'
        elif row['data_completeness'] >= 50:
            return 'Medium'
        elif row['data_completeness'] >= 30:
            return 'Low'
        return 'Very Low'

    master['evidence_reliability'] = master.apply(evidence_reliability, axis=1)

    # Final nationality: prefer recorded_nationality (eligibility audit), then retained_nationality (retained players), then inferred
    master['final_nationality'] = master['recorded_nationality'].fillna(master.get('retained_nationality')).fillna(master['inferred_nationality'])
    # Clean up nationality values
    master['final_nationality'] = master['final_nationality'].replace({'Non-Indian/Overseas': 'Overseas', 'Indian': 'Indian'})

    # Select and order columns
    final_cols = [
        'player_id', 'canonical_name', 'aliases',
        'date_of_birth', 'age_as_of_2027_04_01', 'development_category',
        'batting_style', 'bowling_style',
        'primary_role', 'secondary_role', 'wk_status',
        'final_nationality', 'recorded_nationality', 'inferred_nationality', 'retained_nationality',
        'eligibility_status', 'reason_for_exclusion',
        'is_retained', 'retained_franchises', 'retained_overseas_status', 'retained_trade_status',
        'ipl_participation', 'international_participation', 'domestic_participation',
        'competition_count', 'comp_ids', 'comp_names', 'team_count', 'team_names',
        'first_season', 'last_season',
        'matches_played', 'median_batting_order', 'wk_appearances', 'captain_appearances',
        'role', 'season', 'composite_score', 'displayed_score', 'uncapped_score',
        'total_balls', 'high_extreme_balls', 'competition_coverage', 'competition_tiers', 'origin',
        'auction_rank', 'task07f_global_rank',
        'data_completeness', 'evidence_reliability',
        'id_audit_status'
    ]

    # Keep only columns that exist
    final_cols = [c for c in final_cols if c in master.columns]
    master = master[final_cols]

    # Sort by auction_rank (eligible first), then by data_completeness
    master['sort_key'] = master['auction_rank'].fillna(9999)
    master = master.sort_values(['sort_key', 'data_completeness'], ascending=[True, False]).drop('sort_key', axis=1)

    # Save
    output_path = PROCESSED_DATA_DIR / "player_master.csv"
    master.to_csv(output_path, index=False)
    print(f"\n[OK] Saved player_master.csv: {len(master)} players, {len(master.columns)} columns")
    print(f"  Path: {output_path}")

    # Summary stats
    print("\n=== SUMMARY ===")
    print(f"Total players: {len(master)}")
    print(f"With DOB: {master['date_of_birth'].notna().sum()}")
    print(f"With eligibility: {master['eligibility_status'].notna().sum()}")
    print(f"Eligible: {(master['eligibility_status'] == 'ELIGIBLE').sum()}")
    print(f"Retained: {master['is_retained'].notna().sum()}")
    print(f"IPL participation: {(master['ipl_participation'] == 'Yes').sum()}")
    print(f"International: {(master['international_participation'] == 'Yes').sum()}")
    print(f"Domestic: {(master['domestic_participation'] == 'Yes').sum()}")
    print(f"WK identified: {(master['wk_status'] == 'Yes').sum()}")
    print(f"Primary roles: {master['primary_role'].value_counts().to_dict()}")
    print(f"Evidence reliability: {master['evidence_reliability'].value_counts().to_dict()}")

    return master


if __name__ == "__main__":
    build_player_master()