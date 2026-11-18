#!/usr/bin/env python3
"""
Data Validation & Investigation for SupeRR Selector Season 2

This module investigates data interpretation questions identified in the audit:
1. Duplicate playing_eleven entries
2. Delivery rules (runs, extras, legal balls)
3. Wicket attribution rules
4. Missing ball-by-ball matches
5. Competition scope (IPL vs T20I)
6. Player identity joins
7. Generates validation reports

Does NOT modify raw data. Only reads and analyzes.
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(OUTPUT_DIR / "validation.log", mode="w"),
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


def save_json(data: Any, path: Path) -> None:
    """Save data as JSON with pretty formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    logger.info("Saved JSON: %s", path)


def save_csv(df: pd.DataFrame, path: Path) -> None:
    """Save DataFrame as CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info("Saved CSV: %s (%d rows)", path, len(df))


def save_markdown(lines: list[str], path: Path) -> None:
    """Save lines as Markdown file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info("Saved Markdown: %s", path)


# ---------------------------------------------------------------------------
# Task 1: Investigate Duplicate Playing Eleven Entries
# ---------------------------------------------------------------------------
def investigate_duplicates(playing_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Identify and analyze all 40 duplicate playing_eleven keys."""
    key_cols = ["match_id", "team_id", "player_id"]

    # Find all rows that are part of duplicate groups
    dup_mask = playing_df.duplicated(subset=key_cols, keep=False)
    dup_rows = playing_df[dup_mask].copy()

    logger.info("Found %d rows involved in duplicates (%d unique keys)",
                len(dup_rows), dup_rows[key_cols].drop_duplicates().shape[0])

    # Analyze each duplicate group
    groups = []
    for _, group in dup_rows.groupby(key_cols):
        group_info = {
            "match_id": int(group["match_id"].iloc[0]),
            "team_id": int(group["team_id"].iloc[0]),
            "player_id": int(group["player_id"].iloc[0]),
            "row_count": len(group),
            "columns_differ": {},
        }

        # Check which columns differ within the group
        for col in playing_df.columns:
            if col in key_cols:
                continue
            unique_vals = group[col].dropna().unique()
            if len(unique_vals) > 1:
                group_info["columns_differ"][col] = [str(v) for v in unique_vals]

        groups.append(group_info)

    # Summary
    exact_dupes = sum(1 for g in groups if not g["columns_differ"])
    conflicting_dupes = sum(1 for g in groups if g["columns_differ"])

    summary = {
        "total_duplicate_rows": int(len(dup_rows)),
        "unique_duplicate_keys": len(groups),
        "exact_duplicate_keys": exact_dupes,
        "conflicting_duplicate_keys": conflicting_dupes,
        "groups": groups,
    }

    return dup_rows, summary


# ---------------------------------------------------------------------------
# Task 2: Delivery Rules Investigation
# ---------------------------------------------------------------------------
def investigate_delivery_rules(bbb_df: pd.DataFrame) -> dict:
    """Investigate how runs, extras, and legal balls should be calculated."""

    results = {}

    # 2.1 Runs column analysis
    logger.info("Analyzing runs column...")
    results["runs"] = {
        "value_counts": bbb_df["runs"].value_counts().to_dict(),
        "min": float(bbb_df["runs"].min()),
        "max": float(bbb_df["runs"].max()),
        "mean": float(bbb_df["runs"].mean()),
    }

    # 2.2 Extras type analysis
    logger.info("Analyzing extras...")
    extras_df = bbb_df[bbb_df["extras_type"].notna()].copy()
    results["extras"] = {
        "total_deliveries_with_extras": int(len(extras_df)),
        "extras_type_counts": extras_df["extras_type"].value_counts().to_dict(),
        "extras1_runs_by_type": extras_df.groupby("extras_type")["extras1_runs"].sum().to_dict(),
        "extras2_runs_by_type": extras_df.groupby("extras_type")["extras_2_runs"].sum().to_dict(),
        "extras1_runs_distribution": extras_df["extras1_runs"].value_counts().to_dict(),
        "extras2_runs_distribution": extras_df["extras_2_runs"].value_counts().to_dict(),
    }

    # 2.3 Cross-tab: runs vs extras_type
    logger.info("Cross-tabulating runs vs extras_type...")
    ct = pd.crosstab(bbb_df["extras_type"].fillna("none"), bbb_df["runs"], margins=True)
    results["runs_vs_extras_crosstab"] = ct.to_dict()

    # 2.4 Legal ball determination
    # Key insight: over_ball_num > 6 indicates wides/no-balls (extra balls)
    # But we should also check: does is_wicket ever occur on over_ball_num > 6?
    logger.info("Analyzing legal ball conventions...")

    legal_balls = bbb_df[bbb_df["over_ball_num"].between(1, 6)]
    extra_balls = bbb_df[bbb_df["over_ball_num"] > 6]

    results["legal_balls"] = {
        "count": int(len(legal_balls)),
        "pct": round(len(legal_balls) / len(bbb_df) * 100, 2),
    }
    results["extra_balls"] = {
        "count": int(len(extra_balls)),
        "pct": round(len(extra_balls) / len(bbb_df) * 100, 2),
        "over_ball_num_distribution": extra_balls["over_ball_num"].value_counts().to_dict(),
        "extras_type_distribution": extra_balls["extras_type"].fillna("none").value_counts().to_dict(),
        "wickets_on_extra_balls": int(extra_balls["is_wicket"].sum()),
        "runs_distribution": extra_balls["runs"].value_counts().to_dict(),
    }

    # 2.5 Wickets on extra balls detail
    wickets_on_extras = extra_balls[extra_balls["is_wicket"]]
    if len(wickets_on_extras) > 0:
        results["wickets_on_extra_balls_detail"] = {
            "dismissal_types": wickets_on_extras["dismissal_type"].value_counts().to_dict(),
            "extras_types": wickets_on_extras["extras_type"].fillna("none").value_counts().to_dict(),
        }

    # 2.6 Innings ball numbering
    results["innings_ball_num"] = {
        "max": int(bbb_df["innings_ball_num"].max()),
        "mean": float(bbb_df["innings_ball_num"].mean()),
    }

    # 2.7 Check: runs = batter_runs + extras1_runs + extras_2_runs?
    # We need to understand what 'runs' represents
    logger.info("Testing runs decomposition...")
    # For deliveries with extras, check if runs == extras1 + extras2 (batter scored 0)
    # or runs > extras1 + extras2 (batter scored runs + extras)
    extras_deliveries = bbb_df[bbb_df["extras_type"].notna()].copy()
    extras_deliveries["total_extras"] = extras_deliveries["extras1_runs"] + extras_deliveries["extras_2_runs"]
    extras_deliveries["batter_runs_implied"] = extras_deliveries["runs"] - extras_deliveries["total_extras"]

    results["runs_decomposition"] = {
        "deliveries_with_extras": int(len(extras_deliveries)),
        "batter_runs_implied_distribution": extras_deliveries["batter_runs_implied"].value_counts().to_dict(),
        "cases_batter_runs_negative": int((extras_deliveries["batter_runs_implied"] < 0).sum()),
        "cases_batter_runs_zero": int((extras_deliveries["batter_runs_implied"] == 0).sum()),
        "cases_batter_runs_positive": int((extras_deliveries["batter_runs_implied"] > 0).sum()),
    }

    # 2.8 For non-extras deliveries, runs = batter runs
    non_extras = bbb_df[bbb_df["extras_type"].isna()].copy()
    results["non_extras_runs"] = {
        "count": int(len(non_extras)),
        "runs_distribution": non_extras["runs"].value_counts().to_dict(),
    }

    # 2.9 Over/ball structure validation
    results["over_structure"] = {
        "max_overid": int(bbb_df["overid"].max()),
        "overid_distribution": bbb_df["overid"].value_counts().head(20).to_dict(),
        "balls_per_over_legal": legal_balls.groupby(["match_id", "innings", "overid"]).size().value_counts().to_dict(),
    }

    return results


# ---------------------------------------------------------------------------
# Task 3: Wicket Attribution Rules
# ---------------------------------------------------------------------------
def investigate_wickets(bbb_df: pd.DataFrame) -> dict:
    """Investigate which dismissals count against the bowler."""

    wickets = bbb_df[bbb_df["is_wicket"]].copy()

    results = {
        "total_wickets": int(len(wickets)),
        "dismissal_type_counts": wickets["dismissal_type"].value_counts().to_dict(),
        "dismissal_type_id_counts": wickets["dismissal_type_id"].value_counts().to_dict(),
    }

    # Standard cricket rules:
    # Bowler gets credit: Bowled, Caught, LBW, Stumped, Hit Wicket, Obstructing the field
    # Bowler does NOT get credit: Run Out, Retired Out
    # (Retired hurt/out is not a bowler's wicket)

    bowler_credit_types = ["Bowled", "Caught", "LBW", "Stump", "Hit Wicket", "Obstructing the field", "Obstracting the field"]
    not_bowler_credit_types = ["RunOut", "Retire Out"]

    wickets["bowler_credit"] = wickets["dismissal_type"].apply(
        lambda x: "yes" if x in bowler_credit_types else ("no" if x in not_bowler_credit_types else "unknown")
    )

    results["bowler_credit_breakdown"] = wickets["bowler_credit"].value_counts().to_dict()

    # Check unknown types
    unknown = wickets[wickets["bowler_credit"] == "unknown"]
    if len(unknown) > 0:
        results["unknown_dismissal_types"] = unknown["dismissal_type"].unique().tolist()

    # Wickets by extras type
    results["wickets_by_extras_type"] = wickets["extras_type"].fillna("none").value_counts().to_dict()

    # Wickets on extra balls (over_ball_num > 6)
    wickets_extra_balls = wickets[wickets["over_ball_num"] > 6]
    results["wickets_on_extra_balls"] = {
        "count": int(len(wickets_extra_balls)),
        "dismissal_types": wickets_extra_balls["dismissal_type"].value_counts().to_dict(),
        "extras_types": wickets_extra_balls["extras_type"].fillna("none").value_counts().to_dict(),
    }

    # Dismissed player vs striker/non-striker
    wickets["dismissed_is_striker"] = wickets["dismissed_player_id"] == wickets["striker_id"]
    wickets["dismissed_is_non_striker"] = wickets["dismissed_player_id"] == wickets["non_striker_id"]
    results["dismissed_player_role"] = {
        "striker": int(wickets["dismissed_is_striker"].sum()),
        "non_striker": int(wickets["dismissed_is_non_striker"].sum()),
        "other": int((~wickets["dismissed_is_striker"] & ~wickets["dismissed_is_non_striker"]).sum()),
    }

    return results


# ---------------------------------------------------------------------------
# Task 4: Missing Ball-by-Ball Matches
# ---------------------------------------------------------------------------
def investigate_missing_matches(matches_df: pd.DataFrame, bbb_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Identify the 16 matches missing ball-by-ball data."""

    match_ids_in_matches = set(matches_df["match_id"].dropna().astype(int).unique())
    match_ids_in_bbb = set(bbb_df["match_id"].dropna().astype(int).unique())
    missing_ids = match_ids_in_matches - match_ids_in_bbb

    logger.info("Found %d matches missing ball-by-ball data", len(missing_ids))

    # Get full match details for missing matches
    missing_matches = matches_df[matches_df["match_id"].isin(missing_ids)].copy()

    # Add competition info
    comp_df = load_csv(RAW_DIR / "competitions.csv")
    missing_matches = missing_matches.merge(comp_df[["comp_id", "comp_name", "match_format", "season"]],
                                             on="comp_id", how="left")

    summary = {
        "count": len(missing_matches),
        "match_ids": sorted(missing_ids),
        "by_competition": missing_matches["comp_name"].value_counts().to_dict(),
        "by_format": missing_matches["match_format"].value_counts().to_dict(),
        "by_season": missing_matches["season"].value_counts().to_dict(),
        "stages": missing_matches["stage"].value_counts().to_dict(),
        "results": missing_matches["result"].value_counts().head(20).to_dict(),
        "recommendation": "Exclude from delivery-based rankings (no delivery data available). "
                          "May include in match-level aggregates if result is known.",
    }

    return missing_matches, summary


# ---------------------------------------------------------------------------
# Task 5: Competition Scope Verification
# ---------------------------------------------------------------------------
def investigate_competition_scope(
    comp_df: pd.DataFrame,
    matches_df: pd.DataFrame,
    bbb_df: pd.DataFrame,
    teams_df: pd.DataFrame
) -> dict:
    """Verify IPL and T20I competitions, report implications."""

    # IPL competitions (5)
    ipl_comps = comp_df[comp_df["comp_name"].str.contains("IPL", case=False, na=False)]

    # T20I competitions (134)
    t20i_comps = comp_df[comp_df["match_format"] == "T20I"]

    # Other T20 (non-IPL, non-T20I)
    other_t20_comps = comp_df[
        (comp_df["match_format"] == "T20") &
        (~comp_df["comp_name"].str.contains("IPL", case=False, na=False))
    ]

    # Get match counts per competition
    match_counts = matches_df.groupby("comp_id").size().reset_index(name="match_count")
    bbb_match_counts = bbb_df.groupby("match_id").size().reset_index(name="delivery_count")
    bbb_match_counts = bbb_match_counts.merge(matches_df[["match_id", "comp_id"]], on="match_id")
    bbb_comp_deliveries = bbb_match_counts.groupby("comp_id")["delivery_count"].sum().reset_index()

    # Merge with competitions
    ipl_detail = ipl_comps.merge(match_counts, on="comp_id", how="left")
    ipl_detail = ipl_detail.merge(bbb_comp_deliveries, on="comp_id", how="left")
    ipl_detail["match_count"] = ipl_detail["match_count"].fillna(0).astype(int)
    ipl_detail["delivery_count"] = ipl_detail["delivery_count"].fillna(0).astype(int)

    t20i_detail = t20i_comps.merge(match_counts, on="comp_id", how="left")
    t20i_detail = t20i_detail.merge(bbb_comp_deliveries, on="comp_id", how="left")
    t20i_detail["match_count"] = t20i_detail["match_count"].fillna(0).astype(int)
    t20i_detail["delivery_count"] = t20i_detail["delivery_count"].fillna(0).astype(int)

    other_t20_detail = other_t20_comps.merge(match_counts, on="comp_id", how="left")
    other_t20_detail = other_t20_detail.merge(bbb_comp_deliveries, on="comp_id", how="left")
    other_t20_detail["match_count"] = other_t20_detail["match_count"].fillna(0).astype(int)
    other_t20_detail["delivery_count"] = other_t20_detail["delivery_count"].fillna(0).astype(int)

    # Team types in IPL vs T20I
    ipl_matches = matches_df[matches_df["comp_id"].isin(ipl_comps["comp_id"])]
    t20i_matches = matches_df[matches_df["comp_id"].isin(t20i_comps["comp_id"])]

    ipl_teams = set(ipl_matches["home_team_id"].unique()) | set(ipl_matches["away_team_id"].unique())
    t20i_teams = set(t20i_matches["home_team_id"].unique()) | set(t20i_matches["away_team_id"].unique())

    ipl_team_names = teams_df[teams_df["team_id"].isin(ipl_teams)][["team_id", "team_name"]].drop_duplicates()
    t20i_team_names = teams_df[teams_df["team_id"].isin(t20i_teams)][["team_id", "team_name"]].drop_duplicates()

    results = {
        "ipl_competitions": ipl_detail[["comp_id", "comp_name", "match_format", "season", "match_count", "delivery_count"]].to_dict("records"),
        "ipl_total_matches": int(ipl_detail["match_count"].sum()),
        "ipl_total_deliveries": int(ipl_detail["delivery_count"].sum()),
        "ipl_teams": ipl_team_names.to_dict("records"),
        "t20i_competitions_count": len(t20i_comps),
        "t20i_total_matches": int(t20i_detail["match_count"].sum()),
        "t20i_total_deliveries": int(t20i_detail["delivery_count"].sum()),
        "t20i_teams_sample": t20i_team_names.head(20).to_dict("records"),
        "other_t20_competitions": other_t20_detail[["comp_id", "comp_name", "match_format", "season", "match_count", "delivery_count"]].to_dict("records"),
        "implications": {
            "ipl_only": {
                "description": "Franchise T20 only, consistent playing conditions, same teams each season",
                "matches": int(ipl_detail["match_count"].sum()),
                "deliveries": int(ipl_detail["delivery_count"].sum()),
                "seasons": 5,
                "teams": len(ipl_teams),
                "pros": ["Consistent format", "Same teams", "High quality", "Pressure contexts well-defined"],
                "cons": ["Small sample per player per season", "Only 5 seasons", "No international pressure"],
            },
            "ipl_plus_t20i": {
                "description": "Franchise + International T20, broader pressure contexts",
                "matches": int(ipl_detail["match_count"].sum()) + int(t20i_detail["match_count"].sum()),
                "deliveries": int(ipl_detail["delivery_count"].sum()) + int(t20i_detail["delivery_count"].sum()),
                "seasons": "5 IPL + multiple T20I years",
                "teams": len(ipl_teams | t20i_teams),
                "pros": ["Larger sample", "International pressure", "Different conditions", "More players"],
                "cons": ["Different playing conditions", "Variable opposition quality", "Home/away bias", "Squad rotation in T20I"],
            },
            "recommendation": "Use IPL+T20I for primary analysis with competition_type as a feature. "
                              "Report IPL-only as a sensitivity check. Exclude other T20 (Emerging Teams, Rising Stars) "
                              "as they are development tournaments with different pressure profiles.",
        },
    }

    return results


# ---------------------------------------------------------------------------
# Task 6: Player Identity Joins
# ---------------------------------------------------------------------------
def investigate_player_identity(
    mapping_df: pd.DataFrame,
    playing_df: pd.DataFrame,
    bbb_df: pd.DataFrame,
    teams_df: pd.DataFrame
) -> dict:
    """Verify joins between player mapping, playing_eleven, and ball-by-ball IDs."""

    # Unique player IDs in each source
    mapping_players = set(mapping_df["player_id"].unique())
    playing_players = set(playing_df["player_id"].unique())
    bbb_batters = set(bbb_df["striker_id"].unique()) | set(bbb_df["non_striker_id"].unique())
    bbb_bowlers = set(bbb_df["bowler_id"].unique())
    bbb_all = bbb_batters | bbb_bowlers

    results = {
        "unique_players": {
            "competition_team_player_mapping": len(mapping_players),
            "playing_eleven": len(playing_players),
            "ball_by_ball_batters": len(bbb_batters),
            "ball_by_ball_bowlers": len(bbb_bowlers),
            "ball_by_ball_all": len(bbb_all),
        },
        "overlap": {
            "mapping_and_playing": len(mapping_players & playing_players),
            "mapping_and_bbb": len(mapping_players & bbb_all),
            "playing_and_bbb": len(playing_players & bbb_all),
            "all_three": len(mapping_players & playing_players & bbb_all),
        },
        "only_in_mapping": len(mapping_players - playing_players - bbb_all),
        "only_in_playing": len(playing_players - mapping_players - bbb_all),
        "only_in_bbb": len(bbb_all - mapping_players - playing_players),
        "in_bbb_not_in_mapping_or_playing": sorted(list(bbb_all - mapping_players - playing_players))[:20],
    }

    # Check player name consistency across sources
    # mapping: player_id -> player_name
    # playing_eleven: player_id (no name)
    # ball_by_ball: striker_id -> striker_name, bowler_id -> bowler_name

    # Create name maps
    mapping_names = mapping_df.drop_duplicates("player_id").set_index("player_id")["player_name"]
    bbb_striker_names = bbb_df.drop_duplicates("striker_id").set_index("striker_id")["striker_name"]
    bbb_bowler_names = bbb_df.drop_duplicates("bowler_id").set_index("bowler_id")["bowler_name"]

    # Compare names for overlapping IDs
    overlap_ids = mapping_players & bbb_all
    name_mismatches = []
    for pid in overlap_ids:
        m_name = mapping_names.get(pid)
        b_name = bbb_striker_names.get(pid) or bbb_bowler_names.get(pid)
        if m_name and b_name and m_name != b_name:
            name_mismatches.append({
                "player_id": int(pid),
                "mapping_name": str(m_name),
                "bbb_name": str(b_name),
            })

    results["name_mismatches"] = name_matches[:50] if (name_matches := name_mismatches) else []
    results["name_mismatch_count"] = len(name_matches) if name_matches else 0

    # Check for duplicate player_ids with different names in mapping
    mapping_dup_names = mapping_df.groupby("player_id")["player_name"].nunique()
    mapping_multi_name = mapping_dup_names[mapping_dup_names > 1]
    results["mapping_multiple_names_per_id"] = mapping_multi_name.to_dict()

    # Check for same name, different IDs in mapping
    mapping_name_ids = mapping_df.groupby("player_name")["player_id"].nunique()
    mapping_multi_id = mapping_name_ids[mapping_name_ids > 1]
    results["mapping_multiple_ids_per_name"] = mapping_multi_id.head(20).to_dict()

    return results


# ---------------------------------------------------------------------------
# Main Validation Pipeline
# ---------------------------------------------------------------------------
def run_validation() -> dict:
    """Run all validation investigations."""
    logger.info("=" * 60)
    logger.info("Starting SupeRR Selector Season 2 Data Validation")
    logger.info("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load all data
    logger.info("Loading all CSV files...")
    comp_df = load_csv(RAW_DIR / "competitions.csv")
    teams_df = load_csv(RAW_DIR / "teams.csv")
    matches_df = load_csv(RAW_DIR / "matches.csv")
    bbb_df = load_csv(RAW_DIR / "ball_by_ball.csv")
    mapping_df = load_csv(RAW_DIR / "competition_team_player_mapping.csv")
    playing_df = load_csv(RAW_DIR / "playing_eleven.csv")

    all_results = {}

    # Task 1: Duplicates
    logger.info("Task 1: Investigating duplicate playing_eleven entries...")
    dup_rows, dup_summary = investigate_duplicates(playing_df)
    save_csv(dup_rows, OUTPUT_DIR / "duplicate_playing_eleven_review.csv")
    all_results["duplicates"] = dup_summary

    # Task 2: Delivery Rules
    logger.info("Task 2: Investigating delivery rules...")
    delivery_rules = investigate_delivery_rules(bbb_df)
    all_results["delivery_rules"] = delivery_rules

    # Task 3: Wickets
    logger.info("Task 3: Investigating wicket attribution...")
    wicket_rules = investigate_wickets(bbb_df)
    all_results["wicket_rules"] = wicket_rules

    # Task 4: Missing Matches
    logger.info("Task 4: Investigating missing ball-by-ball matches...")
    missing_matches_df, missing_summary = investigate_missing_matches(matches_df, bbb_df)
    save_csv(missing_matches_df, OUTPUT_DIR / "missing_ball_by_ball_matches.csv")
    all_results["missing_matches"] = missing_summary

    # Task 5: Competition Scope
    logger.info("Task 5: Investigating competition scope...")
    comp_scope = investigate_competition_scope(comp_df, matches_df, bbb_df, teams_df)
    all_results["competition_scope"] = comp_scope

    # Task 6: Player Identity
    logger.info("Task 6: Investigating player identity joins...")
    player_identity = investigate_player_identity(mapping_df, playing_df, bbb_df, teams_df)
    all_results["player_identity"] = player_identity

    # Save machine-readable summary
    save_json(all_results, OUTPUT_DIR / "delivery_rules_summary.json")

    # Generate Markdown report
    logger.info("Generating validation report...")
    generate_validation_report(all_results, OUTPUT_DIR / "data_validation_report.md")

    logger.info("=" * 60)
    logger.info("Validation complete. Outputs saved to %s", OUTPUT_DIR)
    logger.info("=" * 60)

    return all_results


def generate_validation_report(results: dict, path: Path) -> None:
    """Generate human-readable validation report."""
    lines = [
        "# Data Validation Report - SupeRR Selector Season 2",
        "",
        f"Generated: {pd.Timestamp.now().isoformat()}",
        "",
        "## 1. Duplicate Playing Eleven Entries",
        "",
        f"- Total duplicate rows: {results['duplicates']['total_duplicate_rows']}",
        f"- Unique duplicate keys (match_id, team_id, player_id): {results['duplicates']['unique_duplicate_keys']}",
        f"- Exact duplicates (all columns same): {results['duplicates']['exact_duplicate_keys']}",
        f"- Conflicting duplicates (some columns differ): {results['duplicates']['conflicting_duplicate_keys']}",
        "",
    ]

    if results['duplicates']['conflicting_duplicate_keys'] > 0:
        lines.append("### Conflicting Duplicate Groups")
        lines.append("")
        for g in results['duplicates']['groups']:
            if g['columns_differ']:
                lines.append(f"- Match {g['match_id']}, Team {g['team_id']}, Player {g['player_id']}: "
                             f"Differing columns: {list(g['columns_differ'].keys())}")
                for col, vals in g['columns_differ'].items():
                    lines.append(f"  - {col}: {vals}")
        lines.append("")

    lines.extend([
        "## 2. Delivery Rules Investigation",
        "",
        "### Runs Column",
        f"- Range: {results['delivery_rules']['runs']['min']} to {results['delivery_rules']['runs']['max']}",
        f"- Mean: {results['delivery_rules']['runs']['mean']:.3f}",
        f"- Value counts: {results['delivery_rules']['runs']['value_counts']}",
        "",
        "### Extras Analysis",
        f"- Deliveries with extras: {results['delivery_rules']['extras']['total_deliveries_with_extras']}",
        f"- Extras types: {results['delivery_rules']['extras']['extras_type_counts']}",
        f"- Extras1 runs by type: {results['delivery_rules']['extras']['extras1_runs_by_type']}",
        f"- Extras2 runs by type: {results['delivery_rules']['extras']['extras2_runs_by_type']}",
        "",
        "### Runs vs Extras Cross-tabulation (sample)",
        f"- See delivery_rules_summary.json for full table",
        "",
        "### Legal Ball Convention",
        f"- Legal balls (over_ball_num 1-6): {results['delivery_rules']['legal_balls']['count']} ({results['delivery_rules']['legal_balls']['pct']}%)",
        f"- Extra balls (over_ball_num >6): {results['delivery_rules']['extra_balls']['count']} ({results['delivery_rules']['extra_balls']['pct']}%)",
        f"- Extra balls over_ball_num distribution: {results['delivery_rules']['extra_balls']['over_ball_num_distribution']}",
        f"- Extra balls extras_type: {results['delivery_rules']['extra_balls']['extras_type_distribution']}",
        f"- Wickets on extra balls: {results['delivery_rules']['extra_balls']['wickets_on_extra_balls']}",
        "",
        "### Runs Decomposition (for deliveries with extras)",
        f"- Total extras deliveries analyzed: {results['delivery_rules']['runs_decomposition']['deliveries_with_extras']}",
        f"- Implied batter runs = runs - (extras1 + extras2)",
        f"- Batter runs implied distribution: {results['delivery_rules']['runs_decomposition']['batter_runs_implied_distribution']}",
        f"- Cases batter runs < 0: {results['delivery_rules']['runs_decomposition']['cases_batter_runs_negative']}",
        f"- Cases batter runs = 0: {results['delivery_rules']['runs_decomposition']['cases_batter_runs_zero']}",
        f"- Cases batter runs > 0: {results['delivery_rules']['runs_decomposition']['cases_batter_runs_positive']}",
        "",
        "### Non-Extras Deliveries",
        f"- Count: {results['delivery_rules']['non_extras_runs']['count']}",
        f"- Runs distribution: {results['delivery_rules']['non_extras_runs']['runs_distribution']}",
        "",
        "### Key Finding: Runs Column Interpretation",
        "- For non-extras deliveries: `runs` = batter runs (0, 1, 2, 3, 4, 6)",
        "- For extras deliveries: `runs` = total runs on delivery (batter runs + extras)",
        "- `extras1_runs` = wides/no-balls runs + byes/legbyes/penalty runs",
        "- `extras_2_runs` = additional penalty runs (rare)",
        "- Batter runs on extras delivery = `runs - extras1_runs - extras_2_runs`",
        "",
        "## 3. Wicket Attribution Rules",
        "",
        f"- Total wickets: {results['wicket_rules']['total_wickets']}",
        f"- Dismissal types: {results['wicket_rules']['dismissal_type_counts']}",
        f"- Bowler credit breakdown: {results['wicket_rules']['bowler_credit_breakdown']}",
        "",
        "### Bowler Gets Credit (Standard Cricket Rules)",
        "- Bowled, Caught, LBW, Stump, Hit Wicket, Obstructing the field",
        "",
        "### Bowler Does NOT Get Credit",
        "- RunOut, Retire Out",
        "",
        f"- Wickets by extras type: {results['wicket_rules']['wickets_by_extras_type']}",
        f"- Wickets on extra balls (over_ball_num > 6): {results['wicket_rules']['wickets_on_extra_balls']['count']}",
        f"  - Dismissal types: {results['wicket_rules']['wickets_on_extra_balls']['dismissal_types']}",
        f"  - Extras types: {results['wicket_rules']['wickets_on_extra_balls']['extras_types']}",
        "",
        f"- Dismissed player role: {results['wicket_rules']['dismissed_player_role']}",
        "",
        "## 4. Missing Ball-by-Ball Matches",
        "",
        f"- Count: {results['missing_matches']['count']}",
        f"- Match IDs: {results['missing_matches']['match_ids']}",
        f"- By competition: {results['missing_matches']['by_competition']}",
        f"- By format: {results['missing_matches']['by_format']}",
        f"- By season: {results['missing_matches']['by_season']}",
        f"- By stage: {results['missing_matches']['stages']}",
        f"- Results: {results['missing_matches']['results']}",
        "",
        f"- **Recommendation**: {results['missing_matches']['recommendation']}",
        "",
        "## 5. Competition Scope",
        "",
        "### IPL Competitions (5)",
        "",
    ])

    for c in results['competition_scope']['ipl_competitions']:
        lines.append(f"- comp_id={c['comp_id']}, {c['comp_name']}, Season {c['season']}: "
                     f"{c['match_count']} matches, {c['delivery_count']} deliveries")

    lines.extend([
        "",
        f"- **IPL Total**: {results['competition_scope']['ipl_total_matches']} matches, "
        f"{results['competition_scope']['ipl_total_deliveries']} deliveries",
        f"- **IPL Teams**: {len(results['competition_scope']['ipl_teams'])} franchise teams",
        "",
        "### T20I Competitions (134)",
        f"- Total matches: {results['competition_scope']['t20i_total_matches']}",
        f"- Total deliveries: {results['competition_scope']['t20i_total_deliveries']}",
        f"- Team sample: {results['competition_scope']['t20i_teams_sample'][:5]} ...",
        "",
        "### Other T20 Competitions (2 - Emerging Teams, Rising Stars)",
        "",
    ])

    for c in results['competition_scope']['other_t20_competitions']:
        lines.append(f"- comp_id={c['comp_id']}, {c['comp_name']}, Season {c['season']}: "
                     f"{c['match_count']} matches, {c['delivery_count']} deliveries")

    lines.extend([
        "",
        "### Implications & Recommendation",
        f"- **IPL Only**: {results['competition_scope']['implications']['ipl_only']}",
        f"- **IPL + T20I**: {results['competition_scope']['implications']['ipl_plus_t20i']}",
        f"- **Recommendation**: {results['competition_scope']['implications']['recommendation']}",
        "",
        "## 6. Player Identity Joins",
        "",
        f"- Unique players in mapping: {results['player_identity']['unique_players']['competition_team_player_mapping']}",
        f"- Unique players in playing_eleven: {results['player_identity']['unique_players']['playing_eleven']}",
        f"- Unique batters in ball_by_ball: {results['player_identity']['unique_players']['ball_by_ball_batters']}",
        f"- Unique bowlers in ball_by_ball: {results['player_identity']['unique_players']['ball_by_ball_bowlers']}",
        f"- Unique all in ball_by_ball: {results['player_identity']['unique_players']['ball_by_ball_all']}",
        "",
        f"- Overlap mapping ∩ playing: {results['player_identity']['overlap']['mapping_and_playing']}",
        f"- Overlap mapping ∩ bbb: {results['player_identity']['overlap']['mapping_and_bbb']}",
        f"- Overlap playing ∩ bbb: {results['player_identity']['overlap']['playing_and_bbb']}",
        f"- Overlap all three: {results['player_identity']['overlap']['all_three']}",
        "",
        f"- Only in mapping: {results['player_identity']['only_in_mapping']}",
        f"- Only in playing: {results['player_identity']['only_in_playing']}",
        f"- Only in ball_by_ball: {results['player_identity']['only_in_bbb']}",
        f"- In ball_by_ball but not mapping/playing (sample): {results['player_identity']['in_bbb_not_in_mapping_or_playing']}",
        "",
        f"- Name mismatches across sources: {results['player_identity']['name_mismatch_count']}",
        "",
    ])

    if results['player_identity']['name_mismatches']:
        lines.append("### Name Mismatches (sample)")
        lines.append("")
        for m in results['player_identity']['name_mismatches'][:10]:
            lines.append(f"- Player {m['player_id']}: mapping='{m['mapping_name']}' vs bbb='{m['bbb_name']}'")
        lines.append("")

    if results['player_identity']['mapping_multiple_names_per_id']:
        lines.append("### Multiple Names per Player ID in Mapping")
        lines.append("")
        for pid, count in results['player_identity']['mapping_multiple_names_per_id'].items():
            lines.append(f"- Player {pid}: {count} different names")
        lines.append("")

    if results['player_identity']['mapping_multiple_ids_per_name']:
        lines.append("### Multiple Player IDs per Name in Mapping")
        lines.append("")
        for name, count in results['player_identity']['mapping_multiple_ids_per_name'].items():
            lines.append(f"- '{name}': {count} different IDs")
        lines.append("")

    lines.extend([
        "## 7. Unresolved Questions & Recommended Modelling Decisions",
        "",
        "### Unresolved Questions",
        "1. **Extras_2_runs**: What do the 84 runs in extras_2_runs represent? (Penalty runs?)",
        "2. **Overstep vs noball**: Is 'Overstep' the only no-ball type? Are there other no-balls?",
        "3. **Innings 3 & 4**: 38 deliveries in innings 3/4 - are these Super Overs? Confirm.",
        "4. **Duplicate playing_eleven**: 40 duplicate keys - are they data entry errors or impact player substitutions?",
        "5. **Missing 16 matches**: Why no ball-by-ball data? Abandoned? Data loss?",
        "6. **Player name mismatches**: Some IDs have different names across sources - which is canonical?",
        "7. **Bowl_speed = -1 or 0**: Missing data indicator or genuine values?",
        "",
        "### Recommended Modelling Decisions",
        "1. **Legal ball definition**: `over_ball_num BETWEEN 1 AND 6` AND `extras_type NOT IN ('wide', 'Overstep')` for strict legal balls. "
           "For bowler economy: count all balls bowled (including wides/no-balls) as balls faced by batter? No - "
           "standard cricket: wides/no-balls count as balls faced by batter but NOT as legal balls for over count.",
        "2. **Batter runs**: `runs - extras1_runs - extras_2_runs` for all deliveries.",
        "3. **Bowling runs conceded**: `runs - extras_2_runs` (bowler not charged for byes/legbyes/penalty). "
           "But charged for wides and no-balls (extras1_runs for wide/Overstep).",
        "4. **Wicket attribution**: Only count dismissals where bowler_credit='yes' for bowler stats. "
           "All dismissals count for batter dismissal record.",
        "5. **Competition scope**: Primary analysis on IPL + T20I. Add `competition_type` feature "
           "('IPL' vs 'T20I'). Exclude 'Mens T20 Emerging Teams Asia Cup 2024' and 'Asia Cup Rising Stars 2025'.",
        "6. **Player identity**: Use `competition_team_player_mapping` as canonical for player names. "
           "Join ball_by_ball on player_id only. Flag name mismatches for manual review.",
        "7. **Missing matches**: Exclude from delivery-based metrics. Include in match-level win/loss if result known.",
        "8. **Duplicate playing_eleven**: For now, deduplicate by keeping first row per key. "
           "Flag for review - may indicate impact player substitutions (IPL 2023+).",
        "",
    ])

    save_markdown(lines, path)


if __name__ == "__main__":
    try:
        run_validation()
        logger.info("SUCCESS: Validation pipeline completed")
    except Exception as e:
        logger.exception("Validation pipeline failed: %s", e)
        sys.exit(1)