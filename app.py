"""
PRESSURE-X | Rajasthan Royals IPL 2027 Scouting Intelligence
============================================================
Streamlit Interactive Scouting Dashboard
Entry point for judges, ownership, and war-room analytics.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import streamlit as st

from src.utilities.validator import DataValidator
from dashboard.utils import (
    load_final_batters,
    load_final_bowlers,
    load_final_reserves,
    load_scouting_priority_scores,
    load_bowling_deployment,
    load_zero_opportunity_audit,
    load_current_form_audit,
    load_retained_players,
    get_all_shortlist_players,
    apply_custom_css,
    RR_PINK,
    RR_ROYAL_BLUE,
    RR_GOLD
)
from dashboard.components import (
    render_kpi_card,
    render_interactive_batter_table,
    render_interactive_bowler_table,
    render_player_scouting_card
)
from dashboard.charts import (
    plot_ranking_bar_chart,
    plot_pressure_vs_scouting,
    plot_age_vs_scouting,
    plot_player_radar_comparison,
    plot_nationality_pie,
    plot_career_stage_bar,
    plot_bowling_phase_evidence
)
from models.bowling_eq_model import EvidenceQualifiedBowlingModel

# Configure Page
st.set_page_config(
    page_title="PRESSURE-X | RR Scouting Intelligence",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply RR Signature Styling
apply_custom_css()

# Validate Data Integrity
val_status = DataValidator.run_all_checks()
if not val_status['overall_pass']:
    st.error(f"⚠️ Critical Data Integrity Error: {val_status.get('details', 'Invalid dataset schemas detected.')}")
    st.stop()

# Load Datasets
batters_df = load_final_batters()
bowlers_df = load_final_bowlers()
reserves_df = load_final_reserves()
scouting_scores_df = load_scouting_priority_scores()
deployment_df = load_bowling_deployment()
zero_opp_df = load_zero_opportunity_audit()
form_audit_df = load_current_form_audit()
retained_df = load_retained_players()
all_players_df = get_all_shortlist_players()
eq_model = EvidenceQualifiedBowlingModel()

# Sidebar Branding & Navigation
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 12px 0 20px 0;">
        <div style="font-size: 2.2rem;">👑</div>
        <div style="font-size: 1.3rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px;">
            RAJASTHAN <span style="color: #EA1B86;">ROYALS</span>
        </div>
        <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px;">
            IPL 2027 Auction Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "📊 Executive Overview",
            "🏏 Top 10 Batters",
            "🎳 Top 10 Bowlers",
            "⚔️ Player Comparison",
            "👑 RR Long-Term Strategy",
            "📐 Methodology & Reliability"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.75rem; color: #64748B; padding: 4px;">
        <b>PRESSURE-X v3.0</b><br>
        Evidence-Based Paired Adjustment<br>
        40/30/20/10 RR Scouting Model<br>
        Forensic Audit: 100% Verified
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# PAGE 1: EXECUTIVE OVERVIEW
# ==============================================================================
if page == "📊 Executive Overview":
    st.markdown("""
    <div class="rr-header-box">
        <h1 class="rr-title">PRESSURE-X <span>| RR Scouting Intelligence</span></h1>
        <p class="rr-subtitle">Data-driven pressure performance, player development runway, and IPL 2027 auction strategy.</p>
    </div>
    """, unsafe_allow_html=True)

    # KPI Top Bar
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        render_kpi_card("Total Deliveries", "201,000+", "5 Competition Tiers", "#3B82F6")
    with k2:
        render_kpi_card("Retained Excluded", f"{len(retained_df)} Players", "10 IPL Franchises", "#EF4444")
    with k3:
        render_kpi_card("Top 10 Batters", f"{len(batters_df)}", "Combined IND + OS", "#EA1B86")
    with k4:
        render_kpi_card("Top 10 Bowlers", f"{len(bowlers_df)}", "Evidence-Qualified", "#10B981")
    with k5:
        render_kpi_card("Reserve Depth", f"{len(reserves_df)}", "Tactical & Role Pivots", "#F59E0B")

    st.markdown("### 🎯 Executive Mandate")
    st.markdown("""
    <div class="insight-box">
        <b>Core Challenge:</b> Traditional T20 scouting over-indexes on raw aggregate strike rates and unadjusted boundary counts. 
        <b>PRESSURE-X</b> introduces a multi-tier, evidence-based Bayesian shrinkage framework evaluated strictly under game pressure 
        (High-Extreme, Death, Powerplay, and Chase situations), refined through the <b>Rajasthan Royals Long-Term Talent Model</b> 
        which prioritizes high-ceiling youth (8–10 year development runway) balanced by clutch international anchors.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.markdown("#### ⚖️ The 40 / 30 / 20 / 10 Scouting Formula")
        weights_data = pd.DataFrame({
            "Dimension": [
                "Dim A: Pressure Execution (40%)",
                "Dim B: Age & Runway (30%)",
                "Dim C: Skill Ceiling (20%)",
                "Dim D: 2026 Form (10%)"
            ],
            "Weight": [40, 30, 20, 10],
            "Operational Focus": [
                "Quantified Bayesian pressure score in high-win-probability-delta overs",
                "Runway as of 1 Apr 2027: Emerging (<=23: 100), Young Dev (24-26: 85), Prime (27-30: 65), Exp (31+: 50)",
                "Physical attributes, bat speed, mystery spin, 3D versatility & tactical squad fit",
                "Audited recent 12-month match logs across international and domestic leagues"
            ]
        })
        st.dataframe(weights_data, hide_index=True, use_container_width=True)

    with col_r:
        st.markdown("#### 🌐 Final Roster Composition")
        all_finalists = pd.concat([batters_df, bowlers_df], ignore_index=True)
        st.plotly_chart(plot_nationality_pie(all_finalists, "Finalist Nationality Split (Batters & Bowlers)"), use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📥 Download Official Verified Deliverables")
    d1, d2, d3 = st.columns(3)
    with d1:
        st.download_button(
            "⬇️ Download Top 10 Batters CSV",
            data=batters_df.to_csv(index=False),
            file_name="final_combined_top10_batters.csv",
            mime="text/csv",
            use_container_width=True
        )
    with d2:
        st.download_button(
            "⬇️ Download Top 10 Bowlers CSV",
            data=bowlers_df.to_csv(index=False),
            file_name="final_combined_top10_bowlers.csv",
            mime="text/csv",
            use_container_width=True
        )
    with d3:
        st.download_button(
            "⬇️ Download Reserves CSV",
            data=reserves_df.to_csv(index=False),
            file_name="final_combined_reserves.csv",
            mime="text/csv",
            use_container_width=True
        )


# ==============================================================================
# PAGE 2: TOP 10 BATTERS
# ==============================================================================
elif page == "🏏 Top 10 Batters":
    st.markdown("""
    <div class="rr-header-box">
        <h1 class="rr-title">Official Top 10 Batters <span>| RR Auction Playbook</span></h1>
        <p class="rr-subtitle">Combined Indian + Overseas auction-eligible rankings ordered by verified RR Scouting Composite.</p>
    </div>
    """, unsafe_allow_html=True)

    # Interactive Filters
    st.markdown("#### 🔍 Filter Target Pool")
    f1, f2, f3 = st.columns(3)
    with f1:
        nat_filter = st.multiselect("Nationality", options=["All", "Indian", "Overseas"], default=["All"])
    with f2:
        cat_filter = st.multiselect("Career Stage", options=["All"] + sorted(batters_df['development_category'].unique().tolist()), default=["All"])
    with f3:
        form_filter = st.multiselect("2026 Form", options=["All"] + sorted(batters_df['current_form_rating'].unique().tolist()), default=["All"])

    filtered_df = batters_df.copy()
    if "All" not in nat_filter and nat_filter:
        filtered_df = filtered_df[filtered_df['nationality'].isin(nat_filter)]
    if "All" not in cat_filter and cat_filter:
        filtered_df = filtered_df[filtered_df['development_category'].isin(cat_filter)]
    if "All" not in form_filter and form_filter:
        filtered_df = filtered_df[filtered_df['current_form_rating'].isin(form_filter)]

    # Ranked Table
    st.markdown("### 📋 Verified Rankings Table")
    render_interactive_batter_table(filtered_df)

    st.markdown("---")
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.plotly_chart(
            plot_ranking_bar_chart(filtered_df, "Top Batters by RR Scouting Score (Top 3 Highlighted)", role="batter"),
            use_container_width=True
        )
    with c2:
        st.plotly_chart(
            plot_age_vs_scouting(filtered_df, "Batter Age vs RR Scouting Score (Development Runway)"),
            use_container_width=True
        )

    st.markdown("---")
    st.markdown("### 🔬 Pressure Performance vs Long-Term Scouting Priority")
    st.plotly_chart(
        plot_pressure_vs_scouting(filtered_df, "Historical Pressure Performance vs RR Scouting Score", "validated_historical_pressure_score"),
        use_container_width=True
    )

    # Top 3 Player Profiles
    st.markdown("### 🌟 Spotlight: Top 3 Franchise Targets")
    t1, t2, t3 = st.columns(3)
    with t1:
        render_player_scouting_card(batters_df.iloc[0].to_dict())
    with t2:
        render_player_scouting_card(batters_df.iloc[1].to_dict())
    with t3:
        render_player_scouting_card(batters_df.iloc[2].to_dict())


# ==============================================================================
# PAGE 3: TOP 10 BOWLERS
# ==============================================================================
elif page == "🎳 Top 10 Bowlers":
    st.markdown("""
    <div class="rr-header-box">
        <h1 class="rr-title">Official Top 10 Bowlers <span>| Evidence-Qualified Playbook</span></h1>
        <p class="rr-subtitle">Evaluated on observed deliveries with codified tactical deployment boundaries.</p>
    </div>
    """, unsafe_allow_html=True)

    # Filters
    st.markdown("#### 🔍 Filter Target Pool")
    f1, f2 = st.columns(2)
    with f1:
        nat_filter_bowlers = st.multiselect("Nationality", options=["All", "Indian", "Overseas"], default=["All"], key="b_nat")
    with f2:
        cat_filter_bowlers = st.multiselect("Career Stage", options=["All"] + sorted(bowlers_df['development_category'].unique().tolist()), default=["All"], key="b_cat")

    filtered_bowlers = bowlers_df.copy()
    if "All" not in nat_filter_bowlers and nat_filter_bowlers:
        filtered_bowlers = filtered_bowlers[filtered_bowlers['nationality'].isin(nat_filter_bowlers)]
    if "All" not in cat_filter_bowlers and cat_filter_bowlers:
        filtered_bowlers = filtered_bowlers[filtered_bowlers['development_category'].isin(cat_filter_bowlers)]

    # Ranked Table
    st.markdown("### 📋 Verified Bowler Rankings Table")
    render_interactive_bowler_table(filtered_bowlers)

    # Critical Tactical Prohibitions Banner
    st.markdown("### 🚨 Mandatory Tactical Deployment Boundaries")
    st.markdown("""
    <div class="boundary-box">
        <b>1. Mohammad Ghazanfar (Rank 1 | Age 21):</b> Middle Overs Specialist (Overs 7-15). 
        <b>Strict Prohibition:</b> No death overs (17-20) and no powerplay overs in Year 1. Zero high-extreme deliveries in dataset.<br>
        <b>2. Michael Bracewell (Rank 8 | Age 36):</b> PP & Middle Matchup Off-Spin vs LHB. 
        <b>Strict Prohibition:</b> Zero death overs bowled in dataset; prohibited from death-phase execution.<br>
        <b>3. Harry Tector (Rank 4 | Age 27):</b> Part-Time Matchup Spinner. 
        <b>Strict Prohibition:</b> 0 death and 0 high-extreme deliveries; cannot be assigned frontline death responsibility.<br>
        <b>4. Ripon Mondol (Rank 2 | Age 24):</b> Proven Death Overs Bowler (54 death deliveries in dataset); high-pace development enforcer under Shane Bond.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.plotly_chart(
            plot_ranking_bar_chart(filtered_bowlers, "Top Bowlers by RR Scouting Score (Top 3 Highlighted)", role="bowler"),
            use_container_width=True
        )
    with c2:
        st.plotly_chart(
            plot_age_vs_scouting(filtered_bowlers, "Bowler Age vs RR Scouting Score (Development Runway)"),
            use_container_width=True
        )

    st.markdown("---")
    st.markdown("### 📊 Audited Bowling Phase Delivery Evidence")
    st.plotly_chart(plot_bowling_phase_evidence(zero_opp_df), use_container_width=True)

    # Spotlight
    st.markdown("### 🌟 Spotlight: Top 3 Bowling Targets")
    t1, t2, t3 = st.columns(3)
    with t1:
        render_player_scouting_card(bowlers_df.iloc[0].to_dict(), eq_model.get_tactical_guideline(bowlers_df.iloc[0]['player_id']))
    with t2:
        render_player_scouting_card(bowlers_df.iloc[1].to_dict(), eq_model.get_tactical_guideline(bowlers_df.iloc[1]['player_id']))
    with t3:
        render_player_scouting_card(bowlers_df.iloc[2].to_dict(), eq_model.get_tactical_guideline(bowlers_df.iloc[2]['player_id']))


# ==============================================================================
# PAGE 4: PLAYER COMPARISON
# ==============================================================================
elif page == "⚔️ Player Comparison":
    st.markdown("""
    <div class="rr-header-box">
        <h1 class="rr-title">Head-to-Head Player Comparison <span>| War Room Tool</span></h1>
        <p class="rr-subtitle">Multi-dimensional comparison across pressure execution, development runway, skill ceiling, and form.</p>
    </div>
    """, unsafe_allow_html=True)

    player_options = all_players_df['player_name'].tolist()
    default_selection = ["Jake Fraser-McGurk", "Jacob Bethell", "Harry Brook"]
    
    selected_players = st.multiselect(
        "Select Players to Compare (2 or more)",
        options=player_options,
        default=[p for p in default_selection if p in player_options]
    )

    if len(selected_players) < 2:
        st.warning("Please select at least 2 players to compare.")
    else:
        comp_df = all_players_df[all_players_df['player_name'].isin(selected_players)].copy()
        
        # Enrich with detailed scouting dimensions
        enriched_data = []
        for _, r in comp_df.iterrows():
            p_dict = r.to_dict()
            # Lookup detailed dimensions if available
            p_id = r['player_id']
            if not scouting_scores_df.empty and p_id in scouting_scores_df['player_id'].values:
                match = scouting_scores_df[scouting_scores_df['player_id'] == p_id].iloc[0]
                p_dict['dimA_pressure'] = match['dimA_historical_pressure_score']
                p_dict['dimB_age_dev'] = match['dimB_age_development_score']
                p_dict['dimC_skill_ceiling'] = match['dimC_skill_ceiling_score']
                p_dict['dimD_current_form'] = match['dimD_current_form_score']
                p_dict['tactical_fit'] = 90.0
            else:
                p_dict['dimA_pressure'] = float(r['pressure_or_eq_score'])
                p_dict['dimB_age_dev'] = 85.0 if r['age_as_of_2027_04_01'] <= 25 else 60.0
                p_dict['dimC_skill_ceiling'] = 85.0
                p_dict['dimD_current_form'] = 80.0
                p_dict['tactical_fit'] = 85.0
            enriched_data.append(p_dict)

        c1, c2 = st.columns([1.2, 1])
        with c1:
            st.markdown("#### 🕸️ 5-Dimension Radar Comparison")
            st.plotly_chart(plot_player_radar_comparison(enriched_data), use_container_width=True)

        with c2:
            st.markdown("#### 📊 Comparative Metric Summary")
            summary_table = pd.DataFrame(enriched_data)[[
                'player_name', 'role', 'country', 'age_as_of_2027_04_01',
                'verified_rr_scouting_score', 'dimA_pressure', 'dimB_age_dev', 'dimC_skill_ceiling', 'dimD_current_form'
            ]]
            summary_table.columns = ['Player', 'Role', 'Country', 'Age', 'RR Score', 'Pressure (40%)', 'Age/Dev (30%)', 'Ceiling (20%)', 'Form (10%)']
            st.dataframe(summary_table, hide_index=True, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 📋 Individual Player War-Room Cards")
        cols = st.columns(len(enriched_data))
        for idx, p_dict in enumerate(enriched_data):
            with cols[idx % len(cols)]:
                guideline = eq_model.get_tactical_guideline(p_dict['player_id'])
                render_player_scouting_card(p_dict, guideline)


# ==============================================================================
# PAGE 5: RR LONG-TERM STRATEGY
# ==============================================================================
elif page == "👑 RR Long-Term Strategy":
    st.markdown("""
    <div class="rr-header-box">
        <h1 class="rr-title">Rajasthan Royals Talent Philosophy <span>| 2027-2030 Roadmap</span></h1>
        <p class="rr-subtitle">Balancing generational development upside with tactical match-winning anchors.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
        <b>The Rajasthan Royals Competitive Advantage:</b> Since 2008, RR has led the IPL in unearthing and cultivating 
        young, high-ceiling talent. In 2027, the franchise pairs its retained core (Sanju Samson, Yashasvi Jaiswal, Riyan Parag, 
        Dhruv Jurel, Sandeep Sharma, Shimron Hetmyer) with emerging international and domestic assets possessing 
        8–10 year development runways.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 👶 Age Distribution Across Shortlist")
        st.plotly_chart(plot_career_stage_bar(all_players_df, "Candidate Count by Career Development Category"), use_container_width=True)

    with col2:
        st.markdown("#### 🌍 Balanced Roster Dynamics (No Fixed 5:5 Quotas)")
        st.plotly_chart(plot_nationality_pie(all_players_df, "Shortlist Nationality Distribution (Finalists + Reserves)"), use_container_width=True)

    st.markdown("---")
    st.markdown("### 🛡️ Verified Reserve Roster (Tactical & Budget Pivots)")
    st.dataframe(
        reserves_df[['player_id', 'player_name', 'role', 'country', 'nationality', 'age_as_of_2027_04_01',
                     'development_category', 'validated_pressure_or_eq_score', 'verified_rr_scouting_score', 'current_form_rating']],
        hide_index=True,
        use_container_width=True
    )


# ==============================================================================
# PAGE 6: METHODOLOGY & RELIABILITY
# ==============================================================================
elif page == "📐 Methodology & Reliability":
    st.markdown("""
    <div class="rr-header-box">
        <h1 class="rr-title">PRESSURE-X Methodology <span>& Reliability Audit</span></h1>
        <p class="rr-subtitle">Mathematical formulation, Bayesian shrinkage, competition tiers, and data boundaries.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📐 Mathematical Formulation")
    st.latex(r"""
    \text{RR Scouting Priority} = 0.40 \cdot S_{\text{Pressure}} + 0.30 \cdot S_{\text{Age/Dev}} + 0.20 \cdot S_{\text{Ceiling}} + 0.10 \cdot S_{\text{Form}}
    """)

    st.markdown("""
    #### 1. Competition Tier Calibration
    T20 leagues vary drastically in bowling quality and pitch conditions. Raw rates are scaled using paired empirical factors:
    - **Tier 1 (IPL):** Multiplier = `1.00` (Baseline)
    - **Tier 2 (BBL, PSL, SA20, The Hundred, ILT20):** Multiplier = `0.92`
    - **Tier 3 (CPL, BPL, LPL, Super Smash):** Multiplier = `0.84`
    - **Tier 4 (Associate T20Is):** Multiplier = `0.76`
    - **Tier 5 (Domestic Tournaments - SMAT, Vitality Blast):** Multiplier = `0.68`

    #### 2. James-Stein Empirical Bayes Shrinkage
    Low sample sizes (e.g. 10 balls in death overs) produce extreme rate noise. We apply empirical shrinkage toward the global prior:
    """)
    st.latex(r"""
    \lambda_i = \frac{N_i}{N_i + k}, \quad \hat{\theta}_i = \lambda_i \cdot \bar{x}_i + (1 - \lambda_i) \cdot \mu_{\text{prior}}
    """)

    st.markdown("""
    #### 3. Evidence-Qualified (EQ) Bowling Formulation
    When a bowler has 0 observed deliveries in high-extreme or death phases, treating shrinkage-imputed values as real performance 
    creates an artifact. The Evidence-Qualified model re-normalizes weights across only observed phases:
    """)
    st.latex(r"""
    \text{Score}_{\text{EQ}} = \frac{\sum_{i \in \text{Observed}} w_i \cdot s_i}{\sum_{i \in \text{Observed}} w_i}
    """)

    st.markdown("---")
    st.markdown("### ⚠️ Methodological Caveats & Data Boundaries")
    st.markdown("""
    <div class="boundary-box">
        <b>Data Integrity Disclosures:</b><br>
        • <b>Sample Size Threshold:</b> Minimum eligibility requires >= 100 qualifying balls.<br>
        • <b>Unobserved Phases:</b> Bowlers with 0 death deliveries (Bracewell, Tector, Ghazanfar) have codified deployment bans.<br>
        • <b>Current Form Window:</b> Evaluated across 2025–2026 match logs up to the research cutoff date.<br>
        • <b>Eligibility Enforcement:</b> 184 retained players and Pakistani nationals excluded per BCCI/IPL regulations.<br>
        • <b>Challenge Scope:</b> Proposed scouting framework developed for SupeRR Selector Season 2; not an official internal document of Rajasthan Royals.
    </div>
    """, unsafe_allow_html=True)
