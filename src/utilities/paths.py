"""
Path Utilities
Provides robust, OS-independent relative path resolution.
Ensures zero hardcoded absolute Windows paths in code or dashboard.
"""

from pathlib import Path

# Project root directory (resolved from this file location: src/utilities/paths.py -> 2 levels up)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Standard Directory Paths
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

OUTPUTS_DIR = PROJECT_ROOT / "outputs"
SUPPORTING_EVIDENCE_DIR = OUTPUTS_DIR / "supporting_evidence"

REPORTS_DIR = PROJECT_ROOT / "reports"
ASSETS_DIR = PROJECT_ROOT / "assets"
DASHBOARD_VISUALS_DIR = ASSETS_DIR / "dashboard_visuals"


def get_data_file(filename: str, processed: bool = True) -> Path:
    """Return path to data file."""
    base = PROCESSED_DATA_DIR if processed else RAW_DATA_DIR
    return base / filename


def get_output_file(filename: str, is_evidence: bool = False) -> Path:
    """Return path to output CSV/report."""
    base = SUPPORTING_EVIDENCE_DIR if is_evidence else OUTPUTS_DIR
    return base / filename

