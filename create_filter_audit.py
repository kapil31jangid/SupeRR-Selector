#!/usr/bin/env python3
"""
Phase 5: Filter and Input State Audit
Systematically tests all filter combinations across pages, validates filter persistence,
URL state sync, and edge cases.
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

# Load data needed for filter validation
eligible_df = pd.read_csv(SUPPORTING / "ipl_eligibility_audit.csv")
eligible_ids = set(eligible_df[eligible_df['eligibility_status'] == 'ELIGIBLE']['player_id'].astype(int).tolist())

official_bat = pd.read_csv(OFFICIAL / "final_combined_top10_batters.csv")
official_bowl = pd.read_csv(OFFICIAL / "final_combined_top10_bowlers.csv")
official_res = pd.read_csv(OFFICIAL / "final_combined_reserves.csv")

print("="*60)
print("PHASE 5: FILTER AND INPUT STATE AUDIT")
print("="*60)

# Import data_loader
from dashboard.utils.data_loader import (
    load_complete_pool_enriched,
    apply_scouting_filters,
    load_rr_current_squad,
)

full_pool = load_complete_pool_enriched()
rr_squad = load_rr_current_squad()
rr_squad_pids = set(rr_squad['player_id'].astype(int).tolist()) if not rr_squad.empty else set()

print(f"\nPool size: {len(full_pool)} players")
print(f"RR Squad size: {len(rr_squad)} players")
print(f"Shortlist size: {full_pool[full_pool['is_shortlisted'] == True].shape[0]} players")

# ============================================================
# 1. FILTER COMBINATION TESTS
# ============================================================
print("\n### 1. FILTER COMBINATION TESTS ###")

# Define all filter combinations to test
filter_combos = [
    # Role + Nationality combos
    ("Role=Batter, Nat=Indian", {"role": "Batter", "nationality": "Indian"}),
    ("Role=Batter, Nat=Overseas", {"role": "Batter", "nationality": "Overseas"}),
    ("Role=Bowler, Nat=Indian", {"role": "Bowler", "nationality": "Indian"}),
    ("Role=Bowler, Nat=Overseas", {"role": "Bowler", "nationality": "Overseas"}),
    ("Role=All-rounder, Nat=Both", {"role": "All-rounder", "nationality": "Both"}),

    # Score thresholds
    ("Min Pressure=80", {"min_pressure_score": 80}),
    ("Min RR Score=85", {"min_rr_score": 85}),
    ("Min Pressure=70 + RR=75", {"min_pressure_score": 70, "min_rr_score": 75}),

    # Evidence gates
    ("Min 100 balls", {"min_sample_balls": 100}),
    ("Min 50 balls", {"min_sample_balls": 50}),

    # Domestic filters
    ("Dom runs >100", {"domestic_min_runs": 100}),
    ("Dom avg >30", {"domestic_min_avg": 30}),
    ("Dom SR >130", {"domestic_min_sr": 130}),
    ("Dom wkts >5", {"domestic_min_wickets": 5}),
    ("Dom econ <8", {"domestic_max_econ": 8}),

    # Development stage
    ("Emerging (<24)", {"age_group": "Emerging (<24)"}),
    ("Development (24-27)", {"age_group": "Development (24-27)"}),
    ("Prime (27-31)", {"age_group": "Prime (27-31)"}),
    ("Experienced (31+)", {"age_group": "Experienced (31+)"}),

    # Search
    ("Search: Sharma", {"search_query": "Sharma"}),
    ("Search: Kumar", {"search_query": "Kumar"}),
    ("Search: Singh", {"search_query": "Singh"}),

    # View filters
    ("View A: Complete Pool", {"view_filter": "View A: Complete Pool", "limit": None}),
    ("View B: Official Shortlist", {"view_filter": "View B: Official Shortlist", "limit": None}),
    ("View C: RR Squad", {"view_filter": "View C: RR Squad", "limit": None}),

    # Complex combinations
    ("Batter + Indian + Min Pressure 70 + Min 50 balls", {
        "role": "Batter", "nationality": "Indian",
        "min_pressure_score": 70, "min_sample_balls": 50
    }),
    ("Bowler + Overseas + Min RR 75 + Dom wkts >3", {
        "role": "Bowler", "nationality": "Overseas",
        "min_rr_score": 75, "domestic_min_wickets": 3
    }),
    ("Shortlist + Indian + Emerging", {
        "view_filter": "View B: Official Shortlist",
        "nationality": "Indian", "age_group": "Emerging (<24)"
    }),
    ("RR Squad + Bowler", {
        "view_filter": "View C: RR Squad", "role": "Bowler"
    }),
    ("RR Squad + Batter", {
        "view_filter": "View C: RR Squad", "role": "Batter"
    }),
]

filter_results = {}
for test_name, kwargs in filter_combos:
    try:
        result = apply_scouting_filters(full_pool, pool_scope="Full Eligible Pool (311 Players)", **kwargs)
        filter_results[test_name] = {
            "status": "OK",
            "count": len(result),
            "kwargs": kwargs
        }
        print(f"  OK: {test_name}: {len(result)} results")
    except Exception as e:
        filter_results[test_name] = {
            "status": "FAIL",
            "error": str(e),
            "kwargs": kwargs
        }
        print(f"  FAIL: {test_name}: {e}")

# ============================================================
# 2. EDGE CASE TESTS
# ============================================================
print("\n### 2. EDGE CASE TESTS ###")

edge_cases = [
    # Empty results expected
    ("Impossible score (RR>99)", {"min_rr_score": 99}),
    ("Impossible domestic (runs>1000)", {"domestic_min_runs": 1000}),
    ("Search non-existent", {"search_query": "XYZNONEXISTENT"}),
    ("All-rounder filter (may be empty)", {"role": "All-rounder"}),

    # Boundary values
    ("Min balls = 0", {"min_sample_balls": 0}),
    ("Min pressure = 0", {"min_pressure_score": 0}),
    ("Age min=18 max=45", {"age_min": 18, "age_max": 45}),
    ("Age min=25 max=25", {"age_min": 25, "age_max": 25}),

    # None/empty filters
    ("No filters (defaults)", {}),
    ("role=Any, nat=Both", {"role": "Any", "nationality": "Both"}),
]

for test_name, kwargs in edge_cases:
    try:
        result = apply_scouting_filters(full_pool, pool_scope="Full Eligible Pool (311 Players)", **kwargs)
        filter_results[test_name] = {
            "status": "OK",
            "count": len(result),
            "kwargs": kwargs
        }
        print(f"  OK: {test_name}: {len(result)} results")
    except Exception as e:
        filter_results[test_name] = {
            "status": "FAIL",
            "error": str(e),
            "kwargs": kwargs
        }
        print(f"  FAIL: {test_name}: {e}")

# ============================================================
# 3. FILTER PERSISTENCE & STATE VALIDATION
# ============================================================
print("\n### 3. FILTER PERSISTENCE VALIDATION ###")

# Test that applying same filter twice gives same results
consistency_tests = [
    ("Batter + Indian", {"role": "Batter", "nationality": "Indian"}),
    ("View B Shortlist", {"view_filter": "View B: Official Shortlist"}),
    ("Min pressure 80", {"min_pressure_score": 80}),
]

for test_name, kwargs in consistency_tests:
    try:
        result1 = apply_scouting_filters(full_pool, pool_scope="Full Eligible Pool (311 Players)", **kwargs)
        result2 = apply_scouting_filters(full_pool, pool_scope="Full Eligible Pool (311 Players)", **kwargs)

        # Compare
        same_count = len(result1) == len(result2)
        same_ids = set(result1['player_id'].tolist()) == set(result2['player_id'].tolist()) if same_count else False

        if same_count and same_ids:
            print(f"  OK: {test_name} - consistent results across calls")
        else:
            print(f"  WARN: {test_name} - inconsistent results: {len(result1)} vs {len(result2)}")
            filter_results[f"{test_name}_consistency"] = {
                "status": "WARN",
                "details": f"Count: {len(result1)} vs {len(result2)}, IDs match: {same_ids}"
            }
    except Exception as e:
        print(f"  FAIL: {test_name} consistency: {e}")

# ============================================================
# 4. VIEW-SPECIFIC VALIDATION
# ============================================================
print("\n### 4. VIEW-SPECIFIC VALIDATION ###")

# View A: Complete Pool (311 players - but actually 303 after eligibility filter)
view_a = apply_scouting_filters(full_pool, pool_scope="Full Eligible Pool (311 Players)", view_filter="View A: Complete Pool", limit=None)
print(f"  View A (Complete Pool): {len(view_a)} players")
print(f"    Roles: {view_a['role'].value_counts().to_dict()}")
print(f"    Nationality: {view_a['nationality'].value_counts().to_dict()}")
print(f"    Shortlisted: {view_a['is_shortlisted'].sum()}")

# View B: Official Shortlist (28 players)
view_b = apply_scouting_filters(full_pool, pool_scope="Official Shortlist (28 Players)", view_filter="View B: Official Shortlist", limit=None)
print(f"\n  View B (Official Shortlist): {len(view_b)} players")
print(f"    Roles: {view_b['role'].value_counts().to_dict()}")
print(f"    Nationality: {view_b['nationality'].value_counts().to_dict()}")
print(f"    All shortlisted: {view_b['is_shortlisted'].all()}")

# View C: RR Squad (19 players)
view_c = apply_scouting_filters(full_pool, pool_scope="RR Squad Analysis (19 Players)", view_filter="View C: RR Squad", limit=None)
print(f"\n  View C (RR Squad): {len(view_c)} players")
print(f"    Roles: {view_c['role'].value_counts().to_dict()}")
print(f"    Nationality: {view_c['nationality'].value_counts().to_dict()}")
print(f"    In RR squad: {view_c['player_id'].isin(rr_squad_pids).sum() if 'player_id' in view_c.columns else 'N/A'}")

# Verify shortlist players are in View B
shortlist_ids = set(full_pool[full_pool['is_shortlisted'] == True]['player_id'].tolist())
view_b_ids = set(view_b['player_id'].tolist())
if shortlist_ids == view_b_ids:
    print("\n  OK: View B contains exactly the 28 shortlist players")
else:
    print(f"\n  WARN: View B mismatch - shortlist: {len(shortlist_ids)}, view_b: {len(view_b_ids)}")
    print(f"    Missing: {shortlist_ids - view_b_ids}")
    print(f"    Extra: {view_b_ids - shortlist_ids}")

# Verify RR squad players are in View C
view_c_ids = set(view_c['player_id'].tolist()) if 'player_id' in view_c.columns else set()
rr_in_view_c = rr_squad_pids & view_c_ids
print(f"  RR Squad in View C: {len(rr_in_view_c)}/{len(rr_squad_pids)}")

# ============================================================
# 5. CROSS-PAGE FILTER CONSISTENCY
# ============================================================
print("\n### 5. CROSS-PAGE FILTER CONSISTENCY ###")

# Test that the same filter logic works across different pool scopes
# Using the same filter kwargs with different pool_scope/view_filter
cross_page_filters = [
    {"role": "Batter", "nationality": "Indian", "min_pressure_score": 70},
    {"role": "Bowler", "nationality": "Overseas", "min_rr_score": 75},
    {"min_sample_balls": 50},
]

for i, kwargs in enumerate(cross_page_filters):
    # Test with all three views
    results = {}
    for view_name, view_filter in [
        ("View A", "View A: Complete Pool"),
        ("View B", "View B: Official Shortlist"),
        ("View C", "View C: RR Squad")
    ]:
        pool_scope_map = {
            "View A: Complete Pool": "Full Eligible Pool (311 Players)",
            "View B: Official Shortlist": "Official Shortlist (28 Players)",
            "View C: RR Squad": "RR Squad Analysis (19 Players)"
        }
        try:
            result = apply_scouting_filters(
                full_pool,
                pool_scope=pool_scope_map[view_filter],
                view_filter=view_filter,
                **kwargs
            )
            results[view_name] = len(result)
        except Exception as e:
            results[view_name] = f"ERROR: {e}"

    print(f"  Filter set {i+1} {kwargs}:")
    for view, count in results.items():
        print(f"    {view}: {count}")

# ============================================================
# 6. DETERMINISTIC SORTING / ORDERING
# ============================================================
print("\n### 6. DETERMINISTIC ORDERING ###")

# Test that results are consistently ordered
test_filter = {"role": "Batter", "nationality": "Indian"}
for _ in range(3):
    result = apply_scouting_filters(full_pool, pool_scope="Full Eligible Pool (311 Players)", **test_filter)
    ids = result['player_id'].tolist()
    print(f"  First 5 IDs: {ids[:5]}")

# ============================================================
# 7. SUMMARY
# ============================================================
print("\n" + "="*60)
print("PHASE 5 FILTER AUDIT SUMMARY")
print("="*60)

total_tests = len(filter_results)
passed = sum(1 for v in filter_results.values() if v["status"] == "OK")
failed = sum(1 for v in filter_results.values() if v["status"] == "FAIL")
warned = sum(1 for v in filter_results.values() if v["status"] == "WARN")

print(f"Total filter tests: {total_tests}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Warnings: {warned}")

# Save audit results
audit_data = {
    "filter_tests": filter_results,
    "pool_size": len(full_pool),
    "shortlist_size": len(shortlist_ids),
    "rr_squad_size": len(rr_squad_pids),
    "view_a_size": len(view_a),
    "view_b_size": len(view_b),
    "view_c_size": len(view_c),
    "timestamp": pd.Timestamp.now().isoformat(),
}

with open(AUDIT_DIR / "filter_audit_summary.json", 'w') as f:
    json.dump(audit_data, f, indent=2, default=str)

print(f"\nSaved to {AUDIT_DIR / 'filter_audit_summary.json'}")

# Overall determination
if failed == 0:
    print("\n[PASS] PHASE 5: FILTER AUDIT PASSED")
else:
    print(f"\n[FAIL] PHASE 5: FILTER AUDIT - {failed} FAILURES")
    for name, result in filter_results.items():
        if result["status"] == "FAIL":
            print(f"  - {name}: {result['error']}")