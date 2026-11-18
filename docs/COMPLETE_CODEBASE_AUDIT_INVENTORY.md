# PRESSURE-X 2.0 — COMPLETE CODEBASE AUDIT INVENTORY

**Project:** SupeRR Selector 2027  
**Repository:** https://github.com/kapil31jangid/SupeRR-Selector  
**Branch:** main  
**Audit Date:** 2026-11-18  
**Latest Commit:** 169ddc2 (Domestic Intelligence leaderboard fix)

---

## 1. REPOSITORY STRUCTURE

```
SupeRR-Selector-2027/
├── app.py                                    # Main Streamlit entry point (10-page navigation)
├── requirements.txt                          # 8 dependencies
├── .python-version                           # Python 3.11 pin for Streamlit Cloud
├── .streamlit/secrets.toml                   # API keys (gitignored)
├── .claude/settings.local.json               # Local permissions
├── README.md                                 # Project documentation
├── DATA_DICTIONARY.md                        # Data field definitions
├── data/
│   ├── raw/                                  # 6 raw CSV files
│   │   ├── ball_by_ball.csv                  # 200K+ deliveries
│   │   ├── competition_team_player_mapping.csv
│   │   ├── competitions.csv                  # 5-tier competition definitions
│   │   ├── matches.csv
│   │   ├── playing_eleven.csv
│   │   └── teams.csv
│   ├── processed/                            # 15+ processed CSV files
│   │   ├── player_master.csv                 # 1,570 canonical players
│   │   ├── player_performance_by_competition_batter.csv   # 4,317 records
│   │   ├── player_performance_by_competition_bowler.csv   # 3,095 records
│   │   ├── player_performance_by_season_batter.csv        # 2,226 records
│   │   ├── player_performance_by_season_bowler.csv        # 1,602 records
│   │   ├── player_pressure_metrics_batter.csv
│   │   ├── player_pressure_metrics_bowler.csv
│   │   ├── player_domestic_metrics_batter.csv
│   │   ├── player_domestic_metrics_bowler.csv
│   │   ├── player_bowling_phase_metrics.csv
│   │   ├── player_current_form.csv
│   │   ├── all_competition_batter_season_features.csv
│   │   ├── all_competition_bowler_season_features.csv
│   │   ├── all_competition_batter_match_features.csv
│   │   ├── all_competition_bowler_match_features.csv
│   │   ├── ipl_only_batter_season_features.csv
│   │   ├── ipl_only_bowler_season_features.csv
│   │   ├── ipl_only_batter_match_features.csv
│   │   └── ipl_only_bowler_match_features.csv
│   └── reference/
│       └── rr_current_squad.csv              # 19 retained RR players
├── outputs/
│   ├── official_reference/                   # Immutable View B deliverables
│   │   ├── final_combined_top10_batters.csv
│   │   ├── final_combined_top10_bowlers.csv
│   │   └── final_combined_reserves.csv
│   └── supporting_evidence/                  # 15+ audit CSV files
│       ├── rr_scouting_priority_scores.csv
│       ├── evidence_qualified_bowler_comparison.csv
│       ├── bowling_deployment_validation.csv
│       ├── current_form_source_verification.csv
│       ├── retained_players.csv
│       ├── ipl_eligibility_audit.csv
│       ├── auction_eligible_player_pool.csv
│       ├── player_identity_traceability.csv
│       ├── final_shortlist_corrections.csv
│       ├── age_verification.csv
│       ├── bowling_zero_opportunity_audit.csv
│       └── ...
├── dashboard/
│   ├── app.py imports...
│   ├── components/
│   │   ├── __init__.py
│   │   ├── kpi_cards.py
│   │   ├── player_card.py
│   │   └── tables.py
│   ├── charts/
│   │   ├── __init__.py
│   │   ├── bar_charts.py
│   │   ├── distributions.py
│   │   ├── radar_charts.py
│   │   └── scatter_plots.py
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── ai_scouting_lab.py            # Page 8: Backboard × Gemini
│   │   ├── domestic_intelligence.py      # Page 6: Tier 5 leaderboards
│   │   ├── dynamic_ranking.py            # Page 3: Custom weights
│   │   ├── rr_squad_analysis.py          # Page 5: Gap analysis
│   │   └── scouting_explorer.py          # Page 2: Filter-first explorer
│   └── utils/
│       ├── __init__.py
│       ├── data_loader.py                # Centralized data loading (550+ lines)
│       ├── formatting.py                 # Badge renderers, colors
│       └── scouting_data.py              # Legacy pool loader (600+ lines)
├── src/
│   ├── ai/
│   │   ├── __init__.py
│   │   └── backboard_scouting_assistant.py  # Backboard API integration
│   ├── data_cleaning/
│   │   ├── __init__.py
│   │   ├── build_player_master.py        # 1,570 player canonical DB
│   │   ├── build_performance_database.py # 15+ performance CSVs
│   │   ├── build_rr_squad.py
│   │   ├── clean_deliveries.py
│   │   └── player_normalizer.py
│   ├── feature_engineering/
│   │   ├── __init__.py
│   │   ├── pressure_features.py          # Phase rate aggregation
│   │   └── shrinkage.py
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   ├── match_state.py                # Pre-delivery state reconstruction
│   │   └── tier_mapping.py               # Competition tier multipliers
│   ├── scoring/
│   │   ├── __init__.py
│   │   └── dynamic_scouting_engine.py    # 40/30/20/10 configurable engine
│   ├── utilities/
│   │   ├── __init__.py
│   │   ├── paths.py                      # Path resolution (no hardcoded paths)
│   │   └── validator.py                  # Pre-dashboard data validation
│   └── pipeline.py                       # End-to-end validation runner
├── models/
│   ├── __init__.py
│   ├── pressure_model.py                 # Bayesian pressure scoring
│   ├── bowling_eq_model.py               # Evidence-Qualified bowling
│   └── rr_scouting_model.py
├── tests/
│   ├── __init__.py
│   ├── test_backboard_integration.py
│   └── test_scouting_explorer.py         # 17 test cases
└── docs/
    ├── COMPLETE_CODEBASE_AUDIT_INVENTORY.md  # THIS FILE
    ├── DATASET_COVERAGE_AUDIT.md
    ├── DEPLOYMENT_GUIDE.md
    ├── FINAL_PROJECT_AUDIT.md
    ├── FINAL_PUBLICATION_CHECK.md
    ├── FINAL_SUBMISSION_REPORT.md
    ├── METHODOLOGY.md
    ├── RR_SCOUTING_STRATEGY.md
    └── VALIDATION_AND_LIMITATIONS.md
```

---

## 2. DASHBOARD PAGES (10 PAGES)

| # | Page | File | Primary Function | Key Inputs | Data Sources |
|---|------|------|------------------|------------|--------------|
| 1 | Executive Overview | app.py (inline) | KPIs, mandate, View A/B/C summary | None (static) | final_* CSVs, complete_pool, RR squad |
| 2 | Scouting Explorer | scouting_explorer.py | Filter-first 311-player table + AI | 20+ filters | complete_pool_enriched |
| 3 | Dynamic Ranking Engine | dynamic_ranking.py | Custom 40/30/20/10 weights | 6 weight profiles, 5 filters, missing policy | complete_pool, dynamic_scouting_engine |
| 4 | RR Current Squad | app.py (inline) | 19 retained players, roles, ages | None | rr_current_squad.csv |
| 5 | RR Gap Analysis | rr_squad_analysis.py | Need vs strength, vacancy fit | 4 filters (role, nat, age, min fit) | RR squad + complete_pool |
| 6 | Domestic Intelligence | domestic_intelligence.py | Tier 5 leaderboards, drilldown | Tier, mode, thresholds, metrics | comp_batter/bowler, player_master |
| 7 | Player Comparison | app.py (inline) | Multi-player radar, metrics | 2-10 player multiselect | complete_pool, EQ model |
| 8 | AI Assistant | ai_scouting_lab.py | Backboard × Gemini, persistent threads | Pool scope, role, nat, age, query | complete_pool, Backboard API |
| 9 | Standard Scouting Report | app.py (inline) | 60+ column CSV export | Scope, role, nat, limit | complete_pool, scouting_data |
| 10 | Methodology & Reliability | app.py (inline) | Formulas, shrinkage, EQ bowling, caveats | None (static) | N/A |

---

## 3. INTERACTIVE CONTROLS INVENTORY (ALL PAGES)

### Page 2: Scouting Explorer (22 controls)
| Control | Type | Default | Affects | Validation |
|---------|------|---------|---------|------------|
| Data Scope | selectbox | Full Pool (311) | pool filter | ✅ Tested |
| Player Category | selectbox | Any | role filter | ✅ Tested |
| Nationality | selectbox | Both | nationality filter | ✅ Tested |
| Country (Specific) | selectbox | All | country filter | ⚠️ Not verified |
| Age Group | selectbox | All | age filter | ✅ Tested |
| Min/Max Age | sliders | 18/42 | age filter | ✅ Tested |
| Min Pressure/EQ | slider | 0 | score filter | ✅ Tested |
| Min RR Score | slider | 0 | score filter | ✅ Tested |
| Min Career Balls | number_input | 0 | evidence filter | ✅ Tested |
| Results Limit | selectbox | 10 | output limit | ✅ Tested |
| Characteristics | selectbox | All | text filter | ✅ Tested |
| Development Pref | selectbox | All | dev_category filter | ✅ Tested |
| Search Query | text_input | "" | name/country/char filter | ✅ Tested |
| Domestic Min Runs | number_input | 0 | domestic filter | ⚠️ Limited test |
| Domestic Min Avg | number_input | 0 | domestic filter | ⚠️ Limited test |
| Domestic Min SR | number_input | 0 | domestic filter | ⚠️ Limited test |
| Domestic Min Wkts | number_input | 0 | domestic filter | ⚠️ Limited test |
| Domestic Max Econ | number_input | 15 | domestic filter | ⚠️ Limited test |
| Apply Filters | button | - | triggers filter | ✅ Tested |
| Reset Filters | button | - | resets all | ✅ Tested |
| AI Quick-start | selectbox | - | AI prompt | ✅ Tested |
| AI Prompt | text_area | - | AI query | ✅ Tested |
| Generate AI | button | - | AI call | ✅ Tested |

### Page 3: Dynamic Ranking Engine (15 controls)
| Control | Type | Default | Affects |
|---------|------|---------|---------|
| Weight Profile | selectbox | RR Default | weights |
| Custom Weight Sliders (4) | sliders | 40/30/20/10 | weights |
| Missing Data Policy | selectbox | Pop Mean | imputation |
| Min Sample Threshold | number_input | 30 | evidence gating |
| Enable Evidence Gating | checkbox | True | score penalty |
| Confidence Penalty | slider | 0.1 | score penalty |
| Domestic Bonus | number_input | 0 | bonus points |
| Data Scope | selectbox | View A | view filter |
| Role Filter | selectbox | Any | role filter |
| Nationality Filter | selectbox | Both | nat filter |
| Max Age | slider | 40 | age filter |
| Min RR Score | slider | 0 | score filter |
| Results Limit | selectbox | 20 | output limit |

### Page 5: RR Gap Analysis (7 controls)
| Control | Type | Default | Affects |
|---------|------|---------|---------|
| Target Role | selectbox | All | candidate filter |
| Nationality | selectbox | All | candidate filter |
| Age Band | selectbox | All | candidate filter |
| Min Vacancy Fit | slider | 40 | fit score filter |

### Page 6: Domestic Intelligence (10 controls) — **RECENTLY FIXED**
| Control | Type | Default | Affects |
|---------|------|---------|---------|
| Competition Tier | selectbox | All Tiers | tier filter |
| Leaderboard Mode | radio | Mode A | A/B mode |
| Min Balls Faced (Bat) | number_input | 60 | batter threshold |
| Min Balls Bowled (Bowl) | number_input | 60 | bowler threshold |
| Min Matches | number_input | 1 | innings threshold |
| Batter Ranking Metric | selectbox | Strike Rate | sort key |
| Bowler Ranking Metric | selectbox | Wicket Rate | sort key |

### Page 8: AI Assistant (9 controls)
| Control | Type | Default | Affects |
|---------|------|---------|---------|
| Search Scope | selectbox | Complete Dataset | pool filter |
| Role Filter | selectbox | All | candidate filter |
| Nationality Filter | selectbox | All | candidate filter |
| Development Stage | selectbox | All | candidate filter |
| Max Age | number_input | 35 | candidate filter |
| Example Query | selectbox | - | AI prompt |
| Custom Query | text_area | - | AI query |
| Generate/Continue/New | buttons | - | AI execution |

### Page 9: Standard Scouting Report (5 controls)
| Control | Type | Default | Affects |
|---------|------|---------|---------|
| Report Scope | selectbox | All 311 | pool filter |
| Role Filter | selectbox | All | role filter |
| Nationality | selectbox | All | nat filter |
| Max Players | number_input | 50 | limit |
| Generate Buttons | buttons | - | CSV export |

---

## 4. DATASETS INVENTORY

### Raw Data (6 files)
| File | Rows | Key Columns | Purpose |
|------|------|-------------|---------|
| ball_by_ball.csv | 201,000+ | striker_id, bowler_id, runs_off_bat, extras_type, is_wicket, is_legal_ball, pressure_category, phase | Primary delivery data |
| competition_team_player_mapping.csv | ~5,000 | player_id, player_name, comp_id, comp_name, team_id | Identity source |
| competitions.csv | ~30 | comp_id, comp_name, comp_tier, comp_type, season | Competition metadata |
| matches.csv | ~1,500 | match_id, comp_id, team1, team2, date | Match context |
| playing_eleven.csv | ~22,000 | match_id, player_id, batting_order, is_wk, is_captain | Role evidence |
| teams.csv | ~30 | team_id, team_name | Team metadata |

### Processed Data (15+ files)
| File | Rows | Key Columns | Purpose |
|------|------|-------------|---------|
| player_master.csv | 1,570 | player_id, canonical_name, primary_role, age, nationality, eligibility | Canonical identity |
| player_performance_by_competition_batter.csv | 4,317 | striker_id, comp_id, comp_tier, total_balls, total_runs, strike_rate, phase balls/runs | Competition-season batter stats |
| player_performance_by_competition_bowler.csv | 3,095 | bowler_id, comp_id, comp_tier, total_balls, total_wickets, economy, wicket_rate | Competition-season bowler stats |
| player_performance_by_season_batter.csv | 2,226 | striker_id, season, shrunk rates, population adj | Season batter stats |
| player_performance_by_season_bowler.csv | 1,602 | bowler_id, season, shrunk rates, population adj | Season bowler stats |
| player_pressure_metrics_batter.csv | 2,226 | pressure-phase balls/runs/SR | Pressure batter stats |
| player_pressure_metrics_bowler.csv | 1,602 | pressure-phase balls/wkts/econ | Pressure bowler stats |
| player_domestic_metrics_batter.csv | ~500 | Tier 4/5 domestic batter stats | Domestic evidence |
| player_domestic_metrics_bowler.csv | ~300 | Tier 4/5 domestic bowler stats | Domestic evidence |
| player_bowling_phase_metrics.csv | 1,602 | PP/Middle/Death balls, wkts, econ | Phase bowling |
| player_current_form.csv | 28 | form evidence for shortlist | Recent form |
| all_competition_batter_season_features.csv | ~4,000 | Comprehensive batter features | Source for above |
| all_competition_bowler_season_features.csv | ~2,500 | Comprehensive bowler features | Source for above |

### Official Reference (3 files - IMMUTABLE)
| File | Rows | Purpose |
|------|------|---------|
| final_combined_top10_batters.csv | 10 | View B official batter shortlist |
| final_combined_top10_bowlers.csv | 10 | View B official bowler shortlist |
| final_combined_reserves.csv | 8 | View B reserves |

### Supporting Evidence (15+ files)
| File | Rows | Purpose |
|------|------|---------|
| rr_scouting_priority_scores.csv | 28 | 4-dimension score breakdown |
| evidence_qualified_bowler_comparison.csv | 28 | EQ vs standard comparison |
| bowling_deployment_validation.csv | 28 | Phase deployment boundaries |
| current_form_source_verification.csv | 28 | 12-month form audit |
| retained_players.csv | 184 | All franchise retained players |
| ipl_eligibility_audit.csv | 664 | Eligibility per player |
| auction_eligible_player_pool.csv | 664 | Raw pool with composite_score |
| player_identity_traceability.csv | 3 | ID corrections applied |
| final_shortlist_corrections.csv | 5 | Manual corrections |
| age_verification.csv | 28 | DOB verification |
| bowling_zero_opportunity_audit.csv | 28 | Zero-delivery phase audit |

---

## 5. MODEL IMPLEMENTATIONS

### 5.1 Pressure Model (`models/pressure_model.py`)
- **Method**: James-Stein Empirical Bayes shrinkage (prior_weight=30, calibrated on IPL)
- **Tier Multipliers**: T1=1.00, T2=0.92, T3=0.84, T4=0.76, T5=0.68
- **Batter Weights**: overall_sr=30%, high_extreme_sr=25%, chase_sr=20%, PP=10%, death=10%, boundary=5%
- **Bowler Weights**: overall_econ=30%, high_extreme_econ=25%, death_econ=20%, PP=10%, wicket_rate=10%, dot_ball=5%
- **Normalization**: Robust quantile (5th-95th percentile) to 0-100 scale

### 5.2 Evidence-Qualified Bowling Model (`models/bowling_eq_model.py`)
- **Core**: Re-normalize weights across ONLY observed phases
- **Min Phase Deliveries**: 12 balls for "observed" status
- **Codified Guidelines**: 4 bowlers (Ghazanfar, Bracewell, Tector, Mondol) with explicit deployment boundaries
- **UNOBSERVED phases**: Excluded from score, not imputed as elite

### 5.3 Dynamic Scouting Engine (`src/scoring/dynamic_scouting_engine.py`)
- **Default**: 40% Pressure, 30% Age/Runway, 20% Skill Ceiling, 10% Current Form
- **Profiles**: 6 predefined + Custom
- **Missing Data Policies**: 5 options (Zero, Neutral, Pop Mean, Pop Median, Redistribute)
- **Evidence Gating**: Progressive penalty below threshold (default 30 balls)
- **Sensitivity Analysis**: ±15 pts, 7 steps, rank stability metrics

### 5.4 RR Scouting Model (`models/rr_scouting_model.py`)
- Composite of Pressure + Age + Ceiling + Form with 40/30/20/10 weights

---

## 6. CALCULATION MODULES

| Module | Function | Key Formulas |
|--------|----------|--------------|
| `src/feature_engineering/pressure_features.py` | Phase rate aggregation | SR = runs_off_bat / legal_balls × 100; Econ = runs_conceded / (legal_balls/6) |
| `src/feature_engineering/shrinkage.py` | Bayesian shrinkage | λ = n/(n+k); shrunk = λ·obs + (1-λ)·prior |
| `src/preprocessing/match_state.py` | Pre-delivery state | score, wickets, overs, CRR, RRR, balls_remaining, phase |
| `src/preprocessing/tier_mapping.py` | Competition tiers | 5-tier multipliers from paired overlap |
| `src/data_cleaning/clean_deliveries.py` | Delivery cleaning | Legal ball def, wicket credit, bowler runs |
| `src/data_cleaning/player_normalizer.py` | Name/ID resolution | Canonical IDs, alias mapping |

---

## 7. AI INTEGRATIONS

### Backboard Scouting Assistant (`src/ai/backboard_scouting_assistant.py`)
- **Provider**: Backboard API (https://app.backboard.io/api)
- **Model**: Google Gemini (gemini-2.5-pro default, auto-fallback)
- **Authentication**: BACKBOARD_API_KEY from env/secrets
- **Memory**: Persistent Assistants + Threads (UUID validated)
- **Validation**: 
  - Strict JSON schema enforcement
  - Player ID reconciliation against candidate pool
  - Score overwrite with canonical values (no hallucination)
  - Unsupported candidates rejected
- **Fallback**: Deterministic 40/30/20/10 ranking when API unavailable
- **Error Handling**: Graceful degradation with clear UI notice

### Integration Points
1. Page 2 (Scouting Explorer) - Collapsed expander
2. Page 8 (AI Assistant) - Full page
3. Both use `BackboardScoutingAssistant` singleton with `st.cache_resource`

---

## 8. OUTPUT FILES & EXPORTS

| Export | Source | Filters Applied | Metadata Included |
|--------|--------|-----------------|-------------------|
| Top 10 Batters | final_combined_top10_batters.csv | None (immutable) | Rank, scores, age, nat |
| Top 10 Bowlers | final_combined_top10_bowlers.csv | None (immutable) | Rank, scores, age, nat |
| Reserves | final_combined_reserves.csv | None (immutable) | Rank, scores, age, nat |
| RR Squad | rr_current_squad.csv | None | Role, age, nat, retention |
| Filtered Candidates | Scouting Explorer | All active filters | Full enriched record |
| Dynamic Rankings | Dynamic Ranking | Profile + filters | Dimension scores, rank |
| Vacancy Fit | RR Gap Analysis | Role/nat/age/min_fit | Fit score, rationale |
| Standard Report | Page 9 | Scope/role/nat/limit | 60+ columns |
| Player Comparison | Page 7 | Selected players | Radar + metrics |

---

## 9. DEPENDENCY MAP

```
Dashboard Page
    → User Inputs (filters, selectors, prompts)
        → Filtering (apply_scouting_filters / DynamicScoutingEngine)
            → Data Loading (load_complete_pool_enriched / load_* functions)
                → Joins (player_master, performance DB, audit tables)
                    → Calculations (pressure_model, bowling_eq_model, shrinkage)
                        → Ranking (dynamic_scouting_engine, 40/30/20/10)
                            → Visualization (charts, tables, radar)
                                → Export (CSV download with active filters)
```

**Critical Path**: `load_complete_pool_enriched()` → enriches 664 players from 10+ sources → single unified dataframe used by ALL pages

---

## 10. IDENTIFIED RISKS & AUDIT PRIORITIES

### CRITICAL (Must Fix)
| Risk | Location | Impact | Status |
|------|----------|--------|--------|
| Role classification: player_master only has 'batter'/'bowler'/NaN — no all-rounder, WK-batter | `build_player_master.py:192-201` | All leaderboards misclassify all-rounders | ⚠️ **HIGH PRIORITY** |
| Domestic Intelligence: `domestic_batting_avg` incorrectly assigned `strike_rate` value | `data_loader.py:477` | Misleading domestic stats | ⚠️ **HIGH PRIORITY** |
| Scouting Explorer & data_loader have DUPLICATE filter logic (apply_scouting_filters) | `scouting_data.py:462` vs `data_loader.py:572` | Divergent behavior | ⚠️ **HIGH PRIORITY** |
| Player Comparison uses `player_name` for selection (not player_id) | `app.py:398-410` | Name collision risk | ⚠️ **HIGH PRIORITY** |
| `country` field derived from `overseas_status` (Indian/Overseas) not actual country | `app.py:307-309`, `data_loader.py:286-295` | Misleading country labels | ⚠️ **MEDIUM** |

### HIGH (Should Fix)
| Risk | Location | Impact |
|------|----------|--------|
| No minimum sample threshold enforcement in Scouting Explorer batter/bowler tables | `scouting_explorer.py:458-487` | Low-sample players ranked |
| `apply_scouting_filters` in data_loader has `competition_tiers` param but does nothing | `data_loader.py:724-726` | Silent filter failure |
| RR Gap Analysis hardcodes player names for performance scores | `rr_squad_analysis.py:474-477` | Not data-driven |
| AI Assistant `filter_eligible_candidates` doesn't check `is_retained` | `backboard_scouting_assistant.py:330-339` | Could recommend retained players |
| No cache invalidation strategy for `st.cache_data` when data files change | All loaders | Stale data risk |

### MEDIUM (Monitor)
| Risk | Location | Impact |
|------|----------|--------|
| `scouting_data.py` and `data_loader.py` maintain separate pool enrichment logic | Two code paths | Divergence over time |
| Domestic metrics use `Other_T20` string match for tier detection | `scouting_data.py:143` | Fragile tier detection |
| `evidence_balls` calculation differs between loaders | `data_loader.py:505` vs `scouting_data.py:411` | Inconsistent confidence |
| Player Comparison radar hardcodes `tactical_fit=90` for shortlisted | `app.py:419` | Biased visualization |

### DATA INTEGRITY CHECKS NEEDED
1. **Player ID Uniqueness**: Verify 1,570 unique IDs in player_master
2. **Join Integrity**: All merges on `player_id` only — audit for name-based joins
3. **Role Consistency**: Same player must have same role across all pages
4. **Score Reproducibility**: Dynamic rankings must match manual calculation
5. **Filter State**: No stale cached results survive filter changes
6. **Export Consistency**: Downloads must reflect active filters exactly

---

## 11. TEST COVERAGE

### Existing Tests (`tests/test_scouting_explorer.py` - 17 tests)
- ✅ Official rankings integrity (3 tests)
- ✅ Candidate pool enrichment (4 tests)
- ✅ Dynamic filters (7 tests)
- ✅ Player comparison (2 tests)
- ✅ Stale insight hashing (1 test)

### Missing Tests (Gap Analysis)
| Area | Tests Needed |
|------|--------------|
| Domestic Intelligence | Mode A/B, thresholds, roles, aggregates |
| Dynamic Ranking Engine | Weight profiles, missing policies, sensitivity |
| RR Squad Analysis | Vacancy fit, role coverage, retention value |
| Player Comparison | Multi-player, role compat, missing data |
| AI Assistant | Grounding, fallback, thread persistence |
| Data Loaders | Schema, duplicates, join integrity |
| Statistical Calculations | Shrinkage, tier adj, EQ bowling, SR/Econ formulas |
| End-to-End | All 10 pages, filter combinations |

---

## 12. PHASE 0 INVENTORY COMPLETE

This inventory establishes the complete system baseline. All subsequent audit phases (1-14) will reference this document.

**Next Step**: Phase 1 — Player Identity & Role Integrity Audit