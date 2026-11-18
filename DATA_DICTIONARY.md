# DATA DICTIONARY
## PRESSURE-X | SupeRR Selector Season 2 — IPL 2027

This document provides a comprehensive inventory and field specification for every dataset retained in the final submission workspace.

---

## 1. Raw Challenge Datasets (`data/raw/`)

These datasets represent the immutable source data provided for the SupeRR Selector challenge.

### 1.1 `ball_by_ball.csv`
- **Purpose**: Primary delivery-level records covering all matches across five competition tiers.
- **Row Count**: ~201,000+ deliveries
- **Key Columns**:
  - `match_id` *(int)*: Unique match identifier linking to `matches.csv`.
  - `inning` *(int)*: Inning number (1 or 2).
  - `over` *(int)*: Over number (0-indexed, 0 to 19).
  - `ball` *(int)*: Ball within over (1 to 6+).
  - `batter_id` / `batter` *(int/str)*: Striker identity.
  - `bowler_id` / `bowler` *(int/str)*: Bowler delivering the ball.
  - `runs_off_bat` *(int)*: Runs scored off the bat.
  - `extras` *(int)*: Extra runs conceded (wides, no-balls, byes, leg-byes).
  - `wides`, `noballs`, `byes`, `legbyes` *(int)*: Specific extra classifications.
  - `wicket_type` *(str)*: Mode of dismissal (e.g. bowled, caught, lbw, run out).
  - `player_dismissed` *(str)*: Name of dismissed player.
- **Used By**: `src/data_cleaning/`, `src/preprocessing/`, `src/feature_engineering/`.

### 1.2 `matches.csv`
- **Purpose**: Match-level metadata including venues, dates, teams, and match outcomes.
- **Key Columns**:
  - `match_id` *(int)*: Primary key.
  - `season` *(str/int)*: Tournament edition or year.
  - `date` *(date)*: Date match took place.
  - `competition` *(str)*: Tournament name.
  - `venue`, `city` *(str)*: Stadium and geographic location.
  - `toss_winner`, `toss_decision` *(str)*: Coin toss outcome.
  - `winner`, `outcome` *(str)*: Match result.

### 1.3 `competitions.csv`
- **Purpose**: Taxonomy of the five competition tiers (T1–T5) and their respective coverage windows.
- **Key Columns**:
  - `competition_id`, `competition_name`, `tier_level` (T1 to T5), `format`.

### 1.4 `competition_team_player_mapping.csv`
- **Purpose**: Cross-reference mapping linking individual player IDs to official tournament squad rosters.
- **Key Columns**:
  - `player_id`, `player_name`, `team_name`, `competition`, `season`.

### 1.5 `playing_eleven.csv`
- **Purpose**: Verified official playing lineups (XI) for each match.

### 1.6 `teams.csv`
- **Purpose**: Canonical team names and abbreviations across domestic and international leagues.

---

## 2. Essential Processed Feature Datasets (`data/processed/`)

Cleaned, phase-annotated, and Bayesian-adjusted feature tables supporting the PRESSURE-X models and dashboard.

### 2.1 `all_competition_batter_season_features.csv`
- **Purpose**: Season-level aggregated metrics for all qualified batters across T1–T5.
- **Key Columns**:
  - `player_id` *(int)*: Canonical player identifier.
  - `player_name` *(str)*: Standardized player name.
  - `season` *(str)*: Competition season.
  - `competition` *(str)*: Tournament name.
  - `total_balls` *(int)*: Total legal deliveries faced.
  - `total_runs` *(int)*: Aggregate runs scored.
  - `strike_rate` *(float)*: Raw strike rate.
  - `strike_rate_comp_adj` *(float)*: Competition-tier adjusted strike rate.
  - `high_extreme_sr_adj` *(float)*: Bayesian shrunk strike rate in High-Extreme pressure.
  - `chase_strike_rate_adj` *(float)*: Shrunk strike rate while chasing.
  - `death_sr_adj` *(float)*: Shrunk strike rate in overs 17–20.
  - `powerplay_sr_adj` *(float)*: Shrunk strike rate in overs 1–6.
  - `boundary_pct_comp_adj` *(float)*: Shrunk, competition-adjusted boundary percentage.
  - `min_balls_100` *(bool)*: Eligibility threshold flag (>= 100 balls).

### 2.2 `all_competition_bowler_season_features.csv`
- **Purpose**: Season-level aggregated metrics for all qualified bowlers across T1–T5.
- **Key Columns**:
  - `player_id` *(int)*: Canonical player identifier.
  - `player_name` *(str)*: Standardized player name.
  - `season` *(str)*: Competition season.
  - `total_balls` *(int)*: Legal deliveries bowled.
  - `runs_conceded` *(int)*: Aggregate runs allowed.
  - `wickets` *(int)*: Aggregate wickets taken.
  - `economy_rate_comp_adj` *(float)*: Competition-tier adjusted economy rate.
  - `high_extreme_economy_adj` *(float)*: Shrunk economy in High-Extreme pressure.
  - `death_economy_adj` *(float)*: Shrunk economy in overs 17–20.
  - `powerplay_economy_adj` *(float)*: Shrunk economy in overs 1–6.
  - `wicket_rate_comp_adj` *(float)*: Competition-adjusted wicket strike rate.
  - `dot_ball_pct_comp_adj` *(float)*: Shrunk dot-ball percentage.
  - `he_balls`, `death_balls`, `pp_balls` *(int)*: Raw delivery counts in each phase.

### 2.3 `all_competition_batter_match_features.csv` & `all_competition_bowler_match_features.csv`
- **Purpose**: Match-by-match game situation and phase execution records.

### 2.4 `ipl_only_batter_season_features.csv` & `ipl_only_bowler_season_features.csv`
- **Purpose**: Isolated IPL baseline feature tables used for cross-tier calibration.

---

## 3. Final Verified Deliverables (`outputs/`)

Authoritative final outputs submitted for the Rajasthan Royals IPL 2027 auction strategy.

### 3.1 `final_combined_top10_batters.csv` (10 Rows)
- **Columns**:
  - `final_verified_rank` *(int)*: Final overall rank (1 to 10).
  - `player_id` *(int)*: Canonical player ID (e.g. Fraser-McGurk: 7341, Bethell: 23311, Brook: 6280).
  - `player_name` *(str)*: Player name.
  - `country` *(str)*: Country ISO-3 code (AUS, ENG, SL, WI, IND, SA).
  - `nationality` *(str)*: Category ('Indian' or 'Overseas').
  - `age_as_of_2027_04_01` *(int)*: Exact age as of reference date.
  - `development_category` *(str)*: Emerging, Young development candidate, Prime-age performer, Experienced performer.
  - `validated_historical_pressure_score` *(float)*: Historical PRESSURE-X base score (40% dimension).
  - `verified_rr_scouting_score` *(float)*: Final composite 40/30/20/10 RR scouting priority score.
  - `unrounded_scouting_score` *(float)*: High-precision composite score.
  - `current_form_rating` *(str)*: STRONG, POSITIVE, MIXED, WEAK, INSUFFICIENT DATA.
  - `eligibility_status` *(str)*: ELIGIBLE (verified non-retained, non-Pakistani).

### 3.2 `final_combined_top10_bowlers.csv` (10 Rows)
- **Columns**: Same schema as batters, with `validated_evidence_qualified_score` representing the Evidence-Qualified bowling performance.

### 3.3 `final_combined_reserves.csv` (8 Rows)
- **Columns**: Key reserve targets (4 batters, 4 bowlers) providing positional depth and budget pivots.

---

## 4. Supporting Evidence Directory (`outputs/supporting_evidence/`)

Contains the 16 forensic audit files validating all scoring steps, eligibility rulings, and identity reconciliations:
- `age_verification.csv`: Birth date calculations as of 1 April 2027.
- `bowling_deployment_validation.csv`: Codified tactical boundaries for bowlers with unobserved phases.
- `bowling_zero_opportunity_audit.csv`: Delivery counts in High-Extreme, Death, and Powerplay phases.
- `current_form_source_verification.csv`: Verified 2025–2026 match statistics and source URLs.
- `evidence_qualified_bowler_comparison.csv`: Comparison between raw Bayesian and Evidence-Qualified bowler rankings.
- `final_eligibility_audit.csv`: Rule-out audit for all 28 finalists and reserves.
- `final_shortlist_corrections.csv`: Audit log of canonical ID corrections.
- `ipl_eligibility_audit.csv`: Full nationality and BCCI auction eligibility audit.
- `player_identity_traceability.csv`: Source-to-final traceability matrix for every candidate.
- `pressure_definition_methodology.md`: Mathematical definitions of game pressure.
- `retained_players.csv`: Roster of all 184 retained players across the 10 IPL franchises.
- `retained_player_matching_audit.csv`: Matching audit against historical database.
- `rr_scouting_priority_scores.csv`: 4-dimension scoring breakdown for all candidate options.
- `rr_scouting_selection_audit.csv`: Strategic selection rationale for finalists vs reserves.
- `scoring_reproduction.csv`: Mathematical reproduction verification for composite scores.
- `scoring_sensitivity_analysis.csv`: Weight sensitivity tests across model parameters.
