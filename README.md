# SupeRR Selector 2027 — PRESSURE-X

**IPL 2027 Rajasthan Royals Auction Strategy**  
Evidence-Based T20 Player Ranking System

---

## Final Results

### 🏏 Top 10 Batters (IPL 2027 Auction-Eligible)

| Rank | Player | PRESSURE-X | Nationality |
|------|--------|-----------|-------------|
| 1 | Jake Fraser-McGurk | 91.88 | Australian |
| 2 | Jacob Bethell | 90.27 | English |
| 3 | Harry Brook | 89.42 | English |
> **Note:** Rankings are ordered by RR scouting composite score (`verified_rr_scouting_score`). Harry Brook has a higher PRESSURE-X base score (93.30) than Jacob Bethell (87.18); Bethell ranks #2 overall due to his higher RR scouting composite (90.27 vs 89.42), driven by age ceiling advantage.
| 4 | Pathum Nissanka | 81.13 | Sri Lankan |
| 5 | Shai Hope | 76.28 | West Indian |
| 6 | Shahrukh Khan | 73.76 | Indian |
| 7 | Rilee Rossouw | 71.41 | South African |
| 8 | Glenn Maxwell | 70.92 | Australian |
| 9 | Karun Nair | 68.41 | Indian |
| 10 | Vijay Shankar | 66.85 | Indian |

### 🎳 Top 10 Bowlers (IPL 2027 Auction-Eligible)

| Rank | Player | PRESSURE-X | Nationality |
|------|--------|-----------|-------------|
| 1 | Mohammad Ghazanfar | 84.52 | Afghan |
| 2 | Tanvir Islam Mondol (Ripon Mondol) | 81.95 | Bangladeshi |
| 3 | Mujeeb Ur Rahman | 79.94 | Afghan |
| 4 | Harry Tector | 76.18 | Irish |
| 5 | Jason Forde (Matthew Forde) | 75.80 | Trinidadian |
| 6 | Ashton Agar | 74.04 | Australian |
| 7 | Ben Sears | 73.26 | New Zealander |
| 8 | Michael Bracewell | 69.48 | New Zealander |
| 9 | Sikandar Raza | 65.95 | Zimbabwean |
| 10 | Simarjeet Singh | 65.68 | Indian |

> All scores are PRESSURE-X Evidence-Based v3 composites. See `reports/METHODOLOGY.md` for the full scoring methodology.

---

## Project Overview

PRESSURE-X is an evidence-based T20 player ranking system that quantifies performance under match pressure across five competition tiers. It was developed to identify auction targets for Rajasthan Royals' IPL 2027 strategy.

**Key design principles:**
- Pressure-phase performance weighted by game-state win probability
- Competition strength adjustment across T1–T5 tiers
- James-Stein shrinkage to stabilise small-sample estimates
- Full eligibility pipeline: retained-player exclusion + IPL nationality filter
- RR scouting lens: adds age, skill ceiling, and form trajectory dimensions

---

## Directory Structure

```
SupeRR-Selector-2027/
├── README.md                          ← This file
├── requirements.txt                   ← Python dependencies
├── .gitignore
│
├── data/
│   ├── raw/                           ← Original source data (DO NOT MODIFY)
│   │   ├── ball_by_ball.csv
│   │   ├── matches.csv
│   │   ├── competitions.csv
│   │   ├── competition_team_player_mapping.csv
│   │   ├── playing_eleven.csv
│   │   ├── teams.csv
│   │   └── Round 1 Problem Statement SupeRR Selector Season 2.pdf
│   └── processed_v3/                  ← Final cleaned feature tables (8 files)
│       ├── all_competition_batter_season_features.csv
│       ├── all_competition_batter_match_features.csv
│       ├── all_competition_bowler_season_features.csv
│       ├── all_competition_bowler_match_features.csv
│       ├── ipl_only_batter_match_features.csv
│       ├── ipl_only_batter_season_features.csv
│       ├── ipl_only_bowler_match_features.csv
│       └── ipl_only_bowler_season_features.csv
│
├── outputs/
│   ├── final_combined_top10_batters.csv    ← FINAL VERIFIED BATTER RANKINGS
│   ├── final_combined_top10_bowlers.csv    ← FINAL VERIFIED BOWLER RANKINGS
│   ├── final_combined_reserves.csv         ← Reserve shortlist
│   └── supporting_evidence/               ← Audit trail and eligibility docs
│       ├── final_eligibility_audit.csv
│       ├── retained_players.csv
│       ├── ipl_eligibility_audit.csv
│       ├── scoring_reproduction.csv
│       ├── bowling_zero_opportunity_audit.csv
│       ├── evidence_qualified_bowler_comparison.csv
│       ├── rr_scouting_priority_scores.csv
│       ├── pressure_definition_methodology.md
│       └── ...
│
├── reports/
│   ├── FINAL_SUBMISSION_REPORT.md         ← Main submission document
│   ├── METHODOLOGY.md                     ← Full scoring methodology
│   ├── VALIDATION_AND_LIMITATIONS.md      ← Audit findings and caveats
│   └── RR_SCOUTING_STRATEGY.md            ← RR long-term talent strategy
│
├── src/
│   ├── ingestion/                         ← Raw data processing pipeline
│   ├── features/                          ← Feature engineering
│   ├── scoring/                           ← PRESSURE-X scoring + RR scouting
│   └── validation/                        ← Audit and validation scripts
│
└── assets/
    └── final_submission_visuals/          ← Charts and visuals
```

---

## Quick Start

### Requirements

```bash
pip install -r requirements.txt
```

Requires Python 3.9+.

### Run the Pipeline

```bash
# 1. Build processed features (requires data/raw/)
python src/ingestion/build_primary_datasets.py
python src/ingestion/build_all_competition_deliveries.py
python src/ingestion/reconstruct_all_competition_match_state.py
python src/ingestion/build_all_competition_pressure_features.py

# 2. Aggregate player features
python src/features/aggregate_all_competition_player_features.py
python src/features/build_corrected_competition_adjustment.py
python src/features/aggregate_corrected_features.py

# 3. Generate PRESSURE-X scores
python src/scoring/generate_preliminary_scores_v3.py

# 4. Generate RR scouting outputs
python src/scoring/generate_task07l_outputs.py

# 5. Run final audit
python src/validation/generate_task07m_audit_outputs.py
```

> The pipeline writes outputs to `outputs/`. Final verified rankings are in `outputs/final_combined_top10_batters.csv` and `outputs/final_combined_top10_bowlers.csv`.

---

## Reports

| Report | Description |
|--------|-------------|
| [`FINAL_SUBMISSION_REPORT.md`](reports/FINAL_SUBMISSION_REPORT.md) | Main submission with rankings, eligibility decisions and shortlist rationale |
| [`METHODOLOGY.md`](reports/METHODOLOGY.md) | Dataset, pressure definitions, competition adjustment, shrinkage, scoring formula |
| [`VALIDATION_AND_LIMITATIONS.md`](reports/VALIDATION_AND_LIMITATIONS.md) | Task 07M audit findings, ID corrections, caveats |
| [`RR_SCOUTING_STRATEGY.md`](reports/RR_SCOUTING_STRATEGY.md) | Rajasthan Royals talent development philosophy and scouting model |

---

## Key Design Decisions

- **No tier quotas**: Rankings are purely score-ordered across all tiers. No minimum representation by competition tier was enforced.
- **No manual promotion**: No adjustments were made based on player fame or IPL profile.
- **Shrinkage transparency**: Players with zero opportunities in a pressure phase are labelled UNOBSERVED in the evidence audit, not penalised or treated as exceptional.
- **Nationality filter**: Combined Indian + overseas list; no fixed nationality split was applied.

---

## Data Sources

| Source | Description |
|--------|-------------|
| CricSheet / proprietary | Ball-by-ball delivery data, 5 competition tiers, multiple seasons |
| IPL 2027 retention announcements | Retained-player list (all 10 franchises) |
| International cricket boards | Nationality and eligibility verification |

---

*PRESSURE-X | SupeRR Selector Season 2 | Rajasthan Royals IPL 2027 Auction Strategy*
