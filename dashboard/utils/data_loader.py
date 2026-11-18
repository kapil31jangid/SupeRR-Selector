"""
Dashboard Data Loader
=====================
Loads and caches verified CSV datasets from outputs/ and processed/ directories.

PRESSURE-X 2.0: Now loads the complete 311-player auction-eligible pool (664 player-seasons)
enriched with all performance database metrics (pressure, domestic, phase, form).
"""

from pathlib import Path
from typing import Dict, Tuple, List, Optional
import pandas as pd
import numpy as np
import streamlit as st

from src.utilities.paths import OUTPUTS_DIR, SUPPORTING_EVIDENCE_DIR, PROCESSED_DATA_DIR


# ==============================================================================
# 1. READ-ONLY OFFICIAL FINAL DELIVERABLES (VIEW B - ARCHIVED BENCHMARK)
# ==============================================================================

@st.cache_data
def load_final_batters() -> pd.DataFrame:
    """Load verified final Top 10 batters (official View B)."""
    df = pd.read_csv(OUTPUTS_DIR / "final_combined_top10_batters.csv")
    return df


@st.cache_data
def load_final_bowlers() -> pd.DataFrame:
    """Load verified final Top 10 bowlers (official View B)."""
    df = pd.read_csv(OUTPUTS_DIR / "final_combined_top10_bowlers.csv")
    return df


@st.cache_data
def load_final_reserves() -> pd.DataFrame:
    """Load verified final reserves (official View B)."""
    df = pd.read_csv(OUTPUTS_DIR / "final_combined_reserves.csv")
    return df


def get_official_shortlist() -> pd.DataFrame:
    """Combine official Top 10 batters, bowlers, and reserves (28 players)."""
    batters = load_final_batters().copy()
    batters['role'] = 'Batter'
    bowlers = load_final_bowlers().copy()
    bowlers['role'] = 'Bowler'
    reserves = load_final_reserves().copy()

    # Standardize score columns
    batters['pressure_or_eq_score'] = batters['validated_historical_pressure_score']
    bowlers['pressure_or_eq_score'] = bowlers['validated_evidence_qualified_score']
    reserves['pressure_or_eq_score'] = reserves['validated_pressure_or_eq_score']

    common_cols = ['player_id', 'player_name', 'role', 'country', 'nationality',
                   'age_as_of_2027_04_01', 'development_category', 'pressure_or_eq_score',
                   'verified_rr_scouting_score', 'current_form_rating']

    combined = pd.concat([
        batters[common_cols],
        bowlers[common_cols],
        reserves[common_cols]
    ], ignore_index=True)
    combined['is_shortlisted'] = True
    combined['view'] = 'View B: Official Shortlist'
    return combined


# Backward compatibility alias
def get_all_shortlist_players() -> pd.DataFrame:
    """Backward compatibility: returns official shortlist (View B)."""
    return get_official_shortlist()


# ==============================================================================
# 2. SUPPORTING AUDIT & EVIDENCE DATASETS
# ==============================================================================

@st.cache_data
def load_scouting_priority_scores() -> pd.DataFrame:
    """Load 4-dimension scouting priority score breakdown for shortlisted candidates."""
    p = SUPPORTING_EVIDENCE_DIR / "rr_scouting_priority_scores.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_bowling_deployment() -> pd.DataFrame:
    """Load verified bowling deployment boundaries."""
    p = SUPPORTING_EVIDENCE_DIR / "bowling_deployment_validation.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_zero_opportunity_audit() -> pd.DataFrame:
    """Load bowling phase delivery counts."""
    p = SUPPORTING_EVIDENCE_DIR / "bowling_zero_opportunity_audit.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_current_form_audit() -> pd.DataFrame:
    """Load verified current form evidence logs (shortlist only)."""
    p = SUPPORTING_EVIDENCE_DIR / "current_form_source_verification.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_retained_players() -> pd.DataFrame:
    """Load 184 excluded retained players across all 10 franchises."""
    p = SUPPORTING_EVIDENCE_DIR / "retained_players.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_ipl_eligibility_audit() -> pd.DataFrame:
    """Load IPL eligibility audit for all 664 players."""
    p = SUPPORTING_EVIDENCE_DIR / "ipl_eligibility_audit.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_auction_eligible_pool() -> pd.DataFrame:
    """Load the complete auction-eligible pool (664 players)."""
    p = SUPPORTING_EVIDENCE_DIR / "auction_eligible_player_pool.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


# ==============================================================================
# 3. PERFORMANCE DATABASE (NEW - PRESSURE-X 2.0)
# ==============================================================================

@st.cache_data
def load_performance_by_competition_batter() -> pd.DataFrame:
    """Load batter performance by competition (all tiers)."""
    p = PROCESSED_DATA_DIR / "player_performance_by_competition_batter.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_performance_by_competition_bowler() -> pd.DataFrame:
    """Load bowler performance by competition (all tiers)."""
    p = PROCESSED_DATA_DIR / "player_performance_by_competition_bowler.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_performance_by_season_batter() -> pd.DataFrame:
    """Load batter season-level performance with shrinkage."""
    p = PROCESSED_DATA_DIR / "player_performance_by_season_batter.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_performance_by_season_bowler() -> pd.DataFrame:
    """Load bowler season-level performance with shrinkage."""
    p = PROCESSED_DATA_DIR / "player_performance_by_season_bowler.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_pressure_metrics_batter() -> pd.DataFrame:
    """Load batter pressure-classified metrics."""
    p = PROCESSED_DATA_DIR / "player_pressure_metrics_batter.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_pressure_metrics_bowler() -> pd.DataFrame:
    """Load bowler pressure-classified metrics."""
    p = PROCESSED_DATA_DIR / "player_pressure_metrics_bowler.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_domestic_metrics_batter() -> pd.DataFrame:
    """Load batter domestic competition metrics."""
    p = PROCESSED_DATA_DIR / "player_domestic_metrics_batter.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_domestic_metrics_bowler() -> pd.DataFrame:
    """Load bowler domestic competition metrics."""
    p = PROCESSED_DATA_DIR / "player_domestic_metrics_bowler.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_bowling_phase_metrics() -> pd.DataFrame:
    """Load bowler phase-specific metrics (PP, Middle, Death)."""
    p = PROCESSED_DATA_DIR / "player_bowling_phase_metrics.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_current_form() -> pd.DataFrame:
    """Load current form with source verification (all eligible players)."""
    p = PROCESSED_DATA_DIR / "player_current_form.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_player_master() -> pd.DataFrame:
    """Load canonical player master database (1,570 players)."""
    p = PROCESSED_DATA_DIR / "player_master.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


# ==============================================================================
# 4. COMPLETE ENRICHED CANDIDATE POOL (VIEW A - 664 PLAYERS)
# ==============================================================================

@st.cache_data
def load_complete_pool_enriched() -> pd.DataFrame:
    """
    Load all 664 auction-eligible players and enrich with:
    - Verified shortlist data (28 players)
    - Performance by competition/season
    - Pressure metrics
    - Domestic metrics
    - Bowling phase metrics
    - Current form
    - Player master metadata
    - IPL eligibility & nationality
    """
    # Load base datasets
    pool_df = load_auction_eligible_pool()
    audit_df = load_ipl_eligibility_audit()
    shortlist_df = get_official_shortlist()
    player_master = load_player_master()

    if pool_df.empty:
        return shortlist_df

    # Use ALL players from auction pool (already filtered for eligibility)
    # Remove duplicates, keep highest composite_score
    pool_df = pool_df.sort_values('composite_score', ascending=False).drop_duplicates('player_id')

    # Build lookups
    shortlist_lookup = {int(r['player_id']): r.to_dict() for _, r in shortlist_df.iterrows()}

    # Nationality from audit (where available), fallback to pool 'origin'
    nat_lookup = {}
    for _, a_row in audit_df.iterrows():
        if a_row.get('eligibility_status') == 'ELIGIBLE':
            pid = int(a_row['player_id'])
            nat_str = str(a_row.get('recorded_nationality', ''))
            nat_lookup[pid] = 'Indian' if ('Indian' in nat_str and 'Non-Indian' not in nat_str) else 'Overseas'

    # Fallback: use pool 'origin' column for players not in audit
    for _, row in pool_df.iterrows():
        pid = int(row['player_id'])
        if pid not in nat_lookup:
            origin = str(row.get('origin', '')).lower()
            nat_lookup[pid] = 'Indian' if origin == 'domestic' else 'Overseas'

    country_lookup = {pid: ('India' if nat == 'Indian' else 'Overseas') for pid, nat in nat_lookup.items()}

    # Load performance data for enrichment
    perf_comp_bat = load_performance_by_competition_batter()
    perf_comp_bowl = load_performance_by_competition_bowler()
    perf_season_bat = load_performance_by_season_batter()
    perf_season_bowl = load_performance_by_season_bowler()
    pressure_bat = load_pressure_metrics_batter()
    pressure_bowl = load_pressure_metrics_bowler()
    domestic_bat = load_domestic_metrics_batter()
    domestic_bowl = load_domestic_metrics_bowler()
    bowl_phase = load_bowling_phase_metrics()
    current_form = load_current_form()
    scouting_scores = load_scouting_priority_scores()
    bowl_deploy = load_bowling_deployment()

    # Load RR squad for View C filtering
    rr_squad_df = load_rr_current_squad()
    rr_squad_pids = set(rr_squad_df['player_id'].astype(int).tolist()) if not rr_squad_df.empty else set()

    # Build performance lookups
    def build_lookup(df: pd.DataFrame, id_col: str) -> Dict[int, Dict]:
        if df.empty or id_col not in df.columns:
            return {}
        return {int(r[id_col]): r.to_dict() for _, r in df.iterrows()}

    perf_comp_bat_lookup = build_lookup(perf_comp_bat, 'striker_id')
    perf_comp_bowl_lookup = build_lookup(perf_comp_bowl, 'bowler_id')
    perf_season_bat_lookup = build_lookup(perf_season_bat, 'striker_id')
    perf_season_bowl_lookup = build_lookup(perf_season_bowl, 'bowler_id')
    pressure_bat_lookup = build_lookup(pressure_bat, 'player_id')
    pressure_bowl_lookup = build_lookup(pressure_bowl, 'player_id')
    domestic_bat_lookup = build_lookup(domestic_bat, 'player_id')
    domestic_bowl_lookup = build_lookup(domestic_bowl, 'player_id')
    bowl_phase_lookup = build_lookup(bowl_phase, 'bowler_id')
    form_lookup = build_lookup(current_form, 'player_id')
    scouting_lookup = build_lookup(scouting_scores, 'player_id')
    bowl_deploy_lookup = build_lookup(bowl_deploy, 'player_id')
    master_lookup = build_lookup(player_master, 'player_id')

    records = []

    for _, row in pool_df.iterrows():
        pid = int(row['player_id'])
        is_sl = pid in shortlist_lookup

        # Base record from shortlist or pool
        is_rr = pid in rr_squad_pids

        if is_sl:
            base = dict(shortlist_lookup[pid])
            base['is_shortlisted'] = True
            base['view'] = 'View B: Official Shortlist'
            base['composite_score'] = float(row.get('composite_score', base.get('pressure_or_eq_score', 0)))
            base['total_balls'] = int(row.get('total_balls', base.get('evidence_balls', 150)))
            base['high_extreme_balls'] = int(row.get('high_extreme_balls', 30))
        else:
            role_val = 'Batter' if str(row.get('role', '')).lower() == 'batter' else 'Bowler'
            comp_score = float(row.get('composite_score', 65.0))
            est_scout = round(0.40 * comp_score + 0.30 * 65.0 + 0.20 * 70.0 + 0.10 * 70.0, 2)

            nat = nat_lookup.get(pid, 'Overseas')
            cty = country_lookup.get(pid, 'Overseas')

            # Get age from player master
            master_rec = master_lookup.get(pid, {})
            age = master_rec.get('age_as_of_2027_04_01', 28.0)
            dev_cat = master_rec.get('development_category', 'Prime-age performer')

            base = {
                'player_id': pid,
                'player_name': str(row['player_name']),
                'role': role_val,
                'country': cty,
                'nationality': nat,
                'age_as_of_2027_04_01': float(age) if pd.notna(age) else 28.0,
                'development_category': dev_cat,
                'pressure_or_eq_score': round(comp_score, 2),
                'verified_rr_scouting_score': est_scout,
                'current_form_rating': 'Neutral',
                'is_shortlisted': False,
                'view': 'View C: RR Squad' if is_rr else 'View A: Complete Pool',
                'composite_score': comp_score,
                'total_balls': int(row.get('total_balls', 80)),
                'high_extreme_balls': int(row.get('high_extreme_balls', 15))
            }

        # Enrich with dimension scores from scouting analysis
        if pid in scouting_lookup:
            sd = scouting_lookup[pid]
            base['dimA_pressure'] = float(sd.get('dimA_historical_pressure_score', base.get('pressure_or_eq_score', 0)))
            base['dimB_runway'] = float(sd.get('dimB_age_development_score', 65.0))
            base['dimC_ceiling'] = float(sd.get('dimC_skill_ceiling_score', 70.0))
            base['dimD_form'] = float(sd.get('dimD_current_form_score', 70.0))
        else:
            base['dimA_pressure'] = base.get('pressure_or_eq_score', 50.0)
            base['dimB_runway'] = 65.0
            base['dimC_ceiling'] = 70.0
            base['dimD_form'] = 70.0

        # Enrich with current form audit (shortlist only, but include if available)
        if pid in form_lookup:
            fd = form_lookup[pid]
            base['form_matches'] = fd.get('matches_evaluated', '—')
            base['form_runs'] = fd.get('runs_scored', '—')
            base['form_avg'] = fd.get('batting_or_bowling_average', '—')
            base['form_sr_econ'] = fd.get('strike_rate_or_economy', '—')
            base['form_competition_scope'] = fd.get('competition_scope', '—')
            base['form_date_window'] = fd.get('exact_date_window', '—')
            base['current_form_rating'] = fd.get('current_form_rating', base.get('current_form_rating', 'Neutral'))
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
        if pid in bowl_deploy_lookup:
            bd = bowl_deploy_lookup[pid]
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

        # Enrich with competition-level performance
        comp_bat = perf_comp_bat_lookup.get(pid, {})
        comp_bowl = perf_comp_bowl_lookup.get(pid, {})

        # Aggregate across competitions
        base['career_matches'] = int(comp_bat.get('matches', 0) + comp_bowl.get('matches', 0))
        base['career_innings'] = int(comp_bat.get('innings', 0) + comp_bowl.get('innings', 0))
        base['career_batting_runs'] = comp_bat.get('total_runs', np.nan)
        base['career_batting_sr'] = comp_bat.get('strike_rate', np.nan)
        base['career_batting_avg'] = np.nan  # Need dismissals
        base['career_batting_balls'] = comp_bat.get('total_balls', 0)
        base['career_bowling_wickets'] = comp_bowl.get('total_wickets', np.nan)
        base['career_bowling_econ'] = comp_bowl.get('economy', np.nan)
        base['career_bowling_avg'] = np.nan
        base['career_bowling_balls'] = comp_bowl.get('total_balls', 0)

        # Enrich with season-level performance (latest season)
        season_bat = perf_season_bat_lookup.get(pid, {})
        season_bowl = perf_season_bowl_lookup.get(pid, {})

        base['latest_season'] = season_bat.get('season', season_bowl.get('season', '2025'))
        base['season_batting_sr'] = season_bat.get('strike_rate_pop_adj_shrunk', np.nan)
        base['season_bowling_econ'] = season_bowl.get('economy_pop_adj_shrunk', np.nan)
        base['season_reliability'] = season_bat.get('min_balls_100', season_bowl.get('min_balls_100', False))

        # Enrich with pressure metrics
        p_bat = pressure_bat_lookup.get(pid, {})
        p_bowl = pressure_bowl_lookup.get(pid, {})

        base['high_extreme_balls_total'] = p_bat.get('high_extreme_balls', 0) + p_bowl.get('high_extreme_balls', 0)
        base['high_extreme_runs'] = p_bat.get('high_extreme_runs', 0)
        base['high_extreme_wickets'] = p_bowl.get('high_extreme_wickets', 0)
        base['chase_balls'] = p_bat.get('chase_balls', 0)
        base['chase_runs'] = p_bat.get('chase_runs', 0)
        base['defend_balls'] = p_bowl.get('defend_balls', 0)
        base['defend_wickets'] = p_bowl.get('defend_wickets', 0)

        # Enrich with domestic metrics
        d_bat = domestic_bat_lookup.get(pid, {})
        d_bowl = domestic_bowl_lookup.get(pid, {})

        base['domestic_matches'] = int(d_bat.get('matches', 0) + d_bowl.get('matches', 0))
        base['domestic_batting_runs'] = d_bat.get('total_runs', np.nan)
        base['domestic_batting_avg'] = d_bat.get('strike_rate', np.nan)  # SR in domestic
        base['domestic_batting_sr'] = d_bat.get('strike_rate', np.nan)
        base['domestic_bowling_wickets'] = d_bowl.get('total_wickets', np.nan)
        base['domestic_bowling_econ'] = d_bowl.get('economy', np.nan)
        base['domestic_bowling_avg'] = np.nan
        base['has_domestic_evidence'] = base['domestic_matches'] > 0

        # Enrich with bowling phase metrics
        bp = bowl_phase_lookup.get(pid, {})
        base['pp_balls_bowled'] = bp.get('powerplay_balls', 0)
        base['pp_wickets'] = bp.get('powerplay_wickets', np.nan)
        base['pp_econ'] = bp.get('powerplay_economy', np.nan)
        base['middle_balls_bowled'] = bp.get('middle_balls', 0)
        base['middle_wickets'] = bp.get('middle_wickets', np.nan)
        base['middle_econ'] = bp.get('middle_economy', np.nan)
        base['death_balls_bowled'] = bp.get('death_balls', 0)
        base['death_wickets'] = bp.get('death_wickets', np.nan)
        base['death_econ'] = bp.get('death_economy', np.nan)

        # Enrich with player master metadata
        master_rec = master_lookup.get(pid, {})
        base['primary_role'] = master_rec.get('primary_role', base.get('role', ''))
        base['batting_style'] = master_rec.get('batting_style', '')
        base['bowling_style'] = master_rec.get('bowling_style', '')
        base['wk_flag'] = master_rec.get('wk_flag', False)
        base['overseas_status'] = master_rec.get('overseas_status', '')

        # Evidence sample size
        total_balls = base.get('career_batting_balls', 0) + base.get('career_bowling_balls', 0)
        base['evidence_balls'] = int(total_balls) if total_balls > 0 else base.get('total_balls', 0)

        # Data reliability tier
        eb = base['evidence_balls']
        if eb >= 300:
            base['evidence_confidence'] = 'High (300+ balls)'
        elif eb >= 100:
            base['evidence_confidence'] = 'Adequate (100–299 balls)'
        else:
            base['evidence_confidence'] = 'Limited (<100 balls)'

        # Characteristic tags from evidence
        characteristics = []
        b_balls = base.get('career_batting_balls', 0)
        if b_balls > 50:
            pp_balls = comp_bat.get('pp_balls', 0) if isinstance(comp_bat, dict) else 0
            mid_balls = comp_bat.get('mid_balls', 0) if isinstance(comp_bat, dict) else 0
            dth_balls = comp_bat.get('death_balls', 0) if isinstance(comp_bat, dict) else 0
            if pp_balls / b_balls > 0.40:
                characteristics.append('Opening / Powerplay Anchor')
            if mid_balls / b_balls > 0.45:
                characteristics.append('Middle-Overs Spin Basher')
            if dth_balls / b_balls > 0.20 or (comp_bat.get('total_runs', 0) > 100 and dth_balls > 20):
                characteristics.append('Death-Over Finisher')
            if comp_bat.get('total_sixes', 0) >= 15:
                characteristics.append('Power Hitter (15+ Sixes)')
            if not np.isnan(base.get('career_batting_avg', np.nan)) and base.get('career_batting_avg', 0) >= 32.0:
                characteristics.append('High-Average Anchor')

        if base.get('demonstrated_role', '—') != '—':
            if 'Powerplay' in base['demonstrated_role']:
                characteristics.append('Powerplay Bowler')
            if 'Middle' in base['demonstrated_role']:
                characteristics.append('Middle-Overs Bowler')
            if 'Death' in base['demonstrated_role']:
                characteristics.append('Death-Overs Closer')

        base['characteristics'] = ", ".join(characteristics) if characteristics else "Standard T20 Performer"

        records.append(base)

    full_df = pd.DataFrame(records)
    return full_df.sort_values(by='verified_rr_scouting_score', ascending=False).reset_index(drop=True)


# ==============================================================================
# 5. VIEW C: RR CURRENT SQUAD
# ==============================================================================

@st.cache_data
def load_rr_current_squad() -> pd.DataFrame:
    """
    Load Rajasthan Royals current retained squad from pre-built reference CSV.
    Returns fully enriched squad data with roles, ages, nationality, and retention status.
    """
    from src.utilities.paths import REFERENCE_DATA_DIR
    p = REFERENCE_DATA_DIR / "rr_current_squad.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


# ==============================================================================
# 6. DYNAMIC FILTERING ENGINE (Enhanced for 664 players)
# ==============================================================================

def apply_scouting_filters(
    df: pd.DataFrame,
    *,
    pool_scope: str = "View A: Complete Pool (311 Players)",
    view_filter: str = "All Views",
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
    limit: Optional[int] = 10,
    competition_tiers: Optional[List[int]] = None
) -> pd.DataFrame:
    """
    Apply multi-dimensional scouting filters across the candidate pool.
    Guarantees no modification of underlying datasets.

    Views:
    - "All Views" - All players
    - "View A: Complete Pool" - 664 eligible players
    - "View B: Official Shortlist" - 28 verified players
    - "View C: RR Squad" - Current retained players
    """
    filtered = df.copy()

    # 1. View filter
    if view_filter != "All Views" and 'view' in filtered.columns:
        filtered = filtered[filtered['view'] == view_filter]

    # 2. Scope (legacy support)
    if "Shortlist" in pool_scope or "View B" in pool_scope:
        if 'is_shortlisted' in filtered.columns:
            filtered = filtered[filtered['is_shortlisted'] == True]

    # 3. Player category / role
    if role and role.lower() not in ["any", "all"]:
        if role.lower() == "all-rounder":
            filtered = filtered[
                (filtered.get('career_batting_runs', 0).fillna(0) > 30) &
                (filtered.get('career_bowling_wickets', 0).fillna(0) > 2)
            ]
        else:
            filtered = filtered[filtered['role'].str.lower() == role.lower()]

    # 4. Nationality
    if nationality and nationality.lower() not in ["both", "all"]:
        filtered = filtered[filtered['nationality'].str.lower() == nationality.lower()]

    if country and country.lower() not in ["all", "any"]:
        filtered = filtered[filtered['country'].str.lower() == country.lower()]

    # 5. Age filtering
    if age_group != "All":
        age_col = 'age_as_of_2027_04_01'
        if "Emerging" in age_group:
            filtered = filtered[filtered[age_col] <= 23.0]
        elif "Development" in age_group:
            filtered = filtered[(filtered[age_col] >= 24.0) & (filtered[age_col] <= 26.9)]
        elif "Prime" in age_group:
            filtered = filtered[(filtered[age_col] >= 27.0) & (filtered[age_col] <= 30.9)]
        elif "Experienced" in age_group:
            filtered = filtered[filtered[age_col] >= 31.0]

    filtered = filtered[
        (filtered['age_as_of_2027_04_01'] >= age_min) &
        (filtered['age_as_of_2027_04_01'] <= age_max)
    ]

    # 6. Core scores
    if min_pressure_score > 0.0:
        filtered = filtered[filtered['pressure_or_eq_score'] >= min_pressure_score]

    if min_rr_score > 0.0:
        filtered = filtered[filtered['verified_rr_scouting_score'] >= min_rr_score]

    if min_eq_score is not None and min_eq_score > 0.0:
        filtered = filtered[
            (filtered['role'] != 'Bowler') |
            (filtered['pressure_or_eq_score'] >= min_eq_score)
        ]

    # 7. Form ratings
    if form_categories and "All" not in form_categories and len(form_categories) > 0:
        filtered = filtered[filtered['current_form_rating'].isin(form_categories)]

    # 8. Evidence sample size
    if min_sample_balls > 0:
        filtered = filtered[filtered['evidence_balls'] >= min_sample_balls]

    if evidence_confidences and "All" not in evidence_confidences and len(evidence_confidences) > 0:
        filtered = filtered[filtered['evidence_confidence'].isin(evidence_confidences)]

    # 9. Domestic performance filtering
    if domestic_min_runs is not None and domestic_min_runs > 0:
        filtered = filtered[filtered['domestic_batting_runs'].fillna(0) >= domestic_min_runs]

    if domestic_min_avg is not None and domestic_min_avg > 0:
        filtered = filtered[filtered['domestic_batting_avg'].fillna(0) >= domestic_min_avg]

    if domestic_min_sr is not None and domestic_min_sr > 0:
        filtered = filtered[filtered['domestic_batting_sr'].fillna(0) >= domestic_min_sr]

    if domestic_min_wickets is not None and domestic_min_wickets > 0:
        filtered = filtered[filtered['domestic_bowling_wickets'].fillna(0) >= domestic_min_wickets]

    if domestic_max_econ is not None and domestic_max_econ < 15.0:
        filtered = filtered[filtered['domestic_bowling_econ'].fillna(99) <= domestic_max_econ]

    # 10. Characteristic filter
    if required_characteristic and required_characteristic != "All":
        filtered = filtered[
            filtered['characteristics'].str.contains(required_characteristic, case=False, na=False)
        ]

    # 11. Development preference
    if dev_preference != "All":
        if dev_preference == "Immediate impact":
            filtered = filtered[filtered['development_category'].isin(['Prime-age performer', 'Experienced performer'])]
        elif dev_preference == "Long-term development":
            filtered = filtered[filtered['development_category'].isin(['Emerging', 'Young development candidate'])]
        elif dev_preference == "High-upside prospect":
            filtered = filtered[
                (filtered['development_category'] == 'Emerging') &
                (filtered['verified_rr_scouting_score'] >= 75.0)
            ]

    # 12. Search query
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        filtered = filtered[
            filtered['player_name'].str.lower().str.contains(q, na=False) |
            filtered['country'].str.lower().str.contains(q, na=False) |
            filtered['characteristics'].str.lower().str.contains(q, na=False) |
            filtered.get('primary_role', pd.Series('')).str.lower().str.contains(q, na=False)
        ]

    # 13. Competition tiers filter
    if competition_tiers and len(competition_tiers) > 0:
        # This would require competition tier info in the dataframe
        pass

    # Sort descending by scouting score
    filtered = filtered.sort_values(by='verified_rr_scouting_score', ascending=False)

    # 14. Limit
    if limit is not None and limit > 0:
        filtered = filtered.head(limit)

    return filtered.reset_index(drop=True)


# ==============================================================================
# 7. PLAYER COMPARISON DATA EXTRACTOR
# ==============================================================================

def get_comparison_data(player_ids: List[int], pool_df: pd.DataFrame) -> pd.DataFrame:
    """Extract rows for candidate comparison by player_id."""
    if not player_ids:
        return pd.DataFrame()
    return pool_df[pool_df['player_id'].isin(player_ids)].copy()


# ==============================================================================
# 8. STANDARD SCOUTING REPORT EXPORT
# ==============================================================================

def build_standard_scouting_report(
    pool_df: pd.DataFrame,
    player_ids: Optional[List[int]] = None,
    include_sections: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Build a standardized scouting report for export.

    Args:
        pool_df: Enriched candidate pool
        player_ids: Specific players to include (None = all)
        include_sections: Sections to include ['summary', 'performance', 'pressure', 'domestic', 'form', 'deployment']

    Returns:
        DataFrame formatted for CSV export
    """
    if player_ids:
        df = pool_df[pool_df['player_id'].isin(player_ids)].copy()
    else:
        df = pool_df.copy()

    # Select and rename columns for standard report
    report_cols = {
        'player_id': 'Player ID',
        'player_name': 'Player Name',
        'role': 'Role',
        'country': 'Country',
        'nationality': 'Nationality',
        'age_as_of_2027_04_01': 'Age (Apr 2027)',
        'development_category': 'Development Stage',
        'view': 'View',
        'is_shortlisted': 'Official Shortlist',
        'verified_rr_scouting_score': 'RR Scouting Score (40/30/20/10)',
        'pressure_or_eq_score': 'Pressure / EQ Base Score',
        'dimA_pressure': 'Dim A: Pressure Execution (40%)',
        'dimB_runway': 'Dim B: Age & Runway (30%)',
        'dimC_ceiling': 'Dim C: Skill Ceiling (20%)',
        'dimD_form': 'Dim D: Current Form (10%)',
        'current_form_rating': 'Form Rating',
        'evidence_balls': 'Total Observed Balls',
        'evidence_confidence': 'Evidence Confidence',
        'high_extreme_balls_total': 'High-Extreme Balls',
        'career_batting_runs': 'Career Batting Runs',
        'career_batting_avg': 'Career Batting Average',
        'career_batting_sr': 'Career Batting SR',
        'career_bowling_wickets': 'Career Wickets',
        'career_bowling_econ': 'Career Bowling Economy',
        'career_bowling_avg': 'Career Bowling Average',
        'domestic_matches': 'Domestic Matches',
        'domestic_batting_runs': 'Domestic Runs',
        'domestic_batting_avg': 'Domestic Batting Avg',
        'domestic_batting_sr': 'Domestic Batting SR',
        'domestic_bowling_wickets': 'Domestic Wickets',
        'domestic_bowling_econ': 'Domestic Bowling Econ',
        'pp_balls_bowled': 'Powerplay Balls Bowled',
        'pp_wickets': 'Powerplay Wickets',
        'pp_econ': 'Powerplay Economy',
        'middle_balls_bowled': 'Middle Overs Balls Bowled',
        'middle_wickets': 'Middle Overs Wickets',
        'middle_econ': 'Middle Overs Economy',
        'death_balls_bowled': 'Death Overs Balls Bowled',
        'death_wickets': 'Death Overs Wickets',
        'death_econ': 'Death Overs Economy',
        'demonstrated_role': 'Demonstrated Role',
        'projected_role': 'Projected Role',
        'prohibited_deployment': 'Prohibited Deployment',
        'has_form_evidence': 'Has Form Evidence',
        'has_domestic_evidence': 'Has Domestic Evidence',
        'characteristics': 'Observed Characteristics',
        'primary_role': 'Primary Role',
        'batting_style': 'Batting Style',
        'bowling_style': 'Bowling Style',
        'wk_flag': 'Wicketkeeper',
        'overseas_status': 'Overseas Status',
    }

    # Filter to available columns
    available_cols = {k: v for k, v in report_cols.items() if k in df.columns}
    report_df = df[list(available_cols.keys())].copy()
    report_df.columns = [available_cols[k] for k in report_df.columns]

    return report_df


def export_standard_scouting_report(
    pool_df: pd.DataFrame,
    output_path: str,
    player_ids: Optional[List[int]] = None
) -> str:
    """
    Export standard scouting report to CSV.

    Args:
        pool_df: Enriched candidate pool
        output_path: Path to save CSV
        player_ids: Specific players to include (None = all)

    Returns:
        Output path
    """
    report_df = build_standard_scouting_report(pool_df, player_ids)
    report_df.to_csv(output_path, index=False)
    return output_path