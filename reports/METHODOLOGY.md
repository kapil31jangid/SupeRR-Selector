# PRESSURE-X Methodology
## SupeRR Selector Season 2 — IPL 2027 Rajasthan Royals Auction Strategy

---

## 1. Dataset

| File | Description |
|------|-------------|
| `data/raw/ball_by_ball.csv` | Ball-by-ball delivery records |
| `data/raw/matches.csv` | Match metadata |
| `data/raw/competitions.csv` | Competition definitions |
| `data/raw/competition_team_player_mapping.csv` | Player–team–competition links |
| `data/processed_v3/` | Final cleaned feature tables (v3 pipeline) |

Five competition tiers (T1–T5) are covered:  
**T1** = IPL · **T2** = Other full-member T20Is (BBL, PSL, SA20, ILT20, CPL) · **T3** = Emerging member T20 leagues · **T4** = Associate T20Is · **T5** = Domestic/developmental T20

---

## 2. Pressure Phase Definitions

Pressure deliveries are classified by game-state at the time of each ball:

| Phase | Definition |
|-------|-----------|
| **High-Extreme** | Win probability differential > 15%, last 5 overs |
| **Death** | Overs 17–20 |
| **Powerplay** | Overs 1–6 |
| **Middle** | Overs 7–16 |

Each delivery is assigned exactly one primary phase. Win probability is computed from match-state reconstruction using a logistic model calibrated on historical T20 outcomes.

---

## 3. Feature Engineering

### Batter Features
- **Runs scored** in each pressure phase
- **Balls faced** in each pressure phase
- **Boundary rate** (4s + 6s per ball)
- **Strike rate** vs competition-adjusted baseline

### Bowler Features
- **Wickets taken** in each pressure phase
- **Balls bowled** in each pressure phase
- **Economy rate** vs competition-adjusted baseline
- **High-value wicket rate** (top-5 batter dismissals)

Minimum eligibility thresholds:
- Batters: ≥ 100 balls faced across the analysis window
- Bowlers: ≥ 100 balls bowled across the analysis window

---

## 4. Competition Adjustment (Evidence-Based v3)

A competition strength factor `C` is derived for each tier using an empirical calibration:

```
C(T1) = 1.00   # IPL baseline
C(T2) = 0.92
C(T3) = 0.84
C(T4) = 0.76
C(T5) = 0.68
```

Raw pressure scores are multiplied by `C` before pooling across tiers:

```
adjusted_score = raw_pressure_score × C(tier)
```

---

## 5. Shrinkage (James-Stein)

To stabilise estimates for players with low sample sizes, empirical Bayes shrinkage is applied:

```
shrunk_score = grand_mean + (1 - λ) × (adjusted_score - grand_mean)
```

where `λ` (the shrinkage factor) increases as sample size decreases:

```
λ = prior_variance / (prior_variance + observed_variance / n)
```

Players with very few observations are pulled strongly toward the global mean. This prevents statistical artefacts from appearing in the rankings for low-sample players.

> **Important**: Perfect component scores (1.00) in a pressure phase with zero observed opportunities are a shrinkage artefact — they represent the population mean, not exceptional performance.

---

## 6. PRESSURE-X Composite Score

The final composite score for each player-season combines four phase components:

```
PRESSURE-X = w_HE × S_HE + w_D × S_D + w_PP × S_PP + w_M × S_M
```

Weights:
| Component | Weight |
|-----------|--------|
| High-Extreme (HE) | 0.40 |
| Death (D) | 0.30 |
| Powerplay (PP) | 0.20 |
| Middle (M) | 0.10 |

Scores are scaled 0–100 relative to the eligible pool. Scores are **not rounded** for ranking purposes.

---

## 7. Evidence-Qualified Assessment

For the final bowling audit (Task 07K), an evidence-qualified comparison was produced that marks unobserved phases as `UNOBSERVED` rather than treating shrinkage-imputed values as real performance evidence. This does not change the original PRESSURE-X scores but provides transparency about data coverage.

---

## 8. Eligibility Pipeline

1. **Season window**: Player-seasons with ≥ 100 qualifying balls in the analysis period
2. **Retained player exclusion**: 184 IPL 2027 retained players removed (Task 07H)
3. **IPL eligibility filter**: Pakistan-nationality players excluded (Task 07J addendum)
4. **Retirement/opt-out filter**: Players who have retired or formally withdrawn from IPL (Task 07L)

---

## 9. RR Scouting Composite (Task 07L)

For the Rajasthan Royals long-term talent lens, four scouting dimensions are combined:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| PRESSURE-X Performance | 40% | Validated historical pressure score |
| Skill Ceiling | 30% | Projected development potential |
| Age/Career Stage | 20% | Youth bonus + peak-window assessment |
| Current Form | 10% | 2025–26 T20 form trajectory |

```
RR_Score = 0.40 × PRESSURE-X + 0.30 × Ceiling + 0.20 × Age + 0.10 × Form
```

This formula does not alter the PRESSURE-X scores; it adds an independent scouting layer.

---

## 10. Pipeline Execution Order

```
src/ingestion/build_primary_datasets.py
src/ingestion/build_all_competition_deliveries.py
src/ingestion/reconstruct_all_competition_match_state.py
src/ingestion/build_all_competition_pressure_features.py
src/features/aggregate_all_competition_player_features.py
src/features/build_corrected_competition_adjustment.py
src/features/aggregate_corrected_features.py
src/scoring/generate_preliminary_scores_v3.py
src/scoring/generate_task07l_outputs.py
src/validation/generate_task07m_audit_outputs.py
```

See `README.md` for quick-start instructions.

