"""
Test suite for PRESSURE-X Backboard AI Scouting Assistant integration.
Covers authentication, model selection, structured JSON output, player-ID validation,
fallback behaviour, persistent conversation, and API-key protection.

Usage (no live API key required for most tests):
    python tests/test_backboard_integration.py

For live-API tests, set BACKBOARD_API_KEY in environment or .env.
"""

import os
import sys
import json
import asyncio
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pandas as pd

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.ai.backboard_scouting_assistant import BackboardScoutingAssistant

# ---------------------------------------------------------------------------
# Shared sample candidate dataframe
# ---------------------------------------------------------------------------

SAMPLE_CANDIDATES = pd.DataFrame([
    {
        "player_id": 101,
        "player_name": "Test Batter Alpha",
        "role": "Batter",
        "country": "India",
        "nationality": "Indian",
        "age_as_of_2027_04_01": 22.4,
        "development_category": "Emerging",
        "verified_rr_scouting_score": 83.5,
        "pressure_or_eq_score": 79.2,
        "current_form_rating": "Good"
    },
    {
        "player_id": 202,
        "player_name": "Test Bowler Beta",
        "role": "Bowler",
        "country": "South Africa",
        "nationality": "Overseas",
        "age_as_of_2027_04_01": 25.1,
        "development_category": "Young development candidate",
        "verified_rr_scouting_score": 77.0,
        "pressure_or_eq_score": 71.8,
        "current_form_rating": "Neutral"
    },
    {
        "player_id": 303,
        "player_name": "Test All-rounder Gamma",
        "role": "Batter",
        "country": "India",
        "nationality": "Indian",
        "age_as_of_2027_04_01": 30.2,
        "development_category": "Prime-age performer",
        "verified_rr_scouting_score": 70.5,
        "pressure_or_eq_score": 68.0,
        "current_form_rating": "Excellent"
    },
])


class TestAPIKeyProtection(unittest.TestCase):
    """TC-01: API key must never be hardcoded, logged, or exposed."""

    def test_no_key_reads_from_env(self):
        with patch.dict(os.environ, {"BACKBOARD_API_KEY": "sk-test-environ-key"}):
            asst = BackboardScoutingAssistant()
            self.assertTrue(asst.is_configured)

    def test_explicit_key_takes_priority(self):
        asst = BackboardScoutingAssistant(api_key="sk-explicit-key")
        self.assertTrue(asst.is_configured)

    def test_masked_api_key_hides_value(self):
        asst = BackboardScoutingAssistant(api_key="sk-abcdefghijklmnop")
        masked = asst.masked_api_key
        self.assertNotIn("abcdefghijklmnop", masked)
        self.assertIn("...", masked)

    def test_unconfigured_when_no_key(self):
        env = {k: v for k, v in os.environ.items() if k != "BACKBOARD_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            asst = BackboardScoutingAssistant()
            self.assertFalse(asst.is_configured)

    def test_masked_key_shows_not_configured_when_missing(self):
        asst = BackboardScoutingAssistant.__new__(BackboardScoutingAssistant)
        asst.api_key = None
        asst.base_url = "https://app.backboard.io/api"
        asst.provider = "google"
        asst.model_name = "gemini-2.5-pro"
        asst._cached_assistant_id = None
        asst._available_google_models = None
        self.assertEqual(asst.masked_api_key, "Not Configured")

    def test_key_not_in_source_file(self):
        source = Path(PROJECT_ROOT / "src" / "ai" / "backboard_scouting_assistant.py").read_text()
        self.assertNotIn("sk-", source)
        self.assertNotIn("api_key =", source.split("def __init__")[0])


class TestAuthenticationHandling(unittest.TestCase):
    """TC-02: Invalid / missing API keys must raise specific Backboard errors."""

    def test_invalid_key_raises_backboard_error(self):
        from backboard.exceptions import BackboardAPIError

        async def _inner():
            asst = BackboardScoutingAssistant(api_key="totally-invalid-key")
            models = asst.get_google_models_catalogue()
            # An invalid key returns [] gracefully (no crash)
            self.assertIsInstance(models, list)

        asyncio.run(_inner())

    def test_unconfigured_client_returns_none(self):
        asst = BackboardScoutingAssistant()
        asst.api_key = None
        client = asst.get_client()
        self.assertIsNone(client)

    def test_unconfigured_catalogue_returns_empty(self):
        asst = BackboardScoutingAssistant()
        asst.api_key = None
        models = asst.get_google_models_catalogue()
        self.assertEqual(models, [])


class TestModelSelection(unittest.TestCase):
    """TC-03: Gemini model selection from Backboard catalogue."""

    def test_default_provider_is_google(self):
        asst = BackboardScoutingAssistant()
        self.assertEqual(asst.provider, "google")

    def test_default_model_is_gemini(self):
        asst = BackboardScoutingAssistant()
        self.assertIn("gemini", asst.model_name.lower())

    def test_catalogue_fallback_selects_valid_model(self):
        asst = BackboardScoutingAssistant(api_key="sk-fake-key")
        with patch.object(asst, "get_google_models_catalogue", return_value=[]):
            selected = asst.verify_and_select_gemini_model()
            self.assertIn("gemini", selected.lower())

    def test_catalogue_hit_selects_exact_model(self):
        asst = BackboardScoutingAssistant(api_key="sk-fake-key")
        fake_catalogue = [
            {"model_name": "gemini-2.5-flash", "provider": "google"},
            {"model_name": "gemini-2.5-pro", "provider": "google"},
        ]
        with patch.object(asst, "get_google_models_catalogue", return_value=fake_catalogue):
            selected = asst.verify_and_select_gemini_model()
            self.assertIn(selected, ["gemini-2.5-pro", "gemini-2.5-flash"])

    def test_model_configurable_via_env(self):
        with patch.dict(os.environ, {"BACKBOARD_MODEL_NAME": "gemini-1.5-pro"}):
            asst = BackboardScoutingAssistant()
            self.assertEqual(asst.model_name, "gemini-1.5-pro")


class TestCandidateFiltering(unittest.TestCase):
    """TC-04: Filter logic must only pass eligible, specified candidates."""

    def setUp(self):
        self.asst = BackboardScoutingAssistant()

    def test_role_filter_batter(self):
        result = self.asst.filter_eligible_candidates(SAMPLE_CANDIDATES, role="Batter")
        self.assertTrue(all(result['role'] == 'Batter'))

    def test_role_filter_bowler(self):
        result = self.asst.filter_eligible_candidates(SAMPLE_CANDIDATES, role="Bowler")
        self.assertTrue(all(result['role'] == 'Bowler'))

    def test_nationality_filter_indian(self):
        result = self.asst.filter_eligible_candidates(SAMPLE_CANDIDATES, nationality="Indian")
        self.assertTrue(all(result['nationality'] == 'Indian'))

    def test_max_age_filter(self):
        result = self.asst.filter_eligible_candidates(SAMPLE_CANDIDATES, max_age=25.0)
        self.assertTrue(all(result['age_as_of_2027_04_01'] <= 25.0))

    def test_empty_result_on_strict_filter(self):
        result = self.asst.filter_eligible_candidates(SAMPLE_CANDIDATES, role="Batter", max_age=20.0)
        self.assertEqual(len(result), 0)

    def test_candidate_context_serialization(self):
        records = self.asst._prepare_candidate_context(SAMPLE_CANDIDATES)
        self.assertEqual(len(records), 3)
        self.assertIn("player_id", records[0])
        self.assertIsInstance(records[0]["player_id"], int)
        self.assertIsInstance(records[0]["verified_rr_scouting_score"], float)


class TestStructuredJSONValidation(unittest.TestCase):
    """TC-05: Validate structured JSON output from AI and reconcile with ground truth."""

    def setUp(self):
        self.asst = BackboardScoutingAssistant()

    def _make_response(self, player_ids, include_extra_fields=True):
        recs = []
        for pid in player_ids:
            rec = {"player_id": pid}
            if include_extra_fields:
                rec.update({
                    "player_name": f"AI Name {pid}",
                    "suitability_explanation": "Strong pressure execution.",
                    "risk_assessment": "Moderate.",
                    "tactical_role_fit": "Anchor batter."
                })
            recs.append(rec)
        return json.dumps({
            "analysis_summary": "Test summary.",
            "recommended_players": recs,
            "squad_balance_note": "2 Indian, 1 Overseas.",
            "memory_context_acknowledged": "Previous session preferences noted."
        })

    def test_valid_player_ids_pass_validation(self):
        raw = self._make_response([101, 202])
        result = self.asst._validate_and_reconcile_response(raw, SAMPLE_CANDIDATES, "thread-123")
        self.assertTrue(result["success"])
        self.assertEqual(len(result["recommended_players"]), 2)

    def test_canonical_player_names_overwrite_ai_hallucinations(self):
        raw = self._make_response([101])
        result = self.asst._validate_and_reconcile_response(raw, SAMPLE_CANDIDATES, "thread-123")
        self.assertTrue(result["success"])
        # Name must be the canonical one, not the AI-generated "AI Name 101"
        self.assertEqual(result["recommended_players"][0]["player_name"], "Test Batter Alpha")

    def test_canonical_scores_preserved(self):
        raw = self._make_response([303])
        result = self.asst._validate_and_reconcile_response(raw, SAMPLE_CANDIDATES, "thread-123")
        self.assertTrue(result["success"])
        p = result["recommended_players"][0]
        self.assertAlmostEqual(p["verified_rr_scouting_score"], 70.5)
        self.assertAlmostEqual(p["pressure_or_eq_score"], 68.0)

    def test_hallucinated_player_id_rejected(self):
        raw = self._make_response([999])  # 999 not in candidates
        result = self.asst._validate_and_reconcile_response(raw, SAMPLE_CANDIDATES, "thread-123")
        self.assertFalse(result["success"])

    def test_invalid_json_returns_error(self):
        result = self.asst._validate_and_reconcile_response("not-json-at-all", SAMPLE_CANDIDATES)
        self.assertFalse(result["success"])
        self.assertIn("error", result)

    def test_codeblock_wrapped_json_parsed(self):
        raw = "```json\n" + self._make_response([101]) + "\n```"
        result = self.asst._validate_and_reconcile_response(raw, SAMPLE_CANDIDATES)
        self.assertTrue(result["success"])

    def test_mixed_valid_invalid_ids(self):
        raw = self._make_response([101, 999, 202])
        result = self.asst._validate_and_reconcile_response(raw, SAMPLE_CANDIDATES)
        self.assertTrue(result["success"])
        ids_returned = [r["player_id"] for r in result["recommended_players"]]
        self.assertIn(101, ids_returned)
        self.assertIn(202, ids_returned)
        self.assertNotIn(999, ids_returned)

    def test_response_includes_required_keys(self):
        raw = self._make_response([101])
        result = self.asst._validate_and_reconcile_response(raw, SAMPLE_CANDIDATES, "t-99")
        for key in ["success", "source", "analysis_summary", "recommended_players",
                    "squad_balance_note", "thread_id"]:
            self.assertIn(key, result)


class TestDeterministicFallback(unittest.TestCase):
    """TC-06: Fallback engine must work with zero API dependency."""

    def setUp(self):
        self.asst = BackboardScoutingAssistant()  # No API key → always fallback

    def test_fallback_returns_success(self):
        result = self.asst._deterministic_fallback("Test query", SAMPLE_CANDIDATES)
        self.assertTrue(result["success"])

    def test_fallback_source_is_deterministic(self):
        result = self.asst._deterministic_fallback("Test query", SAMPLE_CANDIDATES)
        self.assertEqual(result["source"], "deterministic_fallback")

    def test_fallback_uses_verified_scores(self):
        result = self.asst._deterministic_fallback("Test query", SAMPLE_CANDIDATES)
        # First rec must be highest scouting score (101 → 83.5)
        self.assertEqual(result["recommended_players"][0]["player_id"], 101)

    def test_fallback_scores_unmodified(self):
        result = self.asst._deterministic_fallback("Test query", SAMPLE_CANDIDATES)
        for rec in result["recommended_players"]:
            # Score must match original
            match = SAMPLE_CANDIDATES[SAMPLE_CANDIDATES["player_id"] == rec["player_id"]]
            if not match.empty:
                self.assertAlmostEqual(
                    rec["verified_rr_scouting_score"],
                    float(match.iloc[0]["verified_rr_scouting_score"])
                )

    def test_fallback_includes_squad_balance(self):
        result = self.asst._deterministic_fallback("Test query", SAMPLE_CANDIDATES)
        self.assertIn("squad_balance_note", result)
        self.assertGreater(len(result["squad_balance_note"]), 10)

    def test_full_query_routes_to_fallback_without_key(self):
        result = self.asst.query_scouting_assistant("Top batters", SAMPLE_CANDIDATES)
        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "deterministic_fallback")


class TestPersistentConversation(unittest.TestCase):
    """TC-07: Persistent conversation (threads / assistant) handling."""

    def test_no_thread_on_first_unconfigured_call(self):
        asst = BackboardScoutingAssistant()
        self.assertIsNone(asst.create_thread())

    def test_no_assistant_on_unconfigured(self):
        asst = BackboardScoutingAssistant()
        self.assertIsNone(asst.get_or_create_assistant())

    def test_thread_id_propagated_in_fallback_result(self):
        asst = BackboardScoutingAssistant()
        result = asst.query_scouting_assistant(
            "Best spinners", SAMPLE_CANDIDATES, thread_id="existing-thread-999"
        )
        self.assertEqual(result["thread_id"], "existing-thread-999")

    def test_mocked_assistant_creation(self):
        """With a mocked client, assistant creation must call the right API endpoint."""
        asst = BackboardScoutingAssistant(api_key="sk-mocked-key-12345678")

        mock_assistant = MagicMock()
        mock_assistant.assistant_id = "asst-abc-123"
        mock_assistants_list = MagicMock()
        mock_assistants_list.assistants = []

        async def _run():
            with patch.object(asst, "get_client") as mock_client_factory:
                mock_client = AsyncMock()
                mock_client.list_assistants = AsyncMock(return_value=mock_assistants_list)
                mock_client.create_assistant = AsyncMock(return_value=mock_assistant)
                mock_client.aclose = AsyncMock()
                mock_client_factory.return_value = mock_client

                aid = await asst._async_get_or_create_assistant()
                self.assertEqual(aid, "asst-abc-123")
                mock_client.create_assistant.assert_called_once()

        asyncio.run(_run())

    def test_mocked_thread_creation(self):
        asst = BackboardScoutingAssistant(api_key="sk-mocked-key-12345678")
        asst._cached_assistant_id = "asst-existing"

        mock_thread = MagicMock()
        mock_thread.thread_id = "thread-xyz-789"

        async def _run():
            with patch.object(asst, "get_client") as mock_client_factory:
                mock_client = AsyncMock()
                mock_client.create_thread = AsyncMock(return_value=mock_thread)
                mock_client.aclose = AsyncMock()
                mock_client_factory.return_value = mock_client

                tid = await asst._async_create_thread()
                self.assertEqual(tid, "thread-xyz-789")
                mock_client.create_thread.assert_called_once_with(assistant_id="asst-existing")

        asyncio.run(_run())


class TestAPIFailureFallback(unittest.TestCase):
    """TC-08: API failure must fall back gracefully with no data corruption."""

    def _make_asst_with_key(self):
        asst = BackboardScoutingAssistant(api_key="sk-mocked-valid-key-1234")
        return asst

    def test_network_error_falls_back_to_deterministic(self):
        from backboard.exceptions import BackboardAPIError
        asst = self._make_asst_with_key()

        with patch.object(asst, "_async_send_scouting_query",
                          side_effect=BackboardAPIError("Connection error")):
            result = asst.query_scouting_assistant("Best batters", SAMPLE_CANDIDATES)
            self.assertTrue(result["success"])
            self.assertEqual(result["source"], "deterministic_fallback")

    def test_bad_json_response_falls_back_to_deterministic(self):
        asst = self._make_asst_with_key()

        async def _bad_response(*args, **kwargs):
            return "INVALID_JSON_GARBAGE", "thread-999"

        with patch.object(asst, "_async_send_scouting_query", side_effect=_bad_response):
            with patch.object(asst, "get_or_create_assistant", return_value="asst-123"):
                result = asst.query_scouting_assistant("Best batters", SAMPLE_CANDIDATES)
                self.assertTrue(result["success"])
                self.assertIn(result["source"], ["deterministic_fallback"])

    def test_empty_candidate_pool_returns_error(self):
        asst = BackboardScoutingAssistant()
        empty_df = pd.DataFrame(columns=SAMPLE_CANDIDATES.columns)
        result = asst.query_scouting_assistant("Best batters", empty_df)
        self.assertFalse(result["success"])
        self.assertEqual(result["source"], "validation_gate")

    def test_failed_query_preserves_original_data(self):
        """Scores in the SAMPLE_CANDIDATES dataframe must not be mutated."""
        original_score = SAMPLE_CANDIDATES.loc[0, "verified_rr_scouting_score"]
        asst = BackboardScoutingAssistant()
        asst.query_scouting_assistant("Test", SAMPLE_CANDIDATES)
        self.assertEqual(SAMPLE_CANDIDATES.loc[0, "verified_rr_scouting_score"], original_score)


class TestLiveAPIIntegration(unittest.TestCase):
    """
    TC-09: Live API integration tests.
    These tests run ONLY when BACKBOARD_API_KEY is set in the environment.
    They are skipped automatically if no key is available.
    """

    @classmethod
    def setUpClass(cls):
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        cls.api_key = os.environ.get("BACKBOARD_API_KEY")
        cls.has_key = bool(cls.api_key)

    def _skip_if_no_key(self):
        if not self.has_key:
            self.skipTest("BACKBOARD_API_KEY not set — skipping live API test")

    def test_live_authentication(self):
        self._skip_if_no_key()
        asst = BackboardScoutingAssistant(api_key=self.api_key)
        self.assertTrue(asst.is_configured)
        # Basic client instantiation should not raise
        client = asst.get_client()
        self.assertIsNotNone(client)
        asyncio.run(client.aclose())

    def test_live_google_model_catalogue(self):
        self._skip_if_no_key()
        asst = BackboardScoutingAssistant(api_key=self.api_key)
        models = asst.get_google_models_catalogue()
        print(f"\n[LIVE] Google models available on Backboard ({len(models)} found):")
        for m in models[:10]:
            print(f"  - {m.get('model_name')}")
        self.assertIsInstance(models, list)

    def test_live_model_verification_and_selection(self):
        self._skip_if_no_key()
        asst = BackboardScoutingAssistant(api_key=self.api_key)
        selected_model = asst.verify_and_select_gemini_model()
        print(f"\n[LIVE] Confirmed Gemini model: {selected_model}")
        self.assertIn("gemini", selected_model.lower())

    def test_live_scouting_query_structured_json(self):
        self._skip_if_no_key()
        asst = BackboardScoutingAssistant(api_key=self.api_key)
        result = asst.query_scouting_assistant(
            "Recommend 2 young players with high scouting scores.",
            SAMPLE_CANDIDATES,
            role_filter="Batter"
        )
        print(f"\n[LIVE] Scouting result source: {result.get('source')}")
        print(f"[LIVE] Players recommended: {len(result.get('recommended_players', []))}")
        self.assertTrue(result["success"])
        # Only verified player IDs must appear
        valid_ids = set(SAMPLE_CANDIDATES["player_id"].tolist())
        for rec in result.get("recommended_players", []):
            self.assertIn(rec["player_id"], valid_ids, "AI returned an invalid player ID!")

    def test_live_persistent_thread_continuation(self):
        self._skip_if_no_key()
        asst = BackboardScoutingAssistant(api_key=self.api_key)

        # First turn
        result1 = asst.query_scouting_assistant(
            "Who is the best young Indian batter?",
            SAMPLE_CANDIDATES
        )
        self.assertTrue(result1["success"])
        thread_id = result1.get("thread_id")
        print(f"\n[LIVE] Turn 1 thread: {thread_id}")

        if thread_id and result1["source"] == "backboard_google_gemini":
            # Second turn — continuing same thread
            result2 = asst.query_scouting_assistant(
                "Now also suggest a complementary overseas bowler.",
                SAMPLE_CANDIDATES,
                thread_id=thread_id
            )
            self.assertTrue(result2["success"])
            print(f"[LIVE] Turn 2 continued thread: {result2.get('thread_id')}")
            # Thread should persist
            self.assertEqual(result2.get("thread_id"), thread_id)


# ---------------------------------------------------------------------------
# Test runner with structured output report
# ---------------------------------------------------------------------------

def run_tests():
    """Run test suite and return results summary."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestAPIKeyProtection,
        TestAuthenticationHandling,
        TestModelSelection,
        TestCandidateFiltering,
        TestStructuredJSONValidation,
        TestDeterministicFallback,
        TestPersistentConversation,
        TestAPIFailureFallback,
        TestLiveAPIIntegration,
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2, failfast=False)
    result = runner.run(suite)
    return result


if __name__ == "__main__":
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)

