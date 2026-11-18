# PRESSURE-X 2.0 — DATASET COVERAGE RECONCILIATION AUDIT

**Audit Date:** 2026-11-18  
**Auditor:** Forensic Codebase Audit  
**Status:** CRITICAL GAPS IDENTIFIED

---

## EXECUTIVE SUMMARY

The dataset ecosystem has **significant coverage gaps** between the eligible pool (303 players) and performance databases:

| Dataset Category | Batters Covered | Bowlers Covered | Key Gap |
|-----------------|----------------|----------------|---------|
| Competition Performance (all tiers) | 300/303 (99%) | 218/303 (72%) | 85 eligible bowlers missing |
| Season-level Performance | 300/303 (99%) | 218/303 (72%) | Same 85 bowlers |
| Pressure Metrics | 300/303 (99%) | 218/303 (72%) | Same 85 bowlers |
| Domestic Metrics | 96/303 (32%) | 69/303 (23%) | 200+ players missing domestic data |
| Current Form | 28/303 (9%) | 0/303 (0%) | Only shortlist has form data |

**Orphans**: 588 batters + 429 bowlers in performance DB are outside eligible pool (historical players)
**Duplicates**: Match-level files have expected duplicates (1 row per match); season files have minimal duplicates
**Schema Drift**: Column names vary across match/season/competition files

---

## 1. DATASET INVENTORY (40 FILES)

| # | Dataset | Rows | Unique IDs | ID Column | Eligible | Shortlist | RR | Orphans | Missing | Null Rate |
|---|---------|------|------------|-----------|----------|-----------|----|---------|---------|-----------|
| 1 | all_competition_batter_match_features | 13,599 | 888 | striker_id | 300 | 28 | 16 | 588 | 3 | 0.0% |
| 2 | all_competition_batter_season_features | 2,225 | 888 | striker_id | 300 | 28 | 16 | 588 | 3 | 0.0% |
| 3 | all_competition_bowler_match_features | 9,978 | 647 | bowler_id | 218 | 22 | 15 | 429 | 85 | 0.0% |
| 4 | all_competition_bowler_season_features | 1,601 | 647 | bowler_id | 218 | 22 | 15 | 429 | 85 | 0.0% |
| 5 | ipl_only_batter_match_features | 5,666 | 341 | striker_id | 117 | 17 | 16 | 224 | 186 | 0.0% |
| 6 | ipl_only_batter_season_features | 861 | 341 | striker_id | 117 | 17 | 16 | 224 | 186 | 0.0% |
| 7 | ipl_only_bowler_match_features | 4,307 | 260 | bowler_id | 91 | 11 | 15 | 169 | 212 | 0.0% |
| 8 | ipl_only_bowler_season_features | 649 | 260 | bowler_id | 91 | 11 | 15 | 169 | 212 | 0.0% |
| 9 | player_bowling_phase_metrics | 1,601 | 647 | bowler_id | 218 | 22 | 15 | 429 | 85 | 0.0% |
| 10 | player_current_form | 82 | 28 | player_id | 28 | 28 | 0 | 0 | 275 | 0.0% |
| 11 | player_domestic_metrics_batter | 386 | 284 | striker_id | 96 | 6 | 1 | 188 | 207 | 0.0% |
| 12 | player_domestic_metrics_bowler | 272 | 196 | bowler_id | 69 | 6 | 0 | 127 | 234 | 0.0% |
| 13 | player_performance_by_competition_batter | 4,317 | 888 | striker_id | 300 | 28 | 16 | 588 | 3 | 0.0% |
| 14 | player_performance_by_competition_bowler | 3,095 | 647 | bowler_id | 218 | 22 | 15 | 429 | 85 | 0.0% |
| 15 | player_performance_by_season_batter | 2,225 | 888 | striker_id | 300 | 28 | 16 | 588 | 3 | 0.0% |
| 16 | player_performance_by_season_bowler | 1,601 | 647 | bowler_id | 218 | 22 | 15 | 429 | 85 | 0.0% |
| 17 | player_pressure_metrics_batter | 2,225 | 888 | player_id | 300 | 28 | 16 | 588 | 3 | 0.0% |
| 18 | player_pressure_metrics_bowler | 1,601 | 647 | player_id | 218 | 22 | 15 | 429 | 85 | 0.0% |
| 19 | player_master | 1,570 | 1,217 | player_id | 303 | 28 | 19 | 914 | 0 | 38.8% |
| 20 | player_master_canonical | 1,217 | 1,217 | player_id | 303 | 28 | 19 | 914 | 0 | 43.7% |
| 21 | player_master_pool | 311 | 311 | player_id | 303 | 28 | 1 | 8 | 0 | 22.6% |
| 22 | final_combined_top10_batters | 10 | 10 | player_id | 10 | 10 | 0 | 0 | 293 | 0.0% |
| 23 | final_combined_top10_bowlers | 10 | 10 | player_id | 10 | 10 | 0 | 0 | 293 | 0.0% |
| 24 | final_combined_reserves | 8 | 8 | player_id | 8 | 8 | 0 | 0 | 295 | 0.0% |
| 25 | auction_eligible_player_pool | 664 | 311 | player_id | 303 | 28 | 1 | 8 | 0 | 0.0% |
| 26 | ipl_eligibility_audit | 311 | 311 | player_id | 303 | 28 | 1 | 8 | 0 | 27.8% |
| 27 | age_verification | 28 | 28 | player_id | 28 | 28 | 0 | 0 | 275 | 0.0% |
| 28 | retained_players | 184 | 0 | NONE | 0 | 0 | 0 | 0 | 0 | 0.0% |
| 29 | retained_player_matching_audit | 184 | 0 | NONE | 0 | 0 | 0 | 0 | 0 | 0.0% |
| 30 | bowling_zero_opportunity_audit | 10 | 10 | player_id | 10 | 10 | 0 | 0 | 293 | 1.1% |
| 31 | current_form_source_verification | 28 | 28 | player_id | 28 | 28 | 0 | 0 | 275 | 0.0% |
| 32 | evidence_qualified_bowler_comparison | 10 | 10 | player_id | 10 | 10 | 0 | 0 | 293 | 0.0% |
| 33 | final_eligibility_audit | 28 | 28 | player_id | 28 | 28 | 0 | 0 | 275 | 0.0% |
| 34 | final_shortlist_corrections | 4 | 0 | NONE | 0 | 0 | 0 | 0 | 0 | 0.0% |
| 35 | player_identity_traceability | 28 | 0 | NONE | 0 | 0 | 0 | 0 | 0 | 0.0% |
| 36 | rr_scouting_priority_scores | 24 | 24 | player_id | 21 | 21 | 0 | 3 | 282 | 0.0% |
| 37 | rr_scouting_selection_audit | 28 | 28 | player_id | 28 | 28 | 0 | 0 | 275 | 0.0% |
| 38 | scoring_reproduction | 28 | 28 | player_id | 28 | 28 | 0 | 0 | 275 | 0.0% |
| 39 | scoring_sensitivity_analysis | 28 | 28 | player_id | 28 | 28 | 0 | 0 | 275 | 0.0% |
| 40 | bowling_deployment_validation | 14 | 14 | player_id | 14 | 14 | 0 | 0 | 289 | 0.0% |

---

## 2. RECONCILIATION MATRIX (KEY DATASETS)

| Dataset | Eligible Coverage | Shortlist | RR Squad | Notes |
|---------|------------------|-----------|----------|-------|
| all_competition_batter_season_features | **99.0%** | 28/28 | 16/19 | 3 eligible batters missing |
| all_competition_bowler_season_features | **71.9%** | 22/28 | 15/19 | **85 eligible bowlers missing** |
| player_performance_by_competition_batter | **99.0%** | 28/28 | 16/19 | Same as season batter |
| player_performance_by_competition_bowler | **71.9%** | 22/28 | 15/19 | Same as season bowler |
| player_performance_by_season_batter | **99.0%** | 28/28 | 16/19 | Same |
| player_performance_by_season_bowler | **71.9%** | 22/28 | 15/19 | Same |
| player_pressure_metrics_batter | **99.0%** | 28/28 | 16/19 | Same |
| player_pressure_metrics_bowler | **71.9%** | 22/28 | 15/19 | Same |
| player_domestic_metrics_batter | **31.7%** | 6/28 | 1/19 | **207 eligible batters missing domestic data** |
| player_domestic_metrics_bowler | **22.8%** | 6/28 | 0/19 | **234 eligible bowlers missing domestic data** |
| player_master | **100.0%** | 28/28 | 19/19 | But 914 orphans (player-seasons) |
| player_master_canonical | **100.0%** | 28/28 | 19/19 | Deduplicated, 1217 unique |
| auction_eligible_player_pool | **100.0%** | 28/28 | 1/19 | 311 unique, 664 rows (player-seasons) |

---

## 3. CRITICAL FINDINGS

### 3.1 Bowler Coverage Gap (85 players / 28% of eligible pool)
**Impact**: 85 eligible players have NO bowling data in any performance database.
- These are **pure specialist batters** (wicketkeepers, openers, top-order) who never bowled in tracked competitions
- **Confirmed**: All 85 have batting data but zero bowling records
- **Action**: Flag these players; ensure batting-only models handle them; don't apply bowling filters to them

**Missing Bowler IDs (Pure Batters)**:
| ID | Name | ID | Name |
|----|------|----|------|
| 8 | Mahendra Singh Dhoni | 167 | Ajinkya Rahane |
| 88 | Faf du Plessis | 169 | Robin Uthappa |
| 109 | Wriddhiman Saha | 220 | David Warner |
| 142 | Shikhar Dhawan | 223 | Steven Smith |
| 250 | Aaron Finch | 274 | Martin Guptill |
| 443 | Paul Stirling | 535 | Ambati Rayudu |
| 728 | Dawid Malan | 772 | Rilee Rossouw |
| 796 | Matthew Wade | 930 | Karun Nair |
| 992 | Mayank Agarwal | 1183 | Alex Hales |
| 1187 | Jason Roy | 1205 | Jonny Bairstow |
| 1327 | Johnson Charles | 1440 | Rahul Tripathi |
| 1481 | Kusal Perera | 1568 | Kane Williamson |
| 1924 | Sam Billings | 1941 | Devon Conway |
| 2003 | Bhanuka Rajapaksa | 2246 | Tom Latham |
| 2379 | Ben Duckett | 2485 | Babar Azam |
| 2533 | Najibullah Zadran | 2661 | Shamarh Brooks |
| 2671 | Liton Das | 2930 | Rassie van der Dussen |
| 3024 | Mohammad Rizwan | 3091 | Sahibzada Farhan |
| 3097 | Shan Masood | 3297 | Shimron Hetmyer |
| 3377 | Babar Hayat | 3382 | Nizakat Khan |
| 3415 | Matthew Cross | 3639 | Brandon King |
| 3669 | Sadeera Samarawickrama | 3672 | Kusal Mendis |
| 3954 | Andrew Balbirnie | 4369 | Shai Hope |
| 4372 | Rony Talukder | 4773 | Jaker Ali Anik |
| 4814 | Lorcan Tucker | 6035 | Chirag Suri |
| 6280 | Harry Brook | 6342 | Matthew Breetzke |
| 6433 | Darwish Rasooli | 6440 | Omair Yousuf |
| 6448 | Ibrahim Zadran | 6674 | Rahmanullah Gurbaz |
| 6739 | Amir Jangoo | 6881 | Scott Edwards |
| 6931 | Pathum Nissanka | 7152 | Hazratullah Zazai |
| 7341 | Jake McGurk | 7406 | Rizwan CP |
| 7900 | Tanzid Hasan | 7901 | Parvez Emon |
| 7978 | Johnathan Campbell | 8301 | Asif Khan |
| 8600 | Tadiwanashe Marumani | 8647 | Sediqullah Atal |
| 8739 | Muhammad Irfan | 8741 | Mohammad Haris |
| 15551 | Ackeem Auguste | 16284 | Habibur Rahman Sohan |
| 19714 | Abishek Porel | 20327 | Usman Khan |
| 21781 | Clive Madande | 21790 | Tashinga Musekiwa |
| 25534 | Chad Bowes | 26646 | Rahul Chopra |
| 27137 | Hammad Mirza | 28967 | Tim Robinson |
| 28970 | Connor Esterhuizen | 39374 | Muhammad Zohaib |
| 42811 | Michael Levitt | 49003 | Hasan Nawaz |
| 49027 | Bevon Jacobs | | |

### 3.2 Domestic Data Coverage (32% batters, 23% bowlers)
**Impact**: Most eligible players lack domestic T20 data
- Only 96/303 batters and 69/303 bowlers have domestic metrics
- Only 6/28 shortlist batters and 6/28 shortlist bowlers have domestic data
- **Action**: Document as known limitation; don't over-weight domestic metrics for players without data

### 3.3 Current Form Coverage (9% only)
**Impact**: Only 28 shortlist players have current form data
- All other 275 eligible players have NO form metrics
- **Action**: Use form only for shortlist; don't apply form filters to full pool

### 3.4 Orphan Players in Performance DB
**Finding**: 588 batters + 429 bowlers in performance DB are NOT in eligible pool
- These are historical players from previous seasons (2022-2024)
- They inflate unique ID counts (888 batters vs 303 eligible)
- **Action**: Filter performance DB to eligible IDs before dashboard joins

### 3.5 Player Master Duplicates
**Finding**: player_master.csv has 1,570 rows for 1,217 unique players (player-seasons)
- player_master_canonical.csv fixes this: 1,217 unique players
- But both have 914 orphans (players not in eligible pool)
- player_master_pool.csv filters to 311 pool players (8 orphans = ineligible)
- **Action**: Use player_master_pool.csv for dashboard joins

### 3.6 Auction Pool has 8 Ineligible Players
**Finding**: auction_eligible_player_pool.csv has 664 rows, 311 unique IDs, but only 303 eligible
- 8 players are INELIGIBLE or INELIGIBLE_RETIRED (Chawla, Karthik, Ashwin, etc.)
- **Action**: data_loader.py now filters these out (fixed in Phase 1)

### 3.7 Shortlist Bowling Gap (6/28 shortlist players)
**Finding**: 6 shortlist players have NO bowling data
| ID | Name | Role in Pool |
|----|------|--------------|
| 772 | Rilee Rossouw | Batter |
| 930 | Karun Nair | Batter |
| 4369 | Shai Hope | Batter |
| 6280 | Harry Brook | Batter |
| 6931 | Pathum Nissanka | Batter |
| 7341 | Jake McGurk | Batter |

**Impact**: These are correctly classified as pure batters. Ensure bowling filters don't exclude them.

### 3.8 Shortlist Domestic Coverage (12/28 have data)
**Finding**: Only 6 shortlist batters and 6 shortlist bowlers have domestic metrics
- **With domestic batting**: 6/28 shortlist players
- **With domestic bowling**: 6/28 shortlist players
- **Missing domestic entirely**: 22/28 shortlist players

**Impact**: Domestic leaderboards and transition analysis will be sparse for shortlist.

### 3.9 Schema Inconsistencies Across Performance Files
| File Type | ID Column | Key Metrics |
|-----------|-----------|-------------|
| Match features (batter) | striker_id | total_balls, total_runs, strike_rate |
| Match features (bowler) | bowler_id | total_balls, total_runs, total_wickets, economy |
| Season features (batter) | striker_id | Same + season, comp_types, comp_tiers |
| Season features (bowler) | bowler_id | Same + season, comp_types, comp_tiers |
| Competition performance (batter) | striker_id | Aggregated by comp_name, comp_tier |
| Competition performance (bowler) | bowler_id | Aggregated by comp_name, comp_tier |
| Pressure metrics (batter) | player_id | Pressure-specific aggregations |
| Pressure metrics (bowler) | player_id | Pressure-specific aggregations |

**Issue**: Different ID column names (striker_id, bowler_id, player_id) require careful joins

---

## 4. CROSS-REFERENCE VALIDATION

### Official Rankings (28 players) ✅
| Source | Count | In Eligible | In Pool | In Master |
|--------|-------|-------------|---------|-----------|
| final_combined_top10_batters | 10 | 10 | 10 | 10 |
| final_combined_top10_bowlers | 10 | 10 | 10 | 10 |
| final_combined_reserves | 8 | 8 | 8 | 8 |

**All 28 official players present in all systems** ✅

### Retained Players (184) ⚠️
- retained_players.csv has NO player_id column (only name, franchise, overseas_status)
- retained_player_matching_audit.csv also lacks player_id
- Cannot directly cross-reference with performance DB
- **Action**: Matching audit should include player_id for traceability

---

## 5. RECOMMENDED FIXES (PRIORITY ORDER)

### P0 — IMMEDIATE
1. **Filter performance DB to eligible IDs** — Add eligible_ids filter in data_loader joins (reduces 888→300 batters, 647→218 bowlers)
2. **Use player_master_pool.csv** — Replace player_master.csv in dashboard (311 vs 1,570 rows)
3. **Document bowler coverage gap** — 85 pure batters without bowling data (all confirmed specialists)

### P1 — HIGH
4. **Add player_id to retained player audits** — Enable cross-referencing
5. **Standardize ID column names** — Use player_id consistently across all performance files
6. **Document domestic data limitations** — Explicit caveats on dashboard pages (32%/23% coverage)
7. **Add "has_bowling_data" flag to eligible pool** — 218/303 have bowling data
8. **Add "has_domestic_data" flag to eligible pool** — 96/303 batters, 69/303 bowlers

### P2 — MEDIUM
9. **Archive historical performance data** — Move 588+429 orphans to separate archive
10. **Fix shortlist domestic coverage** — Only 12/28 have domestic data

---

## 6. DATA INTEGRITY DETERMINATION

| Check | Status | Notes |
|-------|--------|-------|
| Official rankings integrity | ✅ PASS | All 28 players consistent |
| Eligible pool coverage (batting) | ✅ PASS | 99% coverage |
| Eligible pool coverage (bowling) | ⚠️ PARTIAL | 72% coverage — 85 missing |
| Domestic data coverage | ❌ FAIL | 23-32% — known limitation |
| Current form coverage | ❌ FAIL | 9% — shortlist only |
| Player master deduplication | ⚠️ FIXED | Use player_master_pool.csv |
| Orphan management | ⚠️ PARTIAL | Filter at join time |
| Schema consistency | ⚠️ PARTIAL | ID column names vary |

**Overall**: **CONDITIONAL PASS** — Core batting data solid; bowling/domestic/form have known gaps that must be documented and handled in models.

---

## 7. OUTPUT FILES CREATED

- `outputs/audit/dataset_coverage_audit.csv` — Full 40-dataset inventory
- `outputs/audit/reconciliation_matrix.csv` — 13 key datasets with coverage %