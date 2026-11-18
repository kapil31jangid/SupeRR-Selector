# PRESSURE-X | Rajasthan Royals IPL 2027 Auction Intelligence

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://rrsuperselector.streamlit.app/)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/)
[![License: Proprietary](https://img.shields.io/badge/license-Proprietary-red.svg)]()

> **Evidence-Based T20 Pressure Performance Modeling & Long-Term Talent Scouting Strategy for Rajasthan Royals (IPL 2027)**  
> Developed for **SupeRR Selector Season 2**.

---

## 1. Executive Summary

Traditional T20 scouting heavily over-indexes on raw aggregate strike rates, overall economy, and unadjusted boundary counts across disparate global competitions. A strike rate of 160 in a domestic developmental league does not translate to high-leverage IPL playoff encounters against express pace and elite mystery spin.

**PRESSURE-X** solves this fundamental valuation problem through:

1. **Match-Situation Win Probability Weighting:** Evaluating ball-by-ball execution strictly under leverage (High-Extreme, Death Overs 17–20, Powerplay Overs 1–6, and 2nd Inning Run Chases).
2. **Empirical Bayes Shrinkage (James-Stein):** Pulling noisy low-sample rate metrics toward global population priors to eliminate small-sample noise.
3. **Cross-Tier Competition Calibration:** Adjusting raw performances across 5 competition tiers (T1 IPL baseline down to T5 domestic) using paired empirical factors.
4. **Evidence-Qualified (EQ) Bowling Formulation:** Replacing zero-opportunity shrinkage artifacts with evidence-weighted scores and codifying strict tactical deployment boundaries.
5. **Rajasthan Royals 40/30/20/10 Talent Scouting Framework:** Combining historical pressure performance with age runway, skill ceiling, and verified 2025–2026 competitive form.

---

## 2. System Architecture

```mermaid
flowchart TD
    subgraph Data Layer
        RAW["Raw Delivery Data<br/>(201,000+ balls, 5 Tiers)"] --> CLEAN["Data Cleaning &<br/>Extras Handling"]
        CLEAN --> STATE["Match State &<br/>Win Probability Reconstruction"]
    end

    subgraph Feature Engineering
        STATE --> FEAT["Phase Feature Aggregation<br/>(HE, Death, PP, Chase)"]
        FEAT --> SHRUNK["James-Stein Shrinkage &<br/>5-Tier Paired Adjustment"]
    end

    subgraph Core Models
        SHRUNK --> PM["Pressure Model<br/>(Bayesian Normalization)"]
        SHRUNK --> EQ["Evidence-Qualified<br/>Bowling Model"]
        PM --> RR["RR Scouting Model<br/>(40/30/20/10 Composite)"]
        EQ --> RR
    end

    subgraph Selection & Governance
        RETAIN["184 Retained Players Excluded"] --> ELIG["Eligibility & Rules Filter"]
        PAK["Pakistani Nationals Excluded"] --> ELIG
        ELIG --> RR
        RR --> SHORT["Final Combined Top 10 Batters<br/>Top 10 Bowlers & 8 Reserves"]
    end

    subgraph Presentation Layer
        SHORT --> DASH["Streamlit Interactive Dashboard<br/>(10 Pages, Plotly Visuals)"]
    end

    style RAW fill:#0B132B,stroke:#004BA0,color:#fff
    style PM fill:#1C2541,stroke:#EA1B86,color:#fff
    style EQ fill:#1C2541,stroke:#10B981,color:#fff
    style RR fill:#EA1B86,stroke:#F59E0B,stroke-width:2px,color:#fff
    style DASH fill:#004BA0,stroke:#EA1B86,stroke-width:2px,color:#fff
```

---

## 3. Official Verified Auction Shortlist (Archived Benchmark — View B)

The following 28 players represent the **immutable, audited shortlist** produced by the PRESSURE-X pipeline. This is the **archived benchmark (View B)** — the complete discovery universe contains **311 unique eligible players (664 player-seasons)** accessible via **View A** in the dashboard.

### 🏏 Top 10 Batters (Combined Indian + Overseas)

| Rank | Player | Country | Nationality | Age (2027) | Career Stage | Historical Pressure | RR Scouting Score | 2026 Form |
|:---:|:---|:---:|:---:|:---:|:---|:---:|:---:|:---:|
| **1** | **Jake Fraser-McGurk** | AUS | Overseas | 24 | Young development candidate | 92.20 | **91.88** | STRONG |
| **2** | **Jacob Bethell** | ENG | Overseas | 23 | Emerging | 87.18 | **90.27** | POSITIVE |
| **3** | **Harry Brook** | ENG | Overseas | 28 | Prime-age performer | 93.30 | **89.42** | STRONG |
| **4** | **Pathum Nissanka** | SL | Overseas | 28 | Prime-age performer | 86.07 | **81.13** | POSITIVE |
| **5** | **Shai Hope** | WI | Overseas | 33 | Experienced performer | 87.20 | **76.28** | STRONG |
| **6** | **M Shahrukh Khan** | IND | Indian | 31 | Experienced performer | 84.65 | **73.76** | POSITIVE |
| **7** | **Rilee Rossouw** | SA | Overseas | 37 | Experienced performer | 89.28 | **71.41** | POSITIVE |
| **8** | **Glenn Maxwell** | AUS | Overseas | 38 | Experienced performer | 89.04 | **70.92** | MIXED |
| **9** | **Karun Nair** | IND | Indian | 35 | Experienced performer | 88.02 | **68.41** | WEAK |
| **10** | **Vijay Shankar** | IND | Indian | 36 | Experienced performer | 85.63 | **66.85** | INSUFFICIENT DATA |

*Note on Bethell (#2) vs Brook (#3):* Harry Brook carries the higher base historical pressure score (93.30 vs 87.18), but Jacob Bethell ranks #2 overall due to his generational age runway (Age 23, Emerging category = 100 pts vs Brook Age 28 = 65 pts), unlocking an 8–10 year franchise core asset.

---

### 🎳 Top 10 Bowlers (Evidence-Qualified & Deployment Bound)

| Rank | Player | Country | Nationality | Age (2027) | Career Stage | EQ Bowling Score | RR Scouting Score | 2026 Form |
|:---:|:---|:---:|:---:|:---:|:---|:---:|:---:|:---:|
| **1** | **Mohammad Ghazanfar** | AFG | Overseas | 21 | Emerging | 70.30 | **84.52** | POSITIVE |
| **2** | **Ripon Mondol** | BAN | Overseas | 24 | Young development candidate | 78.63 | **81.95** | INSUFFICIENT DATA |
| **3** | **Mujeeb Ur Rahman** | AFG | Overseas | 26 | Young development candidate | 72.85 | **79.94** | POSITIVE |
| **4** | **Harry Tector** | IRE | Overseas | 27 | Prime-age performer | 75.71 | **76.18** | POSITIVE |
| **5** | **Matthew Forde** | WI | Overseas | 24 | Young development candidate | 68.76 | **75.80** | INSUFFICIENT DATA |
| **6** | **Ashton Agar** | AUS | Overseas | 33 | Experienced performer | 84.10 | **74.04** | POSITIVE |
| **7** | **Benjamin Sears** | NZ | Overseas | 29 | Prime-age performer | 71.14 | **73.26** | MIXED |
| **8** | **Michael Bracewell** | NZ | Overseas | 36 | Experienced performer | 82.69 | **69.48** | POSITIVE |
| **9** | **Sikandar Raza** | ZIM | Overseas | 40 | Experienced performer | 72.88 | **65.95** | STRONG |
| **10** | **Simarjeet Singh** | IND | Indian | 29 | Prime-age performer | 59.69 | **65.68** | MIXED |

#### 🚨 Codified Bowler Deployment Boundaries
- **Mohammad Ghazanfar (Rank 1):** Middle Overs Specialist (Overs 7–15). **Strict Prohibition:** Prohibited from death-phase and powerplay bowling in Year 1 due to 0 observed high-extreme deliveries.
- **Ripon Mondol (Rank 2):** Death-overs asset (54 observed death balls in dataset); developed under Shane Bond as high-pace death executioner.
- **Michael Bracewell (Rank 8):** Powerplay & middle matchup off-spinner vs LHB. **Strict Prohibition:** Zero death overs bowled; banned from death-overs assignment.
- **Harry Tector (Rank 4):** Matchup off-spin; prohibited from frontline death overs.

---

## 4. Rajasthan Royals Talent Scouting Model Formulation

The final ranking is determined by the multi-criteria optimization formula:

$$\text{RR Scouting Priority} = 0.40 \cdot S_{\text{Pressure}} + 0.30 \cdot S_{\text{Age/Dev}} + 0.20 \cdot S_{\text{Ceiling}} + 0.10 \cdot S_{\text{Form}}$$

Where:
- **$S_{\text{Pressure}}$ (40%):** Validated historical Bayesian pressure score (or Evidence-Qualified bowling score).
- **$S_{\text{Age/Dev}}$ (30%):** Development runway benchmark calculated as of **1 April 2027**:
  - Emerging ($\le 23$ yrs): **100 pts** (8–10+ year runway)
  - Young Development Candidate (24–26 yrs): **85 pts** (6–8 year runway)
  - Prime-Age Performer (27–30 yrs): **65 pts** (3–5 year peak window)
  - Experienced Tactical Asset ($\ge 31$ yrs): **50 pts** (Immediate 1–2 year impact)
- **$S_{\text{Ceiling}}$ (20%):** Composite technical ceiling, athletic fielding, bat speed, mystery variation, and tactical squad fit.
- **$S_{\text{Form}}$ (10%):** Audited 2025–2026 match logs across domestic and international leagues.

---

## 5. Interactive Scouting Dashboard (10 Pages)

The project includes a full-featured **Streamlit + Plotly** scouting application designed for franchise executives, analysts, and coaching staff.

### Page Overview

| Page | Title | Purpose |
|:---:|:---|:---|
| **1** | 📊 **Executive Overview** | High-level KPIs, qualification funnel, 3 platform views (A/B/C), CSV downloads |
| **2** | 🎯 **Scouting Explorer** | Filter-first table with **311 unique eligible players (664 player-seasons)**; role, nationality, age runway, quantitative thresholds, domestic T20 filters; live KPIs, tabbed analytics, player deep-dive |
| **3** | 📐 **Dynamic Ranking Engine** | Customizable 40/30/20/10 weight sliders (must sum to 100); 6 predefined profiles (RR Default, Pressure First, Youth Focus, Ceiling Chaser, Form Watcher, Balanced Evidence); missing data policies; sensitivity analysis with rank stability metrics; CSV export |
| **4** | 🛡️ **RR Current Squad** | 19 retained players with roles, ages, nationalities, retention types; role coverage matrix; age distribution; nationality split; CSV download |
| **5** | 🔍 **RR Gap Analysis** | Need vs strength matrix; vacancy fit scoring (role scarcity, age complementarity, nationality balance, skill gap); top auction targets per gap; retention value assessment |
| **6** | 🏏 **Domestic Intelligence** | Competition tier landscape (5 tiers); domestic batter/bowler leaderboards; competition-level drilldown; emerging domestic talent radar; domestic-to-IPL transition analysis with Tier 5 multiplier (0.68×) projections |
| **7** | ⚔️ **Player Comparison** | Multi-select comparison (up to 5 players); 5-dimension radar charts; metric summary tables; war-room player cards |
| **8** | 🤖 **AI Assistant** | Backboard × Google Gemini (gemini-2.5-pro); persistent conversation threads; candidate filtering before API call; deterministic fallback when offline |
| **9** | 📋 **Standard Scouting Report** | One-click CSV export with 60+ standardized columns; dynamic rankings export; official shortlist export |
| **10** | 📐 **Methodology & Reliability** | Mathematical formulations, shrinkage parameters, EQ bowling logic, data boundary disclosures, validation summary |

---

## 6. Quick Start & Execution Guide

### Prerequisites
- **Python 3.11** (pinned via `.python-version` for Streamlit Cloud)
- Virtual environment recommended

### Installation

```bash
# 1. Clone repository
git clone https://github.com/kapil31jangid/SupeRR-Selector.git
cd SupeRR-Selector

# 2. Install dependencies
pip install -r requirements.txt
```

### Launch Interactive Dashboard

```bash
# Run Streamlit dashboard locally
streamlit run app.py
```
*Access the local web dashboard at `http://localhost:8501`.*

### Run End-to-End Verification Pipeline

```bash
# Execute automated data validation and model initialization
python -m src.pipeline
```

### Run Automated Test Suite

```bash
# Backboard AI integration tests (48 tests)
python -m pytest tests/test_backboard_integration.py -v

# Scouting explorer tests (may need path updates for new output locations)
python -m pytest tests/test_scouting_explorer.py -v
```

---

## 7. Interactive Scouting Explorer & Optional Backboard AI

The **PRESSURE-X** dashboard is designed around a **filter-first architecture**: the primary scouting explorer operates independently through interactive controls, dynamic Plotly visual analytics, searchable candidate tables, and candidate comparison tools—without requiring any chatbot interaction.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   SECTION A: INTERACTIVE SCOUTING EXPLORER             │
│  • Role / Category Filters (Batter, Bowler, All-Rounder, Any)          │
│  • Nationality (Indian, Overseas, Country-Specific)                    │
│  • Age Runway Groups (Emerging ≤23, Development 24-26, Prime, Exp)     │
│  • Quantitative Thresholds (Pressure/EQ, RR Scouting Score, Balls)     │
│  • Real Domestic T20 Performance Filters (Runs, Avg, SR, Wkts, Econ)   │
│  • Observed Characteristics (Powerplay, Death Closer, Anchor, etc.)    │
│  • Live KPI Summary + Tabbed Table & Visual Analytics + Detail Deep-Dive│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Optional)
┌───────────────────────────────────▼────────────────────────────────────┐
│      SECTION B: ASK AI SCOUTING ASSISTANT (COLLAPSED BY DEFAULT)       │
│  • Backboard API Client with Google Gemini (gemini-2.5-pro)            │
│  • Explicit 'Generate AI Insights' trigger (no unsolicited API calls)  │
│  • Strict Evidence Boundary: AI only sees currently filtered candidates│
│  • Ground-Truth ID & Score Invariance (AI cannot hallucinate numbers)  │
│  • Persistent Conversational Memory via Backboard Threads              │
│  • Stale Insight Detection Alert when active filters change            │
│  • Graceful Offline Degradation: deterministic fallback when offline   │
└────────────────────────────────────────────────────────────────────────┘
```

### Setting Up Backboard API Key (Optional)

When Backboard API is configured, AI insights provide natural-language tactical rationales. Get your API key at [app.backboard.io/dashboard/api-keys](https://app.backboard.io/dashboard/api-keys), then configure it in either:

1. **Streamlit Secrets** (`.streamlit/secrets.toml`):
   ```toml
   BACKBOARD_API_KEY = "your_backboard_api_key_here"
   ```
2. **Environment Variable**:
   ```bash
   export BACKBOARD_API_KEY="your_backboard_api_key_here"  # Linux/macOS
   $env:BACKBOARD_API_KEY="your_backboard_api_key_here"    # PowerShell
   ```

*(Note: When no API key is provided, the dashboard functions completely with zero degradation and displays a gentle inline notice rather than an oversized error banner.)*

---

## 8. Project Directory Structure

```
SupeRR-Selector/
├── app.py                             ← Streamlit Interactive Scouting Dashboard (10 pages)
├── README.md                          ← Project Documentation & Landing Page
├── DATA_DICTIONARY.md                 ← Complete Dataset Field Specifications
├── requirements.txt                   ← Dependencies (pandas, numpy, scipy, streamlit, plotly, backboard-sdk)
├── .gitignore                         ← Virtualenv, cache, secrets exclusions
├── .python-version                    ← Python 3.11 pin for Streamlit Cloud
├── .env.example                       ← Environment variable template
│
├── data/
│   ├── raw/                           ← Immutable challenge source data (ball_by_ball, matches, etc.)
│   ├── processed/                     ← 11 cleaned, phase-annotated feature tables across 5 tiers
│   └── reference/
│       └── rr_current_squad.csv       ← 19 RR retained players (enriched)
│
├── models/
│   ├── pressure_model.py              ← Bayesian shrinkage & competition tier scoring
│   ├── bowling_eq_model.py            ← Evidence-Qualified bowling & tactical boundaries
│   └── rr_scouting_model.py           ← 40/30/20/10 RR Scouting Composite Engine
│
├── src/
│   ├── ai/                            ← Backboard AI Assistant (Google Gemini integration)
│   ├── data_cleaning/                 ← Delivery filtering & player identity normalization
│   ├── preprocessing/                 ← Match state reconstruction & competition tiers
│   ├── feature_engineering/           ← Phase feature aggregation & James-Stein shrinkage
│   ├── scoring/
│   │   └── dynamic_scouting_engine.py ← Dynamic ranking engine (custom weights, sensitivity)
│   ├── utilities/                     ← Automated data validator & relative path resolution
│   └── pipeline.py                    ← End-to-end execution runner
│
├── outputs/
│   ├── official_reference/            ← FINAL VERIFIED DELIVERABLES (immutable)
│   │   ├── final_combined_top10_batters.csv
│   │   ├── final_combined_top10_bowlers.csv
│   │   └── final_combined_reserves.csv
│   ├── supporting_evidence/           ← 16 forensic audit CSVs & markdown proofs
│   └── dataset_inventory.csv          ← Complete dataset inventory
│
├── dashboard/
│   ├── pages/                         ← 10 dashboard sub-pages
│   ├── components/                    ← KPI cards, player profiles, styled tables
│   ├── charts/                        ← Plotly bar charts, scatter plots, radar charts, distributions
│   └── utils/                         ← Cached data loaders & RR color palette
│
├── docs/
│   ├── FINAL_SUBMISSION_REPORT.md           ← Comprehensive submission playbook
│   ├── METHODOLOGY.md                       ← Mathematical formulation & shrinkage equations
│   ├── DATASET_COVERAGE_AUDIT.md            ← Dataset sources, coverage, player counts, gaps
│   ├── VALIDATION_AND_LIMITATIONS.md        ← Audit findings, ID corrections & caveats
│   ├── RR_SCOUTING_STRATEGY.md              ← Franchise talent development philosophy
│   ├── DEPLOYMENT_GUIDE.md                  ← Streamlit Cloud deployment instructions
│   ├── FINAL_PROJECT_AUDIT.md               ← Final acceptance engineering audit
│   ├── COMPLETE_CODEBASE_AUDIT_INVENTORY.md ← 40-dataset inventory, 80+ controls, 25+ datasets, 4 models, 7 calculation modules, AI integration, outputs, dependency map, 15+ risks
│   ├── PLAYER_IDENTITY_AND_ROLE_AUDIT.md    ← Player master deduplication (1,570→1,217 unique), role classification fix (All-rounder over-assignment), evidence thresholds
│   ├── DATASET_COVERAGE_RECONCILIATION_AUDIT.md ← 40-dataset inventory, 85 pure batters missing bowling data, domestic coverage (32%/23%), reconciliation matrix
│   ├── BATTING_BOWLING_STATISTICAL_AUDIT.md ← Shrinkage (prior=30), EQ bowling 5-tier, official scores 28/28 within 0.01, sensitivity max delta=3, zero anomalies
│   ├── DOMESTIC_INTELLIGENCE_BUG_FIX_REPORT.md ← 7 requirements fixed: thresholds, roles, two modes, multiple metrics, aggregates, validation notes, deployed
│   ├── REGRESSION_TEST_REPORT.md            ← 50 regression tests covering data loading, filtering, scoring, exports, AI, EQ bowling, data integrity, domestic intelligence
│   └── FINAL_VALIDATION_REPORT.md           ← All 14 phases passed, deployment approved
│
└── assets/
    └── rr_logo.png                    ← Rajasthan Royals official logo
```

---

## 9. Deployment Guide (Streamlit Community Cloud)

### Deployed URL
**Live Dashboard:** https://rrsuperselector.streamlit.app/

### Deployment Configuration
| Setting | Value |
|:---|:---|
| **Repository** | https://github.com/kapil31jangid/SupeRR-Selector |
| **Branch** | `main` |
| **Entry Point** | `app.py` |
| **Python Version** | 3.11 (pinned via `.python-version`) |
| **Dependencies** | `requirements.txt` |

### Steps to Deploy
1. Push repository to GitHub (already done)
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Click **New app**
4. Select repository: `kapil31jangid/SupeRR-Selector`
5. Branch: `main`, Main file: `app.py`
6. **Advanced Settings → Secrets** — add optional Backboard key:
   ```toml
   BACKBOARD_API_KEY = "your_backboard_api_key_here"
   ```
7. Click **Deploy!**

### Environment Variables
| Variable | Required | Description |
|:---|:---|:---|
| `BACKBOARD_API_KEY` | No | Enables AI Scouting Assistant (Google Gemini via Backboard) |

**The application works fully without the API key** — deterministic fallback is used.

---

## 10. Methodological Limitations & Integrity Declarations

- **Unobserved Bowling Phases:** Bowlers with 0 observed deliveries in specific pressure phases (e.g. Ghazanfar, Bracewell) are evaluated using Evidence-Qualified scoring across observed phases only; unobserved phases are never treated as proven capability.
- **Sample Size Restrictions:** A strict threshold of $\ge 100$ qualifying balls faced or bowled was enforced to prevent small-sample bias.
- **Auction Eligibility Filters:** All 184 retained players across the 10 IPL franchises and all Pakistani nationals were strictly excluded in compliance with BCCI regulations.
- **Challenge Scope:** PRESSURE-X was developed independently for the SupeRR Selector Season 2 competition and represents a proposed analytical scouting framework.
- **Archived Benchmark:** The 28-player shortlist (View B) is an immutable, audited benchmark. The complete discovery universe is **View A: 311 unique eligible players (664 player-seasons)** with dynamic ranking.

---

## 11. Repository & Deployment Status

| Metric | Value |
|:---|:---|
| **Repository** | https://github.com/kapil31jangid/SupeRR-Selector |
| **Live Dashboard** | https://rrsuperselector.streamlit.app/ |
| **Default Branch** | `main` |
| **Latest Commit** | `dd58776` (PRESSURE-X 2.0 forensic audit & bug fixes) |
| **Python Version** | 3.11 (pinned) |
| **Dependencies** | 8 packages in `requirements.txt` |

---

*PRESSURE-X | SupeRR Selector Season 2 | Rajasthan Royals IPL 2027 Auction Strategy Group*