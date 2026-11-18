#!/usr/bin/env python3
"""
Build RR Current Squad Database
===============================
Creates data/reference/rr_current_squad.csv by enriching retained_players.csv
with player_master.csv metadata for Rajasthan Royals retained players.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utilities.paths import PROCESSED_DATA_DIR, SUPPORTING_EVIDENCE_DIR, REFERENCE_DATA_DIR


# Known ages for RR players (from public records, approximate as of 2027-04-01)
# These are best estimates for players not in age_verification.csv
RR_PLAYER_AGES = {
    'Aman Rao Perala': 22,
    'Brijesh Sharma': 23,
    'Dasun Shanaka': 35,
    'Dhruv Jurel': 26,
    'Donovan Ferreira': 28,
    'Jofra Archer': 32,
    'Lhuan-dre Pretorius': 20,
    'Manimaran Siddharth': 26,
    'Mohd. Shami': 37,
    'Nandre Burger': 28,
    'Ravi Bishnoi': 26,
    'Ravindra Jadeja': 38,
    'Riyan Parag': 25,
    'Sandeep Sharma': 33,
    'Shubham Dubey': 28,
    'Sushant Mishra': 24,
    'Vaibhav Suryavanshi': 17,  # Vaibhav Sooryavanshi (different spelling)
    'Yash Raj Punja': 22,
    'Yashasvi Jaiswal': 25,
}

# Development category mapping based on age
def get_dev_category(age: float) -> str:
    if pd.isna(age):
        return 'Unknown'
    if age <= 23:
        return 'Emerging'
    elif age <= 26:
        return 'Young development candidate'
    elif age <= 30:
        return 'Prime-age performer'
    else:
        return 'Experienced performer'


def compute_age_from_dob(dob_str: str) -> float:
    """Compute age as of 2027-04-01 from DOB string."""
    if pd.isna(dob_str) or dob_str == '' or str(dob_str).lower() == 'nan':
        return np.nan
    try:
        dob = pd.to_datetime(dob_str, errors='coerce')
        if pd.isna(dob):
            return np.nan
        ref_date = pd.Timestamp('2027-04-01')
        age = (ref_date - dob).days / 365.25
        return round(age, 1)
    except Exception:
        return np.nan


def build_rr_squad():
    print("=" * 70)
    print("BUILDING RR CURRENT SQUAD DATABASE")
    print("=" * 70)

    # Load retained players
    print("\n[1/3] Loading retained players...")
    retained = pd.read_csv(SUPPORTING_EVIDENCE_DIR / "retained_players.csv")
    print(f"  Total retained players: {len(retained)}")

    # Filter for RR
    rr_retained = retained[retained['franchise'] == 'RR'].copy()
    print(f"  RR retained players: {len(rr_retained)}")

    # Load player master
    print("\n[2/3] Loading player master...")
    master = pd.read_csv(PROCESSED_DATA_DIR / "player_master.csv")
    print(f"  Total players in master: {len(master)}")

    # Load age verification for shortlist players
    age_ver = pd.read_csv(SUPPORTING_EVIDENCE_DIR / "age_verification.csv")
    age_lookup = {int(r['player_id']): r.to_dict() for _, r in age_ver.iterrows()}

    # Create lookup by canonical_name (fuzzy match on player_name)
    master_lookup = {}
    for _, row in master.iterrows():
        name = str(row['canonical_name']).strip().lower()
        master_lookup[name] = row.to_dict()

    # Also create lookup by aliases
    alias_lookup = {}
    for _, row in master.iterrows():
        if pd.notna(row['aliases']):
            for alias in str(row['aliases']).split('|'):
                alias_lookup[alias.strip().lower()] = row.to_dict()

    # Name corrections for matching
    name_corrections = {
        'vaibhav suryavanshi': 'vaibhav sooryavanshi',
        'lhuan-dre pretorius': 'dwaine pretorius',
        'yash raj punja': 'yash punja',
        'mohd. shami': 'mohammed shami',
    }

    # Enrich RR squad
    print("\n[3/3] Enriching RR squad with master data...")
    enriched_records = []

    for _, row in rr_retained.iterrows():
        player_name = str(row['player_name']).strip()
        name_key = player_name.lower()

        # Apply name corrections
        if name_key in name_corrections:
            name_key = name_corrections[name_key]

        # Try exact match on canonical_name
        master_rec = master_lookup.get(name_key)

        # Try alias match
        if not master_rec:
            master_rec = alias_lookup.get(name_key)

        # Try partial match (last name)
        if not master_rec:
            last_name = player_name.split()[-1].lower()
            for k, v in master_lookup.items():
                if last_name in k and len(last_name) > 3:
                    master_rec = v
                    break

        # Get age from known ages or age verification
        age = RR_PLAYER_AGES.get(player_name, np.nan)
        dev_cat = get_dev_category(age)

        if master_rec:
            # Try to get age from master DOB
            master_age = master_rec.get('age_as_of_2027_04_01', np.nan)
            if pd.isna(age) and pd.notna(master_age):
                age = master_age
            if pd.isna(age) and pd.notna(master_rec.get('date_of_birth')):
                age = compute_age_from_dob(master_rec['date_of_birth'])

            # Check age verification
            pid = int(master_rec['player_id'])
            if pid in age_lookup:
                age = age_lookup[pid].get('exact_age_as_of_2027_04_01', age)
                dev_cat = age_lookup[pid].get('verified_development_category', dev_cat)

            if pd.isna(age):
                dev_cat = master_rec.get('development_category', dev_cat)

            enriched = {
                'player_id': int(master_rec['player_id']),
                'player_name': player_name,
                'franchise': 'RR',
                'overseas_status': row['overseas_status'],
                'trade_status': row['trade_status'],
                'age_as_of_2027_04_01': age,
                'primary_role': master_rec.get('primary_role', ''),
                'batting_style': master_rec.get('batting_style', ''),
                'bowling_style': master_rec.get('bowling_style', ''),
                'wk_flag': bool(master_rec.get('wk_flag', False)),
                'final_nationality': master_rec.get('final_nationality', ''),
                'is_retained': True,
                'retention_type': row['trade_status'],
                'development_category': dev_cat,
                'eligibility_status': master_rec.get('eligibility_status', ''),
            }
        else:
            print(f"  WARNING: No master match for {player_name}")
            enriched = {
                'player_id': np.nan,
                'player_name': player_name,
                'franchise': 'RR',
                'overseas_status': row['overseas_status'],
                'trade_status': row['trade_status'],
                'age_as_of_2027_04_01': age,
                'primary_role': '',
                'batting_style': '',
                'bowling_style': '',
                'wk_flag': False,
                'final_nationality': row['overseas_status'],
                'is_retained': True,
                'retention_type': row['trade_status'],
                'development_category': dev_cat,
                'eligibility_status': '',
            }

        enriched_records.append(enriched)

    rr_squad = pd.DataFrame(enriched_records)

    # Add derived columns
    rr_squad['nationality'] = rr_squad['final_nationality'].apply(
        lambda x: 'Indian' if str(x).lower() == 'indian' else 'Overseas'
    )

    # Ensure output directory
    REFERENCE_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_path = REFERENCE_DATA_DIR / "rr_current_squad.csv"
    rr_squad.to_csv(output_path, index=False)

    print(f"\n  Saved to: {output_path}")
    print(f"  RR Squad size: {len(rr_squad)}")
    print(f"  Indian: {(rr_squad['nationality'] == 'Indian').sum()}")
    print(f"  Overseas: {(rr_squad['nationality'] == 'Overseas').sum()}")
    print(f"  With player_id: {rr_squad['player_id'].notna().sum()}")
    print(f"  With age: {rr_squad['age_as_of_2027_04_01'].notna().sum()}")

    # Show squad composition
    print("\n  Squad Composition:")
    for _, r in rr_squad.iterrows():
        pid = int(r['player_id']) if pd.notna(r['player_id']) else 'N/A'
        age_str = f"{r['age_as_of_2027_04_01']:.1f}" if pd.notna(r['age_as_of_2027_04_01']) else 'N/A'
        print(f"    {pid} | {r['player_name']} | {r['primary_role']} | {r['nationality']} | Age {age_str} | {r['development_category']} | {r['retention_type']}")

    print("\n" + "=" * 70)
    print("RR SQUAD DATABASE BUILD COMPLETE")
    print("=" * 70)

    return rr_squad


if __name__ == "__main__":
    build_rr_squad()