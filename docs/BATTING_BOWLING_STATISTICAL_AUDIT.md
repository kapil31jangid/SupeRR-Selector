# PRESSURE-X 2.0 — BATTING & BOWLING STATISTICAL AUDIT

**Audit Date:** 2026-11-18  
**Auditor:** Forensic Codebase Audit  
**Status:** VALIDATED — CORE CALCULATIONS CORRECT

---

## EXECUTIVE SUMMARY

The statistical engine passes validation with **zero anomalies** detected:

| Component | Status | Notes |
|-----------|--------|-------|
| Shrinkage (James-Stein, prior=30) | ✅ VALID | Population means ~135 SR / 7.5 econ |
| Minimum balls flags (100/50/30) | ✅ VALID | 311/450/346 batters, 333/484/244 bowlers |
| Pressure metrics (4 categorical + continuous) | ✅ VALID | 843 chase, 896 high-extreme players |
| EQ Bowling (5-tier paired adjustment) | ✅ VALID | 14 bowlers with deployment boundaries |
| Official rankings reproduction | ✅ EXACT | All 28 scores match to 0.01 |
| Sensitivity analysis (4 scenarios) | ✅ VALID | Max rank delta = 3 |
| Competition tier multipliers | ✅ PRESENT | Tiers 1-5 in competition data |
| Statistical anomalies | ✅ NONE | No impossible values |

---

## 1. SHRINKAGE VALIDATION (James-Stein Empirical Bayes)

### 1.1 Implementation Confirmed
- **Prior weight**: 30 balls (hardcoded in population-adjusted aggregation)
- **Method**: `(n * observed + 30 * population_prior) / (n + 30)`
- **Applied to**: Strike rate, dismissal rate, boundary % (batters); Economy, wicket rate, dot %, boundary concession % (bowlers)
- **Population priors**: Tier-adjusted means

### 1.2 Sample Validation
| Player | Balls | Observed SR | Pop-Adj SR | Shrunk SR | Implied Prior |
|--------|-------|-------------|------------|-----------|---------------|
| Jake McGurk | 218 | 203.2 | 204.0 | 196.2 | ~139.5 |
| Harry Brook | 211 | 149.8 | 152.8 | 150.2 | ~132.6 |

**Note**: Implied priors differ slightly (139.5 vs 132.6) suggesting **tier-specific priors** rather than single global prior.

### 1.3 Minimum Sample Flags (Gate Evidence)
| Threshold | Batters | Bowlers | Purpose |
|-----------|---------|---------|---------|
| ≥100 balls | 311 | 333 | High confidence |
| ≥50 balls | 450 | 484 | Adequate evidence |
| ≥30 high/extreme | 346 | 244 | Pressure evidence |
| ≥30 chase | 370 | — | Chase pressure |
| ≥30 defend | — | 428 | Defend pressure |

**Finding**: 516 batter-seasons and 225 bowler-seasons have <50 balls — properly flagged as low evidence.

### 1.4 Shrinkage Column Coverage
- **Batter**: 31 adjusted columns (comp_adj, adj, pop_adj, pop_adj_shrunk across SR, DR, BP)
- **Bowler**: 47 adjusted columns (economy, wicket rate, dot %, boundary concession, wickets/over)
- **Pressure-specific**: 12 batter + 16 bowler adjusted columns per pressure context

---

## 2. PRESSURE METRICS VALIDATION

### 2.1 Four Categorical Pressure Levels
| Level | Batters | Bowlers | Description |
|-------|---------|---------|-------------|
| Low | 966 | 709 | Baseline |
| Medium | 966 | 709 | RRR-CRR moderate |
| High | 966 | 709 | RRR-CRR high |
| Extreme | 966 | 709 | RRR-CRR extreme |

### 2.2 Continuous Pressure Contexts
| Context | Batters | Bowlers | Balls Range |
|---------|---------|---------|-------------|
| Chase | 843 | — | 1-254 |
| High-Extreme | 896 | 709 | 1-103+ |
| Defend | — | 709 | 1-155 |
| Powerplay | 966 | 709 | — |
| Middle | 966 | 709 | — |
| Death | 966 | 709 | — |

### 2.3 Chase Pressure Range Validation
- **Chase SR**: 0.0 – 400.0 (validated)
- **Chase Dismissal Rate**: 0.0 – 1.0 (validated)
- **Zero anomalies**: No values outside cricket-law bounds

---

## 3. EVIDENCE-QUALIFIED (EQ) BOWLING MODEL

### 3.1 5-Tier Paired Adjustment System
| Tier | Description | Players | Multiplier |
|------|-------------|---------|------------|
| 1 | Adequate all phases | 1 (Shakib) | 1.00 |
| 2 | Low sample 1 phase | 5 | 0.95-0.98 |
| 3 | Unobserved 1 phase | 4 | 0.90-0.95 |
| 4 | Dual unobserved | 1 (Ghazanfar) | 0.80-0.85 |
| 5 | Severe artifact | 3 | <0.80 |

### 3.2 Prohibited Deployments (Codified Boundaries)
| Player | Prohibited | Reason |
|--------|------------|--------|
| Mohammad Ghazanfar | Death + Powerplay (initial) | 0 death, 0 PP balls |
| Harry Tector | Death overs | 0 death balls |
| Michael Bracewell | Death overs | 0 death balls |
| Sikandar Raza | Powerplay | 0 PP balls (2025) |
| Murugan Ashwin | Death (low sample) | 6 death balls only |
| Ehsan Khan | High-Extreme | 0 HE balls |

### 3.3 Zero-Opportunity Audit (10 Players)
All 10 players have **artifact diagnoses** documenting exact shrinkage impact:
- **Michael Bracewell**: Death econ shrunk to 8.73 RPO (artificial 100 score) — 20pt inflation
- **Harry Tector**: Zero-death artifact inflated score by 20.0 points
- **Mohammad Ghazanfar**: Dual artifact (PP + Death) — two artificial 100s = 30% weight
- **Sikandar Raza**: 0 PP balls in 2025 gave artificial 100 PP score (10% weight)

### 3.4 EQ Comparison Validation
- 10 shortlist bowlers ranked under 3 evidence standards
- Ranking adjustment rationale documented per player
- Scores match official within 0.01

---

## 4. OFFICIAL RANKINGS REPRODUCTION

### 4.1 Perfect Match (28/28)
| Player | Role | Official | Reproduced | Delta |
|--------|------|----------|------------|-------|
| Jake Fraser-McGurk | Batter | 91.88 | 91.8812 | +0.001 |
| Harry Brook | Batter | 89.42 | 89.4206 | +0.001 |
| Jacob Bethell | Batter | 88.57 | 88.5730 | +0.003 |
| ... | ... | ... | ... | <0.01 |
| Ehsan Khan | Bowler | 54.09 | 54.0925 | +0.003 |

**All 28 official scores reproduce within 0.01** — mathematical verification PASSED.

### 4.2 Scoring Formula (40/30/20/10)
```
RR_Scouting_Score = 0.40 × DimA_Pressure + 0.30 × DimB_AgeDev + 0.20 × DimC_Ceiling + 0.10 × DimD_Form
```

**Batter DimA**: `validated_historical_pressure_score` (0-100)
**Bowler DimA**: `validated_evidence_qualified_score` (0-100)
**DimB**: Age/Development score (younger = higher)
**DimC**: Skill ceiling (pressure metrics + competition tier)
**DimD**: Current form (shortlist only, else neutral 70)

---

## 5. SENSITIVITY ANALYSIS (4 Scenarios)

| Scenario | Weights (A/B/C/D) | Max Rank Delta |
|----------|-------------------|----------------|
| Base (Official) | 40/30/20/10 | — |
| Youth-Focused | 35/35/20/10 | 3 |
| Performance-Heavy | 50/20/20/10 | 3 |
| Skill-Focused | 40/25/25/10 | 3 |

**Finding**: Rank stability is high — no player moves more than 3 positions across scenarios.
**Implication**: 40/30/20/10 weighting is robust.

---

## 6. COMPETITION TIER WEIGHTS

### 6.1 Tier Distribution (Eligible Players)
| Tier | Name | Multiplier | Batter Records | Bowler Records |
|------|------|------------|----------------|----------------|
| 1 | IPL / T20I | 1.00 | 255 | 209 |
| 2 | Major Domestic | 0.90 | 1,209 | 869 |
| 3 | Regional | 0.75 | 479 | 363 |
| 4 | Associate | 0.60 | 120 | 89 |
| 5 | Domestic T20 | 0.50 | 58 | 41 |

### 6.2 Tier Application
- Tier multipliers applied in `population_adjusted_aggregation.py`
- Competition-adjusted metrics (`*_comp_adj`) feed into shrinkage
- Verified: Fraser-McGurk has 6 competition entries across Tiers 1-3

---

## 7. DOMESTIC METRICS VALIDATION

### 7.1 Coverage
- **Batters**: 167 eligible (55% of 303) — 96 with domestic evidence
- **Bowlers**: 121 eligible (40% of 303) — 69 with domestic evidence

### 7.2 Calculation Integrity
- Batting Average = Runs / Dismissals (when dismissals > 0)
- Bowling Economy = (Runs / Balls) × 6
- Bowling Average = Runs / Wickets (when wickets > 0)
- **Validated**: No division-by-zero errors

---

## 8. STATISTICAL ANOMALY SCAN

| Check | Result |
|-------|--------|
| SR > 400 | ✅ NONE |
| Dismissal Rate > 1.0 | ✅ NONE |
| Economy > 20 | ✅ NONE |
| Wickets > Balls | ✅ NONE |
| Chase SR > 500 | ✅ NONE |

**Zero anomalies** across all 1,675 eligible player-seasons.

---

## 9. CRITICAL FINDINGS & RECOMMENDATIONS

### 9.1 Validated Correct (No Action Needed)
- ✅ Shrinkage formula (prior=30) correctly implemented
- ✅ Minimum sample flags gate evidence properly
- ✅ EQ Bowling 5-tier system codified with deployment boundaries
- ✅ Official rankings mathematically reproducible
- ✅ Sensitivity analysis confirms weight robustness
- ✅ Competition tier multipliers present in data

### 9.2 Documentation Gaps (P1 — HIGH)
1. **Population priors per tier** — Not explicitly documented; implied from data (~135 SR, ~7.5 econ)
2. **EQ Bowling tier definitions** — 5-tier logic in code but not in methodology docs
3. **Chase/Defend pressure formulas** — Methodology mentions RRR-CRR but exact formula not shown

### 9.3 Model Limitations (P2 — MEDIUM)
1. **Prior variation** — Implied priors differ (139.5 vs 132.6) suggesting tier-specific but undocumented
2. **Domestic data sparse** — Only 32%/23% coverage; not representative
3. **Form data limited** — Only 28/303 players have current form metrics

---

## 10. OUTPUT FILES CREATED

| File | Description |
|------|-------------|
| `outputs/audit/statistical_audit_summary.json` | Machine-readable summary |
| `docs/BATTING_BOWLING_STATISTICAL_AUDIT.md` | This document |

---

## 11. DATA INTEGRITY DETERMINATION

| Check | Status |
|-------|--------|
| Shrinkage math | ✅ PASS |
| Minimum evidence flags | ✅ PASS |
| Pressure metrics completeness | ✅ PASS |
| EQ Bowling deployment boundaries | ✅ PASS |
| Official ranking reproduction | ✅ PASS |
| Sensitivity analysis | ✅ PASS |
| Competition tier weights | ✅ PASS |
| Domestic calculations | ✅ PASS |
| Statistical anomalies | ✅ PASS (0 found) |

**OVERALL: PASS** — Statistical engine is mathematically sound and reproducible.

---

## 12. NEXT PHASE

**Phase 4: All 10 Dashboard Pages Audit** — Validate each page renders correct data, filters work, exports match.