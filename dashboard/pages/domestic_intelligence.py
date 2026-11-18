"""
PRESSURE-X Domestic Performance Intelligence Explorer
=====================================================
Deep-dive into domestic T20 competition performance across all tiers.

Sections:
- Domestic Competition Landscape
- Player Domestic Performance Profiles
- Competition Tier Comparison
- Emerging Domestic Talent Radar
- Domestic-to-IPL Transition Analysis
"""

import pandas as pd
import streamlit as st
import numpy as np

from dashboard.utils.data_loader import (
    load_complete_pool_enriched,
    load_domestic_metrics_batter,
    load_domestic_metrics_bowler,
    load_performance_by_competition_batter,
    load_performance_by_competition_bowler,
    load_player_master,
    apply_scouting_filters
)
from dashboard.utils.formatting import (
    format_category_badge,
    format_nationality_badge,
    RR_PINK,
    RR_ROYAL_BLUE,
    RR_GOLD
)
from dashboard.charts import (
    plot_ranking_bar_chart,
    plot_nationality_pie,
    plot_career_stage_bar
)


# -----------------------------------------------------------------------------
# COMPETITION TIER INFO
# -----------------------------------------------------------------------------

COMPETITION_TIERS = {
    1: {"name": "IPL", "tier_name": "Tier 1: IPL", "multiplier": 1.00, "color": "#EA1B86"},
    2: {"name": "BBL/PSL/SA20/Hundred/ILT20", "tier_name": "Tier 2: Major Franchise Leagues", "multiplier": 0.92, "color": "#10B981"},
    3: {"name": "CPL/BPL/LPL/Super Smash", "tier_name": "Tier 3: Regional Franchise Leagues", "multiplier": 0.84, "color": "#F59E0B"},
    4: {"name": "Associate T20Is", "tier_name": "Tier 4: Associate Internationals", "multiplier": 0.76, "color": "#3B82F6"},
    5: {"name": "Domestic (SMAT/Vitality Blast/Other)", "tier_name": "Tier 5: Domestic Tournaments", "multiplier": 0.68, "color": "#6366F1"},
}

TIER_ORDER = [1, 2, 3, 4, 5]


# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------

def _get_competition_coverage(df: pd.DataFrame, id_col: str) -> pd.DataFrame:
    """Get competition participation matrix for players."""
    if df.empty or 'comp_id' not in df.columns:
        return pd.DataFrame()

    # Count matches per player per competition
    coverage = df.groupby([id_col, 'comp_id', 'comp_name', 'comp_tier', 'comp_type']).agg(
        matches=('match_id', 'nunique'),
        balls=('total_balls', 'sum') if 'total_balls' in df.columns else ('balls_faced', 'sum'),
        runs=('total_runs', 'sum') if 'total_runs' in df.columns else ('runs_scored', 'sum')
    ).reset_index()

    return coverage


def _render_domestic_player_card(player: pd.Series, role: str) -> str:
    """Render a domestic performance player card."""
    nat_badge = format_nationality_badge(player.get('nationality', ''))
    cat_badge = format_category_badge(player.get('development_category', ''))
    age = player.get('age_as_of_2027_04_01', 0)

    if role == 'Batter':
        dom_runs = player.get('domestic_batting_runs', 0)
        dom_sr = player.get('domestic_batting_sr', 0)
        dom_avg = player.get('domestic_batting_avg', 0)
        dom_matches = player.get('domestic_matches', 0)

        metric_label = "Domestic Runs"
        metric_val = f"{int(dom_runs)}" if pd.notna(dom_runs) else "—"
        secondary = f"SR: {dom_sr:.1f} | Avg: {dom_avg:.1f} | Matches: {int(dom_matches)}"
    else:
        dom_wkts = player.get('domestic_bowling_wickets', 0)
        dom_econ = player.get('domestic_bowling_econ', 0)
        dom_avg = player.get('domestic_bowling_avg', 0)
        dom_matches = player.get('domestic_matches', 0)

        metric_label = "Domestic Wickets"
        metric_val = f"{int(dom_wkts)}" if pd.notna(dom_wkts) else "—"
        secondary = f"Econ: {dom_econ:.2f} | Avg: {dom_avg:.1f} | Matches: {int(dom_matches)}"

    evidence_note = "✅ Verified domestic evidence" if player.get('has_domestic_evidence') else "⚠️ No domestic T20 evidence in dataset"

    return f"""
<div style="background:#1C2541;border:1px solid rgba(234,27,134,0.3);border-radius:8px;padding:14px 18px;margin-bottom:12px;">
<div style="display:flex;justify-content:space-between;align-items:baseline;">
<div>
<span style="font-size:1.15rem;font-weight:800;color:#FFFFFF;">{player.get('player_name','')}</span>
<span style="font-size:0.8rem;color:#94A3B8;margin-left:8px;">{nat_badge} {cat_badge}</span>
</div>
<div style="font-size:0.7rem;color:#F59E0B;background:rgba(245,158,11,0.1);padding:2px 8px;border-radius:10px;">{role}</div>
</div>
<div style="font-size:0.8rem;color:#CBD5E1;margin:6px 0;">
<b>Age:</b> {age:.1f} · <b>Primary Role:</b> {player.get('primary_role', player.get('role', ''))} · <b>Bat:</b> {player.get('batting_style','—')} · <b>Bowl:</b> {player.get('bowling_style','—')}
</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:10px 0;">
<div style="background:#0B132B;padding:10px;border-radius:8px;text-align:center;">
<div style="font-size:0.7rem;color:#94A3B8;text-transform:uppercase;">{metric_label}</div>
<div style="font-size:1.4rem;font-weight:800;color:#10B981;">{metric_val}</div>
</div>
<div style="background:#0B132B;padding:10px;border-radius:8px;text-align:center;">
<div style="font-size:0.7rem;color:#94A3B8;text-transform:uppercase;">Domestic Matches</div>
<div style="font-size:1.4rem;font-weight:700;color:#FFFFFF;">{int(dom_matches) if pd.notna(dom_matches) else 0}</div>
</div>
<div style="background:#0B132B;padding:10px;border-radius:8px;text-align:center;">
<div style="font-size:0.7rem;color:#94A3B8;text-transform:uppercase;">RR Scouting Score</div>
<div style="font-size:1.4rem;font-weight:800;color:{RR_PINK};">{player.get('verified_rr_scouting_score', 0):.2f}</div>
</div>
</div>
<div style="font-size:0.8rem;color:#94A3B8;">{secondary}</div>
<div style="font-size:0.75rem;color:#F59E0B;margin-top:6px;">{evidence_note}</div>
</div>
"""


# -----------------------------------------------------------------------------
# MAIN RENDER FUNCTION
# -----------------------------------------------------------------------------

def render_domestic_intelligence():
    """Render the Domestic Performance Intelligence page."""
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0B132B 60%,#2a0a1a);
                border:1px solid rgba(234,27,134,0.4);border-radius:12px;
                padding:22px 28px;margin-bottom:20px;">
        <div style="font-size:1.7rem;font-weight:800;color:#FFFFFF;">
            🏏 Domestic Performance Intelligence
            <span style="font-size:0.9rem;font-weight:400;color:#94A3B8;"> | Tier 5 & Regional Leagues Deep Dive</span>
        </div>
        <div style="font-size:0.88rem;color:#94A3B8;margin-top:6px;">
            Analyze player performance in domestic T20 competitions (SMAT, Vitality Blast, Regional Leagues).
            Identify hidden gems and validate IPL transition potential. Note: Domestic ball-by-ball data is limited;
            metrics derived from available competition-level aggregates.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Load data
    full_pool = load_complete_pool_enriched()
    dom_bat = load_domestic_metrics_batter()
    dom_bowl = load_domestic_metrics_bowler()
    comp_bat = load_performance_by_competition_batter()
    comp_bowl = load_performance_by_competition_bowler()
    master = load_player_master()

    # =========================================================================
    # SECTION 1: COMPETITION TIER LANDSCAPE
    # =========================================================================
    st.markdown("### 🌍 Competition Tier Landscape")

    tier_cols = st.columns(5)
    for idx, tier_num in enumerate(TIER_ORDER):
        info = COMPETITION_TIERS[tier_num]
        with tier_cols[idx]:
            st.markdown(f"""
            <div style="background:#1C2541;border:1px solid {info['color']};border-radius:8px;padding:14px;text-align:center;">
            <div style="font-size:0.7rem;color:{info['color']};font-weight:700;text-transform:uppercase;">{info['tier_name']}</div>
            <div style="font-size:0.9rem;color:#FFFFFF;margin-top:4px;">Multiplier: {info['multiplier']:.2f}x</div>
            <div style="font-size:0.75rem;color:#94A3B8;margin-top:4px;">{info['name']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # =========================================================================
    # SECTION 2: DOMESTIC PERFORMANCE OVERVIEW
    # =========================================================================
    st.markdown("### 📊 Domestic Evidence Coverage")

    # Count players with domestic evidence
    has_dom = full_pool['has_domestic_evidence'].fillna(False)
    dom_players = full_pool[has_dom].copy()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Players w/ Domestic Evidence", int(has_dom.sum()))
    with c2:
        st.metric("Total Eligible Players", len(full_pool))
    with c3:
        pct = (has_dom.sum() / len(full_pool) * 100) if len(full_pool) > 0 else 0
        st.metric("Coverage %", f"{pct:.1f}%")
    with c4:
        ind_dom = ((dom_players['nationality'] == 'Indian') if not dom_players.empty else pd.Series([False])).sum()
        os_dom = ((dom_players['nationality'] == 'Overseas') if not dom_players.empty else pd.Series([False])).sum()
        st.metric("IND / OS", f"{ind_dom} / {os_dom}")

    # Nationality split of domestic evidence
    if not dom_players.empty:
        col_viz1, col_viz2 = st.columns(2)
        with col_viz1:
            st.plotly_chart(plot_nationality_pie(dom_players, "Domestic Evidence: Nationality Split"), use_container_width=True)
        with col_viz2:
            st.plotly_chart(plot_career_stage_bar(dom_players, "Domestic Evidence: Career Stage"), use_container_width=True)

    st.markdown("---")

    # =========================================================================
    # SECTION 3: DOMESTIC BATTER LEADERBOARD
    # =========================================================================
    st.markdown("### 🏏 Domestic Batter Leaderboard")

    # Filters
    db_f1, db_f2, db_f3 = st.columns(3)
    with db_f1:
        db_nat = st.selectbox("Nationality", ["All", "Indian", "Overseas"], key="db_nat")
    with db_f2:
        db_min_runs = st.number_input("Min Domestic Runs", 0, 2000, 100, key="db_min_runs")
    with db_f3:
        db_min_sr = st.number_input("Min Strike Rate", 0, 220, 120, key="db_min_sr")

    # Filter batters with domestic evidence
    bat_dom = dom_players[dom_players['role'] == 'Batter'].copy()
    if db_nat != "All":
        bat_dom = bat_dom[bat_dom['nationality'] == db_nat]
    bat_dom = bat_dom[
        (bat_dom['domestic_batting_runs'].fillna(0) >= db_min_runs) &
        (bat_dom['domestic_batting_sr'].fillna(0) >= db_min_sr)
    ].sort_values('domestic_batting_runs', ascending=False)

    if not bat_dom.empty:
        # Summary table
        display_cols = ['player_id', 'player_name', 'nationality', 'age_as_of_2027_04_01',
                        'development_category', 'domestic_matches', 'domestic_batting_runs',
                        'domestic_batting_avg', 'domestic_batting_sr', 'verified_rr_scouting_score']
        clean_bat = bat_dom[[c for c in display_cols if c in bat_dom.columns]].copy()
        clean_bat.insert(0, 'Rank', range(1, len(clean_bat) + 1))

        st.dataframe(
            clean_bat,
            column_config={
                "Rank": st.column_config.NumberColumn("Rank", width="small"),
                "player_id": st.column_config.NumberColumn("ID", width="small"),
                "player_name": st.column_config.TextColumn("Player", width="medium"),
                "nationality": st.column_config.TextColumn("Nat", width="small"),
                "age_as_of_2027_04_01": st.column_config.NumberColumn("Age", format="%.1f", width="small"),
                "development_category": st.column_config.TextColumn("Dev Stage", width="medium"),
                "domestic_matches": st.column_config.NumberColumn("Matches", width="small"),
                "domestic_batting_runs": st.column_config.NumberColumn("Runs", width="small"),
                "domestic_batting_avg": st.column_config.NumberColumn("Avg", format="%.1f", width="small"),
                "domestic_batting_sr": st.column_config.ProgressColumn("SR", format="%.1f", min_value=0, max_value=220, width="medium"),
                "verified_rr_scouting_score": st.column_config.ProgressColumn("RR Score", format="%.2f", min_value=0, max_value=100, width="medium")
            },
            hide_index=True,
            use_container_width=True,
            height=min(400, 40 * len(clean_bat) + 40)
        )

        # Top player cards
        st.markdown("#### 🌟 Top Domestic Batters")
        top_batters = bat_dom.head(6)
        for _, player in top_batters.iterrows():
            card = _render_domestic_player_card(player, 'Batter')
            st.markdown(card, unsafe_allow_html=True)
    else:
        st.info("No batters match the current domestic filters.")

    st.markdown("---")

    # =========================================================================
    # SECTION 4: DOMESTIC BOWLER LEADERBOARD
    # =========================================================================
    st.markdown("### 🎳 Domestic Bowler Leaderboard")

    db_f1, db_f2, db_f3 = st.columns(3)
    with db_f1:
        db_nat_b = st.selectbox("Nationality", ["All", "Indian", "Overseas"], key="db_nat_b")
    with db_f2:
        db_min_wkt = st.number_input("Min Domestic Wickets", 0, 100, 5, key="db_min_wkt")
    with db_f3:
        db_max_econ = st.number_input("Max Economy", 4.0, 15.0, 9.0, step=0.5, key="db_max_econ")

    bowl_dom = dom_players[dom_players['role'] == 'Bowler'].copy()
    if db_nat_b != "All":
        bowl_dom = bowl_dom[bowl_dom['nationality'] == db_nat_b]
    bowl_dom = bowl_dom[
        (bowl_dom['domestic_bowling_wickets'].fillna(0) >= db_min_wkt) &
        (bowl_dom['domestic_bowling_econ'].fillna(99) <= db_max_econ)
    ].sort_values('domestic_bowling_wickets', ascending=False)

    if not bowl_dom.empty:
        display_cols = ['player_id', 'player_name', 'nationality', 'age_as_of_2027_04_01',
                        'development_category', 'domestic_matches', 'domestic_bowling_wickets',
                        'domestic_bowling_econ', 'domestic_bowling_avg', 'verified_rr_scouting_score']
        clean_bowl = bowl_dom[[c for c in display_cols if c in bowl_dom.columns]].copy()
        clean_bowl.insert(0, 'Rank', range(1, len(clean_bowl) + 1))

        st.dataframe(
            clean_bowl,
            column_config={
                "Rank": st.column_config.NumberColumn("Rank", width="small"),
                "player_id": st.column_config.NumberColumn("ID", width="small"),
                "player_name": st.column_config.TextColumn("Player", width="medium"),
                "nationality": st.column_config.TextColumn("Nat", width="small"),
                "age_as_of_2027_04_01": st.column_config.NumberColumn("Age", format="%.1f", width="small"),
                "development_category": st.column_config.TextColumn("Dev Stage", width="medium"),
                "domestic_matches": st.column_config.NumberColumn("Matches", width="small"),
                "domestic_bowling_wickets": st.column_config.NumberColumn("Wickets", width="small"),
                "domestic_bowling_econ": st.column_config.ProgressColumn("Econ", format="%.2f", min_value=4, max_value=12, width="medium"),
                "domestic_bowling_avg": st.column_config.NumberColumn("Avg", format="%.1f", width="small"),
                "verified_rr_scouting_score": st.column_config.ProgressColumn("RR Score", format="%.2f", min_value=0, max_value=100, width="medium")
            },
            hide_index=True,
            use_container_width=True,
            height=min(400, 40 * len(clean_bowl) + 40)
        )

        # Top player cards
        st.markdown("#### 🌟 Top Domestic Bowlers")
        top_bowlers = bowl_dom.head(6)
        for _, player in top_bowlers.iterrows():
            card = _render_domestic_player_card(player, 'Bowler')
            st.markdown(card, unsafe_allow_html=True)
    else:
        st.info("No bowlers match the current domestic filters.")

    st.markdown("---")

    # =========================================================================
    # SECTION 5: COMPETITION-LEVEL DRILLDOWN
    # =========================================================================
    st.markdown("### 🔬 Competition-Level Drilldown")

    st.markdown("""
    **Note:** Competition-level data includes all tiers (1-5). Filter by tier to analyze
    performance in specific competition categories.
    """)

    # Combine batter and bowler competition data
    comp_bat_filtered = comp_bat.copy() if not comp_bat.empty else pd.DataFrame()
    comp_bowl_filtered = comp_bowl.copy() if not comp_bowl.empty else pd.DataFrame()

    # Tier filter
    tier_filter = st.selectbox(
        "Filter by Competition Tier",
        ["All Tiers"] + [f"Tier {t}: {COMPETITION_TIERS[t]['name']}" for t in TIER_ORDER],
        key="comp_tier_filter"
    )

    if tier_filter != "All Tiers":
        tier_num = int(tier_filter.split(":")[0].replace("Tier ", ""))
        if not comp_bat_filtered.empty:
            comp_bat_filtered = comp_bat_filtered[comp_bat_filtered['comp_tier'] == tier_num]
        if not comp_bowl_filtered.empty:
            comp_bowl_filtered = comp_bowl_filtered[comp_bowl_filtered['comp_tier'] == tier_num]

    # Show top performers in selected tier
    ct1, ct2 = st.columns(2)

    with ct1:
        st.markdown(f"#### 🏏 Top Batters in {tier_filter}")
        if not comp_bat_filtered.empty:
            top_bat = comp_bat_filtered.nlargest(10, 'strike_rate')[
                ['striker_name', 'comp_name', 'comp_tier', 'total_balls', 'total_runs', 'strike_rate', 'boundary_pct']
            ].copy()
            top_bat.columns = ['Player', 'Competition', 'Tier', 'Balls', 'Runs', 'SR', 'Boundary %']
            st.dataframe(top_bat, hide_index=True, use_container_width=True)
        else:
            st.info("No batter data for selected tier.")

    with ct2:
        st.markdown(f"#### 🎳 Top Bowlers in {tier_filter}")
        if not comp_bowl_filtered.empty:
            top_bowl = comp_bowl_filtered.nlargest(10, 'wicket_rate')[
                ['bowler_name', 'comp_name', 'comp_tier', 'total_balls', 'total_wickets', 'economy', 'wicket_rate']
            ].copy()
            top_bowl.columns = ['Player', 'Competition', 'Tier', 'Balls', 'Wickets', 'Econ', 'Wicket Rate']
            st.dataframe(top_bowl, hide_index=True, use_container_width=True)
        else:
            st.info("No bowler data for selected tier.")

    st.markdown("---")

    # =========================================================================
    # SECTION 6: EMERGING DOMESTIC TALENT RADAR
    # =========================================================================
    st.markdown("### 🎯 Emerging Domestic Talent Radar")

    st.markdown("""
    Players with strong domestic evidence who are **not** in the official shortlist but
    warrant scouting attention for IPL transition potential.
    """)

    # Filter: has domestic evidence, not shortlisted, emerging/young
    radar_pool = full_pool[
        (full_pool['has_domestic_evidence'] == True) &
        (full_pool['is_shortlisted'] == False) &
        (full_pool['age_as_of_2027_04_01'] <= 26)
    ].copy()

    if not radar_pool.empty:
        radar_pool = radar_pool.sort_values('verified_rr_scouting_score', ascending=False).head(15)

        display_cols = ['player_id', 'player_name', 'role', 'nationality', 'age_as_of_2027_04_01',
                        'development_category', 'domestic_matches',
                        'domestic_batting_runs', 'domestic_batting_sr',
                        'domestic_bowling_wickets', 'domestic_bowling_econ',
                        'verified_rr_scouting_score', 'characteristics']
        clean_radar = radar_pool[[c for c in display_cols if c in radar_pool.columns]].copy()
        clean_radar.insert(0, 'Rank', range(1, len(clean_radar) + 1))

        st.dataframe(
            clean_radar,
            column_config={
                "Rank": st.column_config.NumberColumn("Rank", width="small"),
                "player_id": st.column_config.NumberColumn("ID", width="small"),
                "player_name": st.column_config.TextColumn("Player", width="medium"),
                "role": st.column_config.TextColumn("Role", width="small"),
                "nationality": st.column_config.TextColumn("Nat", width="small"),
                "age_as_of_2027_04_01": st.column_config.NumberColumn("Age", format="%.1f", width="small"),
                "development_category": st.column_config.TextColumn("Dev Stage", width="medium"),
                "domestic_matches": st.column_config.NumberColumn("Dom Matches", width="small"),
                "domestic_batting_runs": st.column_config.NumberColumn("Dom Runs", width="small"),
                "domestic_batting_sr": st.column_config.ProgressColumn("Dom SR", format="%.1f", min_value=0, max_value=220, width="medium"),
                "domestic_bowling_wickets": st.column_config.NumberColumn("Dom Wkts", width="small"),
                "domestic_bowling_econ": st.column_config.ProgressColumn("Dom Econ", format="%.2f", min_value=4, max_value=12, width="medium"),
                "verified_rr_scouting_score": st.column_config.ProgressColumn("RR Score", format="%.2f", min_value=0, max_value=100, width="medium"),
                "characteristics": st.column_config.TextColumn("Characteristics", width="large")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No emerging domestic talent found matching criteria.")

    st.markdown("---")

    # =========================================================================
    # SECTION 7: DOMESTIC-TO-IPL TRANSITION ANALYSIS
    # =========================================================================
    st.markdown("### 📈 Domestic-to-IPL Transition Analysis")

    st.markdown("""
    **Framework for evaluating domestic-to-IPL transition potential:**

    1. **Competition Quality Adjustment**: Domestic stats multiplied by 0.68x (Tier 5 multiplier)
    2. **Sample Size Reliability**: Minimum 5 matches / 100 balls for credible projection
    3. **Skill Translation**: Power hitting (SR), wicket-taking (econ), phase versatility
    4. **Age & Runway**: U-25 preferred for long-term development
    5. **Role Clarity**: Defined role (opener, finisher, death bowler, etc.)
    """)

    # Show projection for top domestic performers
    proj_pool = full_pool[
        (full_pool['has_domestic_evidence'] == True) &
        (full_pool['domestic_matches'].fillna(0) >= 3)
    ].copy()

    if not proj_pool.empty:
        # Calculate projected IPL metrics
        proj_pool['proj_ipl_batting_sr'] = (proj_pool['domestic_batting_sr'] * 0.68).round(1)
        proj_pool['proj_ipl_bowling_econ'] = (proj_pool['domestic_bowling_econ'] / 0.68).round(2)

        proj_display = proj_pool.nlargest(10, 'verified_rr_scouting_score')[
            ['player_id', 'player_name', 'role', 'nationality', 'age_as_of_2027_04_01',
             'domestic_matches', 'domestic_batting_sr', 'proj_ipl_batting_sr',
             'domestic_bowling_econ', 'proj_ipl_bowling_econ',
             'verified_rr_scouting_score']
        ].copy()

        proj_display.columns = ['ID', 'Player', 'Role', 'Nat', 'Age', 'Dom Matches',
                                'Dom SR', 'Proj IPL SR', 'Dom Econ', 'Proj IPL Econ', 'RR Score']

        st.dataframe(
            proj_display,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Player": st.column_config.TextColumn("Player", width="medium"),
                "Role": st.column_config.TextColumn("Role", width="small"),
                "Nat": st.column_config.TextColumn("Nat", width="small"),
                "Age": st.column_config.NumberColumn("Age", format="%.1f", width="small"),
                "Dom Matches": st.column_config.NumberColumn("Dom Matches", width="small"),
                "Dom SR": st.column_config.ProgressColumn("Dom SR", format="%.1f", min_value=0, max_value=220, width="medium"),
                "Proj IPL SR": st.column_config.ProgressColumn("Proj IPL SR", format="%.1f", min_value=0, max_value=200, width="medium"),
                "Dom Econ": st.column_config.ProgressColumn("Dom Econ", format="%.2f", min_value=4, max_value=12, width="medium"),
                "Proj IPL Econ": st.column_config.ProgressColumn("Proj IPL Econ", format="%.2f", min_value=5, max_value=15, width="medium"),
                "RR Score": st.column_config.ProgressColumn("RR Score", format="%.2f", min_value=0, max_value=100, width="medium")
            },
            hide_index=True,
            use_container_width=True
        )

        st.caption("Projection uses Tier 5 multiplier (0.68x). Actual IPL performance depends on opposition quality, conditions, and role definition.")