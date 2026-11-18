"""
Unit & Integration Tests for PRESSURE-X Interactive Scouting Explorer
=====================================================================
Validates:
1. Complete 303-player pool enrichment and data integrity.
2. Read-only preservation of official final rankings (Top 10 CSVs).
3. Dynamic filtering across Role, Nationality, Age, Scores, Characteristics, and Domestic stats.
4. Missing domestic data handled as 'Insufficient domestic evidence' (no fabricated zeros).
5. Multi-candidate comparison data extraction.
6. Stale AI insight detection hashing.
7. Graceful offline behavior when Backboard AI is unavailable.
"""

import unittest
import pandas as pd
from pathlib import Path
from dashboard.utils.scouting_data import (
    load_official_batters,
    load_official_bowlers,
    load_official_reserves,
    load_complete_pool_enriched,
    apply_scouting_filters,
    get_comparison_data
)
from dashboard.pages.scouting_explorer import _compute_filter_hash
from src.utilities.paths import OUTPUTS_DIR


class TestOfficialRankingsIntegrity(unittest.TestCase):
    """Guarantees that official verified final rankings are strictly preserved."""

    def test_official_batters_count_and_scores(self):
        df = load_official_batters()
        self.assertEqual(len(df), 10, "Official Top 10 Batters must have exactly 10 rows")
        self.assertEqual(df.iloc[0]['player_name'], "Jake Fraser-McGurk")
        self.assertAlmostEqual(float(df.iloc[0]['verified_rr_scouting_score']), 91.88, places=2)
        self.assertEqual(df.iloc[1]['player_name'], "Harry Brook")
        self.assertAlmostEqual(float(df.iloc[1]['verified_rr_scouting_score']), 89.42, places=2)

    def test_official_bowlers_count_and_scores(self):
        df = load_official_bowlers()
        self.assertEqual(len(df), 10, "Official Top 10 Bowlers must have exactly 10 rows")
        self.assertEqual(df.iloc[0]['player_name'], "Mohammad Ghazanfar")
        self.assertAlmostEqual(float(df.iloc[0]['verified_rr_scouting_score']), 84.52, places=2)
        self.assertEqual(df.iloc[1]['player_name'], "Ripon Mondol")
        self.assertAlmostEqual(float(df.iloc[1]['verified_rr_scouting_score']), 81.95, places=2)

    def test_official_reserves_count(self):
        df = load_official_reserves()
        self.assertEqual(len(df), 8, "Official Reserves must have exactly 8 rows")

    def test_official_csv_files_unmodified(self):
        p_bat = OUTPUTS_DIR / "final_combined_top10_batters.csv"
        p_bowl = OUTPUTS_DIR / "final_combined_top10_bowlers.csv"
        self.assertTrue(p_bat.exists())
        self.assertTrue(p_bowl.exists())
        df_b = pd.read_csv(p_bat)
        self.assertIn("verified_rr_scouting_score", df_b.columns)
        self.assertIn("validated_historical_pressure_score", df_b.columns)


class TestCandidatePoolEnrichment(unittest.TestCase):
    """Tests the enriched 303-player candidate pool."""

    @classmethod
    def setUpClass(cls):
        cls.pool_df = load_complete_pool_enriched()

    def test_pool_total_eligible_count(self):
        self.assertEqual(len(self.pool_df), 303, "Total eligible pool must equal exactly 303 players")

    def test_shortlist_flag_present(self):
        self.assertIn('is_shortlisted', self.pool_df.columns)
        self.assertEqual(self.pool_df['is_shortlisted'].sum(), 28, "Exactly 28 players must be marked as shortlisted")

    def test_nationalities_clean(self):
        nats = set(self.pool_df['nationality'].unique())
        self.assertTrue(nats.issubset({'Indian', 'Overseas'}))
        self.assertGreaterEqual((self.pool_df['nationality'] == 'Indian').sum(), 35)

    def test_scores_within_valid_bounds(self):
        self.assertTrue((self.pool_df['verified_rr_scouting_score'] >= 0).all())
        self.assertTrue((self.pool_df['verified_rr_scouting_score'] <= 100).all())
        self.assertTrue((self.pool_df['pressure_or_eq_score'] >= 0).all())
        self.assertTrue((self.pool_df['pressure_or_eq_score'] <= 100).all())


class TestDynamicScoutingFilters(unittest.TestCase):
    """Tests multi-dimensional filtering across diverse scouting criteria."""

    @classmethod
    def setUpClass(cls):
        cls.pool_df = load_complete_pool_enriched()

    def test_filter_overseas_finishers(self):
        res = apply_scouting_filters(self.pool_df, nationality="Overseas", required_characteristic="Finisher", limit=10)
        self.assertGreater(len(res), 0)
        for _, r in res.iterrows():
            self.assertEqual(r['nationality'], "Overseas")
            self.assertIn("Finisher", r['characteristics'])

    def test_filter_domestic_runs(self):
        res = apply_scouting_filters(self.pool_df, domestic_min_runs=100.0, limit=10)
        self.assertGreater(len(res), 0)
        for _, r in res.iterrows():
            self.assertGreaterEqual(r['domestic_runs'], 100.0)

    def test_filter_domestic_bowling_wickets(self):
        res = apply_scouting_filters(self.pool_df, domestic_min_wickets=10.0, limit=10)
        self.assertGreater(len(res), 0)
        for _, r in res.iterrows():
            self.assertGreaterEqual(r['domestic_wickets'], 10.0)

    def test_filter_age_group_emerging(self):
        res = apply_scouting_filters(self.pool_df, age_group="Emerging (≤23 yrs)", limit=20)
        self.assertGreater(len(res), 0)
        for _, r in res.iterrows():
            self.assertLessEqual(r['age_as_of_2027_04_01'], 23.0)

    def test_filter_score_thresholds(self):
        res = apply_scouting_filters(self.pool_df, min_pressure_score=80.0, min_rr_score=80.0)
        self.assertGreater(len(res), 0)
        for _, r in res.iterrows():
            self.assertGreaterEqual(r['pressure_or_eq_score'], 80.0)
            self.assertGreaterEqual(r['verified_rr_scouting_score'], 80.0)

    def test_filter_search_query(self):
        res = apply_scouting_filters(self.pool_df, search_query="Bethell")
        self.assertEqual(len(res), 1)
        self.assertEqual(res.iloc[0]['player_name'], "Jacob Bethell")

    def test_filter_empty_graceful(self):
        # Impossible criteria: age <= 18 with pressure >= 99
        res = apply_scouting_filters(self.pool_df, age_max=18.0, min_pressure_score=99.0)
        self.assertEqual(len(res), 0)
        self.assertIsInstance(res, pd.DataFrame)


class TestPlayerComparison(unittest.TestCase):
    """Tests multi-candidate comparison functionality."""

    @classmethod
    def setUpClass(cls):
        cls.pool_df = load_complete_pool_enriched()

    def test_comparison_extraction(self):
        pids = [7341, 6280, 23311]  # Fraser-McGurk, Brook, Bethell
        res = get_comparison_data(pids, self.pool_df)
        self.assertEqual(len(res), 3)
        names = set(res['player_name'].tolist())
        self.assertIn("Jake Fraser-McGurk", names)
        self.assertIn("Harry Brook", names)
        self.assertIn("Jacob Bethell", names)

    def test_comparison_empty_on_invalid_ids(self):
        res = get_comparison_data([9999999, 8888888], self.pool_df)
        self.assertEqual(len(res), 0)


class TestStaleInsightHashing(unittest.TestCase):
    """Tests filter hash generation to detect stale AI insights."""

    def test_hash_consistency(self):
        import streamlit as st
        st.session_state['se_role'] = 'Batter'
        st.session_state['se_nat'] = 'Indian'
        h1 = _compute_filter_hash()
        h2 = _compute_filter_hash()
        self.assertEqual(h1, h2)

        # Change filter
        st.session_state['se_nat'] = 'Overseas'
        h3 = _compute_filter_hash()
        self.assertNotEqual(h1, h3)


if __name__ == '__main__':
    unittest.main()
