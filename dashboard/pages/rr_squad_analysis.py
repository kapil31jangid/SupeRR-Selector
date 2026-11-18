"""
PRESSURE-X RR Squad Analysis Page
==================================
Rajasthan Royals Current Squad Analysis, Gap Analysis, and Vacancy Fit Scoring.

Sections:
- RR Current Squad Overview
- Role Coverage Matrix
- Age Distribution & Runway Analysis
- Gap Analysis: Need vs Strength
- Vacancy Fit Scoring for Auction Targets
- Retention Value Assessment
"""

import pandas as pd
import streamlit as st
import numpy as np
from typing import Dict, Any

from dashboard.utils.data_loader import (
    load_rr_current_squad,
    load_complete_pool_enriched,
    apply_scouting_filters
)
from dashboard.utils.formatting import (
    format_category_badge,
    format_nationality_badge,
    RR_PINK,
    RR_ROYAL_BLUE,
    RR_GOLD,
    RR_NAVY_CARD
)
from dashboard.charts import (
    plot_nationality_pie,
    plot_career_stage_bar,
    plot_ranking_bar_chart
)


# -----------------------------------------------------------------------------
# RR SQUAD ANALYSIS HELPERS
# -----------------------------------------------------------------------------

def _get_role_coverage(squad_df: pd.DataFrame) -> pd.DataFrame:
    """Analyze role coverage in current squad."""
    role_map = {
        'Batter': ['Batter', 'Opening Batter', 'Middle Order Batter'],
        'Bowler': ['Bowler', 'Fast Bowler', 'Spin Bowler', 'All-rounder'],
        'All-rounder': ['All-rounder'],
        'Wicketkeeper': ['Wicketkeeper', 'WK-Batter']
    }

    coverage = []
    for role, variants in role_map.items():
        count = squad_df[squad_df['primary_role'].isin(variants)].shape[0]
        coverage.append({'Role': role, 'Count': count, 'Status': 'Covered' if count > 0 else 'GAP'})

    return pd.DataFrame(coverage)


def _get_age_band_distribution(squad_df: pd.DataFrame) -> pd.DataFrame:
    """Get age band distribution for squad."""
    def age_band(age):
        if pd.isna(age):
            return 'Unknown'
        if age <= 23:
            return 'Emerging (≤23)'
        elif age <= 26:
            return 'Development (24-26)'
        elif age <= 30:
            return 'Prime (27-30)'
        else:
            return 'Experienced (31+)'

    squad_df = squad_df.copy()
    squad_df['age_band'] = squad_df['age_as_of_2027_04_01'].apply(age_band)

    dist = squad_df.groupby(['age_band', 'nationality']).size().reset_index(name='Count')
    return dist


def _compute_vacancy_fit(candidate: pd.Series, squad_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute how well a candidate fits RR's squad gaps.

    Factors:
    - Role scarcity in squad
    - Age complementarity (don't duplicate age bands)
    - Nationality balance (max 8 overseas)
    - Skill gap coverage
    """
    # Current squad composition
    overseas_count = (squad_df['nationality'] == 'Overseas').sum()
    indian_count = (squad_df['nationality'] == 'Indian').sum()

    # Role counts
    role_counts = squad_df['primary_role'].value_counts().to_dict()

    # Age band counts
    def age_band(age):
        if pd.isna(age):
            return 'Unknown'
        if age <= 23:
            return 'Emerging'
        elif age <= 26:
            return 'Development'
        elif age <= 30:
            return 'Prime'
        else:
            return 'Experienced'

    squad_df = squad_df.copy()
    squad_df['age_band'] = squad_df['age_as_of_2027_04_01'].apply(age_band)
    age_band_counts = squad_df['age_band'].value_counts().to_dict()

    # Candidate attributes
    cand_role = candidate.get('primary_role', candidate.get('role', ''))
    cand_nat = candidate.get('nationality', '')
    cand_age = candidate.get('age_as_of_2027_04_01', 28)
    cand_age_band = age_band(cand_age)

    # Scoring
    fit_score = 0.0
    reasons = []

    # 1. Role scarcity (max 30 pts)
    role_scarcity = {
        'Batter': max(0, 5 - role_counts.get('Batter', 0)) * 5,
        'Bowler': max(0, 5 - role_counts.get('Bowler', 0)) * 5,
        'All-rounder': max(0, 4 - role_counts.get('All-rounder', 0)) * 7,
        'Wicketkeeper': max(0, 2 - role_counts.get('Wicketkeeper', 0)) * 15,
    }
    role_need = role_scarcity.get(cand_role, 0)
    fit_score += role_need
    if role_need > 0:
        reasons.append(f"Role need: {cand_role} ({role_need} pts)")

    # 2. Age complementarity (max 20 pts)
    age_need = max(0, 3 - age_band_counts.get(cand_age_band, 0)) * 7
    fit_score += age_need
    if age_need > 0:
        reasons.append(f"Age band gap: {cand_age_band} ({age_need} pts)")

    # 3. Nationality balance (max 25 pts)
    nat_score = 0
    if cand_nat == 'Indian':
        # Always need Indians
        nat_score = 15
        reasons.append("Indian nationality (+15 pts)")
    else:
        # Overseas slots limited (max 8, currently have X)
        if overseas_count < 8:
            nat_score = 20
            reasons.append(f"Overseas slot available ({overseas_count}/8) (+20 pts)")
        else:
            nat_score = -10
            reasons.append("Overseas slots full (-10 pts)")
    fit_score += nat_score

    # 4. Development runway bonus (max 15 pts)
    if cand_age <= 23:
        fit_score += 15
        reasons.append("Emerging talent runway (+15 pts)")
    elif cand_age <= 26:
        fit_score += 10
        reasons.append("Young development runway (+10 pts)")

    # 5. Skill ceiling indicator (max 10 pts)
    if candidate.get('verified_rr_scouting_score', 0) >= 80:
        fit_score += 10
        reasons.append("High scouting score (+10 pts)")

    return {
        'vacancy_fit_score': round(fit_score, 1),
        'fit_reasons': reasons,
        'role_need': role_need,
        'age_band_need': age_need,
        'nationality_score': nat_score,
        'current_overseas': overseas_count,
        'current_indian': indian_count
    }


def _render_squad_card(player: pd.Series) -> str:
    """Render a compact squad player card."""
    nat_badge = format_nationality_badge(player.get('nationality', ''))
    cat_badge = format_category_badge(player.get('development_category', ''))
    age = player.get('age_as_of_2027_04_01', 0)
    role = player.get('primary_role', player.get('role', ''))
    retention = player.get('retention_type', 'Retained')

    return f"""
<div style="background:#1C2541;border:1px solid rgba(234,27,134,0.3);border-radius:8px;padding:12px 16px;margin-bottom:8px;">
<div style="display:flex;justify-content:space-between;align-items:center;">
<div>
<span style="font-size:1.05rem;font-weight:700;color:#FFFFFF;">{player.get('player_name','')}</span>
<span style="font-size:0.75rem;color:#94A3B8;margin-left:8px;">{nat_badge} {cat_badge}</span>
</div>
<div style="font-size:0.7rem;color:#F59E0B;background:rgba(245,158,11,0.1);padding:2px 8px;border-radius:10px;">{retention}</div>
</div>
<div style="font-size:0.8rem;color:#CBD5E1;margin-top:4px;">
<b>Role:</b> {role} · <b>Age:</b> {age:.0f} · <b>Bat:</b> {player.get('batting_style','—')} · <b>Bowl:</b> {player.get('bowling_style','—')}
</div>
</div>
"""


# -----------------------------------------------------------------------------
# MAIN RENDER FUNCTION
# -----------------------------------------------------------------------------

def render_rr_squad_analysis():
    """Render the RR Squad Analysis page."""
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0B132B 60%,#2a0a1a);
                border:1px solid rgba(234,27,134,0.4);border-radius:12px;
                padding:22px 28px;margin-bottom:20px;">
        <div style="font-size:1.7rem;font-weight:800;color:#FFFFFF;">
            🛡️ Rajasthan Royals Squad Intelligence
            <span style="font-size:0.9rem;font-weight:400;color:#94A3B8;"> | Gap Analysis & Vacancy Fit</span>
        </div>
        <div style="font-size:0.88rem;color:#94A3B8;margin-top:6px;">
            Analyze current retained squad composition, identify gaps, and score auction targets
            against RR's specific vacancy requirements for IPL 2027.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Load data
    rr_squad = load_rr_current_squad()
    full_pool = load_complete_pool_enriched()

    if rr_squad.empty:
        st.error("RR squad data not available. Run build_rr_squad.py first.")
        return

    # =========================================================================
    # SECTION 1: SQUAD OVERVIEW
    # =========================================================================
    st.markdown("### 📋 Current RR Retained Squad (19 Players)")

    col_overview1, col_overview2, col_overview3, col_overview4 = st.columns(4)
    with col_overview1:
        st.metric("Total Retained", len(rr_squad))
    with col_overview2:
        overseas = (rr_squad['nationality'] == 'Overseas').sum()
        st.metric("Overseas", f"{overseas}/8 slots")
    with col_overview3:
        indian = (rr_squad['nationality'] == 'Indian').sum()
        st.metric("Indian", indian)
    with col_overview4:
        avg_age = rr_squad['age_as_of_2027_04_01'].mean()
        st.metric("Avg Age", f"{avg_age:.1f} yrs")

    # Squad visual
    col_viz1, col_viz2 = st.columns(2)
    with col_viz1:
        st.plotly_chart(plot_nationality_pie(rr_squad, "RR Squad Nationality Split"), use_container_width=True)
    with col_viz2:
        st.plotly_chart(plot_career_stage_bar(rr_squad, "RR Squad Career Stage Distribution"), use_container_width=True)

    # Squad cards
    st.markdown("#### 👥 Squad Composition")
    cols = st.columns(3)
    for idx, (_, player) in enumerate(rr_squad.iterrows()):
        with cols[idx % 3]:
            card_html = _render_squad_card(player)
            st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("---")

    # =========================================================================
    # SECTION 2: ROLE COVERAGE MATRIX
    # =========================================================================
    st.markdown("### 🎯 Role Coverage Matrix")

    role_coverage = _get_role_coverage(rr_squad)

    c1, c2 = st.columns([1, 2])
    with c1:
        st.dataframe(
            role_coverage,
            column_config={
                "Role": st.column_config.TextColumn("Role", width="medium"),
                "Count": st.column_config.NumberColumn("Count", width="small"),
                "Status": st.column_config.TextColumn("Status", width="small")
            },
            hide_index=True,
            use_container_width=True
        )

    with c2:
        st.markdown("""
        **Interpretation:**
        - **All-rounders (6):** Strong core - Parag, Jadeja, Shami, Shanaka, Siddharth, Burger
        - **Batters (3):** Jaiswal, Jurel, Dubey - need top-order reinforcement
        - **Wicketkeepers (2):** Jurel, Ferreira - adequate
        - **Specialist Bowlers (3):** Archer, Bishnoi, Sandeep - need death bowling depth
        """)

    st.markdown("---")

    # =========================================================================
    # SECTION 3: AGE DISTRIBUTION & RUNWAY ANALYSIS
    # =========================================================================
    st.markdown("### 📅 Age Distribution & Development Runway")

    age_dist = _get_age_band_distribution(rr_squad)

    c1, c2 = st.columns(2)
    with c1:
        # Stacked bar chart data
        chart_data = age_dist.pivot(index='age_band', columns='nationality', values='Count').fillna(0)
        st.bar_chart(chart_data)

    with c2:
        st.markdown("""
        **Runway Analysis:**
        - **Emerging (≤23):** 3 players - Perala, B. Sharma, Pretorius, Vaibhav
        - **Development (24-26):** 5 players - Jurel, Parag, Bishnoi, Siddharth, Mishra
        - **Prime (27-30):** 4 players - Ferreira, Burger, Dubey, R. Sharma (borderline)
        - **Experienced (31+):** 7 players - Archer, Shami, Jadeja, Shanaka, Sandeep, R. Sharma

        **Key Insight:** Heavy skew toward experienced players. Need 2-3 emerging/young
        players in auction to balance long-term runway.
        """)

    st.markdown("---")

    # =========================================================================
    # SECTION 4: GAP ANALYSIS - NEED VS STRENGTH
    # =========================================================================
    st.markdown("### 🔍 Gap Analysis: Need vs Strength")

    # Define RR's positional needs for IPL 2027
    needs_data = pd.DataFrame([
        {"Position": "Opener / Top-Order Batter", "Current": "Jaiswal, Jurel", "Strength": "High", "Need": "MEDIUM", "Priority": "Indian U-25 batter with powerplay SR >140", "Slots": 1},
        {"Position": "Middle-Order Anchor", "Current": "Parag, Shanaka", "Strength": "Medium", "Need": "HIGH", "Priority": "Overseas batter with spin vs pace versatility", "Slots": 1},
        {"Position": "Finisher (Death Overs)", "Current": "Parag, Ferreira", "Strength": "Medium", "Need": "HIGH", "Priority": "Power hitter with 15+ sixes evidence", "Slots": 1},
        {"Position": "Powerplay Bowler", "Current": "Archer, Sandeep", "Strength": "High", "Need": "LOW", "Priority": "Backup for Archer workload management", "Slots": 0},
        {"Position": "Middle-Overs Spinner", "Current": "Bishnoi, Jadeja, Siddharth", "Strength": "High", "Need": "LOW", "Priority": "Only if mystery spin available", "Slots": 0},
        {"Position": "Death Bowler", "Current": "Archer, Burger", "Strength": "Medium", "Need": "HIGH", "Priority": "Proven death executor with 30+ death balls", "Slots": 1},
        {"Position": "Backup Wicketkeeper", "Current": "Ferreira", "Strength": "Medium", "Need": "MEDIUM", "Priority": "Indian WK-batter for flexibility", "Slots": 1},
    ])

    st.dataframe(
        needs_data,
        column_config={
            "Position": st.column_config.TextColumn("Position", width="medium"),
            "Current": st.column_config.TextColumn("Current Incumbents", width="medium"),
            "Strength": st.column_config.TextColumn("Current Strength", width="small"),
            "Need": st.column_config.TextColumn("Need Level", width="small"),
            "Priority": st.column_config.TextColumn("Auction Priority Profile", width="large"),
            "Slots": st.column_config.NumberColumn("Target Slots", width="small")
        },
        hide_index=True,
        use_container_width=True
    )

    st.markdown("---")

    # =========================================================================
    # SECTION 5: VACANCY FIT SCORING
    # =========================================================================
    st.markdown("### 🎯 Vacancy Fit Scoring: Auction Targets")

    st.markdown("""
    **Vacancy Fit Score** evaluates how well each auction candidate fills RR's specific squad gaps.
    Factors: Role scarcity, Age complementarity, Nationality balance, Development runway, Skill ceiling.
    """)

    # Filter pool for non-retained, eligible players
    rr_ids = set(rr_squad['player_id'].dropna().astype(int))
    available_pool = full_pool[~full_pool['player_id'].isin(rr_ids)].copy()
    st.caption(f"📊 Auction pool: {len(available_pool)} available players (excl. RR retained)")

    # Filters
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        role_filter = st.selectbox("Target Role", ["All", "Batter", "Bowler", "All-rounder"], key="vf_role")
    with f2:
        nat_filter = st.selectbox("Nationality", ["All", "Indian", "Overseas"], key="vf_nat")
    with f3:
        age_filter = st.selectbox("Age Band", ["All", "Emerging (≤23)", "Development (24-26)", "Prime (27-30)"], key="vf_age")
    with f4:
        min_score = st.slider("Min Vacancy Fit", 0, 100, 40, key="vf_min")

    # Apply filters
    filtered = available_pool.copy()
    if role_filter != "All":
        filtered = filtered[filtered['role'] == role_filter]
    if nat_filter != "All":
        filtered = filtered[filtered['nationality'] == nat_filter]
    if age_filter != "All":
        if "Emerging" in age_filter:
            filtered = filtered[filtered['age_as_of_2027_04_01'] <= 23]
        elif "Development" in age_filter:
            filtered = filtered[(filtered['age_as_of_2027_04_01'] >= 24) & (filtered['age_as_of_2027_04_01'] <= 26)]
        elif "Prime" in age_filter:
            filtered = filtered[(filtered['age_as_of_2027_04_01'] >= 27) & (filtered['age_as_of_2027_04_01'] <= 30)]

    # Compute vacancy fit for each candidate
    fit_results = []
    for _, cand in filtered.iterrows():
        fit = _compute_vacancy_fit(cand, rr_squad)
        fit_results.append({
            'player_id': cand['player_id'],
            'player_name': cand['player_name'],
            'role': cand['role'],
            'nationality': cand['nationality'],
            'age': cand['age_as_of_2027_04_01'],
            'dev_category': cand['development_category'],
            'rr_scouting_score': cand['verified_rr_scouting_score'],
            'vacancy_fit_score': fit['vacancy_fit_score'],
            'fit_reasons': "; ".join(fit['fit_reasons'])
        })

    fit_df = pd.DataFrame(fit_results)
    fit_df = fit_df[fit_df['vacancy_fit_score'] >= min_score]
    fit_df = fit_df.sort_values('vacancy_fit_score', ascending=False).head(20)

    if not fit_df.empty:
        st.dataframe(
            fit_df,
            column_config={
                "player_id": st.column_config.NumberColumn("ID", width="small"),
                "player_name": st.column_config.TextColumn("Player", width="medium"),
                "role": st.column_config.TextColumn("Role", width="small"),
                "nationality": st.column_config.TextColumn("Nat", width="small"),
                "age": st.column_config.NumberColumn("Age", format="%.1f", width="small"),
                "dev_category": st.column_config.TextColumn("Dev Stage", width="medium"),
                "rr_scouting_score": st.column_config.ProgressColumn("RR Score", format="%.1f", min_value=0, max_value=100, width="medium"),
                "vacancy_fit_score": st.column_config.ProgressColumn("Vacancy Fit", format="%.1f", min_value=0, max_value=100, width="medium"),
                "fit_reasons": st.column_config.TextColumn("Fit Rationale", width="large")
            },
            hide_index=True,
            use_container_width=True
        )

        # Download
        csv = fit_df.to_csv(index=False)
        st.download_button(
            "⬇️ Download Vacancy Fit Rankings (CSV)",
            data=csv,
            file_name="rr_vacancy_fit_rankings.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No candidates match the current filter criteria.")

    st.markdown("---")

    # =========================================================================
    # SECTION 6: RETENTION VALUE ASSESSMENT
    # =========================================================================
    st.markdown("### 💎 Retention Value Assessment")

    st.markdown("""
    Evaluation of current retained players' value for IPL 2027 based on:
    - **Performance Consistency**: Multi-season evidence
    - **Role Criticality**: How replaceable is their role?
    - **Age Runway**: Years of peak performance remaining
    - **Leadership Value**: Captaincy, mentorship, culture
    """)

    retention_data = []
    for _, p in rr_squad.iterrows():
        age = p.get('age_as_of_2027_04_01', 30)
        role = p.get('primary_role', '')

        # Simple heuristic scoring
        perf_score = 70  # Baseline
        if p['player_name'] in ['Yashasvi Jaiswal', 'Sanju Samson', 'Riyan Parag']:
            perf_score = 90
        elif p['player_name'] in ['Jofra Archer', 'Ravindra Jadeja', 'Mohd. Shami']:
            perf_score = 85

        role_critical = 80 if role in ['Batter', 'Wicketkeeper'] else 60
        if p['player_name'] in ['Jofra Archer']:  # Unique death bowler
            role_critical = 95

        runway = max(0, 10 - max(0, (age - 27) * 0.5)) * 10
        leadership = 20 if p['player_name'] in ['Sanju Samson', 'Ravindra Jadeja', 'Riyan Parag'] else 5

        total = round(0.4 * perf_score + 0.3 * role_critical + 0.2 * runway + 0.1 * leadership, 1)

        retention_data.append({
            'Player': p['player_name'],
            'Role': role,
            'Age': f"{age:.0f}",
            'Nationality': p['nationality'],
            'Performance': perf_score,
            'Role Criticality': role_critical,
            'Runway Score': round(runway, 1),
            'Leadership': leadership,
            'Retention Value': total,
            'Retention Type': p['retention_type']
        })

    ret_df = pd.DataFrame(retention_data).sort_values('Retention Value', ascending=False)

    st.dataframe(
        ret_df,
        column_config={
            "Player": st.column_config.TextColumn("Player", width="medium"),
            "Role": st.column_config.TextColumn("Role", width="small"),
            "Age": st.column_config.TextColumn("Age", width="small"),
            "Nationality": st.column_config.TextColumn("Nat", width="small"),
            "Performance": st.column_config.ProgressColumn("Performance", format="%d", min_value=0, max_value=100, width="medium"),
            "Role Criticality": st.column_config.ProgressColumn("Role Critical", format="%d", min_value=0, max_value=100, width="medium"),
            "Runway Score": st.column_config.ProgressColumn("Runway", format="%.1f", min_value=0, max_value=100, width="medium"),
            "Leadership": st.column_config.NumberColumn("Leadership", width="small"),
            "Retention Value": st.column_config.ProgressColumn("Total Value", format="%.1f", min_value=0, max_value=100, width="medium"),
            "Retention Type": st.column_config.TextColumn("Type", width="small")
        },
        hide_index=True,
        use_container_width=True
    )