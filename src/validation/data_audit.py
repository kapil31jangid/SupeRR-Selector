#!/usr/bin/env python3
"""
Data Audit Pipeline for SupeRR Selector Season 2

This module performs comprehensive data quality checks on the official
cricket data pack. It validates the six expected CSV files, checks
referential integrity, inspects data types and distributions, and
identifies anomalies without making corrections.

Usage:
    python -m src.data_audit
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

EXPECTED_FILES = [
    "competitions.csv",
    "teams.csv",
    "matches.csv",
    "ball_by_ball.csv",
    "competition_team_player_mapping.csv",
    "playing_eleven.csv",
]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(OUTPUT_DIR / "audit.log", mode="w"),
    ],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------------
def load_csv(path: Path) -> pd.DataFrame:
    """Load a CSV file with robust error handling."""
    try:
        df = pd.read_csv(path, low_memory=False)
        logger.info("Loaded %s: %d rows, %d cols", path.name, len(df), len(df.columns))
        return df
    except Exception as e:
        logger.error("Failed to load %s: %s", path.name, e)
        raise


def summarize_dataframe(df: pd.DataFrame, name: str) -> dict[str, Any]:
    """Generate a comprehensive summary of a DataFrame."""
    summary = {
        "file": name,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "columns": {},
        "missing_values": {},
        "duplicate_rows": int(df.duplicated().sum()),
        "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
    }

    for col in df.columns:
        col_info = {
            "dtype": str(df[col].dtype),
            "non_null_count": int(df[col].notna().sum()),
            "null_count": int(df[col].isna().sum()),
            "null_pct": round(df[col].isna().mean() * 100, 2),
        }

        # Add type-specific info
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info.update({
                "min": float(df[col].min()) if df[col].notna().any() else None,
                "max": float(df[col].max()) if df[col].notna().any() else None,
                "mean": float(df[col].mean()) if df[col].notna().any() else None,
            })
        elif pd.api.types.is_string_dtype(df[col]) or df[col].dtype == object:
            col_info["unique_count"] = int(df[col].nunique())
            if df[col].notna().any():
                col_info["sample_values"] = df[col].dropna().unique()[:5].tolist()

        summary["columns"][col] = col_info
        summary["missing_values"][col] = col_info["null_count"]

    return summary


def save_json(data: dict, path: Path) -> None:
    """Save dictionary as JSON with pretty formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    logger.info("Saved JSON: %s", path)


def save_markdown_report(findings: dict, path: Path) -> None:
    """Generate a human-readable Markdown audit report."""
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Data Audit Report - SupeRR Selector Season 2",
        "",
        f"Generated: {pd.Timestamp.now().isoformat()}",
        f"Project Root: {PROJECT_ROOT}",
        f"Raw Data Dir: {RAW_DIR}",
        "",
        "## Summary",
        "",
    ]

    # File verification
    lines.append("### File Verification")
    lines.append("")
    for f in findings.get("file_verification", {}).get("files", []):
        status = "✅" if f["exists"] else "❌"
        lines.append(f"- {status} {f['filename']}: {f.get('row_count', 'N/A')} rows, {f.get('col_count', 'N/A')} cols")
    lines.append("")

    # Match ID validation
    mid = findings.get("match_id_validation", {})
    lines.append("### Match ID Validation")
    lines.append("")
    lines.append(f"- Matches in matches.csv: {mid.get('matches_in_matches', 0)}")
    lines.append(f"- Unique match_ids in ball_by_ball.csv: {mid.get('unique_match_ids_in_ball_by_ball', 0)}")
    lines.append(f"- Match IDs in both: {mid.get('match_ids_in_both', 0)}")
    lines.append(f"- Match IDs only in matches.csv: {mid.get('only_in_matches', 0)}")
    lines.append(f"- Match IDs only in ball_by_ball.csv: {mid.get('only_in_ball_by_ball', 0)}")
    if mid.get("mismatch_details"):
        lines.append("")
        lines.append("#### Mismatch Details")
        for d in mid["mismatch_details"][:10]:
            lines.append(f"- {d}")
    lines.append("")

    # Competition formats
    comp = findings.get("competition_formats", {})
    lines.append("### Competition Formats & Seasons")
    lines.append("")
    lines.append(f"- Total competitions: {comp.get('total_competitions', 0)}")
    lines.append(f"- Unique formats: {comp.get('unique_formats', [])}")
    lines.append(f"- Unique seasons: {comp.get('unique_seasons', [])}")
    lines.append("")
    lines.append("#### Format Distribution")
    for fmt, count in comp.get("format_counts", {}).items():
        lines.append(f"- {fmt}: {count} competitions")
    lines.append("")
    lines.append("#### IPL Competitions (identified by 'IPL' in name)")
    for c in comp.get("ipl_competitions", []):
        lines.append(f"- comp_id={c['comp_id']}, name={c['comp_name']}, format={c['match_format']}, season={c['season']}")
    lines.append("")
    lines.append("#### T20I Competitions (identified by 'T20I' in format)")
    for c in comp.get("t20i_competitions", [])[:10]:
        lines.append(f"- comp_id={c['comp_id']}, name={c['comp_name']}, format={c['match_format']}, season={c['season']}")
    if len(comp.get("t20i_competitions", [])) > 10:
        lines.append(f"- ... and {len(comp['t20i_competitions']) - 10} more")
    lines.append("")

    # Player ID validation
    pid = findings.get("player_id_validation", {})
    lines.append("### Player ID Validation")
    lines.append("")
    lines.append(f"- Unique players in competition_team_player_mapping: {pid.get('unique_players_in_mapping', 0)}")
    lines.append(f"- Unique players in playing_eleven: {pid.get('unique_players_in_playing_eleven', 0)}")
    lines.append(f"- Players in both: {pid.get('players_in_both', 0)}")
    lines.append(f"- Players only in mapping: {pid.get('only_in_mapping', 0)}")
    lines.append(f"- Players only in playing_eleven: {pid.get('only_in_playing_eleven', 0)}")
    lines.append("")

    # Delivery-level inspection
    deliv = findings.get("delivery_inspection", {})
    lines.append("### Delivery-Level Inspection (ball_by_ball.csv)")
    lines.append("")
    lines.append(f"- Total deliveries: {deliv.get('total_deliveries', 0)}")
    lines.append(f"- Unique matches: {deliv.get('unique_matches', 0)}")
    lines.append(f"- Unique innings: {deliv.get('unique_innings', [])}")
    lines.append(f"- Innings distribution: {deliv.get('innings_distribution', {})}")
    lines.append("")
    lines.append("#### Runs Distribution")
    for k, v in deliv.get("runs_distribution", {}).items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("#### Extras Analysis")
    lines.append(f"- Deliveries with extras: {deliv.get('deliveries_with_extras', 0)} ({deliv.get('extras_pct', 0)}%)")
    lines.append(f"- Extras types: {deliv.get('extras_types', {})}")
    lines.append("")
    lines.append("#### Wickets Analysis")
    lines.append(f"- Total wickets: {deliv.get('total_wickets', 0)}")
    lines.append(f"- Dismissal types: {deliv.get('dismissal_types', {})}")
    lines.append("")
    lines.append("#### Legal Ball Convention Check")
    lines.append(f"- Deliveries where over_ball_num > 6 (potential wides/no-balls): {deliv.get('over_ball_num_gt_6', 0)}")
    lines.append(f"- Max over_ball_num: {deliv.get('max_over_ball_num', 0)}")
    lines.append("")

    # Anomalies
    anomalies = findings.get("anomalies", [])
    lines.append("### Anomalies & Data Quality Issues")
    lines.append("")
    if anomalies:
        for a in anomalies:
            lines.append(f"- **{a['severity']}**: {a['description']}")
            if a.get("details"):
                lines.append(f"  - Details: {a['details']}")
    else:
        lines.append("No major anomalies detected.")
    lines.append("")

    # Assumptions
    assumptions = findings.get("assumptions", [])
    lines.append("### Assumptions (Not Verified)")
    lines.append("")
    for a in assumptions:
        lines.append(f"- {a}")
    lines.append("")

    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info("Saved Markdown report: %s", path)


def save_csv_summary(findings: dict, path: Path) -> None:
    """Save a flattened CSV summary of key metrics."""
    path.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    # File summaries
    for f in findings.get("file_verification", {}).get("files", []):
        rows.append({
            "category": "file_verification",
            "metric": f["filename"],
            "value": f"{f.get('row_count', 'N/A')} rows, {f.get('col_count', 'N/A')} cols",
            "status": "PASS" if f["exists"] else "FAIL",
        })

    # Match ID validation
    mid = findings.get("match_id_validation", {})
    for k, v in mid.items():
        if isinstance(v, (int, float, str)):
            rows.append({"category": "match_id_validation", "metric": k, "value": v, "status": "INFO"})

    # Competition formats
    comp = findings.get("competition_formats", {})
    for fmt, count in comp.get("format_counts", {}).items():
        rows.append({"category": "competition_formats", "metric": f"format_{fmt}", "value": count, "status": "INFO"})

    # Player ID validation
    pid = findings.get("player_id_validation", {})
    for k, v in pid.items():
        if isinstance(v, (int, float, str)):
            rows.append({"category": "player_id_validation", "metric": k, "value": v, "status": "INFO"})

    # Delivery inspection
    deliv = findings.get("delivery_inspection", {})
    for k, v in deliv.items():
        if isinstance(v, (int, float, str)):
            rows.append({"category": "delivery_inspection", "metric": k, "value": v, "status": "INFO"})

    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    logger.info("Saved CSV summary: %s", path)


# ---------------------------------------------------------------------------
# Audit Functions
# ---------------------------------------------------------------------------
def verify_files() -> dict:
    """Verify all six expected CSV files exist and are readable."""
    results = {"files": [], "all_exist": True}

    for fname in EXPECTED_FILES:
        fpath = RAW_DIR / fname
        exists = fpath.exists()
        if not exists:
            results["all_exist"] = False
            logger.warning("Missing file: %s", fname)

        row_count = col_count = None
        if exists:
            try:
                df = pd.read_csv(fpath, nrows=0)
                col_count = len(df.columns)
                df = pd.read_csv(fpath)
                row_count = len(df)
            except Exception as e:
                logger.error("Error reading %s: %s", fname, e)
                row_count = col_count = "ERROR"

        results["files"].append({
            "filename": fname,
            "exists": exists,
            "path": str(fpath),
            "row_count": row_count,
            "col_count": col_count,
        })

    return results


def validate_match_ids(matches_df: pd.DataFrame, bbb_df: pd.DataFrame) -> dict:
    """Validate match IDs between matches.csv and ball_by_ball.csv."""
    matches_ids = set(matches_df["match_id"].dropna().astype(int).unique())
    bbb_ids = set(bbb_df["match_id"].dropna().astype(int).unique())

    in_both = matches_ids & bbb_ids
    only_in_matches = matches_ids - bbb_ids
    only_in_bbb = bbb_ids - matches_ids

    mismatch_details = []
    if only_in_matches:
        mismatch_details.append(f"{len(only_in_matches)} match_ids in matches.csv but not in ball_by_ball.csv")
    if only_in_bbb:
        mismatch_details.append(f"{len(only_in_bbb)} match_ids in ball_by_ball.csv but not in matches.csv")

    return {
        "matches_in_matches": len(matches_ids),
        "unique_match_ids_in_ball_by_ball": len(bbb_ids),
        "match_ids_in_both": len(in_both),
        "only_in_matches": len(only_in_matches),
        "only_in_ball_by_ball": len(only_in_bbb),
        "mismatch_details": mismatch_details,
    }


def inspect_competition_formats(comp_df: pd.DataFrame) -> dict:
    """Inspect competition formats and seasons, identify IPL and T20I."""
    results = {
        "total_competitions": len(comp_df),
        "unique_formats": sorted(comp_df["match_format"].dropna().unique().tolist()),
        "unique_seasons": sorted(comp_df["season"].dropna().unique().tolist()),
        "format_counts": comp_df["match_format"].value_counts().to_dict(),
        "season_counts": comp_df["season"].value_counts().to_dict(),
    }

    # Identify IPL competitions (name contains 'IPL')
    ipl_mask = comp_df["comp_name"].str.contains("IPL", case=False, na=False)
    results["ipl_competitions"] = comp_df[ipl_mask][
        ["comp_id", "comp_name", "match_format", "season"]
    ].to_dict("records")

    # Identify T20I competitions (format == 'T20I')
    t20i_mask = comp_df["match_format"] == "T20I"
    results["t20i_competitions"] = comp_df[t20i_mask][
        ["comp_id", "comp_name", "match_format", "season"]
    ].to_dict("records")

    # Other T20 (non-IPL, non-T20I)
    other_t20_mask = (comp_df["match_format"] == "T20") & ~ipl_mask
    results["other_t20_competitions"] = comp_df[other_t20_mask][
        ["comp_id", "comp_name", "match_format", "season"]
    ].to_dict("records")

    return results


def validate_player_ids(mapping_df: pd.DataFrame, playing_df: pd.DataFrame) -> dict:
    """Validate player IDs against mapping and playing eleven."""
    mapping_players = set(mapping_df["player_id"].dropna().astype(int).unique())
    playing_players = set(playing_df["player_id"].dropna().astype(int).unique())

    in_both = mapping_players & playing_players
    only_in_mapping = mapping_players - playing_players
    only_in_playing = playing_players - mapping_players

    return {
        "unique_players_in_mapping": len(mapping_players),
        "unique_players_in_playing_eleven": len(playing_players),
        "players_in_both": len(in_both),
        "only_in_mapping": len(only_in_mapping),
        "only_in_playing_eleven": len(only_in_playing),
    }


def inspect_deliveries(bbb_df: pd.DataFrame) -> dict:
    """Inspect delivery-level fields, extras, wickets, innings, legal-ball conventions."""
    results = {
        "total_deliveries": len(bbb_df),
        "unique_matches": int(bbb_df["match_id"].nunique()),
        "unique_innings": sorted(bbb_df["innings"].dropna().unique().tolist()),
        "innings_distribution": bbb_df["innings"].value_counts().to_dict(),
    }

    # Runs distribution
    runs_col = "runs"
    if runs_col in bbb_df.columns:
        results["runs_distribution"] = {
            "min": float(bbb_df[runs_col].min()),
            "max": float(bbb_df[runs_col].max()),
            "mean": float(bbb_df[runs_col].mean()),
            "value_counts": bbb_df[runs_col].value_counts().head(20).to_dict(),
        }

    # Extras analysis
    extras_col = "extras_type"
    if extras_col in bbb_df.columns:
        extras_not_null = bbb_df[extras_col].notna() & (bbb_df[extras_col] != "None")
        results["deliveries_with_extras"] = int(extras_not_null.sum())
        results["extras_pct"] = round(extras_not_null.mean() * 100, 2)
        results["extras_types"] = bbb_df.loc[extras_not_null, extras_col].value_counts().to_dict()

    # Extras runs
    for ec in ["extras1_runs", "extras_2_runs"]:
        if ec in bbb_df.columns:
            results[f"{ec}_sum"] = float(bbb_df[ec].sum())
            results[f"{ec}_max"] = float(bbb_df[ec].max())

    # Wickets analysis
    wicket_col = "is_wicket"
    if wicket_col in bbb_df.columns:
        wickets = bbb_df[bbb_df[wicket_col] == True]
        results["total_wickets"] = len(wickets)
        if "dismissal_type" in bbb_df.columns:
            results["dismissal_types"] = wickets["dismissal_type"].value_counts().to_dict()

    # Legal ball convention: over_ball_num should typically be 1-6 for legal balls
    if "over_ball_num" in bbb_df.columns:
        results["over_ball_num_gt_6"] = int((bbb_df["over_ball_num"] > 6).sum())
        results["max_over_ball_num"] = int(bbb_df["over_ball_num"].max())
        results["over_ball_num_distribution"] = bbb_df["over_ball_num"].value_counts().to_dict()

    # Innings ball numbering
    if "innings_ball_num" in bbb_df.columns:
        results["max_innings_ball_num"] = int(bbb_df["innings_ball_num"].max())

    # Check for duplicate delivery identifiers
    if all(c in bbb_df.columns for c in ["match_id", "innings", "overid", "over_ball_num"]):
        dup_deliveries = bbb_df.duplicated(
            subset=["match_id", "innings", "overid", "over_ball_num"]
        ).sum()
        results["duplicate_delivery_keys"] = int(dup_deliveries)

    return results


def detect_anomalies(
    comp_df: pd.DataFrame,
    teams_df: pd.DataFrame,
    matches_df: pd.DataFrame,
    bbb_df: pd.DataFrame,
    mapping_df: pd.DataFrame,
    playing_df: pd.DataFrame,
) -> list[dict]:
    """Detect anomalies and potential data-quality issues."""
    anomalies = []

    # 1. Matches with no ball-by-ball data
    match_ids_in_matches = set(matches_df["match_id"].dropna().astype(int).unique())
    match_ids_in_bbb = set(bbb_df["match_id"].dropna().astype(int).unique())
    missing_bbb = match_ids_in_matches - match_ids_in_bbb
    if missing_bbb:
        anomalies.append({
            "severity": "WARNING",
            "description": f"{len(missing_bbb)} matches have no ball-by-ball data",
            "details": f"Missing match_ids: {sorted(missing_bbb)[:10]}",
        })

    # 2. Ball-by-ball entries for non-existent matches
    extra_bbb = match_ids_in_bbb - match_ids_in_matches
    if extra_bbb:
        anomalies.append({
            "severity": "WARNING",
            "description": f"{len(extra_bbb)} ball-by-ball entries reference non-existent matches",
            "details": f"Extra match_ids: {sorted(extra_bbb)[:10]}",
        })

    # 3. Duplicate match_ids in matches.csv
    dup_matches = matches_df["match_id"].duplicated().sum()
    if dup_matches:
        anomalies.append({
            "severity": "ERROR",
            "description": f"Duplicate match_ids in matches.csv: {dup_matches}",
            "details": "Primary key violation",
        })

    # 4. Matches with missing critical fields
    critical_fields = ["comp_id", "match_date", "home_team_id", "away_team_id"]
    for field in critical_fields:
        missing = matches_df[field].isna().sum()
        if missing:
            anomalies.append({
                "severity": "WARNING",
                "description": f"matches.csv: {missing} rows missing '{field}'",
                "details": "Critical field for join/analysis",
            })

    # 5. Competitions with no matches
    comp_ids_in_matches = set(matches_df["comp_id"].dropna().astype(int).unique())
    comp_ids_in_comp = set(comp_df["comp_id"].dropna().astype(int).unique())
    comps_no_matches = comp_ids_in_comp - comp_ids_in_matches
    if comps_no_matches:
        anomalies.append({
            "severity": "INFO",
            "description": f"{len(comps_no_matches)} competitions have no matches",
            "details": f"comp_ids: {sorted(comps_no_matches)[:10]}",
        })

    # 6. Ball-by-ball: negative runs
    if "runs" in bbb_df.columns:
        neg_runs = (bbb_df["runs"] < 0).sum()
        if neg_runs:
            anomalies.append({
                "severity": "WARNING",
                "description": f"{neg_runs} deliveries have negative runs",
                "details": "Check if these are penalty runs or data errors",
            })

    # 7. Ball-by-ball: over_ball_num == 0 or > 6 (potential data issues)
    if "over_ball_num" in bbb_df.columns:
        zero_ball = (bbb_df["over_ball_num"] == 0).sum()
        if zero_ball:
            anomalies.append({
                "severity": "WARNING",
                "description": f"{zero_ball} deliveries have over_ball_num == 0",
                "details": "Expected 1-6 for legal deliveries; 0 may indicate wides/no-balls or data error",
            })

    # 8. Playing eleven: players not in mapping
    playing_players = set(playing_df["player_id"].dropna().astype(int).unique())
    mapping_players = set(mapping_df["player_id"].dropna().astype(int).unique())
    unmapped = playing_players - mapping_players
    if unmapped:
        anomalies.append({
            "severity": "WARNING",
            "description": f"{len(unmapped)} players in playing_eleven not in competition_team_player_mapping",
            "details": f"Sample: {sorted(unmapped)[:10]}",
        })

    # 9. Playing eleven: duplicate player entries per match/team
    if all(c in playing_df.columns for c in ["match_id", "team_id", "player_id"]):
        dup_players = playing_df.duplicated(subset=["match_id", "team_id", "player_id"]).sum()
        if dup_players:
            anomalies.append({
                "severity": "ERROR",
                "description": f"{dup_players} duplicate player entries in playing_eleven (same match/team/player)",
                "details": "Primary key violation",
            })

    # 10. Teams in playing_eleven not in teams.csv
    if "team_id" in teams_df.columns:
        teams_ids = set(teams_df["team_id"].dropna().astype(int).unique())
        playing_teams = set(playing_df["team_id"].dropna().astype(int).unique())
        unknown_teams = playing_teams - teams_ids
        if unknown_teams:
            anomalies.append({
                "severity": "WARNING",
                "description": f"{len(unknown_teams)} team_ids in playing_eleven not in teams.csv",
                "details": f"team_ids: {sorted(unknown_teams)}",
            })

    # 11. Extras type "None" as string vs actual None
    if "extras_type" in bbb_df.columns:
        none_string = (bbb_df["extras_type"] == "None").sum()
        actual_none = bbb_df["extras_type"].isna().sum()
        anomalies.append({
            "severity": "INFO",
            "description": f"extras_type: {none_string} rows have string 'None', {actual_none} are actual NaN",
            "details": "Consider standardizing to NaN for 'no extras'",
        })

    # 12. Check for inconsistent team names across files
    if "home_team_id" in matches_df.columns and "team_id" in teams_df.columns:
        match_team_ids = set(matches_df["home_team_id"].dropna().astype(int).unique()) | \
                         set(matches_df["away_team_id"].dropna().astype(int).unique())
        teams_ids = set(teams_df["team_id"].dropna().astype(int).unique())
        unmatched_teams = match_team_ids - teams_ids
        if unmatched_teams:
            anomalies.append({
                "severity": "WARNING",
                "description": f"{len(unmatched_teams)} team_ids in matches.csv not found in teams.csv",
                "details": f"team_ids: {sorted(unmatched_teams)}",
            })

    return anomalies


def get_assumptions() -> list[str]:
    """List assumptions made during audit that are not verified from data alone."""
    return [
        "match_format values 'T20' and 'T20I' are assumed to represent franchise T20 and international T20 respectively",
        "IPL competitions identified by 'IPL' in comp_name; assumes no other competition contains 'IPL' in name",
        "runs column in ball_by_ball.csv represents total runs scored on the delivery (batter runs + extras), not batter-only runs",
        "extras_type 'None' (string) indicates no extras; actual NaN values also indicate no extras",
        "over_ball_num 1-6 = legal deliveries; >6 or 0 = wides/no-balls/penalty balls (not explicitly coded)",
        "innings values 1 and 2 represent first and second innings; assumes no Super Over data or it's coded differently",
        "player_id is globally unique across all competitions and seasons",
        "team_id is globally unique; franchise teams (IPL) and national teams share the same ID space",
        "competition_team_player_mapping represents squad lists; playing_eleven represents actual XI per match",
        "is_wicket=True with dismissal_type indicates a wicket; run-outs may have dismissal_type='RunOut'",
        "DLS/Duckworth-Lewis revised targets in matches.csv (first_inn_revised_overs, etc.) are assumed correct as-is",
        "man_of_the_match = 0 indicates no player of match awarded or data not available",
        "bowl_speed = 0 may indicate missing data rather than actual 0 km/h",
        "batting_order in playing_eleven assumes 1-11 for batting positions; 0 may indicate did not bat",
    ]


# ---------------------------------------------------------------------------
# Main Audit Pipeline
# ---------------------------------------------------------------------------
def run_audit() -> dict:
    """Run the complete data audit pipeline."""
    logger.info("=" * 60)
    logger.info("Starting SupeRR Selector Season 2 Data Audit")
    logger.info("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    findings = {}

    # 1. Verify files exist
    logger.info("Step 1: Verifying expected files...")
    findings["file_verification"] = verify_files()
    if not findings["file_verification"]["all_exist"]:
        logger.error("Some expected files are missing!")
        # Continue anyway for partial audit

    # Load all dataframes
    logger.info("Loading all CSV files...")
    dfs = {}
    for fname in EXPECTED_FILES:
        fpath = RAW_DIR / fname
        if fpath.exists():
            key = fname.replace(".csv", "")
            dfs[key] = load_csv(fpath)

    # 2. Summarize each file
    logger.info("Step 2: Summarizing each file...")
    findings["file_summaries"] = {}
    for key, df in dfs.items():
        findings["file_summaries"][key] = summarize_dataframe(df, key + ".csv")

    # 3. Validate match IDs
    logger.info("Step 3: Validating match IDs...")
    if "matches" in dfs and "ball_by_ball" in dfs:
        findings["match_id_validation"] = validate_match_ids(dfs["matches"], dfs["ball_by_ball"])

    # 4. Inspect competition formats
    logger.info("Step 4: Inspecting competition formats...")
    if "competitions" in dfs:
        findings["competition_formats"] = inspect_competition_formats(dfs["competitions"])

    # 5. Validate player IDs
    logger.info("Step 5: Validating player IDs...")
    if "competition_team_player_mapping" in dfs and "playing_eleven" in dfs:
        findings["player_id_validation"] = validate_player_ids(
            dfs["competition_team_player_mapping"], dfs["playing_eleven"]
        )

    # 6. Inspect deliveries
    logger.info("Step 6: Inspecting delivery-level data...")
    if "ball_by_ball" in dfs:
        findings["delivery_inspection"] = inspect_deliveries(dfs["ball_by_ball"])

    # 7. Detect anomalies
    logger.info("Step 7: Detecting anomalies...")
    findings["anomalies"] = detect_anomalies(
        dfs.get("competitions", pd.DataFrame()),
        dfs.get("teams", pd.DataFrame()),
        dfs.get("matches", pd.DataFrame()),
        dfs.get("ball_by_ball", pd.DataFrame()),
        dfs.get("competition_team_player_mapping", pd.DataFrame()),
        dfs.get("playing_eleven", pd.DataFrame()),
    )

    # 8. Record assumptions
    findings["assumptions"] = get_assumptions()

    # Save outputs
    logger.info("Saving outputs to %s...", OUTPUT_DIR)

    # Machine-readable JSON
    save_json(findings, OUTPUT_DIR / "audit.json")

    # Human-readable Markdown
    save_markdown_report(findings, OUTPUT_DIR / "audit_report.md")

    # CSV summary
    save_csv_summary(findings, OUTPUT_DIR / "audit_summary.csv")

    # Log anomalies
    for a in findings["anomalies"]:
        logger.log(
            logging.WARNING if a["severity"] in ("WARNING", "INFO") else logging.ERROR,
            "%s: %s | %s", a["severity"], a["description"], a.get("details", ""),
        )

    logger.info("=" * 60)
    logger.info("Audit complete. Outputs saved to %s", OUTPUT_DIR)
    logger.info("Anomalies found: %d", len(findings["anomalies"]))
    logger.info("=" * 60)

    return findings


if __name__ == "__main__":
    try:
        run_audit()
        logger.info("SUCCESS: Audit pipeline completed")
    except Exception as e:
        logger.exception("Audit pipeline failed: %s", e)
        sys.exit(1)