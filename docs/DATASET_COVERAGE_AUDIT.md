# PRESSURE-X 2.0 — DATASET COVERAGE AUDIT REPORT
## Complete Forensic Inventory of All Project Data Assets

**Date:** 2026-11-18  
**Project:** PRESSURE-X | SupeRR Selector Season 2  
**Target:** Rajasthan Royals IPL 2027 Recruitment Intelligence

---

## EXECUTIVE SUMMARY

This audit catalogs **100% of available project datasets** — raw, cleaned, aggregated, and derived — to establish the complete candidate universe for the PRESSURE-X 2.0 recruitment intelligence platform.

**Total Datasets Audited:** 34 files  
**Total Raw Deliveries:** 200,999 ball-by-ball records  
**Total Matches:** 883 matches across 143 competitions  
**Total Players (Raw):** ~2,800 unique player IDs in competition mappings  
**Eligible Candidate Pool (Post-Filters):** 664 players (auction_eligible_player_pool.csv)  
**Official Shortlist:** 28 players (10 batters, 10 bowlers, 8 reserves)  
**RR Current Squad (Retained):** 184 players across 10 franchises  

---

## 1. RAW DATASETS (Source of Truth)

### 1.1 competitions.csv
| Attribute | Value |
|-----------|-------|
| **Rows** | 143 |
| **Columns** | 4 (comp_id, comp_name, match_format, season) |
| **Coverage** | 2022–2026 seasons |
| **Formats** | T20 (IPL, franchise, development), T20I (international) |
| **Primary Keys** | comp_id |
| **Seasons** | 2022, 2023, 2024, 2025, 2026, 2022/23, 2023/24, 2024/25 |
| **Competition Tiers** | Not explicitly labeled — requires tier_mapping.py |

### 1.2 matches.csv
| Attribute | Value |
|-----------|-------|
| **Rows** | 883 (882 matches + header) |
| **Columns** | 22 |
| **Coverage** | All 143 competitions |
| **Primary Keys** | match_id |
| **Foreign Keys** | comp_id → competitions.csv |
| **Key Fields** | match_date, stage, venue, teams, toss, result, win_team_id |
| **Seasons** | 2022–2026 (derived from comp_id → competitions.season) |

### 1.3 teams.csv
| Attribute | Value |
|-----------|-------|
| **Rows** | ~300 (team-competition pairs) |
| **Columns** | 3 (comp_id, team_id, team_name) |
| **Coverage** | All teams in all competitions |
| **Primary Keys** | (comp_id, team_id) |

### 1.4 ball_by_ball.csv
| Attribute | Value |
|-----------|-------|
| **Rows** | 200,999 (200,998 deliveries + header) |
| **Columns** | 30 |
| **Coverage** | All 883 matches |
| **Primary Keys** | (match_id, innings, over_ball_num) |
| **Foreign Keys** | match_id → matches.csv, striker_id/bowler_id → player mappings |
| **Key Metrics** | runs, extras_type, extras1_runs, extras_2_runs, dismissal_type, wicket info, phase info, pace/spin, speed, stroke, delivery style |
| **Raw → Legal Deliveries** | 200,999 → 198,948 legal balls (excludes wides/overstep no-balls) |

### 1.5 playing_eleven.csv
| Attribute | Value |
|-----------|-------|
| **Rows** | 28,382 (28,381 records + header) |
| **Columns** | 8 |
| **Coverage** | All 883 matches × 2 teams × ~11 players |
| **Primary Keys** | (match_id, team_id, player_id) |
| **Key Fields** | batting_order, is_played, is_captain, is_wk, is_impact |
| **Data Quality** | 35 playing eleven conflicts identified in Task 05 |

### 1.6 competition_team_player_mapping.csv
| Attribute | Value |
|-----------|-------|
| **Rows** | 6,414 (6,413 records + header) |
| **Columns** | 6 |
| **Coverage** | All competition-team-player combinations |
| **Primary Keys** | (comp_id, team_id, player_id) |
| **Key Fields** | player_name (alias per competition) |
| **Data Quality** | Name mismatches tracked; player_id is canonical join key |

---

## 2. PROCESSED DATASETS (Derived / Aggregated)

### 2.1 data/processed/all_competition_batter_match_features.csv
| Attribute | Value |
|-----------|-------|
| **Rows** | 13,600 |
| **Columns** | ~80 |
| **Grain** | One row per batter per match per innings |
| **Derived From** | ball_by_ball.csv + match state reconstruction (Task 06) |
| **Key Features** | pressure-classified balls/runs/dismissals/boundaries (low/medium/high/extreme), chase stats, phase stats (powerplay/middle/death), raw rates (SR, dismissal_rate, boundary_pct) |
| **Competition Scope** | All 5 tiers (IPL, T20I FMvFM, T20I FMvAssoc, T20I AssocvAssoc, Other T20) |

### 2.2 data/processed/all_competition_bowler_match_features.csv
| Attribute | Value |
|-----------|-------|
| **Rows** | 9,979 |
| **Columns** | ~100 |
| **Grain** | One row per bowler per match per innings |
| **Derived From** | ball_by_ball.csv + match state reconstruction (Task 06) |
| **Key Features** | pressure-classified balls/runs/wickets/dots/boundaries, defend stats, phase stats, raw rates (economy, wicket_rate, dot_ball_pct, boundary_concession_pct, wickets_per_over) |
| **Bowler Runs Logic** | Wides=extras1, No-balls=runs+extras1, Byes/Legbyes/Penalty=0 |

### 2.3 data/processed/all_competition_batter_season_features.csv
| Attribute | Value |
|-----------|-------|
| **Rows** | 2,226 |
| **Columns** | ~120 |
| **Grain** | One row per batter per season |
| **Derived From** | batter_match_features + Bayesian shrinkage (prior_weight=30) |
| **Key Features** | Season aggregates + shrinkage-adjusted rates (_adj, _comp_adj, _pop_adj_shrunk), reliability flags (min_balls_100/50, min_high_extreme_30, min_chase_30), seasons_played |
| **Competition Adjustment** | Paired-player factors from Task 07B (corrected) |

### 2.4 data/processed/all_competition_bowler_season_features.csv
| Attribute | Value |
|-----------|-------|
| **Rows** | 1,602 |
| **Columns** | ~140 |
| **Grain** | One row per bowler per season |
| **Derived From** | bowler_match_features + Bayesian shrinkage (prior_weight=30) |
| **Key Features** | Season aggregates + shrinkage-adjusted rates, reliability flags (min_balls_100/50, min_high_extreme_30, min_defend_30), seasons_played |

### 2.5 data/processed/ipl_only_*_match/season_features.csv
| File | Rows | Purpose |
|------|------|---------|
| ipl_only_batter_match_features.csv | 5,666 | IPL-only (comp_tier=1) match-level batter features |
| ipl_only_bowler_match_features.csv | 4,307 | IPL-only match-level bowler features |
| ipl_only_batter_season_features.csv | 861 | IPL-only season aggregates (315 eligible batters ≥100 balls) |
| ipl_only_bowler_season_features.csv | 649 | IPL-only season aggregates (313 eligible bowlers ≥100 balls) |

---

## 3. SUPPORTING EVIDENCE / AUDIT OUTPUTS

### 3.1 Player Identity & Eligibility
| File | Rows | Purpose |
|------|------|---------|
| player_identity_traceability.csv | 30 | Maps shortlist IDs to canonical IDs; 3 corrections applied |
| age_verification.csv | 30 | Verified DOB & age as of 2027-04-01 for shortlist; ESPNcricinfo sourced |
| ipl_eligibility_audit.csv | 664 | Full eligibility check: 662 ELIGIBLE, 2 INELIGIBLE (Pakistani), 1 INELIGIBLE_RETIRED |
| retained_players.csv | 184 | Current RR squad + all 10 franchises retained players |
| retained_player_matching_audit.csv | 184 | Verification of retained player matching to dataset IDs |

### 3.2 Candidate Pool & Scoring
| File | Rows | Purpose |
|------|------|---------|
| auction_eligible_player_pool.csv | 664 | Complete eligible universe: player_id, name, role, composite_score, competition_coverage, tiers, origin, auction_rank |
| rr_scouting_priority_scores.csv | 28 | Final 40/30/20/10 RR scouting scores for 10 batters, 10 bowlers, 8 reserves |
| final_combined_top10_batters.csv | 10 | Official verified Top 10 batters |
| final_combined_top10_bowlers.csv | 10 | Official verified Top 10 bowlers |
| final_combined_reserves.csv | 8 | Official verified reserves |

### 3.3 Bowling Evidence & Deployment
| File | Rows | Purpose |
|------|------|---------|
| bowling_zero_opportunity_audit.csv | ~400 | Phase delivery counts; identifies bowlers with 0 death/HE balls |
| evidence_qualified_bowler_comparison.csv | 28 | EQ scores for bowlers with unobserved phases |
| bowling_deployment_validation.csv | 28 | Tactical deployment boundaries for Top 10 bowlers |

### 3.4 Current Form & Validation
| File | Rows | Purpose |
|------|------|---------|
| current_form_source_verification.csv | 30 | 2025-2026 form evidence with source URLs |
| scoring_reproduction.csv | 28 | Score reproduction verification |
| scoring_sensitivity_analysis.csv | — | Sensitivity tests |
| final_eligibility_audit.csv | — | Final eligibility sign-off |
| rr_scouting_selection_audit.csv | — | Selection audit trail |
| final_shortlist_corrections.csv | 5 | 3 player_id corrections + 1 alias verification |

---

## 4. COMPETITION TIER STRUCTURE

| Tier | Competition Type | Examples | Baseline Multiplier (Task 07) |
|------|------------------|----------|-------------------------------|
| 1 | IPL | IPL 2022–2026 | 1.00 (baseline) |
| 2 | T20I Full Member vs Full Member | India vs England, Australia vs NZ | 0.92 (paired) / 1.02 (population) |
| 3 | T20I Full Member vs Associate | India vs Nepal, Afghanistan vs Zimbabwe | 0.84 (paired) / 1.00 (population) |
| 4 | T20I Associate vs Associate | UAE vs Nepal, Scotland vs Canada | 0.76 (default) |
| 5 | Other T20 / Domestic | BBL, PSL, SA20, CPL, SMAT, Vitality Blast | 0.68 (default) |

**Paired-Player Evidence (Task 07B Corrected):**
- T1↔T2: 107 batters, 110 bowlers
- T2↔T3: 104 batters, 108 bowlers  
- T3↔T4: No overlap (factors = 1.0)
- T4↔T5: No overlap (factors = 1.0)

**Population Factors (All Primary Deliveries):**
- T1 vs T2: 154,631 legal balls
- T2 vs T3: 19,298 legal balls

---

## 5. DATA QUALITY & LIMITATIONS

### 5.1 Critical Fixes Applied (Tasks 05–07E)
| Issue | Fix | Validation |
|-------|-----|------------|
| Negative batter runs | Use `runs` column directly (not runs - extras) | 0 negatives across 200K+ deliveries |
| Legal ball definition | `extras_type NOT IN ('wide', 'Overstep')` | 7,735 wides correctly excluded |
| Bowler runs per cricket laws | Wides=extras1, No-balls=runs+extras1, Byes/Legbyes=0 | Validated across all deliveries |
| Bowler wicket credit | Only Bowled/Caught/LBW/Stump/Hit Wicket/Obstructing | Runouts excluded |
| Player identity | Join on player_id only; canonical names from mapping | 3 ID corrections in final_shortlist_corrections.csv |
| Data leakage prevention | Monotonicity checks on pre-delivery state variables | All pass (Task 06) |
| Abandoned matches | 16 identified; sensitivity analysis applied | Handled |
| Innings with 3/4 deliveries | 38 identified | Handled |
| Playing XI conflicts | 35 identified | Resolved in Task 05 |

### 5.2 Remaining Limitations
| Limitation | Impact | Mitigation |
|------------|--------|------------|
| No domestic ball-by-ball data | Domestic metrics unavailable for most players | Clearly flag as "Not Available" |
| No player DOB in raw data | Age from age_verification.csv (shortlist only) | Need to source DOB for full pool |
| No batting/bowling style in raw data | Role classification limited | Use primary_role from mappings |
| No wicketkeeping flag in raw data | WK identification missing | Need external source |
| T3/T4/T5 competition adjustment factors | No paired overlap; defaults used | Document as assumptions |
| Single-season players in Top 10 | 2 bowlers (Agar 2022, Ghazanfar 2022) with minimal pressure data | Flag in reliability audit |

### 5.3 Coverage Gaps
| Domain | Status | Notes |
|--------|--------|-------|
| IPL Ball-by-Ball | Complete | 83,297 legal deliveries (2022–2026) |
| T20I Ball-by-Ball | Complete | All T20I matches in competitions.csv |
| Other T20 (BBL, PSL, etc.) | Partial | Via competition mappings; verify coverage |
| Domestic (SMAT, Ranji, etc.) | Minimal | Only match-level aggregates available |
| Current Form (2025-26) | Shortlist only | 30 players verified; need for full pool |
| Player Metadata (DOB, style, WK) | Shortlist only | 30 players in age_verification.csv |

---

## 6. RECOMMENDED NEXT STEPS FOR PRESSURE-X 2.0

### Phase 1: Build Complete Player Master (Priority 1)
- Create `data/processed/player_master.csv` from competition_team_player_mapping + playing_eleven + age_verification + retained_players
- Enrich with DOB from external source for full 664 eligible players
- Add batting/bowling style, WK status, primary/secondary role

### Phase 2: Build Complete Performance Database (Priority 2)
- Use existing processed season/match features as foundation
- Add domestic performance table from available domestic competition data
- Add current form metrics for all eligible players (not just shortlist)

### Phase 3: Remove Shortlist Restrictions (Priority 3)
- Refactor dashboard data loaders to use auction_eligible_player_pool.csv (664 players)
- Preserve official shortlist as View B (archived benchmark)
- Build View A (complete universe), View C (RR squad), View D (dynamic candidates)

### Phase 4: Dynamic Ranking Engine (Priority 4)
- Implement `src/scoring/dynamic_scouting_engine.py`
- User-configurable weights with normalization
- Missing data policy with evidence reliability flags

### Phase 5: RR Squad Integration (Priority 5)
- Create `data/reference/rr_current_squad.csv` from retained_players.csv (filter RR)
- Build squad gap analysis and player comparison pages

---

## 7. FILE INVENTORY SUMMARY

| Category | Count | Total Rows |
|----------|-------|------------|
| Raw Data | 6 | 236,680 |
| Processed Match Features | 4 | 23,579 |
| Processed Season Features | 4 | 3,828 |
| IPL-Only Features | 4 | 11,483 |
| Supporting Evidence / Audit | 16 | ~2,500 |
| **TOTAL** | **34** | **~278,000** |

---

*Report generated by PRESSURE-X Pipeline — Dataset Coverage Audit*