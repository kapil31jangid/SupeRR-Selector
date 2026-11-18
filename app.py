"""
PRESSURE-X 2.0 | Rajasthan Royals IPL 2027 Scouting Intelligence
=================================================================
Complete Interactive Cricket Recruitment Intelligence Platform

10-Page Navigation:
1. Executive Overview — KPIs, mandate, official deliverables
2. Scouting Explorer — Filter-first table with 664 players (View A)
3. Dynamic Ranking Engine — Custom weight sliders, missing data policy, sensitivity
4. RR Current Squad — Retained players from retained_players.csv (View C)
5. RR Gap Analysis — Need vs strength, vacancy fit scoring
6. Domestic Intelligence — All domestic competition tiers (Tier 5)
7. Player Comparison — Multi-player radar, phase overlays
8. Backboard AI Assistant — Persistent thread, natural language queries
9. Standard Scouting Report — One-click CSV export
10. Methodology & Reliability — Mathematical formulation, caveats
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
    load_complete_pool_enriched,
    load_rr_current_squad,
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
from PIL import Image
import base64

from models.bowling_eq_model import EvidenceQualifiedBowlingModel
from dashboard.pages.ai_scouting_lab import render_ai_scouting_lab
from dashboard.pages.scouting_explorer import render_scouting_explorer
from dashboard.pages.rr_squad_analysis import render_rr_squad_analysis
from dashboard.pages.domestic_intelligence import render_domestic_intelligence
from dashboard.pages.dynamic_ranking import render_dynamic_ranking

# Resolve official logo path
LOGO_PATH = PROJECT_ROOT / "assets" / "rr_logo.png"
app_icon = Image.open(LOGO_PATH) if LOGO_PATH.exists() else "👑"

# Configure Page
st.set_page_config(
    page_title="PRESSURE-X 2.0 | RR Scouting Intelligence",
    page_icon=app_icon,
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

# Load Core Datasets
batters_df = load_final_batters()
bowlers_df = load_final_bowlers()
reserves_df = load_final_reserves()
scouting_scores_df = load_scouting_priority_scores()
deployment_df = load_bowling_deployment()
zero_opp_df = load_zero_opportunity_audit()
form_audit_df = load_current_form_audit()
retained_df = load_retained_players()
official_shortlist_df = get_all_shortlist_players()
complete_pool_df = load_complete_pool_enriched()
rr_squad_df = load_rr_current_squad()
eq_model = EvidenceQualifiedBowlingModel()

# Sidebar Branding & Navigation
with st.sidebar:
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as _f_img:
            _b64_logo = base64.b64encode(_f_img.read()).decode()
        st.markdown(f"""
        <div style="text-align: center; padding: 10px 0 16px 0;">
            <div style="background: #FFFFFF; border-radius: 12px; padding: 10px 16px; display: inline-block; box-shadow: 0 4px 14px rgba(0,0,0,0.4); margin-bottom: 8px;">
                <img src="data:image/png;base64,{_b64_logo}" style="width: 140px; display: block; margin: 0 auto;" alt="Rajasthan Royals">
            </div>
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">
                IPL 2027 Auction Intelligence
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 12px 0 20px 0;">
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
            "📊 1. Executive Overview",
            "🎯 2. Scouting Explorer",
            "📐 3. Dynamic Ranking Engine",
            "🛡️ 4. RR Current Squad",
            "🔍 5. RR Gap Analysis",
            "🏏 6. Domestic Intelligence",
            "⚔️ 7. Player Comparison",
            "🤖 8. AI Assistant",
            "📋 9. Standard Scouting Report",
            "📐 10. Methodology & Reliability"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.75rem; color: #64748B; padding: 4px;">
        <b>PRESSURE-X 2.0</b><br>
        311 Unique Eligible Players (664 Player-Seasons)<br>
        Dynamic 40/30/20/10 Model<br>
        RR Squad Gap Analysis<br>
        Forensic Audit: 100% Verified
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# PAGE 1: EXECUTIVE OVERVIEW
# ==============================================================================
if page == "📊 1. Executive Overview":
    st.markdown("""
    <div class="rr-header-box">
        <h1 class="rr-title">PRESSURE-X 2.0 <span>| RR Scouting Intelligence</span></h1>
        <p class="rr-subtitle">Complete cricket recruitment intelligence platform for IPL 2027 auction.</p>
    </div>
    """, unsafe_allow_html=True)

    # KPI Top Bar
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        render_kpi_card("Total Deliveries", "201,000+", "5 Competition Tiers", "#3B82F6")
    with k2:
        render_kpi_card("Eligible Pool", "311 Players", "All 5 Tiers (664 player-seasons)", "#EA1B86")
    with k3:
        render_kpi_card("Official Shortlist", "28 Players", "View B (Archived)", "#10B981")
    with k4:
        render_kpi_card("RR Retained Squad", f"{len(rr_squad_df)} Players", "View C", "#F59E0B")
    with k5:
        render_kpi_card("Retained Excluded", f"{len(retained_df)} Players", "10 IPL Franchises", "#EF4444")
    with k6:
        render_kpi_card("Domestic Evidence", f"{(complete_pool_df['has_domestic_evidence'].sum() if not complete_pool_df.empty else 0):.0f} Players", "Tier 5 Coverage", "#6366F1")

    st.markdown("### 🎯 Executive Mandate")
    st.markdown("""
    <div class="insight-box">
        <b>Core Challenge:</b> Traditional T20 scouting over-indexes on raw aggregate strike rates and unadjusted boundary counts.
        <b>PRESSURE-X 2.0</b> introduces a complete interactive recruitment intelligence platform with:
        <ul>
        <li><b>View A:</b> Complete 664-player auction-eligible pool with dynamic ranking engine</li>
        <li><b>View B:</b> Official 28-player verified shortlist (archived benchmark)</li>
        <li><b>View C:</b> RR current squad with gap analysis and vacancy fit scoring</li>
        <li><b>Dynamic Ranking:</b> Customizable 40/30/20/10 weights with sensitivity analysis</li>
        <li><b>Domestic Intelligence:</b> Tier 5 competition deep-dive for hidden gems</li>
        <li><b>AI Assistant:</b> Backboard × Google Gemini with persistent conversation threads</li>
        </ul>
        All evaluated under game pressure (High-Extreme, Death, Powerplay, Chase) with
        Bayesian shrinkage (prior_weight=30), competition tier adjustment, and evidence-qualified bowling.
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
                "Runway as of 1 Apr 2027: Emerging (≤23: 100), Young Dev (24-26: 85), Prime (27-30: 65), Exp (31+: 50)",
                "Physical attributes, bat speed, mystery spin, 3D versatility & tactical squad fit",
                "Audited recent 12-month match logs across international and domestic leagues"
            ]
        })
        st.dataframe(weights_data, hide_index=True, use_container_width=True)

    with col_r:
        st.markdown("#### 🌐 Platform Views")
        view_data = pd.DataFrame({
            "View": ["View A: Complete Pool", "View B: Official Shortlist", "View C: RR Squad"],
            "Players": [664, 28, len(rr_squad_df)],
            "Purpose": [
                "Full auction universe with dynamic ranking",
                "Verified benchmark (10 bat, 10 bowl, 8 res)",
                "Current retained squad with gap analysis"
            ],
            "Key Features": [
                "Custom weights, sensitivity, filters",
                "Read-only, audited, immutable",
                "Vacancy fit, role coverage, runway"
            ]
        })
        st.dataframe(view_data, hide_index=True, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📥 Download Official Verified Deliverables (View B)")
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
# PAGE 2: SCOUTING EXPLORER (FILTER-FIRST WITH 664 PLAYERS)
# ==============================================================================
elif page == "🎯 2. Scouting Explorer":
    render_scouting_explorer()


# ==============================================================================
# PAGE 3: DYNAMIC RANKING ENGINE
# ==============================================================================
elif page == "📐 3. Dynamic Ranking Engine":
    render_dynamic_ranking()


# ==============================================================================
# PAGE 4: RR CURRENT SQUAD
# ==============================================================================
elif page == "🛡️ 4. RR Current Squad":
    st.markdown("""
    <div class="rr-header-box">
        <h1 class="rr-title">Rajasthan Royals Current Squad <span>| View C: 19 Retained Players</span></h1>
        <p class="rr-subtitle">Complete retained squad from IPL 2027 retention with roles, ages, and nationalities.</p>
    </div>
    """, unsafe_allow_html=True)

    if rr_squad_df.empty:
        st.error("RR squad data not available. Run build_rr_squad.py first.")
    else:
        # Add nationality column derived from overseas_status
        if 'nationality' not in rr_squad_df.columns and 'overseas_status' in rr_squad_df.columns:
            rr_squad_df = rr_squad_df.copy()
            rr_squad_df['nationality'] = rr_squad_df['overseas_status'].map({'Domestic': 'Indian', 'Overseas': 'Overseas'})

        # KPI Row
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Total Retained", len(rr_squad_df))
        with k2:
            overseas = (rr_squad_df['nationality'] == 'Overseas').sum()
            st.metric("Overseas Slots Used", f"{overseas}/8")
        with k3:
            indian = (rr_squad_df['nationality'] == 'Indian').sum()
            st.metric("Indian Players", indian)
        with k4:
            avg_age = rr_squad_df['age_as_of_2027_04_01'].mean()
            st.metric("Average Age", f"{avg_age:.1f} yrs")

        # Visuals
        col_viz1, col_viz2 = st.columns(2)
        with col_viz1:
            st.plotly_chart(plot_nationality_pie(rr_squad_df, "RR Squad Nationality Split"), use_container_width=True)
        with col_viz2:
            st.plotly_chart(plot_career_stage_bar(rr_squad_df, "RR Squad Career Stage Distribution"), use_container_width=True)

        # Squad table
        st.markdown("### 📋 Retained Squad Roster")
        display_cols = ['player_id', 'player_name', 'primary_role', 'nationality', 'age_as_of_2027_04_01',
                        'development_category', 'batting_style', 'bowling_style', 'wk_flag', 'retention_type']
        clean_squad = rr_squad_df[[c for c in display_cols if c in rr_squad_df.columns]].copy()

        st.dataframe(
            clean_squad,
            column_config={
                "player_id": st.column_config.NumberColumn("ID", width="small"),
                "player_name": st.column_config.TextColumn("Player", width="medium"),
                "primary_role": st.column_config.TextColumn("Role", width="medium"),
                "nationality": st.column_config.TextColumn("Nat", width="small"),
                "age_as_of_2027_04_01": st.column_config.NumberColumn("Age", format="%.1f", width="small"),
                "development_category": st.column_config.TextColumn("Dev Stage", width="medium"),
                "batting_style": st.column_config.TextColumn("Bat Style", width="small"),
                "bowling_style": st.column_config.TextColumn("Bowl Style", width="medium"),
                "wk_flag": st.column_config.CheckboxColumn("WK", width="small"),
                "retention_type": st.column_config.TextColumn("Type", width="small")
            },
            hide_index=True,
            use_container_width=True
        )

        # Role coverage
        st.markdown("### 🎯 Role Coverage")
        role_counts = rr_squad_df['primary_role'].value_counts().reset_index()
        role_counts.columns = ['Role', 'Count']
        st.bar_chart(role_counts.set_index('Role'))

        # Download
        csv = rr_squad_df.to_csv(index=False)
        st.download_button(
            "⬇️ Download RR Squad CSV",
            data=csv,
            file_name="rr_current_squad.csv",
            mime="text/csv",
            use_container_width=True
        )


# ==============================================================================
# PAGE 5: RR GAP ANALYSIS
# ==============================================================================
elif page == "🔍 5. RR Gap Analysis":
    render_rr_squad_analysis()


# ==============================================================================
# PAGE 6: DOMESTIC INTELLIGENCE
# ==============================================================================
elif page == "🏏 6. Domestic Intelligence":
    render_domestic_intelligence()


# ==============================================================================
# PAGE 7: PLAYER COMPARISON
# ==============================================================================
elif page == "⚔️ 7. Player Comparison":
    st.markdown("""
    <div class="rr-header-box">
        <h1 class="rr-title">Head-to-Head Player Comparison <span>| War Room Tool</span></h1>
        <p class="rr-subtitle">Multi-dimensional comparison across 664 eligible players with phase overlays.</p>
    </div>
    """, unsafe_allow_html=True)

    player_options = complete_pool_df['player_name'].tolist()
    default_selection = ["Jake Fraser-McGurk", "Jacob Bethell", "Harry Brook"]

    selected_players = st.multiselect(
        "Select Candidates to Compare (Search any of 664 Eligible Players)",
        options=player_options,
        default=[p for p in default_selection if p in player_options]
    )

    if len(selected_players) < 2:
        st.warning("Please select at least 2 players to compare.")
    else:
        comp_df = complete_pool_df[complete_pool_df['player_name'].isin(selected_players)].copy()

        enriched_data = []
        for _, r in comp_df.iterrows():
            p_dict = r.to_dict()
            p_dict['dimA_pressure'] = float(r.get('dimA_pressure', r['pressure_or_eq_score']))
            p_dict['dimB_age_dev'] = float(r.get('dimB_runway', 65.0))
            p_dict['dimC_skill_ceiling'] = float(r.get('dimC_ceiling', 70.0))
            p_dict['dimD_current_form'] = float(r.get('dimD_form', 70.0))
            p_dict['tactical_fit'] = 90.0 if r.get('is_shortlisted') else 75.0
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
        cols = st.columns(min(len(enriched_data), 3))
        for idx, p_dict in enumerate(enriched_data):
            with cols[idx % len(cols)]:
                guideline = eq_model.get_tactical_guideline(p_dict['player_id'])
                render_player_scouting_card(p_dict, guideline)


# ==============================================================================
# PAGE 8: AI ASSISTANT
# ==============================================================================
elif page == "🤖 8. AI Assistant":
    render_ai_scouting_lab(complete_pool_df)


# ==============================================================================
# PAGE 9: STANDARD SCOUTING REPORT
# ==============================================================================
elif page == "📋 9. Standard Scouting Report":
    from dashboard.utils.data_loader import build_standard_scouting_report, export_standard_scouting_report

    st.markdown("""
    <div class="rr-header-box">
        <h1 class="rr-title">Standard Scouting Report <span>| One-Click CSV Export</span></h1>
        <p class="rr-subtitle">Generate standardized scouting reports for any candidate subset.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    **Standard Report Columns:** Player ID, Name, Role, Country, Nationality, Age, Development Stage, View,
    Official Shortlist, RR Scouting Score (40/30/20/10), Pressure/EQ Base Score, 4 Dimension Scores,
    Form Rating, Observed Balls, Evidence Confidence, High-Extreme Balls, Career Stats, Domestic Stats,
    Phase Stats (PP/Mid/Death), Deployment Guidelines, Form Evidence, Domestic Evidence,
    Characteristics, Primary Role, Batting/Bowling Style, WK Flag, Overseas Status.
    """)

    # Filter options
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        report_scope = st.selectbox(
            "Report Scope",
            ["All 311 Players (View A)", "Official Shortlist 28 (View B)", "RR Squad 19 (View C)", "Custom Selection"],
            key="report_scope"
        )
    with col_f2:
        report_role = st.selectbox("Role Filter", ["All", "Batter", "Bowler", "All-rounder"], key="report_role")
    with col_f3:
        report_nat = st.selectbox("Nationality", ["All", "Indian", "Overseas"], key="report_nat")
    with col_f4:
        report_limit = st.number_input("Max Players", 10, 664, 50, key="report_limit")

    # Build filtered pool
    if report_scope == "All 311 Players (View A)":
        report_pool = complete_pool_df.copy()
    elif report_scope == "Official Shortlist 28 (View B)":
        report_pool = complete_pool_df[complete_pool_df['is_shortlisted'] == True].copy()
    elif report_scope == "RR Squad 19 (View C)":
        report_pool = complete_pool_df[complete_pool_df['view'] == 'View C: RR Squad'].copy() if 'view' in complete_pool_df.columns else complete_pool_df[complete_pool_df['player_id'].isin(rr_squad_df['player_id'])].copy()
    else:
        report_pool = complete_pool_df.copy()

    if report_role != "All":
        report_pool = report_pool[report_pool['role'] == report_role]
    if report_nat != "All":
        report_pool = report_pool[report_pool['nationality'] == report_nat]

    report_pool = report_pool.head(report_limit)

    st.info(f"📊 Report will include **{len(report_pool)} players**")

    # Preview
    if st.checkbox("Show Preview (First 5 Rows)", value=True):
        preview_df = build_standard_scouting_report(report_pool.head(5))
        st.dataframe(preview_df, hide_index=True, use_container_width=True)

    # Generate & Download
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📥 Generate & Download Standard Report (CSV)", type="primary", use_container_width=True):
            report_df = build_standard_scouting_report(report_pool)
            csv = report_df.to_csv(index=False)
            st.download_button(
                "⬇️ Download Standard Scouting Report",
                data=csv,
                file_name=f"standard_scouting_report_{report_scope.replace(' ', '_').replace('(', '').replace(')', '')}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.success(f"✅ Report generated with {len(report_df)} players!")

    with c2:
        if st.button("📊 Generate Dynamic Rankings Export", use_container_width=True):
            from src.scoring.dynamic_scouting_engine import create_default_engine
            engine = create_default_engine()
            engine.fit(report_pool)
            ranked = engine.rank_candidates(report_pool)
            csv = ranked.to_csv(index=False)
            st.download_button(
                "⬇️ Download Dynamic Rankings",
                data=csv,
                file_name=f"dynamic_rankings_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.success("✅ Dynamic rankings exported!")


# ==============================================================================
# PAGE 10: METHODOLOGY & RELIABILITY
# ==============================================================================
elif page == "📐 10. Methodology & Reliability":
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
    """)

    st.markdown("#### 2. James-Stein Empirical Bayes Shrinkage")
    st.markdown("Low sample sizes (e.g. 10 balls in death overs) produce extreme rate noise. We apply empirical shrinkage toward the global prior:")
    st.latex(r"""
    \lambda_i = \frac{N_i}{N_i + k}, \quad \hat{\theta}_i = \lambda_i \cdot \bar{x}_i + (1 - \lambda_i) \cdot \mu_{\text{prior}}
    """)
    st.markdown("With prior_weight `k = 30` calibrated on IPL population.")

    st.markdown("#### 3. Evidence-Qualified (EQ) Bowling Formulation")
    st.markdown("When a bowler has 0 observed deliveries in high-extreme or death phases, treating shrinkage-imputed values as real performance creates an artifact. The Evidence-Qualified model re-normalizes weights across only observed phases:")
    st.latex(r"""
    \text{Score}_{\text{EQ}} = \frac{\sum_{i \in \text{Observed}} w_i \cdot s_i}{\sum_{i \in \text{Observed}} w_i}
    """)

    st.markdown("#### 4. Dynamic Ranking Engine")
    st.markdown("""
    The Dynamic Ranking Engine (`src/scoring/dynamic_scouting_engine.py`) enables:
    - **Custom Weight Profiles**: RR Default (40/30/20/10), Pressure First, Youth Focus, Ceiling Chaser, Form Watcher
    - **Missing Data Policies**: Population Mean/Median, Neutral, Zero, Weight Redistribution
    - **Evidence Gating**: Confidence penalty for low sample sizes (< 30 balls default)
    - **Sensitivity Analysis**: Rank stability under weight perturbations (±15 pts, 7 steps)
    - **Domestic Bonus**: Optional bonus for verified domestic T20 evidence
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
        • <b>Domestic Data Limitation:</b> No ball-by-ball data for domestic competitions; metrics from available aggregates only.<br>
        • <b>Player Metadata:</b> DOB, batting/bowling style, WK status only for shortlisted players (30); estimated for rest.<br>
        • <b>Challenge Scope:</b> Proposed scouting framework for SupeRR Selector Season 2; not an official RR internal document.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📊 Validation Summary (Task 07E)")
    val_data = pd.DataFrame({
        "Check": [
            "Monotonicity (Pre-delivery state)",
            "Batter runs ≥ 0",
            "Legal ball definition",
            "Bowler runs per cricket laws",
            "Bowler wicket credit rules",
            "Player identity joins",
            "Paired T1↔T2 factors",
            "Paired T2↔T3 factors",
            "Population T1 vs T2",
            "Population T2 vs T3",
            "Final shortlist corrections"
        ],
        "Status": ["PASS"] * 11,
        "Details": [
            "All pre-delivery variables monotonic",
            "0 negatives across 200K+ deliveries",
            "7,735 wides correctly excluded",
            "Wides=extras1, NB=runs+extras1, Byes=0",
            "Only Bowled/Caught/LBW/Stump/HitWicket/Obstructing",
            "Join on player_id only; 3 ID corrections applied",
            "107 batters, 110 bowlers overlap",
            "104 batters, 108 bowlers overlap",
            "154,631 legal balls; factor 1.02",
            "19,298 legal balls; factor 1.00",
            "5 corrections in final_shortlist_corrections.csv"
        ]
    })
    st.dataframe(val_data, hide_index=True, use_container_width=True)