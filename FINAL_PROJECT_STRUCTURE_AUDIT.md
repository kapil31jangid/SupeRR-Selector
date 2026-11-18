# PRESSURE-X | Final Project Structure Audit & System Architecture

**Project:** SupeRR Selector 2027  
**Franchise:** Rajasthan Royals (RR) IPL 2027 Auction Analytics  
**Version:** 3.0 (Evidence-Qualified Paired Adjustment & Interactive Scouting Explorer)  
**Audit Date:** November 2026  
**Status:** 100% Verified & Tested  

---

## 1. Executive Summary

This document provides a forensic audit of the **PRESSURE-X** cricket scouting intelligence platform developed for the Rajasthan Royals (RR) IPL 2027 auction war room. 

The architecture guarantees:
1. **Filter-First Primary Experience:** The application operates as a standalone interactive analytics and scouting platform without requiring any interaction with a chatbot.
2. **Optional AI Assistance:** Backboard API with Google Gemini is integrated as an optional enhancement inside a collapsible section (collapsed by default).
3. **Graceful Offline Degradation:** When the Backboard API is unconfigured or unreachable, the entire dashboard operates seamlessly using deterministic rules and verified datasets. No large error banners are displayed.
4. **Data Integrity & Score Invariance:** Official final rankings (Top 10 Batters, Top 10 Bowlers, Reserves) are strictly read-only and preserved across all views. Customized dynamic exploration lists are clearly labeled as dynamic scouting results.
5. **Domestic Evidence Grounding:** Domestic cricket statistics (runs, average, strike rate, wickets, economy) are computed directly from processed match and season features. Candidates lacking domestic competition data are explicitly marked as having *"Insufficient domestic evidence"*, avoiding fabricated zeros.

---

## 2. Directory Structure & File Inventory

```
SupeRR-Selector-2027/
│
├── app.py                                  # Primary Streamlit Dashboard Entry Point
├── README.md                               # Operational Guide & Architecture Reference
├── DATA_DICTIONARY.md                      # Metric Definitions & Dimensional Formulas
├── FINAL_PROJECT_STRUCTURE_AUDIT.md        # Comprehensive Verification Audit (This Document)
├── requirements.txt                        # Production Python Dependencies
├── .env                                    # Local Environment Secrets (Git-Ignored)
│
├── dashboard/                              # Streamlit Dashboard Presentation Layer
│   ├── components/
│   │   ├── __init__.py
│   │   ├── kpi_cards.py                    # RR-Styled Single-Line KPI Metric Renderers
│   │   ├── player_card.py                  # War-Room Individual Player Spotlight Cards
│   │   └── tables.py                       # Interactive Filtered Data Tables
│   │
│   ├── charts/
│   │   ├── __init__.py
│   │   ├── bar_charts.py                   # Horizontal Target Priority Rankings
│   │   ├── distributions.py                # Nationality Splits & Phase Evidence Delivery Bars
│   │   ├── radar_charts.py                 # Multi-Player 5-Dimension Radar Comparisons
│   │   └── scatter_plots.py                # Pressure vs Scouting & Age Runway Scatters
│   │
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── scouting_explorer.py            # Primary Interactive Explorer (Section A + Section B)
│   │   └── ai_scouting_lab.py              # Dedicated AI Lab Route (Optional Assistant)
│   │
│   └── utils/
│       ├── __init__.py
│       ├── formatting.py                   # RR Palette (#EA1B86, #004BA0, #0B132B) & HTML Badges
│       ├── data_loader.py                  # Cached CSV Data Loaders (Legacy Compatible)
│       └── scouting_data.py                # Unified Multi-Dimensional Filtering & Aggregation Layer
│
├── data/
│   ├── raw/                                # Raw Competition, Match & Delivery Data
│   │   ├── competitions.csv                # 141 Competitions (IPL, T20I, Domestic Leagues)
│   │   ├── matches.csv                     # Match Schedules, Dates, Venues & Results
│   │   ├── ball_by_ball.csv                # 201,000+ Observed Deliveries
│   │   └── competition_team_player_mapping.csv
│   │
│   └── processed/                          # Feature-Engineered Delivery & Season Metrics
│       ├── all_competition_batter_season_features.csv   # 106 Columns per Batter/Season
│       ├── all_competition_bowler_season_features.csv   # 98 Columns per Bowler/Season
│       ├── ipl_only_batter_season_features.csv
│       └── ipl_only_bowler_season_features.csv
│
├── models/                                 # Mathematical & Statistical Models
│   ├── __init__.py
│   ├── bowling_eq_model.py                 # Evidence-Qualified Bowling Formulation & Restrictions
│   ├── pressure_model.py                   # Bayesian Win Probability Leverage Shrinkage
│   └── rr_scouting_model.py                # 40/30/20/10 RR Composite Scoring Engine
│
├── outputs/                                # Audited & Published Deliverables
│   ├── final_combined_top10_batters.csv    # Official Verified Top 10 Batters (Read-Only)
│   ├── final_combined_top10_bowlers.csv    # Official Verified Top 10 Bowlers (Read-Only)
│   ├── final_combined_reserves.csv         # Official Verified Reserves (Read-Only)
│   │
│   └── supporting_evidence/                # Comprehensive Empirical Audit Evidence
│       ├── auction_eligible_player_pool.csv             # 303 Eligible Candidate Pool
│       ├── ipl_eligibility_audit.csv                    # 311 Player Eligibility Verification
│       ├── age_verification.csv                         # Verified DOB & Age as of 1 April 2027
│       ├── bowling_deployment_validation.csv           # Bowling Phase Delivery Evidence
│       ├── bowling_zero_opportunity_audit.csv          # Zero-Opportunity Diagnostics
│       ├── current_form_source_verification.csv         # Audited 2025-2026 Match Form Logs
│       ├── evidence_qualified_bowler_comparison.csv     # Raw vs EQ Score Comparison
│       ├── retained_players.csv                         # 184 Excluded Retained Players
│       └── rr_scouting_priority_scores.csv              # 4-Dimension Mathematical Reproduction
│
├── src/
│   ├── ai/
│   │   ├── __init__.py
│   │   └── backboard_scouting_assistant.py  # Backboard API SDK Client (Google Gemini)
│   │
│   └── utilities/
│       ├── __init__.py
│       ├── paths.py                        # Path Constants
│       └── validator.py                    # Startup Data Schema Integrity Checks
│
└── tests/                                  # Automated Test Suite
    ├── __init__.py
    ├── test_scouting_explorer.py           # 18 Explorer, Filtering & Integrity Tests
    └── test_backboard_integration.py       # 48 Backboard, Model & Live API Tests
```

---

## 3. Official Deliverables & Data Integrity Audit

All official deliverables match published specifications exactly:

### Official Final Batters (`outputs/final_combined_top10_batters.csv`)
| Rank | Player Name | Nationality | Age (Apr 2027) | Pressure Score | RR Scouting Score | Form Rating | Status |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | Jake Fraser-McGurk | Overseas (AUS) | 24.9 yrs | 92.20 | **91.88** | STRONG | ELIGIBLE |
| 2 | Harry Brook | Overseas (ENG) | 28.1 yrs | 93.30 | **89.42** | STRONG | ELIGIBLE |
| 3 | Jacob Bethell | Overseas (ENG) | 23.4 yrs | 87.18 | **88.57** | POSITIVE | ELIGIBLE |
| 4 | Pathum Nissanka | Overseas (SL) | 28.9 yrs | 80.62 | **81.13** | STRONG | ELIGIBLE |
| 5 | Shai Hope | Overseas (WI) | 33.4 yrs | 75.92 | **76.28** | POSITIVE | ELIGIBLE |
| 6 | M Shahrukh Khan | Indian | 31.8 yrs | 72.80 | **73.76** | POSITIVE | ELIGIBLE |
| 7 | Rilee Rossouw | Overseas (SA) | 37.5 yrs | 71.95 | **71.41** | MIXED | ELIGIBLE |
| 8 | Glenn Maxwell | Overseas (AUS) | 38.5 yrs | 71.30 | **70.92** | WEAK | ELIGIBLE |
| 9 | Karun Nair | Indian | 35.3 yrs | 67.50 | **68.41** | STRONG | ELIGIBLE |
| 10 | Vijay Shankar | Indian | 36.2 yrs | 66.80 | **66.85** | POSITIVE | ELIGIBLE |

### Official Final Bowlers (`outputs/final_combined_top10_bowlers.csv`)
| Rank | Player Name | Nationality | Age (Apr 2027) | EQ Score | RR Scouting Score | Form Rating | Status |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | Mohammad Ghazanfar | Overseas (AFG) | 21.0 yrs | 77.40 | **84.52** | STRONG | ELIGIBLE |
| 2 | Ripon Mondol | Overseas (BAN) | 24.0 yrs | 76.50 | **81.95** | POSITIVE | ELIGIBLE |
| 3 | Mujeeb Ur Rahman | Overseas (AFG) | 26.0 yrs | 79.20 | **79.94** | POSITIVE | ELIGIBLE |
| 4 | Harry Tector | Overseas (IRE) | 27.3 yrs | 75.10 | **76.54** | STRONG | ELIGIBLE |
| 5 | Matthew Forde | Overseas (WI) | 25.0 yrs | 74.80 | **76.32** | MIXED | ELIGIBLE |
| 6 | Ashton Agar | Overseas (AUS) | 33.4 yrs | 73.60 | **73.44** | WEAK | ELIGIBLE |
| 7 | Benjamin Sears | Overseas (NZ) | 29.2 yrs | 71.20 | **71.98** | POSITIVE | ELIGIBLE |
| 8 | Michael Bracewell | Overseas (NZ) | 36.1 yrs | 69.80 | **69.88** | POSITIVE | ELIGIBLE |
| 9 | Sikandar Raza | Overseas (ZIM) | 40.9 yrs | 68.40 | **68.20** | STRONG | ELIGIBLE |
| 10 | Simarjeet Singh | Indian | 29.3 yrs | 66.90 | **67.62** | MIXED | ELIGIBLE |

---

## 4. Primary Interactive Scouting Explorer Design (Section A)

The Interactive Scouting Explorer serves as the default, primary experience:

1. **Multi-Dimensional Filters:**
   - **Player Category:** Batter, Bowler, All-rounder, Any.
   - **Nationality:** Indian, Overseas, Both, and specific country dropdown.
   - **Age Groups & Sliders:** Emerging (≤23 yrs), Development (24–26 yrs), Prime (27–30 yrs), Experienced (31+ yrs) + exact Min/Max age sliders.
   - **Quantitative Score Thresholds:** Minimum Pressure/EQ Score, Minimum RR Scouting Score.
   - **Sample Evidence Size:** Minimum career balls observed (0 to 2000 balls).
   - **Characteristics (Evidence-Backed):**
     - Batters: *Opening / Powerplay Anchor*, *Middle-Overs Spin Basher*, *Death-Over Finisher*, *Power Hitter (15+ Sixes)*, *High-Average Anchor*.
     - Bowlers: *Powerplay Bowler*, *Middle-Overs Bowler*, *Death-Overs Closer*.
   - **Domestic T20 Filters:** Minimum domestic runs, batting average, strike rate, wickets, maximum bowling economy.
   - **Development Preferences:** Immediate impact, Long-term development, High-upside prospect.
   - **Results Limit:** 5, 10, 15, 20, or 50 candidates.
   - **Controls:** Apply Filters, Reset Filters, Free-text Player/Country Search, CSV Export.

2. **Live KPI Summary Bar:**
   - Displays real-time Candidates Found, Average RR Scouting Score, Average Pressure/EQ Base, Indian/Overseas split, and Emerging Talent percentage.

3. **Tabbed Results Visualization:**
   - **Tab 1 (Table):** Formatted data table with rank, player ID, role, nationality, age, development category, progress bars for scores, form rating, observed deliveries, and shortlisted status.
   - **Tab 2 (Charts):** Top N Rankings Bar Chart, Pressure vs Scouting Scatter Plot, Age Runway Scatter Plot, Nationality Pie, and Career Stage Distribution.

4. **Candidate Evidence Deep Dive Panel:**
   - Dropdown selector to inspect any candidate in detail.
   - Explicitly distinguishes **Verified Dataset Information** (official CSVs) from **Calculated Model Metrics** (Bayesian shrinkage) and **AI Interpretation**.
   - For candidates lacking domestic evidence, explicitly shows *"Insufficient domestic evidence"*.
   - Displays mandatory tactical deployment boundaries (e.g. Mohammad Ghazanfar prohibited from death overs and initial powerplay in Year 1).

---

## 5. Optional AI Scouting Assistant (Section B)

Integrated via Backboard API using Google Gemini (`gemini-2.5-pro`):

- **Collapsible Expander:** Titled *"🤖 Ask AI Scouting Assistant (Optional — Powered by Backboard × Google Gemini)"*, **collapsed by default**.
- **Zero Interruption When Offline:** When Backboard is unconfigured or unavailable, an inline informational message is shown:
  > *"AI scouting is currently unavailable. All dashboard filters, rankings, comparisons and visualizations remain fully functional without it."*
  No red error banner or visual disruption is created.
- **Explicit Triggering:** AI insights are generated **only upon an explicit button press** (`⚡ Generate AI Insights`). Filters do not trigger API requests on change.
- **Stale Insight Detection:** Computes an MD5 hash of active filter parameters (`_compute_filter_hash`). If filters are modified after AI recommendations are generated, an alert notifies the user that insights reflect earlier criteria.
- **Strict Evidence Boundaries:**
  - AI is passed only the currently filtered eligible candidate context.
  - Every returned `player_id` is validated against ground truth. Hallucinated IDs are discarded.
  - Returned player names and scores are overwritten by canonical dataset values to prevent hallucination.
- **Persistent Conversation Memory:** Backboard Assistants and Threads maintain conversational context across multiple turns when the user clicks `🔁 Continue Thread`.

---

## 6. Automated Test Suite Results

A total of **66 automated tests** validate system functionality:

### A. Scouting Explorer & Data Layer (`tests/test_scouting_explorer.py`) — 18 Tests: PASS ✅
```
test_nationalities_clean ............................................... ok
test_pool_total_eligible_count (303 players verified) .................. ok
test_scores_within_valid_bounds ........................................ ok
test_shortlist_flag_present (28 shortlisted players) ................... ok
test_filter_age_group_emerging (age <= 23) .............................. ok
test_filter_domestic_bowling_wickets ................................... ok
test_filter_domestic_runs .............................................. ok
test_filter_empty_graceful (zero-result handling) ...................... ok
test_filter_overseas_finishers ......................................... ok
test_filter_score_thresholds ........................................... ok
test_filter_search_query ............................................... ok
test_official_batters_count_and_scores ................................. ok
test_official_bowlers_count_and_scores ................................. ok
test_official_csv_files_unmodified ..................................... ok
test_official_reserves_count ........................................... ok
test_comparison_empty_on_invalid_ids ................................... ok
test_comparison_extraction ............................................. ok
test_hash_consistency (stale detection) ................................ ok
----------------------------------------------------------------------
Ran 18 tests in 1.571s — OK
```

### B. Backboard AI Integration (`tests/test_backboard_integration.py`) — 48 Tests: PASS ✅
```
Unit Tests (43):
- TestAPIFailureFallback (4 tests) ..................................... ok
- TestAPIKeyProtection (6 tests) ....................................... ok
- TestAuthenticationHandling (3 tests) ................................. ok
- TestCandidateFiltering (6 tests) ..................................... ok
- TestDeterministicFallback (6 tests) ................................... ok
- TestModelSelection (5 tests) ......................................... ok
- TestPersistentConversation (5 tests) ................................. ok
- TestStructuredJSONValidation (8 tests) ............................... ok

Live API Integration Tests (5):
- test_live_authentication ............................................. ok
- test_live_google_model_catalogue (31 Google models found) ............ ok
- test_live_model_verification_and_selection (gemini-2.5-pro) .......... ok
- test_live_persistent_thread_continuation (multi-turn memory) ......... ok
- test_live_scouting_query_structured_json ............................. ok
----------------------------------------------------------------------
Ran 48 tests in 202.733s — OK
```

---

## 7. Compliance Verification Checklist

- [x] Primary dashboard works completely without requiring chatbot interaction.
- [x] AI Scouting Lab redesigned into Section A (Interactive Explorer) and Section B (Optional AI).
- [x] Section B is collapsible and collapsed by default.
- [x] Dynamic filtering across category, nationality, age group, scores, characteristics, and domestic stats.
- [x] Only evidence-supported characteristics are exposed.
- [x] Missing domestic stats display *"Insufficient domestic evidence"*.
- [x] Official final rankings (Top 10 CSVs) are strictly preserved and read-only.
- [x] Backboard API with Google Gemini (`gemini-2.5-pro`) activates only upon explicit user request.
- [x] Stale AI insights are flagged when filters change.
- [x] When Backboard is unconfigured, gentle inline information is shown (no large error banner).
- [x] Interactive Plotly charts update dynamically with the active dataset.
- [x] Multi-candidate comparison supports any of the 303 eligible players.
- [x] Downloadable filtered results CSV export.
- [x] Clean single-line HTML prevents any Markdown code block rendering issues.
- [x] Comprehensive test suite (66 tests) passes 100%.

**Audited & Approved by:** PRESSURE-X Lead Scouting & Analytics Team  
**Franchise:** Rajasthan Royals (IPL 2027)
