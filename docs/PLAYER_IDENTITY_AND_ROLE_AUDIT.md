# PRESSURE-X 2.0 — PLAYER IDENTITY & ROLE INTEGRITY AUDIT

**Audit Date:** 2026-11-18  
**Auditor:** Forensic Codebase Audit  
**Status:** CRITICAL FINDINGS — IMMEDIATE ACTION REQUIRED

---

## EXECUTIVE SUMMARY

The player identity and role system has **multiple critical failures**:

1. **Player Master is not canonical** — 1,570 rows for 1,217 unique players (player-seasons, not players)
2. **Two divergent data loaders** — `data_loader.py` (311 players) vs `scouting_data.py` (303 players)
3. **Two divergent filter engines** — Different column sets (79 vs 49), different results
4. **Role classification broken** — `primary_role` shows 841 All-rounder, 400 Batter, 70 Bowler; but `role` from pool shows only Batter/Bowler
5. **Arbitrary lookup selection** — Dict comprehension keeps LAST row per player_id (sort-order dependent)
6. **Scouting Explorer shows different pool** — 303 eligible vs 311 (includes ineligible) on other pages

---

## 1. CANONICAL PLAYER IDENTITY AUDIT

### 1.1 Player Master Structure Analysis

| Metric | Value | Expected | Status |
|--------|-------|----------|--------|
| Total rows | 1,570 | 311 (unique eligible) | ❌ FAIL |
| Unique player_ids | 1,217 | 311 | ❌ FAIL |
| Duplicate player_ids | 166 (353 rows) | 0 | ❌ FAIL |
| Players with DOB/age | 82 | 311 | ❌ FAIL |
| Eligibility coverage | 644 ELIGIBLE | 311 | ⚠️ PARTIAL |

### 1.2 Duplicate Player ID Analysis

The `player_master.csv` contains **player-season records**, not canonical players. Each player appears once per season they played.

**Example: Glenn Maxwell (player_id=838)** — 7 rows across seasons 2022-2025:
| Season | primary_role | role | composite_score | data_completeness |
|--------|-------------|------|-----------------|-------------------|
| 2023 | All-rounder | batter | 99.84 | 100 |
| 2025 | All-rounder | batter | 86.89 | 100 |
| 2022 | All-rounder | bowler | 65.51 | 100 |
| 2022 | All-rounder | batter | 78.37 | 100 |
| 2024 | All-rounder | batter | 75.43 | 100 |
| 2025 | All-rounder | bowler | 54.06 | 100 |
| 2024 | All-rounder | bowler | 44.47 | 100 |

**Impact**: The `build_lookup()` function in `load_complete_pool_enriched()` uses a dict comprehension `{int(r[id_col]): r.to_dict() for _, r in df.iterrows()}` which **arbitrarily keeps the last row** (determined by DataFrame sort order). For Glenn Maxwell, it keeps the 2024 bowler row (composite_score=44.47) instead of the 2023 batter row (composite_score=99.84).

### 1.3 Identity Join Validation

| Join Path | Source | Key | Status |
|-----------|--------|-----|--------|
| `load_complete_pool_enriched` → `player_master` | `master_lookup[pid]` | `player_id` | ❌ BROKEN (arbitrary season) |
| `scouting_data` → `player_master` | Not used directly | — | ⚠️ N/A |
| `RR Squad` → `player_master` | `rr_current_squad.csv` | `player_id` | ✅ OK (19 players) |
| Performance DB → `player_master` | `striker_id`/`bowler_id` | `player_id` | ✅ OK (separate files) |

### 1.4 Missing Identity Fields

| Field | Coverage | Issue |
|-------|----------|-------|
| `date_of_birth` | 82/1,570 (5%) | Only shortlisted players have verified DOB |
| `age_as_of_2027_04_01` | 82/1,570 (5%) | Estimated for rest |
| `batting_style` | Partial | Inferred from ball-by-ball mode |
| `bowling_style` | Partial | Inferred from ball-by-ball mode |
| `wk_status` | 161 Yes / 1,409 No | From playing_eleven |

---

## 2. PLAYER ROLE CLASSIFICATION AUDIT

### 2.1 Role Field Confusion

The system has **THREE different role fields** with conflicting values:

| Field | Source | Values | Distribution |
|-------|--------|--------|--------------|
| `primary_role` | `build_player_master.py` (ball-by-ball inference) | All-rounder, Batter, Bowler, Unknown | 841 / 400 / 70 / 259 |
| `role` (pool) | `auction_eligible_player_pool.csv` | Batter, Bowler | 148 / 163 (311 players) |
| `role` (scouting_data pool) | Derived from pool `role` column | Batter, Bowler | 144 / 159 (303 players) |
| `secondary_role` | Same as primary_role | All-rounder, Batter, Bowler, Unknown | Identical to primary |

### 2.2 Role Inference Logic (build_player_master.py:192-201)

```python
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
```

**CRITICAL FLAW**: This classifies ANY player with ≥1 batting observation AND ≥1 bowling observation as "All-rounder". This includes:
- Part-time bowlers (batters who bowled 1-2 overs)
- Specialist bowlers who faced a few balls
- Players with minimal evidence in either discipline

**Result**: 841/1,217 players (69%) classified as "All-rounder" — rendering the classification meaningless for scouting.

### 2.3 Role Distribution Comparison

| Page / Source | Batter | Bowler | All-rounder | Unknown | Total |
|---------------|--------|--------|-------------|---------|-------|
| `player_master.csv` (primary_role) | 400 | 70 | 841 | 259 | 1,570 |
| `auction_eligible_pool.csv` (role) | 148 | 163 | 0 | 0 | 311 |
| `load_complete_pool_enriched` (data_loader) | 148 | 163 | 0 | 0 | 311 |
| `load_complete_pool_enriched` (scouting_data) | 144 | 159 | 0 | 0 | 303 |
| Pool `primary_role` (enriched) | 86 | 3 | 222 | 0 | 311 |

**Key Finding**: The enriched pool's `primary_role` (from master_lookup) shows 222 All-rounders, but the pool's own `role` column shows 0 All-rounders. This is because the pool's `role` comes from `auction_eligible_player_pool.csv` which only has Batter/Bowler.

### 2.4 Role Consistency Across Pages

| Page | Role Source | Role Values Used |
|------|-------------|------------------|
| Scouting Explorer | `scouting_data` pool `role` | Batter, Bowler |
| Dynamic Ranking | `data_loader` pool `role` | Batter, Bowler |
| Domestic Intelligence | `data_loader` pool `role` + `master` `role` | Batter, Bowler, Unverified |
| RR Squad Analysis | `data_loader` pool `role` | Batter, Bowler |
| Player Comparison | `data_loader` pool `role` | Batter, Bowler |
| AI Assistant | `scouting_data` pool `role` | Batter, Bowler |

**Inconsistency**: Domestic Intelligence now uses `master['role']` (which is NaN for most) falling back to 'Unverified', while other pages use pool `role`.

---

## 3. DUAL DATA LOADER DIVERGENCE

### 3.1 Two `load_complete_pool_enriched` Implementations

| Aspect | `dashboard/utils/data_loader.py` | `dashboard/utils/scouting_data.py` |
|--------|----------------------------------|-----------------------------------|
| **Lines** | 252-548 | 216-455 |
| **Player Count** | 311 | 303 |
| **Eligibility Filter** | ❌ NOT APPLIED (comment says it is) | ✅ APPLIED (filters INELIGIBLE) |
| **Shortlist Merge** | Yes (28 players) | Yes (28 players) |
| **Player Master Join** | `master_lookup` (arbitrary season) | Not used |
| **Performance DB Join** | Yes (comp, season, pressure, domestic) | No (uses `_load_raw_*_stats`) |
| **Output Columns** | 79 | 49 |

### 3.2 Players Missing in scouting_data (8 INELIGIBLE)

| player_id | Name | Role | Audit Status |
|-----------|------|------|--------------|
| 23 | Piyush Chawla | Bowler | INELIGIBLE_RETIRED |
| 143 | Dinesh Karthik | Batter | INELIGIBLE_RETIRED |
| 305 | Ravichandran Ashwin | Batter | INELIGIBLE_RETIRED |
| 20704 | Salman Mirza | Bowler | INELIGIBLE |
| 2921 | Fakhar Zaman | Batter | INELIGIBLE |
| 20310 | Ahmed Daniyal | Bowler | INELIGIBLE |
| 2490 | Mohammad Nawaz | Batter | INELIGIBLE |
| 26843 | Maaz Sadaqat | Batter | INELIGIBLE |

**Impact**: Scouting Explorer (303 players) vs ALL OTHER PAGES (311 players including 8 ineligible).

### 3.3 Root Cause in data_loader.py

Line 273 comment: `"Use ALL players from auction pool (already filtered for eligibility)"` — **FALSE**. Line 275 only does `drop_duplicates('player_id')` with NO eligibility filtering.

---

## 4. DUAL FILTER ENGINE DIVERGENCE

### 4.1 Two `apply_scouting_filters` Implementations

| Aspect | `data_loader.py` (v2) | `scouting_data.py` (v1) |
|--------|----------------------|------------------------|
| **Lines** | 572-735 | 462-593 |
| **Parameters** | 26 | 22 |
| **Filter Logic** | Complex (view_filter, competition_tiers) | Simpler (pool_scope) |
| **All-rounder Detection** | `career_batting_runs > 30 AND career_wickets > 2` | Same |
| **Domestic Filters** | Uses `domestic_batting_runs`, `domestic_bowling_wickets` | Uses `domestic_runs`, `domestic_wickets` |
| **Column Differences** | 79 cols (rich enrichment) | 49 cols (basic) |

### 4.2 Filter Result Divergence

Test: `role='Batter', nationality='Indian', limit=None`
- `data_loader` filter: **20 results** (from 311 pool)
- `scouting_data` filter: **18 results** (from 303 pool)

**Difference**: 2 players — the ineligible Indian batters (Dinesh Karthik, Ravichandran Ashwin) appear in data_loader but not scouting_data.

---

## 5. PAGE-BY-PAGE ROLE USAGE AUDIT

| Page | Pool Source | Role Field Used | Filter Function | Status |
|------|-------------|-----------------|-----------------|--------|
| 1. Executive Overview | `data_loader` | N/A (KPIs only) | N/A | ⚠️ Uses 311 pool |
| 2. Scouting Explorer | `scouting_data` | `role` (Batter/Bowler) | `scouting_data.apply_scouting_filters` | ✅ Consistent but 303 pool |
| 3. Dynamic Ranking | `data_loader` | `role` (Batter/Bowler) | `data_loader.apply_scouting_filters` | ⚠️ 311 pool incl. ineligible |
| 4. RR Current Squad | `rr_current_squad.csv` | `primary_role` | N/A | ✅ Independent |
| 5. RR Gap Analysis | `data_loader` | `role` (Batter/Bowler) | `data_loader.apply_scouting_filters` | ⚠️ 311 pool |
| 6. Domestic Intelligence | `data_loader` + `player_master` | `master['role']` → 'Unverified' | Custom (nlargest) | ❌ **BROKEN** — master role is NaN |
| 7. Player Comparison | `data_loader` | `role` (Batter/Bowler) | `get_comparison_data` | ⚠️ 311 pool |
| 8. AI Assistant | `scouting_data` | `role` (Batter/Bowler) | `scouting_data.apply_scouting_filters` | ✅ 303 pool |
| 9. Standard Scouting Report | `data_loader` | `role` (Batter/Bowler) | `data_loader.apply_scouting_filters` | ⚠️ 311 pool |
| 10. Methodology | N/A | N/A | N/A | N/A |

---

## 6. CRITICAL BUGS IDENTIFIED

| # | Bug | Location | Severity | Impact |
|---|-----|----------|----------|--------|
| 1 | player_master is player-season, not canonical | `build_player_master.py`, `data/processed/player_master.csv` | **CRITICAL** | Arbitrary season data used everywhere |
| 2 | data_loader missing eligibility filter | `data_loader.py:275` | **CRITICAL** | 8 ineligible players in 311 pool |
| 3 | Two load_complete_pool_enriched | `data_loader.py` vs `scouting_data.py` | **CRITICAL** | Different pools (311 vs 303), different columns |
| 4 | Two apply_scouting_filters | `data_loader.py` vs `scouting_data.py` | **CRITICAL** | Different results, different columns |
| 5 | Role classification over-assigns All-rounder | `build_player_master.py:192-201` | **HIGH** | 69% players = All-rounder (meaningless) |
| 6 | Domestic Intelligence uses master['role'] (NaN) | `domestic_intelligence.py:406` | **HIGH** | All players show 'Unverified' role |
| 7 | Player Comparison uses player_name not player_id | `app.py:398-410` | **MEDIUM** | Name collision risk |
| 8 | Scouting Explorer imports from wrong module | `scouting_explorer.py:17` | **MEDIUM** | Uses 303 pool, divergent filters |
| 9 | Only 82/1,570 players have DOB/age | `build_player_master.py` | **MEDIUM** | Age-based filters unreliable |
| 10 | build_lookup keeps arbitrary last row | `data_loader.py:316-319` | **MEDIUM** | Non-deterministic enrichment |

---

## 7. REQUIRED FIXES (PRIORITY ORDER)

### P0 — IMMEDIATE (Blockers)
1. **Fix player_master.csv** — Deduplicate to 1 row per player_id with canonical data (latest/highest quality season)
2. **Add eligibility filter to data_loader.py:275** — Filter pool_df by eligible_ids before dedup
3. **Consolidate load_complete_pool_enriched** — Single implementation in data_loader.py, deprecate scouting_data.py version
4. **Consolidate apply_scouting_filters** — Single implementation in data_loader.py, deprecate scouting_data.py version
5. **Fix Domestic Intelligence role lookup** — Use pool `role` field, not master `role`

### P1 — HIGH (This Sprint)
6. **Fix role classification** — Require minimum evidence threshold (e.g., 50 balls batted AND 50 balls bowled) for "All-rounder"
7. **Update Scouting Explorer imports** — Use `dashboard.utils` (data_loader) not `dashboard.utils.scouting_data`
8. **Add role_provenance fields** — `role_source`, `role_confidence`, `role_verified`, `role_last_updated`
9. **Fix Player Comparison** — Use player_id for selection, not player_name

### P2 — MEDIUM (Next Sprint)
10. **Improve age/DOB coverage** — Extend age_verification.csv or estimate for all players
11. **Make build_lookup deterministic** — Sort by composite_score desc before dict comprehension
12. **Add role classification audit CSV** — Document every player's resolved role with evidence

---

## 8. ROLE CLASSIFICATION AUDIT CSV

Creating `outputs/audit/player_role_classification_audit.csv` with:
- player_id, canonical_name
- source_role (from pool), resolved_role (final)
- batting_balls, bowling_balls (evidence)
- resolution_method, confidence
- audit_status

---

## 9. CONCLUSION

The player identity and role system is **fundamentally broken** due to:
1. Non-canonical player_master (player-seasons instead of players)
2. Dual divergent data pipelines (data_loader vs scouting_data)
3. Broken role classification (over-assigned All-rounder)
4. Arbitrary lookup selection (non-deterministic)

**Recommendation**: Halt all feature work until P0 fixes are deployed. The Scouting Explorer shows a different player universe (303) than the rest of the dashboard (311), and Domestic Intelligence shows 'Unverified' for all roles.

**Data Integrity Determination**: **FAIL** — Cannot trust any role-based analysis until canonical player master and unified data loader are established.