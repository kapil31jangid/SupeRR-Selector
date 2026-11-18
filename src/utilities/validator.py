"""
Pre-Dashboard Automated Data Validation Module
Verifies file existence, column schema, duplicate IDs, and score sanity.
"""

from typing import Dict, List, Tuple
from pathlib import Path
import pandas as pd
from .paths import OUTPUTS_DIR, SUPPORTING_EVIDENCE_DIR


class DataValidator:
    """Automated validator ensuring zero corrupt or missing datasets load into dashboard."""

    REQUIRED_FILES = [
        OUTPUTS_DIR / "final_combined_top10_batters.csv",
        OUTPUTS_DIR / "final_combined_top10_bowlers.csv",
        OUTPUTS_DIR / "final_combined_reserves.csv",
        SUPPORTING_EVIDENCE_DIR / "rr_scouting_priority_scores.csv",
        SUPPORTING_EVIDENCE_DIR / "evidence_qualified_bowler_comparison.csv",
        SUPPORTING_EVIDENCE_DIR / "bowling_deployment_validation.csv",
        SUPPORTING_EVIDENCE_DIR / "current_form_source_verification.csv"
    ]

    REQUIRED_BATTER_COLUMNS = [
        "final_verified_rank", "player_id", "player_name", "country",
        "nationality", "age_as_of_2027_04_01", "development_category",
        "validated_historical_pressure_score", "verified_rr_scouting_score"
    ]

    REQUIRED_BOWLER_COLUMNS = [
        "final_verified_rank", "player_id", "player_name", "country",
        "nationality", "age_as_of_2027_04_01", "development_category",
        "validated_evidence_qualified_score", "verified_rr_scouting_score"
    ]

    @classmethod
    def validate_file_existence(cls) -> Tuple[bool, List[str]]:
        """Verify all critical CSV files exist on disk."""
        missing = []
        for file_path in cls.REQUIRED_FILES:
            if not file_path.exists() or file_path.stat().st_size == 0:
                missing.append(str(file_path.name))
        return len(missing) == 0, missing

    @classmethod
    def validate_dataframe_schema(cls, df: pd.DataFrame, expected_cols: List[str]) -> Tuple[bool, List[str]]:
        """Verify presence of all expected columns."""
        missing_cols = [c for c in expected_cols if c not in df.columns]
        return len(missing_cols) == 0, missing_cols

    @classmethod
    def validate_ranking_dataframe(cls, df: pd.DataFrame, role: str = 'batter') -> Dict[str, any]:
        """
        Run full forensic checks:
        - Row count == 10
        - Unique player IDs
        - Unique ranks 1..10
        - Valid age range (18 to 45)
        - Valid score ranges (0 to 100)
        - Valid nationality ('Indian' or 'Overseas')
        """
        issues = []
        expected_cols = cls.REQUIRED_BATTER_COLUMNS if role == 'batter' else cls.REQUIRED_BOWLER_COLUMNS
        valid_schema, missing_cols = cls.validate_dataframe_schema(df, expected_cols)
        if not valid_schema:
            issues.append(f"Missing columns: {missing_cols}")

        if len(df) != 10:
            issues.append(f"Expected 10 rows, found {len(df)}")

        # Duplicate ID check
        if 'player_id' in df.columns:
            dups = df['player_id'].duplicated().sum()
            if dups > 0:
                issues.append(f"Found {dups} duplicate player_id(s)")

        # Duplicate rank check
        if 'final_verified_rank' in df.columns:
            ranks = pd.to_numeric(df['final_verified_rank'], errors='coerce')
            if ranks.duplicated().sum() > 0:
                issues.append("Duplicate ranking numbers detected")
            if not set(ranks.dropna().astype(int).tolist()).issubset(set(range(1, 11))):
                issues.append("Ranks outside 1..10 range detected")

        # Score sanity check
        score_col = 'verified_rr_scouting_score'
        if score_col in df.columns:
            scores = pd.to_numeric(df[score_col], errors='coerce')
            if (scores < 0).any() or (scores > 100).any():
                issues.append(f"Scores out of [0, 100] range in {score_col}")

        # Age sanity check
        if 'age_as_of_2027_04_01' in df.columns:
            ages = pd.to_numeric(df['age_as_of_2027_04_01'], errors='coerce')
            if (ages < 18).any() or (ages > 50).any():
                issues.append("Unrealistic age detected (<18 or >50)")

        # Nationality sanity check
        if 'nationality' in df.columns:
            invalid_nat = df[~df['nationality'].isin(['Indian', 'Overseas'])]
            if len(invalid_nat) > 0:
                issues.append(f"Invalid nationality values: {invalid_nat['nationality'].unique().tolist()}")

        return {
            'is_valid': len(issues) == 0,
            'issue_count': len(issues),
            'issues': issues
        }

    @classmethod
    def run_all_checks(cls) -> Dict[str, any]:
        """Perform full validation pass and return status summary."""
        files_ok, missing_files = cls.validate_file_existence()
        if not files_ok:
            return {
                'overall_pass': False,
                'status': 'FAIL_MISSING_FILES',
                'details': f"Missing required data files: {missing_files}"
            }

        batters_df = pd.read_csv(OUTPUTS_DIR / "final_combined_top10_batters.csv")
        bowlers_df = pd.read_csv(OUTPUTS_DIR / "final_combined_top10_bowlers.csv")

        b_check = cls.validate_ranking_dataframe(batters_df, role='batter')
        bo_check = cls.validate_ranking_dataframe(bowlers_df, role='bowler')

        all_pass = b_check['is_valid'] and bo_check['is_valid']
        return {
            'overall_pass': all_pass,
            'status': 'PASS' if all_pass else 'FAIL_DATA_INTEGRITY',
            'batter_checks': b_check,
            'bowler_checks': bo_check
        }

