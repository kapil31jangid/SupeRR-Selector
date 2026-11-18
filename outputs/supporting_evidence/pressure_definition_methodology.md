# Pressure Definition Methodology
Pressure-X Feature Engineering — SupeRR Selector Season 2

**Generated:** 2026-11-17  
**Version:** 1.0

---

## Overview

This document defines the pressure contexts used in the Pressure-X feature engineering pipeline. Pressure is categorized into four levels: **Low**, **Medium**, **High**, and **Extreme**, separately for batting and bowling. Definitions are transparent, interpretable, and based on cricket match situation fundamentals.

---

## Core Principles

1. **No invented metrics** — Only use information available *before* each delivery
2. **Separate 1st and 2nd innings** — Chase context fundamentally changes pressure
3. **Continuous + Categorical** — Preserve raw continuous variables (RRR, CRR, wickets, balls) alongside categorical labels
4. **Documented thresholds** — Every boundary is explicit and justifiable
5. **Reproducible** — Same inputs always produce same pressure labels

---

## Key Pre-Delivery State Variables

Available for every delivery (computed from match state reconstruction):

| Variable | Description | 1st Innings | 2nd Innings |
|----------|-------------|-------------|-------------|
| `current_run_rate` (CRR) | Runs per over so far | ✅ | ✅ |
| `required_run_rate` (RRR) | Runs per over needed to win | ❌ | ✅ |
| `wickets_before` | Wickets fallen | ✅ | ✅ |
| `wickets_remaining` | 10 - wickets_before | ✅ | ✅ |
| `legal_balls_before` | Legal balls bowled | ✅ | ✅ |
| `legal_balls_remaining` | 120 - legal_balls_before (or revised) | ✅ | ✅ |
| `overid` | Current over (1-20) | ✅ | ✅ |
| `phase` | powerplay (1-6), middle (7-15), death (16-20) | ✅ | ✅ |
| `target` | Chase target | ❌ | ✅ |
| `required_runs` | target - score_before | ❌ | ✅ |

---

## Batting Pressure Definition

### 2nd Innings (Chase) — Primary Definition

Pressure increases when the **required run rate (RRR)** exceeds what's comfortably achievable, especially with fewer wickets and balls remaining.

| Category | Conditions (ANY true) | Rationale |
|----------|----------------------|-----------|
| **Extreme** | RRR > 12 **OR** (balls < 30 AND RRR > 10) **OR** (wickets ≤ 5 AND RRR > 8) | Near-impossible ask; must take extreme risks |
| **High** | RRR ≥ 9 **OR** (over ≥ 16 AND RRR > 7) | Difficult chase; high boundary requirement |
| **Medium** | RRR ≥ 7 **OR** (middle overs AND wickets ≤ 6) | Challenging; need sustained scoring |
| **Low** | Otherwise | Comfortable or manageable |

**Threshold Justification:**
- RRR 12+ = 2 runs/ball (only boundaries suffice)
- RRR 9-12 = 1.5-2 runs/ball (boundaries + rotation)
- RRR 7-9 = 1.16-1.5 runs/ball (good rotation + occasional boundaries)
- Death overs (16+) amplify pressure due to ball scarcity

### 1st Innings (Setting Target) — Secondary Definition

No RRR exists. Pressure derives from **scoring rate vs. phase par** and **wickets lost**.

| Category | Conditions (ANY true) | Rationale |
|----------|----------------------|-----------|
| **Extreme** | (PP AND wickets ≥ 4) **OR** (Middle AND wickets ≥ 6) **OR** (Death AND wickets ≥ 8) | Collapse imminent; survival mode |
| **High** | (PP AND CRR < 6 AND wickets ≥ 2) **OR** (Middle AND CRR < 7 AND wickets ≥ 4) **OR** (Death AND CRR < 9 AND wickets ≥ 6) | Well below par with wickets down |
| **Medium** | (PP AND wickets ≥ 2) **OR** (Middle AND wickets ≥ 3) **OR** (Death AND wickets ≥ 4) | Wickets falling; need consolidation |
| **Low** | Otherwise | Platform building or acceleration phase |

**Par Scores (approximate):**
- Powerplay (1-6): 8-9 RPO
- Middle (7-15): 7-8 RPO
- Death (16-20): 9-10 RPO

---

## Bowling Pressure Definition

### 2nd Innings (Defending) — Primary Definition

Bowling pressure is **inverse** of batting pressure: high when the batting team is *comfortable* (low RRR, wickets in hand), low when batting team is *struggling*.

| Category | Conditions (ANY true) | Rationale |
|----------|----------------------|-----------|
| **Extreme** | (over ≥ 17 AND wickets_taken ≤ 2 AND RRR < 8) | Batting team cruising; death overs, few wickets |
| **High** | (over ≥ 12 AND wickets_taken ≤ 3 AND RRR < 9) | Batting team on track; middle/death |
| **Medium** | (PP AND wickets_taken = 0) **OR** (Middle AND wickets_taken ≤ 2) | No early breakthroughs |
| **Low** | Otherwise | Bowling team in control |

**Note:** RRR < CRR means batting team ahead of required rate — pressure on bowlers.

### 1st Innings (Restricting) — Secondary Definition

Pressure when opposition scores **above par** for the phase.

| Category | Conditions (ANY true) | Rationale |
|----------|----------------------|-----------|
| **Extreme** | (PP AND CRR > 10 AND 0 wickets) **OR** (Middle AND CRR > 9 AND ≤1 wicket) **OR** (Death AND CRR > 11 AND ≤3 wickets) | Opposition dominating |
| **High** | (PP AND CRR > 9) **OR** (Middle AND CRR > 8) **OR** (Death AND CRR > 10) | Well above par |
| **Medium** | (PP AND CRR > 7) **OR** (Middle AND CRR > 7) **OR** (Death AND CRR > 9) | At or slightly above par |
| **Low** | Otherwise | Bowling team containing |

---

## Continuous Pressure Variables (Preserved)

| Variable | Formula | Interpretation |
|----------|---------|----------------|
| `rrr_minus_crr` | RRR - CRR (2nd inn) | >0 = behind rate, <0 = ahead |
| `wickets_remaining` | 10 - wickets_before | Resources left |
| `balls_per_wicket` | legal_balls_before / max(1, wickets_before) | Wicket frequency |
| `runs_per_ball_required` | required_runs / legal_balls_remaining | Per-ball requirement |
| `chase_difficulty` | RRR / 6 | Normalized difficulty (1.0 = 6 RPO) |
| `wickets_in_hand` | 10 - wickets_before | Categorical: low ≤3, med 4-6, high >6 |

---

## Phase Definitions

| Phase | Overs | Strategic Context |
|-------|-------|-------------------|
| Powerplay | 1-6 | Field restrictions; maximize scoring |
| Middle | 7-15 | Consolidation; rotate strike |
| Death | 16-20 | Maximize boundaries; high risk |

---

## Edge Case Handling

| Situation | Handling |
|-----------|----------|
| `legal_balls_remaining = 0` | RRR = 0, required_runs clipped at 0 |
| `wickets_before = 10` | Innings over (should not occur in primary data) |
| Revised targets (DLS) | Use `revised_target` and `second_inn_revised_overs` from matches.csv |
| Super Over | Excluded entirely (innings 3/4) |
| Abandoned match | Excluded entirely |
| `extras_type = 'other'` | Excluded from primary aggregates |

---

## Implementation Code Reference

```python
# Batting pressure (2nd innings)
def batting_pressure_2nd(row):
    rrr = row['required_run_rate']
    wkts_rem = 10 - row['wickets_before']
    balls_rem = row['legal_balls_remaining']
    if rrr > 12 or (balls_rem < 30 and rrr > 10) or (wkts_rem <= 5 and rrr > 8):
        return 'extreme'
    elif rrr >= 9 or (row['overid'] >= 16 and rrr > 7):
        return 'high'
    elif rrr >= 7 or (row['phase'] == 'middle' and wkts_rem <= 6):
        return 'medium'
    else:
        return 'low'

# Bowling pressure (2nd innings)
def bowling_pressure_2nd(row):
    rrr = row['required_run_rate']
    wkts_taken = row['wickets_before']
    if row['overid'] >= 17 and wkts_taken <= 2 and rrr < 8:
        return 'extreme'
    elif row['overid'] >= 12 and wkts_taken <= 3 and rrr < 9:
        return 'high'
    elif (row['phase'] == 'powerplay' and wkts_taken == 0) or \
         (row['phase'] == 'middle' and wkts_taken <= 2):
        return 'medium'
    else:
        return 'low'
```

---

## Validation of Pressure Distributions (IPL Primary)

| Category | Batting Deliveries | % | Bowling Deliveries | % |
|----------|-------------------|---|-------------------|---|
| Low | 31,641 | 36.2% | 37,599 | 43.0% |
| Medium | 23,135 | 26.5% | 25,242 | 28.9% |
| High | 17,881 | 20.5% | 17,639 | 20.2% |
| Extreme | 14,776 | 16.9% | 6,953 | 8.0% |
| **Total** | **87,433** | **100%** | **87,433** | **100%** |

**Interpretation:** Distributions are well-spread across categories, with more extreme batting pressure than bowling pressure (as expected — batting team feels chase pressure more acutely).

---

## Assumptions & Limitations

1. **Standard 20-over innings** — Revised overs handled via matches.csv but not all edge cases covered
2. **No player-specific par** — Uses league-average par scores
3. **No opposition quality adjustment** — Pressure is absolute, not relative to opponent strength
4. **No venue/conditions adjustment** — Same thresholds apply across all venues
5. **Wicket value constant** — Each wicket treated equally (no batter quality weighting)
6. **No momentum/state carryover** — Each delivery independent given pre-delivery state

---

## Future Refinements

- Venue-specific par scores
- Opposition bowling/batting strength adjustment
- Batter/bowler matchup pressure
- Momentum indicators (recent boundaries/wickets)
- DLS-aware pressure for rain-affected matches