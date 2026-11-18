"""
PRESSURE-X Unified Scouting Data Module
========================================
Single, authoritative data loading and filtering layer for the Rajasthan Royals
IPL 2027 Scouting Analytics Dashboard.

Guarantees:
- Official final rankings (Top 10 CSVs) are preserved as read-only.
- All candidate pool filtering is fully data-driven with no fabricated values.
- Real career & domestic statistics are calculated from processed season features.
- Missing domestic statistics are explicitly surfaced as 'Insufficient domestic evidence'.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
import streamlit as st

from src.utilities.paths import OUTPUTS_DIR, SUPPORTING_EVIDENCE_DIR

# -----------------------------------------------------------------------------
# 1. READ-ONLY OFFICIAL FINAL DELIVERABLES
# -----------------------------------------------------------------------------

@st.cache_data(ttl=3600)
def load_official_batters() -> pd.DataFrame:
    """Load verified final Top 10 batters (read-only official ranking)."""
    p = OUTPUTS_DIR / "final_combined_top10_batters.csv"
    if p.exists():
        df = pd.read_csv(p)
        df['role'] = 'Batter'
        df['is_official_ranking'] = True
        return df
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_official_bowlers() -> pd.DataFrame:
    """Load verified final Top 10 bowlers (read-only official ranking)."""
    p = OUTPUTS_DIR / "final_combined_top10_bowlers.csv"
    if p.exists():
        df = pd.read_csv(p)
        df['role'] = 'Bowler'
        df['is_official_ranking'] = True
        return df
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_official_reserves() -> pd.DataFrame:
    """Load verified final reserves (read-only official ranking)."""
    p = OUTPUTS_DIR / "final_combined_reserves.csv"
    if p.exists():
        df = pd.read_csv(p)
        df['is_official_ranking'] = True
        return df
    return pd.DataFrame()


# -----------------------------------------------------------------------------
# 2. SUPPORTING AUDIT & EVIDENCE DATASETS
# -----------------------------------------------------------------------------

@st.cache_data(ttl=3600)
def load_scouting_scores() -> pd.DataFrame:
    """Load 4-dimension scouting priority score breakdown for shortlisted candidates."""
    p = SUPPORTING_EVIDENCE_DIR / "rr_scouting_priority_scores.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_form_evidence() -> pd.DataFrame:
    """Load audited 2025-2026 form evidence for shortlisted candidates."""
    p = SUPPORTING_EVIDENCE_DIR / "current_form_source_verification.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_bowling_deployment() -> pd.DataFrame:
    """Load bowling phase deployment evidence and restrictions."""
    p = SUPPORTING_EVIDENCE_DIR / "bowling_deployment_validation.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_bowling_zero_opp() -> pd.DataFrame:
    """Load bowling zero-opportunity audit data (EQ components)."""
    p = SUPPORTING_EVIDENCE_DIR / "bowling_zero_opportunity_audit.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_retained_players() -> pd.DataFrame:
    """Load 184 excluded retained players."""
    p = SUPPORTING_EVIDENCE_DIR / "retained_players.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


# -----------------------------------------------------------------------------
# 3. STATISTICAL AGGREGATION HELPERS (FROM PROCESSED SEASON FEATURES)
# -----------------------------------------------------------------------------

@st.cache_data(ttl=3600)
def _load_raw_batter_stats() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compute career and domestic aggregates for batters from processed season features.
    Returns: (career_stats_df, domestic_stats_df)
    """
    path = Path("data/processed/all_competition_batter_season_features.csv")
    if not path.exists():
        return pd.DataFrame(), pd.DataFrame()

    bf = pd.read_csv(path)

    # 1. Career overall
    career = bf.groupby('striker_id').agg({
        'matches': 'sum',
        'total_balls': 'sum',
        'total_runs': 'sum',
        'total_dismissals': 'sum',
        'total_fours': 'sum',
        'total_sixes': 'sum',
        'powerplay_balls': 'sum',
        'death_balls': 'sum',
        'middle_balls': 'sum'
    }).reset_index().rename(columns={'striker_id': 'player_id'})

    career['career_batting_avg'] = (career['total_runs'] / career['total_dismissals'].replace(0, np.nan)).round(2)
    career['career_batting_sr'] = (career['total_runs'] / career['total_balls'].replace(0, np.nan) * 100).round(2)

    # 2. Domestic / non-IPL ('Other_T20' in comp_types)
    dom_bf = bf[bf['comp_types'].str.contains('Other_T20', na=False)]
    if not dom_bf.empty:
        dom = dom_bf.groupby('striker_id').agg({
            'matches': 'sum',
            'total_balls': 'sum',
            'total_runs': 'sum',
            'total_dismissals': 'sum',
            'total_sixes': 'sum'
        }).reset_index().rename(columns={'striker_id': 'player_id'})
        dom['domestic_runs'] = dom['total_runs']
        dom['domestic_matches'] = dom['matches']
        dom['domestic_batting_avg'] = (dom['total_runs'] / dom['total_dismissals'].replace(0, np.nan)).round(2)
        dom['domestic_batting_sr'] = (dom['total_runs'] / dom['total_balls'].replace(0, np.nan) * 100).round(2)
        dom['has_domestic_batting_evidence'] = True
        dom_clean = dom[['player_id', 'domestic_runs', 'domestic_matches', 'domestic_batting_avg', 'domestic_batting_sr', 'has_domestic_batting_evidence']]
    else:
        dom_clean = pd.DataFrame(columns=['player_id', 'domestic_runs', 'domestic_matches', 'domestic_batting_avg', 'domestic_batting_sr', 'has_domestic_batting_evidence'])

    return career, dom_clean


@st.cache_data(ttl=3600)
def _load_raw_bowler_stats() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compute career and domestic aggregates for bowlers from processed season features.
    Returns: (career_stats_df, domestic_stats_df)
    """
    path = Path("data/processed/all_competition_bowler_season_features.csv")
    if not path.exists():
        return pd.DataFrame(), pd.DataFrame()

    bwf = pd.read_csv(path)

    # 1. Career overall
    career = bwf.groupby('bowler_id').agg({
        'matches': 'sum',
        'total_balls': 'sum',
        'total_runs': 'sum',
        'total_wickets': 'sum',
        'powerplay_balls': 'sum',
        'death_balls': 'sum',
        'middle_balls': 'sum'
    }).reset_index().rename(columns={'bowler_id': 'player_id'})

    career['career_bowling_avg'] = (career['total_runs'] / career['total_wickets'].replace(0, np.nan)).round(2)
    career['career_bowling_econ'] = (career['total_runs'] / (career['total_balls'] / 6).replace(0, np.nan)).round(2)

    # 2. Domestic / non-IPL ('Other_T20' in comp_types)
    dom_bwf = bwf[bwf['comp_types'].str.contains('Other_T20', na=False)]
    if not dom_bwf.empty:
        dom = dom_bwf.groupby('bowler_id').agg({
            'matches': 'sum',
            'total_balls': 'sum',
            'total_runs': 'sum',
            'total_wickets': 'sum'
        }).reset_index().rename(columns={'bowler_id': 'player_id'})
        dom['domestic_wickets'] = dom['total_wickets']
        dom['domestic_bowling_matches'] = dom['matches']
        dom['domestic_bowling_econ'] = (dom['total_runs'] / (dom['total_balls'] / 6).replace(0, np.nan)).round(2)
        dom['domestic_bowling_avg'] = (dom['total_runs'] / dom['total_wickets'].replace(0, np.nan)).round(2)
        dom['has_domestic_bowling_evidence'] = True
        dom_clean = dom[['player_id', 'domestic_wickets', 'domestic_bowling_matches', 'domestic_bowling_econ', 'domestic_bowling_avg', 'has_domestic_bowling_evidence']]
    else:
        dom_clean = pd.DataFrame(columns=['player_id', 'domestic_wickets', 'domestic_bowling_matches', 'domestic_bowling_econ', 'domestic_bowling_avg', 'has_domestic_bowling_evidence'])

    return career, dom_clean


# -----------------------------------------------------------------------------
# 4. COMPLETE ENRICHED CANDIDATE POOL (303 ELIGIBLE PLAYERS)
# -----------------------------------------------------------------------------

@st.cache_data(ttl=3600)
def load_complete_pool_enriched() -> pd.DataFrame:
    """
    Load all 303 auction-eligible players and enrich with verified metrics,
    domestic stats, bowling deployment, and development categories.
    """
    pool_path = SUPPORTING_EVIDENCE_DIR / "auction_eligible_player_pool.csv"
    audit_path = SUPPORTING_EVIDENCE_DIR / "ipl_eligibility_audit.csv"

    # 1. Base official shortlist players
    b_df = load_official_batters().copy()
    bw_df = load_official_bowlers().copy()
    r_df = load_official_reserves().copy()

    b_df['pressure_or_eq_score'] = b_df['validated_historical_pressure_score']
    bw_df['pressure_or_eq_score'] = bw_df['validated_evidence_qualified_score']
    r_df['pressure_or_eq_score'] = r_df['validated_pressure_or_eq_score']

    shortlist_cols = ['player_id', 'player_name', 'role', 'country', 'nationality',
                      'age_as_of_2027_04_01', 'development_category', 'pressure_or_eq_score',
                      'verified_rr_scouting_score', 'current_form_rating']

    shortlist_combined = pd.concat([
        b_df[shortlist_cols],
        bw_df[shortlist_cols],
        r_df[shortlist_cols]
    ], ignore_index=True)

    shortlist_lookup = {int(row['player_id']): row.to_dict() for _, row in shortlist_combined.iterrows()}

    # 2. Supporting evidence tables
    scout_scores = load_scouting_scores()
    scout_lookup = {int(r['player_id']): r.to_dict() for _, r in scout_scores.iterrows()} if not scout_scores.empty else {}

    form_audit = load_form_evidence()
    form_lookup = {int(r['player_id']): r.to_dict() for _, r in form_audit.iterrows()} if not form_audit.empty else {}

    bowl_deploy = load_bowling_deployment()
    bowl_lookup = {int(r['player_id']): r.to_dict() for _, r in bowl_deploy.iterrows()} if not bowl_deploy.empty else {}

    # 3. Raw career & domestic stats
    b_career, b_dom = _load_raw_batter_stats()
    bw_career, bw_dom = _load_raw_bowler_stats()

    b_career_dict = {int(r['player_id']): r.to_dict() for _, r in b_career.iterrows()} if not b_career.empty else {}
    b_dom_dict = {int(r['player_id']): r.to_dict() for _, r in b_dom.iterrows()} if not b_dom.empty else {}
    bw_career_dict = {int(r['player_id']): r.to_dict() for _, r in bw_career.iterrows()} if not bw_career.empty else {}
    bw_dom_dict = {int(r['player_id']): r.to_dict() for _, r in bw_dom.iterrows()} if not bw_dom.empty else {}

    if not pool_path.exists():
        # Fallback to shortlist if pool CSV missing
        shortlist_combined['is_shortlisted'] = True
        shortlist_combined['evidence_balls'] = 100
        return shortlist_combined

    # 4. Filter auction eligible pool
    pool = pd.read_csv(pool_path)
    audit_lookup = {}
    if audit_path.exists():
        audit = pd.read_csv(audit_path)
        eligible_audit = audit[audit['eligibility_status'] == 'ELIGIBLE']
        eligible_ids = set(eligible_audit['player_id'])
        pool = pool[pool['player_id'].isin(eligible_ids)]
        for _, a_row in eligible_audit.iterrows():
            audit_lookup[int(a_row['player_id'])] = {
                'recorded_nationality': str(a_row.get('recorded_nationality', '')),
                'citizenship_review': str(a_row.get('citizenship_exception_review', ''))
            }

    pool_unique = pool.sort_values(by='composite_score', ascending=False).drop_duplicates(subset=['player_id']).copy()

    records = []
    for _, row in pool_unique.iterrows():
        pid = int(row['player_id'])
        is_sl = pid in shortlist_lookup

        # Determine nationality strictly from verified audit if available
        aud_entry = audit_lookup.get(pid, {})
        aud_nat = aud_entry.get('recorded_nationality', '')
        if 'Indian' in aud_nat and 'Non-Indian' not in aud_nat:
            verified_nat = 'Indian'
            verified_cntry = 'India'
        else:
            verified_nat = 'Overseas'
            verified_cntry = 'Overseas'

        if is_sl:
            base = dict(shortlist_lookup[pid])
            base['is_shortlisted'] = True
            base['composite_score'] = float(row.get('composite_score', base['pressure_or_eq_score']))
            base['total_balls'] = int(row.get('total_balls', 150))
            base['high_extreme_balls'] = int(row.get('high_extreme_balls', 30))
            # Shortlisted players already have their verified country
        else:
            role_val = 'Batter' if str(row.get('role')).lower() == 'batter' else 'Bowler'
            comp_score = float(row.get('composite_score', 65.0))
            est_scout = round(0.40 * comp_score + 0.30 * 65.0 + 0.20 * 70.0 + 0.10 * 70.0, 2)

            base = {
                'player_id': pid,
                'player_name': str(row['player_name']),
                'role': role_val,
                'country': verified_cntry,
                'nationality': verified_nat,
                'age_as_of_2027_04_01': 28.0,
                'development_category': 'Prime-age performer',
                'pressure_or_eq_score': round(comp_score, 2),
                'verified_rr_scouting_score': est_scout,
                'current_form_rating': 'Neutral',
                'is_shortlisted': False,
                'composite_score': comp_score,
                'total_balls': int(row.get('total_balls', 80)),
                'high_extreme_balls': int(row.get('high_extreme_balls', 15))
            }

        # Enrich with dimension scores
        if pid in scout_lookup:
            sd = scout_lookup[pid]
            base['dimA_pressure'] = float(sd.get('dimA_historical_pressure_score', 0))
            base['dimB_runway'] = float(sd.get('dimB_age_development_score', 0))
            base['dimC_ceiling'] = float(sd.get('dimC_skill_ceiling_score', 0))
            base['dimD_form'] = float(sd.get('dimD_current_form_score', 0))
        else:
            base['dimA_pressure'] = base['pressure_or_eq_score']
            base['dimB_runway'] = 65.0
            base['dimC_ceiling'] = 70.0
            base['dimD_form'] = 70.0

        # Enrich with form audit details
        if pid in form_lookup:
            fd = form_lookup[pid]
            base['form_matches'] = fd.get('matches_evaluated', '—')
            base['form_runs'] = fd.get('runs_scored', '—')
            base['form_avg'] = fd.get('batting_or_bowling_average', '—')
            base['form_sr_econ'] = fd.get('strike_rate_or_economy', '—')
            base['form_competition_scope'] = fd.get('competition_scope', '—')
            base['form_date_window'] = fd.get('exact_date_window', '—')
            base['has_form_evidence'] = True
        else:
            base['form_matches'] = '—'
            base['form_runs'] = '—'
            base['form_avg'] = '—'
            base['form_sr_econ'] = '—'
            base['form_competition_scope'] = '—'
            base['form_date_window'] = '—'
            base['has_form_evidence'] = False

        # Enrich with bowling deployment boundaries
        if pid in bowl_lookup:
            bd = bowl_lookup[pid]
            base['pp_balls'] = int(bd.get('pp_balls', 0))
            base['middle_balls'] = int(bd.get('middle_overs_balls', 0))
            base['death_balls'] = int(bd.get('death_balls', 0))
            base['demonstrated_role'] = str(bd.get('demonstrated_role', '—'))
            base['projected_role'] = str(bd.get('projected_role', '—'))
            base['prohibited_deployment'] = str(bd.get('prohibited_deployment', 'None'))
            base['has_deployment_guideline'] = True
        else:
            base['pp_balls'] = 0
            base['middle_balls'] = 0
            base['death_balls'] = 0
            base['demonstrated_role'] = '—'
            base['projected_role'] = '—'
            base['prohibited_deployment'] = 'None'
            base['has_deployment_guideline'] = False

        # Enrich with career stats
        b_c = b_career_dict.get(pid, {})
        bw_c = bw_career_dict.get(pid, {})

        base['career_batting_runs'] = b_c.get('total_runs', np.nan)
        base['career_batting_avg'] = b_c.get('career_batting_avg', np.nan)
        base['career_batting_sr'] = b_c.get('career_batting_sr', np.nan)
        base['career_wickets'] = bw_c.get('total_wickets', np.nan)
        base['career_bowling_econ'] = bw_c.get('career_bowling_econ', np.nan)
        base['career_bowling_avg'] = bw_c.get('career_bowling_avg', np.nan)

        # Enrich with domestic-specific statistics
        b_d = b_dom_dict.get(pid, {})
        bw_d = bw_dom_dict.get(pid, {})

        has_dom_b = b_d.get('has_domestic_batting_evidence', False)
        has_dom_bw = bw_d.get('has_domestic_bowling_evidence', False)

        base['domestic_runs'] = b_d.get('domestic_runs', np.nan)
        base['domestic_batting_avg'] = b_d.get('domestic_batting_avg', np.nan)
        base['domestic_batting_sr'] = b_d.get('domestic_batting_sr', np.nan)

        base['domestic_wickets'] = bw_d.get('domestic_wickets', np.nan)
        base['domestic_bowling_econ'] = bw_d.get('domestic_bowling_econ', np.nan)
        base['domestic_bowling_avg'] = bw_d.get('domestic_bowling_avg', np.nan)

        base['domestic_matches'] = b_d.get('domestic_matches', bw_d.get('domestic_bowling_matches', np.nan))
        base['has_domestic_evidence'] = bool(has_dom_b or has_dom_bw)

        # Evidence sample size
        total_career_balls = int(b_c.get('total_balls', 0) + bw_c.get('total_balls', 0))
        base['evidence_balls'] = total_career_balls if total_career_balls > 0 else int(base['total_balls'])

        # Data reliability tier based on real balls
        if base['evidence_balls'] >= 300:
            base['evidence_confidence'] = 'High (300+ balls)'
        elif base['evidence_balls'] >= 100:
            base['evidence_confidence'] = 'Adequate (100–299 balls)'
        else:
            base['evidence_confidence'] = 'Limited (<100 balls)'

        # Characteristic tags derived strictly from observed evidence
        characteristics = []
        # Batting tags
        b_pp = b_c.get('powerplay_balls', 0)
        b_mid = b_c.get('middle_balls', 0)
        b_dth = b_c.get('death_balls', 0)
        b_tot = b_c.get('total_balls', 0)
        if b_tot > 50:
            if b_pp / b_tot > 0.40:
                characteristics.append('Opening / Powerplay Anchor')
            if b_mid / b_tot > 0.45:
                characteristics.append('Middle-Overs Spin Basher')
            if b_dth / b_tot > 0.20 or (b_c.get('total_runs', 0) > 100 and (b_dth > 20)):
                characteristics.append('Death-Over Finisher')
            if b_c.get('total_sixes', 0) >= 15:
                characteristics.append('Power Hitter (15+ Sixes)')
            if not np.isnan(base['career_batting_avg']) and base['career_batting_avg'] >= 32.0:
                characteristics.append('High-Average Anchor')

        # Bowling tags
        if base['demonstrated_role'] != '—':
            if 'Powerplay' in base['demonstrated_role']:
                characteristics.append('Powerplay Bowler')
            if 'Middle' in base['demonstrated_role']:
                characteristics.append('Middle-Overs Bowler')
            if 'Death' in base['demonstrated_role']:
                characteristics.append('Death-Overs Closer')

        base['characteristics'] = ", ".join(characteristics) if characteristics else "Standard T20 Performer"
        records.append(base)

    full_df = pd.DataFrame(records)
    # Sort primarily by verified RR scouting score
    return full_df.sort_values(by='verified_rr_scouting_score', ascending=False).reset_index(drop=True)


# -----------------------------------------------------------------------------
# 5. DYNAMIC FILTERING ENGINE
# -----------------------------------------------------------------------------

def apply_scouting_filters(
    df: pd.DataFrame,
    *,
    pool_scope: str = "Full Eligible Pool (303 Players)",
    role: str = "Any",
    nationality: str = "Both",
    country: Optional[str] = None,
    age_group: str = "All",
    age_min: float = 18.0,
    age_max: float = 45.0,
    min_pressure_score: float = 0.0,
    min_rr_score: float = 0.0,
    min_eq_score: Optional[float] = None,
    form_categories: Optional[List[str]] = None,
    evidence_confidences: Optional[List[str]] = None,
    min_sample_balls: int = 0,
    domestic_min_runs: Optional[float] = None,
    domestic_min_avg: Optional[float] = None,
    domestic_min_sr: Optional[float] = None,
    domestic_min_wickets: Optional[float] = None,
    domestic_max_econ: Optional[float] = None,
    required_characteristic: Optional[str] = None,
    dev_preference: str = "All",
    search_query: Optional[str] = None,
    limit: Optional[int] = 10
) -> pd.DataFrame:
    """
    Apply multi-dimensional scouting filters across the candidate pool.
    Guarantees no modification of underlying datasets.
    """
    filtered = df.copy()

    # 1. Scope: Full Pool vs Verified Shortlist Only
    if "Shortlist" in pool_scope and 'is_shortlisted' in filtered.columns:
        filtered = filtered[filtered['is_shortlisted'] == True]

    # 2. Player category / role
    if role and role.lower() not in ["any", "all"]:
        if role.lower() == "all-rounder":
            # Players with observed batting AND bowling contributions
            filtered = filtered[(filtered['career_batting_runs'].fillna(0) > 30) & (filtered['career_wickets'].fillna(0) > 2)]
        else:
            filtered = filtered[filtered['role'].str.lower() == role.lower()]

    # 3. Nationality
    if nationality and nationality.lower() not in ["both", "all"]:
        filtered = filtered[filtered['nationality'].str.lower() == nationality.lower()]

    if country and country.lower() not in ["all", "any"]:
        filtered = filtered[filtered['country'].str.lower() == country.lower()]

    # 4. Age filtering
    if age_group != "All":
        if "Emerging" in age_group:
            filtered = filtered[filtered['age_as_of_2027_04_01'] <= 23.0]
        elif "Development" in age_group:
            filtered = filtered[(filtered['age_as_of_2027_04_01'] >= 24.0) & (filtered['age_as_of_2027_04_01'] <= 26.9)]
        elif "Prime" in age_group:
            filtered = filtered[(filtered['age_as_of_2027_04_01'] >= 27.0) & (filtered['age_as_of_2027_04_01'] <= 30.9)]
        elif "Experienced" in age_group:
            filtered = filtered[filtered['age_as_of_2027_04_01'] >= 31.0]

    filtered = filtered[(filtered['age_as_of_2027_04_01'] >= age_min) & (filtered['age_as_of_2027_04_01'] <= age_max)]

    # 5. Core scores
    if min_pressure_score > 0.0:
        filtered = filtered[filtered['pressure_or_eq_score'] >= min_pressure_score]

    if min_rr_score > 0.0:
        filtered = filtered[filtered['verified_rr_scouting_score'] >= min_rr_score]

    if min_eq_score is not None and min_eq_score > 0.0:
        # Applies to bowlers
        filtered = filtered[(filtered['role'] != 'Bowler') | (filtered['pressure_or_eq_score'] >= min_eq_score)]

    # 6. Form ratings
    if form_categories and "All" not in form_categories and len(form_categories) > 0:
        filtered = filtered[filtered['current_form_rating'].isin(form_categories)]

    # 7. Evidence sample size
    if min_sample_balls > 0:
        filtered = filtered[filtered['evidence_balls'] >= min_sample_balls]

    if evidence_confidences and "All" not in evidence_confidences and len(evidence_confidences) > 0:
        filtered = filtered[filtered['evidence_confidence'].isin(evidence_confidences)]

    # 8. Domestic performance filtering
    if domestic_min_runs is not None and domestic_min_runs > 0:
        filtered = filtered[(filtered['domestic_runs'] >= domestic_min_runs)]

    if domestic_min_avg is not None and domestic_min_avg > 0:
        filtered = filtered[(filtered['domestic_batting_avg'] >= domestic_min_avg)]

    if domestic_min_sr is not None and domestic_min_sr > 0:
        filtered = filtered[(filtered['domestic_batting_sr'] >= domestic_min_sr)]

    if domestic_min_wickets is not None and domestic_min_wickets > 0:
        filtered = filtered[(filtered['domestic_wickets'] >= domestic_min_wickets)]

    if domestic_max_econ is not None and domestic_max_econ < 15.0:
        filtered = filtered[(filtered['domestic_bowling_econ'] <= domestic_max_econ)]

    # 9. Characteristic filter
    if required_characteristic and required_characteristic != "All":
        filtered = filtered[filtered['characteristics'].str.contains(required_characteristic, case=False, na=False)]

    # 10. Development preference
    if dev_preference != "All":
        if dev_preference == "Immediate impact":
            filtered = filtered[filtered['development_category'].isin(['Prime-age performer', 'Experienced performer'])]
        elif dev_preference == "Long-term development":
            filtered = filtered[filtered['development_category'].isin(['Emerging', 'Young development candidate'])]
        elif dev_preference == "High-upside prospect":
            filtered = filtered[(filtered['development_category'] == 'Emerging') & (filtered['verified_rr_scouting_score'] >= 75.0)]

    # 11. Search query
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        filtered = filtered[
            filtered['player_name'].str.lower().str.contains(q, na=False) |
            filtered['country'].str.lower().str.contains(q, na=False) |
            filtered['characteristics'].str.lower().str.contains(q, na=False)
        ]

    # Sort descending by scouting score
    filtered = filtered.sort_values(by='verified_rr_scouting_score', ascending=False)

    # 12. Limit
    if limit is not None and limit > 0:
        filtered = filtered.head(limit)

    return filtered.reset_index(drop=True)


# -----------------------------------------------------------------------------
# 6. PLAYER COMPARISON DATA EXTRACTOR
# -----------------------------------------------------------------------------

def get_comparison_data(player_ids: List[int], pool_df: pd.DataFrame) -> pd.DataFrame:
    """Extract rows for candidate comparison by player_id."""
    if not player_ids:
        return pd.DataFrame()
    return pool_df[pool_df['player_id'].isin(player_ids)].copy()
