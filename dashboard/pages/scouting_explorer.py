"""
PRESSURE-X Interactive Scouting Explorer Page
==============================================
Primary interface for the Rajasthan Royals IPL 2027 Scouting Analytics Dashboard.

Sections:
- Section A: Interactive Scouting Explorer (Primary — Filter-first, charts, tables, player details)
- Section B: Ask AI Scouting Assistant (Optional — Collapsed by default, powered by Backboard x Google Gemini)
"""

import hashlib
import json
from typing import Dict, Any, List, Optional
import pandas as pd
import streamlit as st

from dashboard.utils.scouting_data import (
    load_complete_pool_enriched,
    apply_scouting_filters,
    load_bowling_zero_opp
)
from dashboard.utils.formatting import (
    format_category_badge,
    format_nationality_badge,
    format_form_badge,
    RR_PINK,
    RR_ROYAL_BLUE,
    RR_GOLD,
    RR_NAVY_CARD,
    RR_DARK_NAVY
)
from dashboard.charts import (
    plot_ranking_bar_chart,
    plot_pressure_vs_scouting,
    plot_age_vs_scouting,
    plot_nationality_pie,
    plot_career_stage_bar,
    plot_bowling_phase_evidence
)
from src.ai.backboard_scouting_assistant import BackboardScoutingAssistant


# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------

def _init_session_state():
    defaults = {
        "se_role": "Any",
        "se_nat": "Both",
        "se_country": "All",
        "se_age_grp": "All",
        "se_age_min": 18.0,
        "se_age_max": 42.0,
        "se_min_pressure": 0.0,
        "se_min_rr": 0.0,
        "se_min_eq": 0.0,
        "se_form": ["All"],
        "se_conf": ["All"],
        "se_min_balls": 0,
        "se_dom_runs": 0.0,
        "se_dom_avg": 0.0,
        "se_dom_sr": 0.0,
        "se_dom_wkt": 0.0,
        "se_dom_econ": 15.0,
        "se_char": "All",
        "se_dev_pref": "All",
        "se_limit": 10,
        "se_search": "",
        "se_pool_scope": "Full Eligible Pool (303 Players)",
        "se_ai_result": None,
        "se_ai_thread_id": None,
        "se_ai_filter_hash": None,
        "se_selected_player_id": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _compute_filter_hash() -> str:
    """Create a hash of active filter parameters to detect stale AI insights."""
    filter_dict = {
        "scope": st.session_state.get("se_pool_scope"),
        "role": st.session_state.get("se_role"),
        "nat": st.session_state.get("se_nat"),
        "age_min": st.session_state.get("se_age_min"),
        "age_max": st.session_state.get("se_age_max"),
        "min_pressure": st.session_state.get("se_min_pressure"),
        "min_rr": st.session_state.get("se_min_rr"),
        "char": st.session_state.get("se_char"),
        "dev": st.session_state.get("se_dev_pref"),
        "search": st.session_state.get("se_search")
    }
    return hashlib.md5(json.dumps(filter_dict, sort_keys=True).encode()).hexdigest()[:8]


# -----------------------------------------------------------------------------
# SECTION A: PLAYER DETAIL CARD (VERIFIED EVIDENCE DRIVEN)
# -----------------------------------------------------------------------------

def _render_player_detail_panel(p: Dict[str, Any]):
    """Render comprehensive player detail view with strict evidence separation."""
    cat_b = format_category_badge(p.get('development_category', ''))
    nat_b = format_nationality_badge(p.get('nationality', ''))
    form_b = format_form_badge(p.get('current_form_rating', ''))

    # Build clean single-line metric cards
    age_val = p.get('age_as_of_2027_04_01', 28.0)
    scout_score = float(p.get('verified_rr_scouting_score', 0))
    p_score = float(p.get('pressure_or_eq_score', 0))
    is_sl = p.get('is_shortlisted', False)

    sl_badge = '<span style="background-color:#065F46;color:#6EE7B7;padding:2px 8px;border-radius:10px;font-size:0.75rem;font-weight:600;">⭐ VERIFIED SHORTLIST</span>' if is_sl else '<span style="background-color:#1E293B;color:#94A3B8;padding:2px 8px;border-radius:10px;font-size:0.75rem;font-weight:500;">📋 QUALIFIED POOL</span>'

    # Domestic summary text
    if p.get('has_domestic_evidence'):
        if p.get('role') == 'Batter' or (pd.notnull(p.get('domestic_runs')) and p.get('domestic_runs') > 0):
            dom_text = f"<b>Domestic T20:</b> {int(p.get('domestic_runs', 0))} runs in {int(p.get('domestic_matches', 0))} matches | Avg: {p.get('domestic_batting_avg', '—')} | SR: {p.get('domestic_batting_sr', '—')}"
        else:
            dom_text = f"<b>Domestic T20:</b> {int(p.get('domestic_wickets', 0))} wickets in {int(p.get('domestic_matches', 0))} matches | Econ: {p.get('domestic_bowling_econ', '—')} | Avg: {p.get('domestic_bowling_avg', '—')}"
    else:
        dom_text = "<span style='color:#94A3B8;'><i>Insufficient domestic evidence</i> (Candidate evaluated primarily on global competition coverage)</span>"

    # Restriction warning for bowlers
    restriction_box = ""
    prohib = p.get('prohibited_deployment', 'None')
    if prohib != 'None' and prohib != '—':
        restriction_box = f"""
<div style="background-color:rgba(239,68,68,0.15);border-left:4px solid #EF4444;padding:10px 14px;border-radius:6px;margin:10px 0;font-size:0.82rem;color:#FCA5A5;">
⚠️ <b>DEPLOYMENT BOUNDARY (AUDITED):</b> {prohib}
<div style="font-size:0.75rem;color:#E2E8F0;margin-top:2px;">Demonstrated: {p.get('demonstrated_role','—')} | Projected: {p.get('projected_role','—')}</div>
</div>
"""

    card_html = f"""
<div style="background:#1C2541;border:1px solid rgba(234,27,134,0.35);border-radius:12px;padding:20px;margin-top:14px;box-shadow:0 8px 24px rgba(0,0,0,0.45);">
<div style="display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid rgba(255,255,255,0.1);padding-bottom:12px;">
<div>
<span style="font-size:1.45rem;font-weight:800;color:#FFFFFF;">{p.get('player_name','')}</span>
<span style="font-size:0.85rem;color:#94A3B8;margin-left:8px;">{p.get('country','')} · ID: {p.get('player_id','')} · Role: <b>{p.get('role','')}</b></span>
</div>
<div>{sl_badge}</div>
</div>
<div style="display:flex;gap:6px;margin:10px 0 14px 0;align-items:center;">
{nat_b} {cat_b} {form_b}
<span style="font-size:0.75rem;background:rgba(255,255,255,0.08);padding:2px 8px;border-radius:10px;color:#E2E8F0;">Age: {age_val:.1f} yrs (as of 1 Apr 2027)</span>
<span style="font-size:0.75rem;background:rgba(255,255,255,0.08);padding:2px 8px;border-radius:10px;color:#E2E8F0;">Reliability: {p.get('evidence_confidence','Adequate')}</span>
</div>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px;text-align:center;">
<div style="background:#0B132B;padding:10px;border-radius:8px;border:1px solid rgba(234,27,134,0.3);">
<div style="font-size:0.68rem;color:#94A3B8;text-transform:uppercase;">RR Scouting Score</div>
<div style="font-size:1.5rem;font-weight:800;color:{RR_PINK};">{scout_score:.2f}</div>
<div style="font-size:0.65rem;color:#94A3B8;">40/30/20/10 Model</div>
</div>
<div style="background:#0B132B;padding:10px;border-radius:8px;border:1px solid rgba(0,75,160,0.4);">
<div style="font-size:0.68rem;color:#94A3B8;text-transform:uppercase;">Pressure / EQ Base</div>
<div style="font-size:1.5rem;font-weight:800;color:#FFFFFF;">{p_score:.2f}</div>
<div style="font-size:0.65rem;color:#94A3B8;">Bayesian Execution</div>
</div>
<div style="background:#0B132B;padding:10px;border-radius:8px;">
<div style="font-size:0.68rem;color:#94A3B8;text-transform:uppercase;">Observed Deliveries</div>
<div style="font-size:1.5rem;font-weight:700;color:#10B981;">{p.get('evidence_balls',0)}</div>
<div style="font-size:0.65rem;color:#94A3B8;">Sample Confidence</div>
</div>
<div style="background:#0B132B;padding:10px;border-radius:8px;">
<div style="font-size:0.68rem;color:#94A3B8;text-transform:uppercase;">High-Extreme Balls</div>
<div style="font-size:1.5rem;font-weight:700;color:#F59E0B;">{p.get('high_extreme_balls',0)}</div>
<div style="font-size:0.65rem;color:#94A3B8;">Clutch Phase Depth</div>
</div>
</div>
<div style="background:#0F1C38;padding:12px 14px;border-radius:8px;margin-bottom:10px;font-size:0.83rem;color:#E2E8F0;">
<div style="font-size:0.7rem;font-weight:700;color:#94A3B8;text-transform:uppercase;margin-bottom:4px;">📊 4-Dimension Framework Breakdown (40 / 30 / 20 / 10)</div>
<div style="display:flex;gap:20px;flex-wrap:wrap;">
<div><b>Dim A (Pressure 40%):</b> {p.get('dimA_pressure',0):.1f}</div>
<div><b>Dim B (Age/Runway 30%):</b> {p.get('dimB_runway',0):.1f}</div>
<div><b>Dim C (Skill Ceiling 20%):</b> {p.get('dimC_ceiling',0):.1f}</div>
<div><b>Dim D (Form 10%):</b> {p.get('dimD_form',0):.1f}</div>
</div>
</div>
<div style="background:#0F1C38;padding:10px 14px;border-radius:8px;margin-bottom:10px;font-size:0.82rem;color:#CBD5E1;">
<div style="font-size:0.7rem;font-weight:700;color:#94A3B8;text-transform:uppercase;margin-bottom:4px;">🏏 Audited Domestic Evidence & 2025-2026 Form Log</div>
<div>{dom_text}</div>
<div style="margin-top:4px;font-size:0.78rem;color:#94A3B8;">
<b>Recent Scope:</b> {p.get('form_competition_scope','Global / T20 Leagues')} · <b>Date Window:</b> {p.get('form_date_window','Audited 12-Month')} · <b>Observed Form:</b> {p.get('current_form_rating','Neutral')}
</div>
</div>
{restriction_box}
<div style="font-size:0.72rem;color:#64748B;display:flex;justify-content:space-between;margin-top:8px;">
<span>🔒 <b>Verified Dataset:</b> Audited CSVs (Outputs & Supporting Evidence)</span>
<span>📐 <b>Calculated Metrics:</b> PRESSURE-X v3.0 Bayesian Shrinkage</span>
<span>🏷️ <b>Observed Characteristics:</b> {p.get('characteristics','Standard T20 Performer')}</span>
</div>
</div>
"""
    clean_html = "\n".join(line.strip() for line in card_html.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SECTION B: AI SCOUTING LAB CARD RENDERER
# -----------------------------------------------------------------------------

def _render_ai_player_card(rec: Dict[str, Any], rank: int):
    """Render an individual AI recommendation card."""
    nat_icon = "🇮🇳" if rec.get("nationality") == "Indian" else "🌐"
    score = rec.get("verified_rr_scouting_score", 0.0)
    p_score = rec.get("pressure_or_eq_score", 0.0)
    age = rec.get("age_as_of_2027_04_01", 0.0)

    card_html = f"""
<div style="background:#1C2541;border:1px solid rgba(234,27,134,0.3);border-radius:8px;padding:14px 18px;margin-bottom:12px;">
<div style="font-size:1.05rem;font-weight:800;color:#FFFFFF;">
#{rank} {nat_icon} {rec.get("player_name")}
<span style="font-size:0.8rem;color:#94A3B8;font-weight:400;">
&nbsp;{rec.get("country","")} · {rec.get("role","")} · Age {age:.1f}
</span>
</div>
<div style="font-size:0.78rem;color:#94A3B8;margin:4px 0 8px 0;">{rec.get("development_category","")}</div>
<div style="display:flex;gap:24px;margin-bottom:10px;">
<div>
<span style="font-size:0.7rem;color:#94A3B8;">RR Scouting Score</span><br>
<span style="font-size:1.3rem;font-weight:800;color:#EA1B86;">{score:.2f}</span>
</div>
<div>
<span style="font-size:0.7rem;color:#94A3B8;">Pressure / EQ Score</span><br>
<span style="font-size:1.3rem;font-weight:800;color:#004BA0;">{p_score:.2f}</span>
</div>
<div>
<span style="font-size:0.7rem;color:#94A3B8;">Form</span><br>
<span style="font-size:0.9rem;font-weight:600;color:#F59E0B;">{rec.get("current_form_rating","")}</span>
</div>
</div>
<div style="font-size:0.82rem;color:#E2E8F0;margin-bottom:6px;">
<b style="color:#10B981;">Tactical Fit:</b> {rec.get("tactical_role_fit","")}
</div>
<div style="font-size:0.82rem;color:#CBD5E1;margin-bottom:4px;">
<b style="color:#FFFFFF;">Suitability:</b> {rec.get("suitability_explanation","")}
</div>
<div style="font-size:0.78rem;color:#F59E0B;">
⚠️ <b>Risk:</b> {rec.get("risk_assessment","")}
</div>
</div>
"""
    clean_html = "\n".join(line.strip() for line in card_html.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# MAIN RENDER FUNCTION: SCOUTING EXPLORER + OPTIONAL AI
# -----------------------------------------------------------------------------

def render_scouting_explorer():
    """
    Renders the unified Interactive Scouting Explorer page.
    Filter-first architecture with optional Backboard x Google Gemini AI Assistant.
    """
    _init_session_state()

    # Load complete pool of 303 players
    full_pool_df = load_complete_pool_enriched()
    zero_opp_df = load_bowling_zero_opp()

    # ── Page Header ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0B132B 60%,#2a0a1a);
                border:1px solid rgba(234,27,134,0.4);border-radius:12px;
                padding:22px 28px;margin-bottom:20px;">
        <div style="font-size:1.7rem;font-weight:800;color:#FFFFFF;">
            🎯 Interactive Scouting Explorer
            <span style="font-size:0.9rem;font-weight:400;color:#94A3B8;"> | Complete 303-Player Auction Pool</span>
        </div>
        <div style="font-size:0.88rem;color:#94A3B8;margin-top:6px;">
            Filter, search, and analyze candidates across all 5 competition tiers using verified pressure evidence,
            domestic performance logs, and development runway benchmarks. AI Assistant is fully optional below.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================================
    # SECTION A: INTERACTIVE SCOUTING EXPLORER (PRIMARY)
    # =========================================================================

    with st.expander("🎯 Filter Candidate Pool", expanded=True):
        # Row 1: Core Target Classification
        r1_c1, r1_c2, r1_c3, r1_c4 = st.columns([1.2, 1, 1, 1])
        with r1_c1:
            pool_scope = st.selectbox(
                "Data Scope",
                ["Full Eligible Pool (303 Players)", "Verified Shortlist Only (28 Players)"],
                index=0 if st.session_state.se_pool_scope == "Full Eligible Pool (303 Players)" else 1,
                key="se_pool_scope"
            )
        with r1_c2:
            role = st.selectbox(
                "Player Category",
                ["Any", "Batter", "Bowler", "All-rounder"],
                index=["Any", "Batter", "Bowler", "All-rounder"].index(st.session_state.se_role),
                key="se_role"
            )
        with r1_c3:
            nat = st.selectbox(
                "Nationality",
                ["Both", "Indian", "Overseas"],
                index=["Both", "Indian", "Overseas"].index(st.session_state.se_nat),
                key="se_nat"
            )
        with r1_c4:
            all_countries = ["All"] + sorted([c for c in full_pool_df['country'].dropna().unique().tolist() if c not in ['Overseas', 'India']])
            country = st.selectbox("Country (Specific)", all_countries, index=0, key="se_country")

        # Row 2: Age Group & Runway
        r2_c1, r2_c2, r2_c3 = st.columns([1.2, 1.4, 1.4])
        with r2_c1:
            age_grp = st.selectbox(
                "Age Group (Runway)",
                ["All", "Emerging (≤23 yrs)", "Development (24–26 yrs)", "Prime (27–30 yrs)", "Experienced (31+ yrs)"],
                index=0,
                key="se_age_grp"
            )
        with r2_c2:
            age_min = st.slider("Min Age (Apr 2027)", 18.0, 42.0, float(st.session_state.se_age_min), 0.5, key="se_age_min")
        with r2_c3:
            age_max = st.slider("Max Age (Apr 2027)", 18.0, 42.0, float(st.session_state.se_age_max), 0.5, key="se_age_max")

        # Row 3: Quantitative Performance Thresholds
        r3_c1, r3_c2, r3_c3, r3_c4 = st.columns(4)
        with r3_c1:
            min_pressure = st.slider("Min Pressure / EQ Score", 0.0, 95.0, float(st.session_state.se_min_pressure), 5.0, key="se_min_pressure")
        with r3_c2:
            min_rr = st.slider("Min RR Scouting Score", 0.0, 95.0, float(st.session_state.se_min_rr), 5.0, key="se_min_rr")
        with r3_c3:
            min_balls = st.number_input("Min Career Balls Observed", min_value=0, max_value=2000, value=int(st.session_state.se_min_balls), step=50, key="se_min_balls", help="Evidence sample threshold")
        with r3_c4:
            limit = st.selectbox("Results Limit", [5, 10, 15, 20, 50], index=1, key="se_limit")

        # Row 4: Evidence Confidence, Characteristics & Development Preference
        r4_c1, r4_c2, r4_c3 = st.columns([1.2, 1.4, 1.4])
        with r4_c1:
            char_options = [
                "All",
                "Opening / Powerplay Anchor",
                "Middle-Overs Spin Basher",
                "Death-Over Finisher",
                "Power Hitter (15+ Sixes)",
                "High-Average Anchor",
                "Powerplay Bowler",
                "Middle-Overs Bowler",
                "Death-Overs Closer"
            ]
            char_filter = st.selectbox("Player Characteristics (Evidence-Backed)", char_options, index=0, key="se_char")
        with r4_c2:
            dev_pref = st.selectbox(
                "Development Preference",
                ["All", "Immediate impact", "Long-term development", "High-upside prospect"],
                index=0,
                key="se_dev_pref"
            )
        with r4_c3:
            search_query = st.text_input("🔍 Search Player / Country", value=st.session_state.se_search, key="se_search", placeholder="e.g. Fraser-McGurk, Brook, India...")

        # Row 5: Domestic Performance Filters (Collapsible sub-section)
        with st.expander("🏏 Domestic T20 Performance Filters (Optional)", expanded=False):
            st.caption("Filter candidates based on verified domestic T20 league matches and averages where recorded.")
            d_c1, d_c2, d_c3, d_c4, d_c5 = st.columns(5)
            with d_c1:
                dom_runs = st.number_input("Min Domestic Runs", 0.0, 2000.0, float(st.session_state.se_dom_runs), 50.0, key="se_dom_runs")
            with d_c2:
                dom_avg = st.number_input("Min Batting Avg", 0.0, 60.0, float(st.session_state.se_dom_avg), 5.0, key="se_dom_avg")
            with d_c3:
                dom_sr = st.number_input("Min Strike Rate", 0.0, 220.0, float(st.session_state.se_dom_sr), 10.0, key="se_dom_sr")
            with d_c4:
                dom_wkt = st.number_input("Min Domestic Wkts", 0.0, 100.0, float(st.session_state.se_dom_wkt), 5.0, key="se_dom_wkt")
            with d_c5:
                dom_econ = st.number_input("Max Bowling Econ", 4.0, 15.0, float(st.session_state.se_dom_econ), 0.5, key="se_dom_econ")

        # Action Buttons
        btn_c1, btn_c2, _ = st.columns([1, 1, 4])
        with btn_c1:
            apply_btn = st.button("⚡ Apply Filters", type="primary", use_container_width=True)
        with btn_c2:
            reset_btn = st.button("🔄 Reset Filters", use_container_width=True)

        if reset_btn:
            st.session_state.se_role = "Any"
            st.session_state.se_nat = "Both"
            st.session_state.se_country = "All"
            st.session_state.se_age_grp = "All"
            st.session_state.se_age_min = 18.0
            st.session_state.se_age_max = 42.0
            st.session_state.se_min_pressure = 0.0
            st.session_state.se_min_rr = 0.0
            st.session_state.se_min_balls = 0
            st.session_state.se_dom_runs = 0.0
            st.session_state.se_dom_avg = 0.0
            st.session_state.se_dom_sr = 0.0
            st.session_state.se_dom_wkt = 0.0
            st.session_state.se_dom_econ = 15.0
            st.session_state.se_char = "All"
            st.session_state.se_dev_pref = "All"
            st.session_state.se_limit = 10
            st.session_state.se_search = ""
            st.session_state.se_pool_scope = "Full Eligible Pool (303 Players)"
            st.rerun()

    # Apply filters dynamically
    filtered_df = apply_scouting_filters(
        full_pool_df,
        pool_scope=pool_scope,
        role=role,
        nationality=nat,
        country=None if country == "All" else country,
        age_group=age_grp,
        age_min=age_min,
        age_max=age_max,
        min_pressure_score=min_pressure,
        min_rr_score=min_rr,
        min_sample_balls=min_balls,
        domestic_min_runs=dom_runs if dom_runs > 0 else None,
        domestic_min_avg=dom_avg if dom_avg > 0 else None,
        domestic_min_sr=dom_sr if dom_sr > 0 else None,
        domestic_min_wickets=dom_wkt if dom_wkt > 0 else None,
        domestic_max_econ=dom_econ if dom_econ < 15.0 else None,
        required_characteristic=None if char_filter == "All" else char_filter,
        dev_preference=dev_pref,
        search_query=search_query,
        limit=limit
    )

    # ── Summary KPI Bar ──────────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Candidates Found", f"{len(filtered_df)}")
    with k2:
        avg_score = filtered_df['verified_rr_scouting_score'].mean() if not filtered_df.empty else 0
        st.metric("Avg RR Scouting Score", f"{avg_score:.2f}")
    with k3:
        avg_press = filtered_df['pressure_or_eq_score'].mean() if not filtered_df.empty else 0
        st.metric("Avg Pressure / EQ", f"{avg_press:.2f}")
    with k4:
        ind_count = (filtered_df['nationality'] == 'Indian').sum() if not filtered_df.empty else 0
        os_count = len(filtered_df) - ind_count
        st.metric("Indian / Overseas", f"{ind_count} IND · {os_count} OS")
    with k5:
        em_pct = ((filtered_df['development_category'] == 'Emerging').sum() / len(filtered_df) * 100) if not filtered_df.empty else 0
        st.metric("Emerging Talent %", f"{em_pct:.1f}%")

    st.markdown("---")

    # ── Results Presentation: Tabs for Table vs Charts ────────────────────────
    if filtered_df.empty:
        st.info("⚠️ No candidates match the current filter criteria. Relax the age, score, or domestic performance thresholds to broaden the search.", icon="ℹ️")
    else:
        tab_table, tab_charts = st.tabs(["📋 Filtered Candidate Table", "📊 Visual Analytics"])

        with tab_table:
            # Display Table with clean column config
            display_cols = [
                'player_id', 'player_name', 'role', 'country', 'nationality',
                'age_as_of_2027_04_01', 'development_category',
                'pressure_or_eq_score', 'verified_rr_scouting_score',
                'current_form_rating', 'evidence_balls', 'is_shortlisted'
            ]
            clean_table = filtered_df[[c for c in display_cols if c in filtered_df.columns]].copy()
            clean_table.insert(0, 'Rank', range(1, len(clean_table) + 1))

            st.dataframe(
                clean_table,
                column_config={
                    "Rank": st.column_config.NumberColumn("Rank", width="small"),
                    "player_id": st.column_config.NumberColumn("ID", format="%d", width="small"),
                    "player_name": st.column_config.TextColumn("Candidate Name", width="medium"),
                    "role": st.column_config.TextColumn("Role", width="small"),
                    "country": st.column_config.TextColumn("Country", width="small"),
                    "nationality": st.column_config.TextColumn("Nat", width="small"),
                    "age_as_of_2027_04_01": st.column_config.NumberColumn("Age (Apr 2027)", format="%.1f yrs", width="small"),
                    "development_category": st.column_config.TextColumn("Development Stage", width="medium"),
                    "pressure_or_eq_score": st.column_config.ProgressColumn("Pressure / EQ", format="%.2f", min_value=0, max_value=100, width="medium"),
                    "verified_rr_scouting_score": st.column_config.ProgressColumn("RR Scouting Score", format="%.2f", min_value=0, max_value=100, width="medium"),
                    "current_form_rating": st.column_config.TextColumn("Form", width="small"),
                    "evidence_balls": st.column_config.NumberColumn("Observed Balls", width="small"),
                    "is_shortlisted": st.column_config.CheckboxColumn("Shortlist Verified", width="small")
                },
                hide_index=True,
                use_container_width=True,
                height=min(400, 45 * len(clean_table) + 40)
            )

            # Download Filtered Results CSV
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                "⬇️ Download Filtered Candidate List (CSV)",
                data=csv_data,
                file_name=f"rr_filtered_candidates_{role.lower()}_{nat.lower()}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with tab_charts:
            chart_t1, chart_t2, chart_t3, chart_t4 = st.tabs([
                "🏆 Rankings", "📈 Pressure vs Scouting", "📅 Age & Runway", "🌐 Demographics"
            ])
            with chart_t1:
                st.plotly_chart(
                    plot_ranking_bar_chart(filtered_df, "Candidate Pool Rankings by RR Scouting Score"),
                    use_container_width=True
                )
            with chart_t2:
                st.plotly_chart(
                    plot_pressure_vs_scouting(filtered_df, "Historical Pressure / EQ vs RR Scouting Score", "pressure_or_eq_score"),
                    use_container_width=True
                )
            with chart_t3:
                st.plotly_chart(
                    plot_age_vs_scouting(filtered_df, "Age vs RR Scouting Score (Development Runway)"),
                    use_container_width=True
                )
            with chart_t4:
                d_col1, d_col2 = st.columns(2)
                with d_col1:
                    st.plotly_chart(plot_nationality_pie(filtered_df, "Filtered Pool Nationality Split"), use_container_width=True)
                with d_col2:
                    st.plotly_chart(plot_career_stage_bar(filtered_df, "Career Stage Distribution"), use_container_width=True)

        # ── Section A.3: Comprehensive Player Detail View ─────────────────────
        st.markdown("### 🔎 Candidate Evidence Deep Dive")
        player_names = filtered_df['player_name'].tolist()
        selected_name = st.selectbox(
            "Select candidate for detailed audit & evidence:",
            ["— Select a candidate —"] + player_names,
            index=0,
            key="se_detail_player_select"
        )

        if selected_name != "— Select a candidate —":
            player_row = filtered_df[filtered_df['player_name'] == selected_name].iloc[0].to_dict()
            _render_player_detail_panel(player_row)

    # =========================================================================
    # SECTION B: ASK AI SCOUTING ASSISTANT (OPTIONAL — COLLAPSED BY DEFAULT)
    # =========================================================================

    st.markdown("---")
    assistant = BackboardScoutingAssistant()

    with st.expander("🤖 Ask AI Scouting Assistant (Optional — Powered by Backboard × Google Gemini)", expanded=False):
        if not assistant.is_configured:
            st.info(
                "ℹ️ **AI scouting is currently unavailable.** All dashboard filters, rankings, comparisons "
                "and visualizations remain fully functional without it.\n\n"
                "To activate optional AI features, configure your `BACKBOARD_API_KEY` in `.streamlit/secrets.toml` or `.env`.",
                icon="💡"
            )
        else:
            model_name = assistant.model_name
            st.caption(f"🟢 **Backboard AI Active** | Provider: `{assistant.provider}` | Model: `{model_name}` | Key: `{assistant.masked_api_key}`")

            # Check for stale insights
            curr_hash = _compute_filter_hash()
            stored_hash = st.session_state.get("se_ai_filter_hash")

            if stored_hash and stored_hash != curr_hash and st.session_state.get("se_ai_result"):
                st.warning("⚠️ **Note:** The AI recommendations below reflect previous search criteria. Click '⚡ Generate AI Insights' to refresh for current filters.")

            example_queries = [
                "— Select an example or write your own below —",
                "Find young Indian batters under 24 with high pressure scores for top-order development.",
                "Find overseas finishers with strong pressure scores and long-term runway.",
                "Identify emerging fast bowlers with long-term potential for RR bowling academy.",
                "Compare the best three middle-overs spin prospects based on empirical evidence.",
                "Find players whose domestic form is stronger than their historical pressure ranking."
            ]

            selected_ex = st.selectbox("Quick-start prompt ideas:", example_queries, key="se_ai_example")
            user_prompt = st.text_area(
                "Scouting Requirement / Natural Language Prompt:",
                value="" if selected_ex.startswith("—") else selected_ex,
                height=90,
                placeholder="e.g., 'Recommend 3 young overseas batters under 25 with strong high-extreme pressure scores for RR's middle order.'",
                key="se_ai_prompt"
            )

            c_ai1, c_ai2, c_ai3 = st.columns([2, 1, 1])
            with c_ai1:
                gen_btn = st.button("⚡ Generate AI Insights", type="primary", use_container_width=True, disabled=not user_prompt.strip())
            with c_ai2:
                cont_btn = st.button("🔁 Continue Thread", use_container_width=True, disabled=not (user_prompt.strip() and st.session_state.get("se_ai_thread_id")))
            with c_ai3:
                clear_btn = st.button("🗑️ New Session", use_container_width=True)

            if clear_btn:
                st.session_state.se_ai_result = None
                st.session_state.se_ai_thread_id = None
                st.session_state.se_ai_filter_hash = None
                st.rerun()

            if (gen_btn or cont_btn) and user_prompt.strip():
                thread_to_use = st.session_state.se_ai_thread_id if cont_btn else None

                # Send ONLY the filtered dataset to Backboard AI (preserving eligibility & evidence)
                with st.spinner("🤖 Consulting Backboard AI with Google Gemini..."):
                    ai_res = assistant.query_scouting_assistant(
                        user_query=user_prompt.strip(),
                        candidates_df=filtered_df,
                        thread_id=thread_to_use
                    )

                st.session_state.se_ai_result = ai_res
                st.session_state.se_ai_filter_hash = curr_hash
                if ai_res.get("thread_id"):
                    st.session_state.se_ai_thread_id = ai_res["thread_id"]
                st.rerun()

            # Render AI Response if available
            ai_res = st.session_state.get("se_ai_result")
            if ai_res:
                st.markdown("---")
                src = ai_res.get("source", "unknown")
                if src == "backboard_google_gemini":
                    st.success(f"✅ AI Insights from **Backboard × Google Gemini** | Model: `{ai_res.get('model','')}` | Thread: `{str(ai_res.get('thread_id',''))[:12]}...`")
                else:
                    st.info(f"🔄 **Deterministic Recommendation Engine** — {ai_res.get('fallback_notice','')}")

                st.markdown("#### 📋 Strategic Assessment")
                st.markdown(
                    f"<div style='background:#0F1C38;border-left:3px solid #EA1B86;padding:12px 16px;border-radius:0 6px 6px 0;font-size:0.88rem;color:#E2E8F0;'>"
                    f"{ai_res.get('analysis_summary','')}</div>",
                    unsafe_allow_html=True
                )

                recs = ai_res.get("recommended_players", [])
                if recs:
                    st.markdown(f"#### 👥 Recommended Candidates ({len(recs)})")
                    for i, r in enumerate(recs, 1):
                        _render_ai_player_card(r, i)

                bal = ai_res.get("squad_balance_note")
                if bal:
                    st.info(f"⚖️ **Squad Balance Assessment:** {bal}")
