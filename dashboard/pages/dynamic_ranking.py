"""
PRESSURE-X Dynamic Ranking Engine Page
=======================================
Interactive weight configuration for the 40/30/20/10 RR Scouting Model.

Features:
- Custom weight sliders with real-time recalculation
- Predefined weight profiles (RR Default, Pressure First, Youth Focus, etc.)
- Missing data policy selection
- Sensitivity analysis
- Rank stability visualization
- Export custom rankings
"""

import pandas as pd
import streamlit as st
import numpy as np
import json
from datetime import datetime

from dashboard.utils.data_loader import load_complete_pool_enriched, apply_scouting_filters
from dashboard.utils.formatting import RR_PINK, RR_ROYAL_BLUE, RR_GOLD
from dashboard.charts import plot_ranking_bar_chart, plot_age_vs_scouting
from src.scoring.dynamic_scouting_engine import (
    DynamicScoutingEngine,
    EngineConfig,
    ScoutingWeights,
    WeightProfile,
    MissingDataPolicy,
    create_default_engine,
    create_engine_from_profile
)


# -----------------------------------------------------------------------------
# WEIGHT PROFILE DEFINITIONS
# -----------------------------------------------------------------------------

WEIGHT_PROFILES = {
    "RR Default (40/30/20/10)": {
        "description": "Balanced long-term model prioritizing pressure execution with development runway",
        "weights": {"dimA_pressure": 40, "dimB_age_dev": 30, "dimC_skill_ceiling": 20, "dimD_current_form": 10},
        "use_case": "Standard RR auction strategy"
    },
    "Pressure First (60/15/15/10)": {
        "description": "Win-now approach maximizing high-pressure performance evidence",
        "weights": {"dimA_pressure": 60, "dimB_age_dev": 15, "dimC_skill_ceiling": 15, "dimD_current_form": 10},
        "use_case": "Immediate impact players for playoff push"
    },
    "Youth Focus (25/50/15/10)": {
        "description": "Long-term development prioritizing age runway and upside",
        "weights": {"dimA_pressure": 25, "dimB_age_dev": 50, "dimC_skill_ceiling": 15, "dimD_current_form": 10},
        "use_case": "Building 3-5 year championship window"
    },
    "Ceiling Chaser (30/20/40/10)": {
        "description": "High-upside skills hunting: bat speed, mystery spin, 3D versatility",
        "weights": {"dimA_pressure": 30, "dimB_age_dev": 20, "dimC_skill_ceiling": 40, "dimD_current_form": 10},
        "use_case": "Identifying breakout candidates"
    },
    "Form Watcher (35/20/15/30)": {
        "description": "Current form emphasis for players peaking at right time",
        "weights": {"dimA_pressure": 35, "dimB_age_dev": 20, "dimC_skill_ceiling": 15, "dimD_current_form": 30},
        "use_case": "Late auction value picks"
    },
    "Balanced Evidence (30/30/20/20)": {
        "description": "Equal weight to pressure, age, with boosted form reliability",
        "weights": {"dimA_pressure": 30, "dimB_age_dev": 30, "dimC_skill_ceiling": 20, "dimD_current_form": 20},
        "use_case": "Risk-averse portfolio approach"
    },
}


# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------

def _render_weight_sliders(current_weights: ScoutingWeights, disabled: bool = False) -> ScoutingWeights:
    """Render interactive weight sliders."""
    st.markdown("#### ⚖️ Dimension Weights (must sum to 100)")

    # Use columns for layout
    c1, c2 = st.columns(2)

    with c1:
        w_a = st.slider(
            "Dim A: Pressure Execution",
            0, 100, int(current_weights.dimA_pressure), 5,
            key="w_pressure", disabled=disabled,
            help="Bayesian pressure performance in High-Extreme, Death, Chase, Powerplay"
        )
        w_b = st.slider(
            "Dim B: Age & Development Runway",
            0, 100, int(current_weights.dimB_age_dev), 5,
            key="w_age_dev", disabled=disabled,
            help="Development runway as of 1 Apr 2027: Emerging≤23:100, YoungDev24-26:85, Prime27-30:65, Exp31+:50"
        )

    with c2:
        w_c = st.slider(
            "Dim C: Skill Ceiling",
            0, 100, int(current_weights.dimC_skill_ceiling), 5,
            key="w_skill_ceiling", disabled=disabled,
            help="Physical attributes, bat speed, mystery spin, 3D versatility & tactical squad fit"
        )
        w_d = st.slider(
            "Dim D: Current Form",
            0, 100, int(current_weights.dimD_current_form), 5,
            key="w_current_form", disabled=disabled,
            help="Audited recent 12-month match logs across international and domestic leagues"
        )

    total = w_a + w_b + w_c + w_d

    # Show total
    if total == 100:
        st.success(f"✅ Weights sum to 100%")
    else:
        st.error(f"❌ Weights sum to {total}% — must equal 100%")

    # Auto-normalize option
    if total != 100:
        if st.button("🔧 Auto-Normalize to 100%", key="normalize_weights"):
            factor = 100 / total
            w_a = round(w_a * factor)
            w_b = round(w_b * factor)
            w_c = round(w_c * factor)
            w_d = 100 - w_a - w_b - w_c  # Ensure exact 100
            st.rerun()

    return ScoutingWeights(
        dimA_pressure=float(w_a),
        dimB_age_dev=float(w_b),
        dimC_skill_ceiling=float(w_c),
        dimD_current_form=float(w_d)
    )


def _render_missing_data_policy() -> MissingDataPolicy:
    """Render missing data policy selector."""
    st.markdown("#### 🔧 Missing Data Policy")

    policy = st.selectbox(
        "How to handle missing dimension scores:",
        [
            MissingDataPolicy.POPULATION_MEAN.value,
            MissingDataPolicy.POPULATION_MEDIAN.value,
            MissingDataPolicy.NEUTRAL.value,
            MissingDataPolicy.ZERO.value,
            MissingDataPolicy.DIMENSION_WEIGHT_REDISTRIBUTE.value,
        ],
        index=0,
        key="missing_policy",
        help="""
        - Population Mean: Impute from pool average (recommended)
        - Population Median: Impute from pool median (robust to outliers)
        - Neutral: Treat missing as 50 (neutral)
        - Zero: Treat missing as 0 (harsh penalty)
        - Redistribute: Redistribute weight to observed dimensions only
        """
    )

    return MissingDataPolicy(policy)


def _render_engine_config() -> EngineConfig:
    """Render full engine configuration panel."""
    with st.expander("⚙️ Advanced Engine Settings", expanded=False):
        missing_policy = _render_missing_data_policy()

        c1, c2, c3 = st.columns(3)
        with c1:
            min_sample = st.number_input(
                "Min Sample Threshold (balls)",
                0, 500, 30, 10,
                key="min_sample",
                help="Below this, evidence confidence penalty applies"
            )
        with c2:
            enable_gating = st.checkbox(
                "Enable Evidence Gating",
                value=True,
                key="enable_gating",
                help="Apply confidence penalty for low sample sizes"
            )
        with c3:
            penalty = st.slider(
                "Confidence Penalty",
                0.0, 0.5, 0.1, 0.05,
                key="penalty",
                help="Max penalty multiplier for low evidence"
            )

        domestic_bonus = st.number_input(
            "Domestic Evidence Bonus",
            0.0, 10.0, 0.0, 0.5,
            key="dom_bonus",
            help="Bonus points for players with verified domestic T20 evidence"
        )

    return EngineConfig(
        weights=ScoutingWeights(),  # Will be updated
        missing_data_policy=missing_policy,
        min_sample_threshold=min_sample,
        enable_evidence_gating=enable_gating,
        confidence_penalty=penalty,
        domestic_bonus=domestic_bonus
    )


def _render_sensitivity_chart(engine: DynamicScoutingEngine, pool_df: pd.DataFrame):
    """Render sensitivity analysis visualization."""
    with st.spinner("Running sensitivity analysis..."):
        sens_df = engine.sensitivity_analysis(pool_df, weight_range=15.0, steps=7)

    if sens_df.empty:
        st.info("Sensitivity analysis requires computed scores.")
        return

    st.markdown("#### 📊 Sensitivity Analysis: Rank Stability")

    # Summary metrics
    c1, c2, c3 = st.columns(3)
    with c1:
        avg_shift = sens_df['avg_rank_shift'].mean()
        st.metric("Avg Rank Shift", f"{avg_shift:.1f}")
    with c2:
        max_shift = sens_df['max_rank_shift'].max()
        st.metric("Max Rank Shift", f"{max_shift:.0f}")
    with c3:
        top10_stab = sens_df['top10_stability'].mean()
        st.metric("Top-10 Stability", f"{top10_stab:.0%}")

    # Dimension-wise stability
    dim_stability = sens_df.groupby('varied_dimension').agg({
        'avg_rank_shift': 'mean',
        'max_rank_shift': 'max',
        'top10_stability': 'mean'
    }).round(2)

    st.dataframe(
        dim_stability,
        column_config={
            "varied_dimension": st.column_config.TextColumn("Dimension"),
            "avg_rank_shift": st.column_config.NumberColumn("Avg Rank Shift"),
            "max_rank_shift": st.column_config.NumberColumn("Max Rank Shift"),
            "top10_stability": st.column_config.ProgressColumn("Top-10 Stability", format="%.0%", min_value=0, max_value=1)
        },
        use_container_width=True
    )

    # Interpretation
    st.markdown("""
    **Interpretation:**
    - **Low Avg Rank Shift (<2)**: Rankings are robust to weight changes
    - **High Top-10 Stability (>80%)**: Top candidates remain stable
    - **High Max Shift**: Some players are highly sensitive to specific dimensions
    """)


# -----------------------------------------------------------------------------
# MAIN RENDER FUNCTION
# -----------------------------------------------------------------------------

def render_dynamic_ranking():
    """Render the Dynamic Ranking Engine page."""
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0B132B 60%,#2a0a1a);
                border:1px solid rgba(234,27,134,0.4);border-radius:12px;
                padding:22px 28px;margin-bottom:20px;">
        <div style="font-size:1.7rem;font-weight:800;color:#FFFFFF;">
            📐 Dynamic Ranking Engine
            <span style="font-size:0.9rem;font-weight:400;color:#94A3B8;"> | Customizable 40/30/20/10 Model</span>
        </div>
        <div style="font-size:0.88rem;color:#94A3B8;margin-top:6px;">
            Configure custom weight profiles, missing data policies, and evidence gating.
            Real-time recalculation across all 664 eligible players.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Load full pool
    full_pool = load_complete_pool_enriched()

    if full_pool.empty:
        st.error("Candidate pool not loaded.")
        return

    # =========================================================================
    # SIDEBAR: PROFILE SELECTOR & FILTERS
    # =========================================================================
    with st.sidebar:
        st.markdown("### 🎯 Ranking Configuration")

        # Profile selector
        profile_names = list(WEIGHT_PROFILES.keys()) + ["Custom Weights"]
        selected_profile = st.selectbox(
            "Weight Profile",
            profile_names,
            index=0,
            key="rank_profile"
        )

        # Get base weights
        if selected_profile == "Custom Weights":
            use_custom = True
            base_weights = ScoutingWeights(40, 30, 20, 10)
        else:
            use_custom = False
            profile_info = WEIGHT_PROFILES[selected_profile]
            base_weights = ScoutingWeights.from_dict(profile_info["weights"])
            st.caption(f"📝 {profile_info['description']}")
            st.caption(f"💡 Use case: {profile_info['use_case']}")

        # Show current weights
        st.markdown("**Current Weights:**")
        st.markdown(f"""
        - **Pressure (A):** {base_weights.dimA_pressure:.0f}%
        - **Age/Runway (B):** {base_weights.dimB_age_dev:.0f}%
        - **Skill Ceiling (C):** {base_weights.dimC_skill_ceiling:.0f}%
        - **Current Form (D):** {base_weights.dimD_current_form:.0f}%
        """)

        st.markdown("---")

        # Candidate pool filters
        st.markdown("### 🔍 Candidate Pool Filters")
        pool_scope = st.selectbox(
            "Data Scope",
            ["View A: Complete Pool (311)", "View B: Official Shortlist (28)", "View C: RR Squad (19)"],
            index=0,
            key="rank_pool_scope"
        )

        role_filter = st.selectbox("Role", ["Any", "Batter", "Bowler", "All-rounder"], key="rank_role")
        nat_filter = st.selectbox("Nationality", ["Both", "Indian", "Overseas"], key="rank_nat")
        age_max = st.slider("Max Age", 18, 45, 40, key="rank_age_max")
        min_rr = st.slider("Min RR Score", 0.0, 100.0, 0.0, 5.0, key="rank_min_rr")
        limit = st.selectbox("Results Limit", [10, 20, 50, 100, "All"], index=1, key="rank_limit")

    # Apply filters
    view_filter_map = {
        "View A: Complete Pool (311)": "View A: Complete Pool",
        "View B: Official Shortlist (28)": "View B: Official Shortlist",
        "View C: RR Squad (19)": "View C: RR Squad"
    }

    filtered_pool = apply_scouting_filters(
        full_pool,
        view_filter=view_filter_map[pool_scope],
        role=role_filter,
        nationality=nat_filter,
        age_max=float(age_max),
        min_rr_score=min_rr,
        limit=None if limit == "All" else limit
    )

    st.info(f"📊 **Active Pool:** {len(filtered_pool)} candidates | **Profile:** {selected_profile}")

    # =========================================================================
    # MAIN: WEIGHT CONFIGURATION
    # =========================================================================
    col_config, col_results = st.columns([1, 2])

    with col_config:
        if use_custom:
            weights = _render_weight_sliders(base_weights)
        else:
            # Show profile weights (read-only for predefined)
            weights = base_weights
            _render_weight_sliders(weights, disabled=True)

        st.markdown("---")
        config = _render_engine_config()
        config.weights = weights

    # =========================================================================
    # COMPUTE & DISPLAY RANKINGS
    # =========================================================================
    with col_results:
        # Create and fit engine
        engine = DynamicScoutingEngine(config)
        engine.fit(filtered_pool)
        ranked_df = engine.rank_candidates(filtered_pool)

        # KPI Row
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Candidates Ranked", len(ranked_df))
        with k2:
            top_score = ranked_df['dynamic_scouting_score'].max()
            st.metric("Top Score", f"{top_score:.1f}")
        with k3:
            avg_score = ranked_df['dynamic_scouting_score'].mean()
            st.metric("Avg Score", f"{avg_score:.1f}")
        with k4:
            ind_top = (ranked_df.head(10)['nationality'] == 'Indian').sum()
            st.metric("Indians in Top 10", f"{ind_top}/10")

        # Rankings Table
        st.markdown("### 🏆 Dynamic Rankings")

        display_cols = ['dynamic_rank', 'player_id', 'player_name', 'role', 'nationality',
                        'age_as_of_2027_04_01', 'development_category',
                        'dimA_pressure', 'dimB_runway', 'dimC_ceiling', 'dimD_form',
                        'dynamic_scouting_score', 'evidence_confidence']

        rank_display = ranked_df[[c for c in display_cols if c in ranked_df.columns]].copy()
        rank_display.columns = ['Rank', 'ID', 'Player', 'Role', 'Nat', 'Age', 'Dev Stage',
                                'Pressure (A)', 'Age/Runway (B)', 'Ceiling (C)', 'Form (D)',
                                'Dynamic Score', 'Evidence']

        # Apply limit
        if limit != "All":
            rank_display = rank_display.head(limit)

        st.dataframe(
            rank_display,
            column_config={
                "Rank": st.column_config.NumberColumn("Rank", width="small"),
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Player": st.column_config.TextColumn("Player", width="medium"),
                "Role": st.column_config.TextColumn("Role", width="small"),
                "Nat": st.column_config.TextColumn("Nat", width="small"),
                "Age": st.column_config.NumberColumn("Age", format="%.1f", width="small"),
                "Dev Stage": st.column_config.TextColumn("Dev Stage", width="medium"),
                "Pressure (A)": st.column_config.ProgressColumn("Pressure", format="%.1f", min_value=0, max_value=100, width="medium"),
                "Age/Runway (B)": st.column_config.ProgressColumn("Age/Runway", format="%.1f", min_value=0, max_value=100, width="medium"),
                "Ceiling (C)": st.column_config.ProgressColumn("Ceiling", format="%.1f", min_value=0, max_value=100, width="medium"),
                "Form (D)": st.column_config.ProgressColumn("Form", format="%.1f", min_value=0, max_value=100, width="medium"),
                "Dynamic Score": st.column_config.ProgressColumn("Score", format="%.2f", min_value=0, max_value=100, width="medium"),
                "Evidence": st.column_config.TextColumn("Evidence", width="medium")
            },
            hide_index=True,
            use_container_width=True,
            height=min(500, 40 * len(rank_display) + 40)
        )

        # Download
        csv = ranked_df.to_csv(index=False)
        st.download_button(
            "⬇️ Download Full Dynamic Rankings (CSV)",
            data=csv,
            file_name=f"rr_dynamic_rankings_{selected_profile.replace(' ', '_').replace('/', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # =========================================================================
    # VISUALIZATIONS
    # =========================================================================
    st.markdown("---")
    st.markdown("### 📊 Ranking Visualizations")

    viz_tab1, viz_tab2, viz_tab3 = st.tabs(["🏆 Score Distribution", "📈 Age vs Score", "🔬 Sensitivity"])

    with viz_tab1:
        st.plotly_chart(
            plot_ranking_bar_chart(ranked_df.head(20), "Top 20 by Dynamic Scouting Score"),
            use_container_width=True
        )

    with viz_tab2:
        st.plotly_chart(
            plot_age_vs_scouting(ranked_df, "Age vs Dynamic Scouting Score"),
            use_container_width=True
        )

    with viz_tab3:
        _render_sensitivity_chart(engine, filtered_pool)

    # =========================================================================
    # PLAYER DETAIL: DIMENSION BREAKDOWN
    # =========================================================================
    st.markdown("---")
    st.markdown("### 🔎 Player Dimension Breakdown")

    player_names = ranked_df['player_name'].tolist()
    selected = st.selectbox("Select player for detailed breakdown:", ["— Select —"] + player_names, key="breakdown_player")

    if selected != "— Select —":
        player_row = ranked_df[ranked_df['player_name'] == selected].iloc[0]
        breakdown = engine.get_dimension_breakdown(ranked_df, int(player_row['player_id']))

        if breakdown:
            c1, c2 = st.columns([1, 2])

            with c1:
                st.metric("Dynamic Rank", f"#{breakdown.get('rank', 0)}")
                st.metric("Dynamic Score", f"{breakdown.get('total_score', 0):.2f}")

            with c2:
                st.markdown("**Dimension Contributions:**")
                for dim_key, info in breakdown.items():
                    if dim_key in ['total_score', 'rank']:
                        continue
                    st.markdown(f"""
                    - **{info['name']}** (Weight: {info['weight_pct']}%):
                      Raw Score: {info['raw_score']} → Contribution: {info['contribution']:.2f}
                    """)