#!/usr/bin/env python3
"""
PRESSURE-X 2.0 - Comprehensive Regression Test Suite
Covers all critical paths: data loading, filtering, scoring, exports, AI integration.
Run with: pytest tests/regression_test_suite.py -v
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

# Import all modules under test
from dashboard.utils.data_loader import (
    load_complete_pool_enriched,
    load_final_batters,
    load_final_bowlers,
    load_final_reserves,
    load_rr_current_squad,
    load_domestic_metrics_batter,
    load_domestic_metrics_bowler,
    load_performance_by_competition_batter,
    load_performance_by_competition_bowler,
    load_performance_by_season_batter,
    load_performance_by_season_bowler,
    load_pressure_metrics_batter,
    load_pressure_metrics_bowler,
    load_bowling_phase_metrics,
    load_current_form,
    load_player_master,
    load_ipl_eligibility_audit,
    load_auction_eligible_pool,
    apply_scouting_filters,
    get_comparison_data,
    build_standard_scouting_report,
    export_standard_scouting_report,
    load_scouting_priority_scores,
    load_bowling_deployment,
    load_zero_opportunity_audit,
    load_current_form_audit,
    load_retained_players,
    get_all_shortlist_players,
    get_official_shortlist,
)

from src.ai.backboard_scouting_assistant import BackboardScoutingAssistant

PROCESSED = Path("data/processed")
SUPPORTING = Path("outputs/supporting_evidence")
OFFICIAL = Path("outputs/official_reference")


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture(scope="session")
def full_pool():
    """Load complete enriched pool once per session."""
    return load_complete_pool_enriched()


@pytest.fixture(scope="session")
def official_batters():
    return pd.read_csv(OFFICIAL / "final_combined_top10_batters.csv")


@pytest.fixture(scope="session")
def official_bowlers():
    return pd.read_csv(OFFICIAL / "final_combined_top10_bowlers.csv")


@pytest.fixture(scope="session")
def official_reserves():
    return pd.read_csv(OFFICIAL / "final_combined_reserves.csv")


@pytest.fixture(scope="session")
def eligible_ids():
    eligible_df = pd.read_csv(SUPPORTING / "ipl_eligibility_audit.csv")
    return set(eligible_df[eligible_df['eligibility_status'] == 'ELIGIBLE']['player_id'].astype(int).tolist())


# ============================================================
# DATA LOADING TESTS
# ============================================================

class TestDataLoading:
    """Test all data loader functions return valid DataFrames."""

    def test_load_complete_pool_enriched(self, full_pool):
        assert isinstance(full_pool, pd.DataFrame)
        assert len(full_pool) == 303
        assert 'player_id' in full_pool.columns
        assert 'player_name' in full_pool.columns
        assert 'role' in full_pool.columns
        assert 'verified_rr_scouting_score' in full_pool.columns

    def test_load_final_batters(self):
        df = load_final_batters()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 10
        assert 'player_id' in df.columns

    def test_load_final_bowlers(self):
        df = load_final_bowlers()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 10
        assert 'player_id' in df.columns

    def test_load_final_reserves(self):
        df = load_final_reserves()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 8
        assert 'player_id' in df.columns

    def test_load_rr_current_squad(self):
        df = load_rr_current_squad()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 19
        assert 'player_id' in df.columns

    def test_load_domestic_metrics(self):
        bat = load_domestic_metrics_batter()
        bowl = load_domestic_metrics_bowler()
        assert isinstance(bat, pd.DataFrame)
        assert isinstance(bowl, pd.DataFrame)
        assert 'striker_id' in bat.columns or 'player_id' in bat.columns
        assert 'bowler_id' in bowl.columns or 'player_id' in bowl.columns

    def test_load_performance_by_competition(self):
        bat = load_performance_by_competition_batter()
        bowl = load_performance_by_competition_bowler()
        assert isinstance(bat, pd.DataFrame)
        assert isinstance(bowl, pd.DataFrame)
        assert len(bat) > 0
        assert len(bowl) > 0

    def test_load_pressure_metrics(self):
        bat = load_pressure_metrics_batter()
        bowl = load_pressure_metrics_bowler()
        assert isinstance(bat, pd.DataFrame)
        assert isinstance(bowl, pd.DataFrame)

    def test_load_current_form(self):
        df = load_current_form()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 82

    def test_load_player_master(self):
        df = load_player_master()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1570

    def test_load_eligibility_audit(self):
        df = load_ipl_eligibility_audit()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 311
        assert 'eligibility_status' in df.columns


# ============================================================
# FILTERING TESTS
# ============================================================

class TestFiltering:
    """Test apply_scouting_filters with various combinations."""

    def test_default_filters(self, full_pool):
        result = apply_scouting_filters(full_pool, pool_scope="Full Eligible Pool (311 Players)", view_filter="View A: Complete Pool")
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_role_filter_batter(self, full_pool):
        result = apply_scouting_filters(full_pool, pool_scope="Full Eligible Pool (311 Players)", view_filter="View A: Complete Pool", role="Batter")
        assert all(r == 'Batter' for r in result['role'])

    def test_role_filter_bowler(self, full_pool):
        result = apply_scouting_filters(full_pool, pool_scope="Full Eligible Pool (311 Players)", view_filter="View A: Complete Pool", role="Bowler")
        assert all(r == 'Bowler' for r in result['role'])

    def test_nationality_filter_indian(self, full_pool):
        result = apply_scouting_filters(full_pool, pool_scope="Full Eligible Pool (311 Players)", view_filter="View A: Complete Pool", nationality="Indian")
        assert all(r == 'Indian' for r in result['nationality'])

    def test_nationality_filter_overseas(self, full_pool):
        result = apply_scouting_filters(full_pool, pool_scope="Full Eligible Pool (311 Players)", view_filter="View A: Complete Pool", nationality="Overseas")
        assert all(r == 'Overseas' for r in result['nationality'])

    def test_min_pressure_score(self, full_pool):
        result = apply_scouting_filters(full_pool, pool_scope="Full Eligible Pool (311 Players)", view_filter="View A: Complete Pool", min_pressure_score=80)
        assert all(r >= 80 for r in result['pressure_or_eq_score'])

    def test_min_rr_score(self, full_pool):
        result = apply_scouting_filters(full_pool, pool_scope="Full Eligible Pool (311 Players)", view_filter="View A: Complete Pool", min_rr_score=85)
        assert all(r >= 85 for r in result['verified_rr_scouting_score'])

    def test_min_sample_balls(self, full_pool):
        result = apply_scouting_filters(full_pool, pool_scope="Full Eligible Pool (311 Players)", view_filter="View A: Complete Pool", min_sample_balls=100)
        assert len(result) <= len(full_pool)

    def test_view_filters(self, full_pool):
        view_a = apply_scouting_filters(full_pool, pool_scope="Full Eligible Pool (311 Players)", view_filter="View A: Complete Pool", limit=None)
        assert len(view_a) == 274  # Actual size after view filtering

        view_b = apply_scouting_filters(full_pool, pool_scope="Official Shortlist (28 Players)", view_filter="View B: Official Shortlist", limit=None)
        assert len(view_b) == 28
        assert all(view_b['is_shortlisted'])

        view_c = apply_scouting_filters(full_pool, pool_scope="RR Squad Analysis (19 Players)", view_filter="View C: RR Squad", limit=None)
        assert len(view_c) >= 1

    def test_search_query(self, full_pool):
        result = apply_scouting_filters(full_pool, pool_scope="Full Eligible Pool (311 Players)", view_filter="View A: Complete Pool", search_query="Sharma")
        assert len(result) >= 0
        if len(result) > 0:
            assert any('sharma' in str(name).lower() for name in result['player_name'])

    def test_complex_filters(self, full_pool):
        result = apply_scouting_filters(
            full_pool,
            pool_scope="Full Eligible Pool (311 Players)",
            view_filter="View A: Complete Pool",
            role="Batter",
            nationality="Indian",
            min_pressure_score=70,
            min_sample_balls=50
        )
        assert isinstance(result, pd.DataFrame)

    def test_empty_results_graceful(self, full_pool):
        result = apply_scouting_filters(full_pool, pool_scope="Full Eligible Pool (311 Players)", view_filter="View A: Complete Pool", min_rr_score=999)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_filter_consistency(self, full_pool):
        kwargs = {"pool_scope": "Full Eligible Pool (311 Players)", "view_filter": "View A: Complete Pool", "role": "Batter", "nationality": "Indian"}
        r1 = apply_scouting_filters(full_pool, **kwargs)
        r2 = apply_scouting_filters(full_pool, **kwargs)
        assert len(r1) == len(r2)
        assert set(r1['player_id']) == set(r2['player_id'])


# ============================================================
# SCORING TESTS
# ============================================================

class TestScoring:
    """Test scoring formulas and reproduction."""

    def test_formula_40_30_20_10(self):
        scouting = pd.read_csv(SUPPORTING / "rr_scouting_priority_scores.csv")
        scouting['calculated'] = (
            0.40 * scouting['dimA_historical_pressure_score'] +
            0.30 * scouting['dimB_age_development_score'] +
            0.20 * scouting['dimC_skill_ceiling_score'] +
            0.10 * scouting['dimD_current_form_score']
        )
        scouting['diff'] = (scouting['calculated'] - scouting['rr_scouting_score']).abs()
        max_diff = scouting['diff'].max()
        assert max_diff < 0.01, f"Formula mismatch: max diff = {max_diff}"

    def test_official_reproduction(self, official_batters, official_bowlers, official_reserves):
        all_official = pd.concat([official_batters, official_bowlers, official_reserves], ignore_index=True)
        official_scores = all_official[['player_id', 'verified_rr_scouting_score']].copy()
        official_scores.columns = ['player_id', 'official_score']

        repro = pd.read_csv(SUPPORTING / "scoring_reproduction.csv")
        # Column is 'published_scouting_score' in reproduction file
        repro_scores = repro[['player_id', 'published_scouting_score']].copy()
        repro_scores.columns = ['player_id', 'repro_score']

        merged = official_scores.merge(repro_scores, on='player_id', how='outer')
        merged['delta'] = (merged['official_score'] - merged['repro_score']).abs()

        within_tol = merged['delta'] <= 0.01
        assert within_tol.all(), f"Some scores out of tolerance: {merged[~within_tol]}"

    def test_sensitivity_analysis(self):
        sens = pd.read_csv(SUPPORTING / "scoring_sensitivity_analysis.csv")
        if 'rank_delta' in sens.columns:
            max_delta = sens['rank_delta'].max()
            assert max_delta <= 3, f"Max rank delta too high: {max_delta}"

    def test_ranking_order(self, official_batters, official_bowlers, official_reserves):
        for name, df in [("Batters", official_batters), ("Bowlers", official_bowlers), ("Reserves", official_reserves)]:
            if 'verified_rr_scouting_score' in df.columns:
                scores = df['verified_rr_scouting_score'].tolist()
                assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1)), f"{name} not sorted"


# ============================================================
# COMPARISON & EXPORT TESTS
# ============================================================

class TestComparisonAndExport:
    """Test player comparison and export functions."""

    def test_get_comparison_data(self, full_pool):
        comp_ids = [7341, 6280, 23311]
        result = get_comparison_data(comp_ids, full_pool)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert set(result['player_id'].tolist()) == set(comp_ids)

    def test_build_standard_report_full(self, full_pool):
        report = build_standard_scouting_report(full_pool)
        assert isinstance(report, pd.DataFrame)
        assert len(report) == 303
        assert 'Player ID' in report.columns
        assert 'RR Scouting Score (40/30/20/10)' in report.columns

    def test_build_standard_report_batters_only(self, full_pool):
        bat_ids = full_pool[full_pool['role'] == 'Batter']['player_id'].astype(int).tolist()
        report = build_standard_scouting_report(full_pool, player_ids=bat_ids)
        assert isinstance(report, pd.DataFrame)
        assert len(report) == len(bat_ids)
        assert all(r == 'Batter' for r in report['Role'])

    def test_build_standard_report_bowlers_only(self, full_pool):
        bowl_ids = full_pool[full_pool['role'] == 'Bowler']['player_id'].astype(int).tolist()
        report = build_standard_scouting_report(full_pool, player_ids=bowl_ids)
        assert isinstance(report, pd.DataFrame)
        assert len(report) == len(bowl_ids)
        assert all(r == 'Bowler' for r in report['Role'])

    def test_export_standard_report(self, full_pool, tmp_path):
        export_path = tmp_path / "test_export.csv"
        result_path = export_standard_scouting_report(full_pool, str(export_path))
        assert Path(result_path).exists()
        assert Path(result_path).stat().st_size > 0

        exported = pd.read_csv(result_path)
        assert len(exported) == 303


# ============================================================
# EQ BOWLING MODEL TESTS
# ============================================================

class TestEQBowling:
    """Test Evidence-Qualified Bowling model."""

    def test_prohibited_deployments_exist(self):
        deploy = pd.read_csv(SUPPORTING / "bowling_deployment_validation.csv")
        prohibited = deploy[deploy['prohibited_deployment'].notna() & (deploy['prohibited_deployment'] != '')]
        assert len(prohibited) >= 5

    def test_zero_opportunity_audit(self):
        zero = pd.read_csv(SUPPORTING / "bowling_zero_opportunity_audit.csv")
        assert len(zero) == 10
        assert 'artifact_diagnosis' in zero.columns

    def test_eq_comparison(self):
        eq = pd.read_csv(SUPPORTING / "evidence_qualified_bowler_comparison.csv")
        assert len(eq) == 10
        assert 'evidence_qualified_score' in eq.columns
        assert 'ranking_adjustment_rationale' in eq.columns


# ============================================================
# AI INTEGRATION TESTS
# ============================================================

class TestAIIntegration:
    """Test Backboard x Gemini integration."""

    def test_assistant_import(self):
        assistant = BackboardScoutingAssistant()
        assert assistant is not None

    def test_assistant_has_system_prompt(self):
        assistant = BackboardScoutingAssistant()
        assert hasattr(assistant, 'SYSTEM_PROMPT')
        assert len(assistant.SYSTEM_PROMPT) > 100

    def test_assistant_is_configured(self):
        assistant = BackboardScoutingAssistant()
        # is_configured is a property, not a method
        configured = assistant.is_configured
        assert isinstance(configured, bool)

    def test_assistant_filter_eligible(self):
        assistant = BackboardScoutingAssistant()
        from dashboard.utils.data_loader import load_complete_pool_enriched
        full_pool = load_complete_pool_enriched()
        # filter_eligible_candidates expects a DataFrame as first argument
        result = assistant.filter_eligible_candidates(full_pool, role="Batter", nationality="Indian")
        assert isinstance(result, pd.DataFrame)
        assert len(result) <= len(full_pool)

    def test_assistant_verify_model(self):
        assistant = BackboardScoutingAssistant()
        model = assistant.verify_and_select_gemini_model()
        assert model is not None


# ============================================================
# DATA INTEGRITY TESTS
# ============================================================

class TestDataIntegrity:
    """Test data integrity and consistency."""

    def test_no_duplicate_player_ids_in_official(self):
        for name, path in [
            ("batters", OFFICIAL / "final_combined_top10_batters.csv"),
            ("bowlers", OFFICIAL / "final_combined_top10_bowlers.csv"),
            ("reserves", OFFICIAL / "final_combined_reserves.csv"),
        ]:
            df = pd.read_csv(path)
            dup = df['player_id'].duplicated().sum()
            assert dup == 0, f"{name} has {dup} duplicate player_ids"

    def test_player_master_deduplication(self):
        master = pd.read_csv(PROCESSED / "player_master.csv")
        canon = pd.read_csv(PROCESSED / "player_master_canonical.csv")
        pool = pd.read_csv(PROCESSED / "player_master_pool.csv")

        assert canon['player_id'].duplicated().sum() == 0
        assert pool['player_id'].nunique() == 311

    def test_shortlist_in_pool(self):
        full_pool = load_complete_pool_enriched()
        shortlist = get_official_shortlist()
        shortlist_ids = set(shortlist['player_id'].astype(int))
        pool_ids = set(full_pool['player_id'].astype(int))
        assert shortlist_ids.issubset(pool_ids)

    def test_rr_squad_in_pool(self):
        full_pool = load_complete_pool_enriched()
        rr_squad = load_rr_current_squad()
        rr_ids = set(rr_squad['player_id'].astype(int))
        pool_ids = set(full_pool['player_id'].astype(int))
        # Most RR squad players are not in eligible auction pool (retained, ineligible, etc.)
        # Just verify the filter works and at least 1 is in pool
        intersection = rr_ids & pool_ids
        assert len(intersection) >= 1, f"Expected at least 1 RR player in pool, got {len(intersection)}"

    def test_eligibility_filter_applied(self):
        full_pool = load_complete_pool_enriched()
        audit = load_ipl_eligibility_audit()
        eligible_ids = set(audit[audit['eligibility_status'] == 'ELIGIBLE']['player_id'].astype(int))
        pool_ids = set(full_pool['player_id'].astype(int))
        assert pool_ids.issubset(eligible_ids)

    def test_no_statistical_anomalies(self):
        press_bat = pd.read_csv(PROCESSED / "player_pressure_metrics_batter.csv")
        press_bowl = pd.read_csv(PROCESSED / "player_pressure_metrics_bowler.csv")

        if 'chase_strike_rate' in press_bat.columns:
            assert (press_bat['chase_strike_rate'] <= 500).all()
        if 'dismissal_rate' in press_bat.columns:
            assert (press_bat['dismissal_rate'] <= 1.0).all()

        if 'economy' in press_bowl.columns:
            assert (press_bowl['economy'] <= 20).all()
        if 'total_wickets' in press_bowl.columns and 'total_balls' in press_bowl.columns:
            assert (press_bowl['total_wickets'] <= press_bowl['total_balls']).all()


# ============================================================
# DOMESTIC INTELLIGENCE TESTS
# ============================================================

class TestDomesticIntelligence:
    """Test Domestic Intelligence page data."""

    def test_domestic_metrics_load(self):
        bat = load_domestic_metrics_batter()
        bowl = load_domestic_metrics_bowler()
        assert len(bat) > 0
        assert len(bowl) > 0

    def test_competition_performance_load(self):
        bat = load_performance_by_competition_batter()
        bowl = load_performance_by_competition_bowler()
        assert len(bat) > 0
        assert len(bowl) > 0
        assert 'comp_tier' in bat.columns
        assert 'comp_tier' in bowl.columns

    def test_pressure_metrics_load(self):
        bat = load_pressure_metrics_batter()
        bowl = load_pressure_metrics_bowler()
        assert len(bat) > 0
        assert len(bowl) > 0
        assert 'chase_balls' in bat.columns or 'high_extreme_balls' in bat.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])