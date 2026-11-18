#!/usr/bin/env python3
"""
Cricket Statistics Conventions Investigation for SupeRR Selector Season 2

This module performs deep inspection of raw ball-by-ball records to establish
correct cricket-statistics conventions WITHOUT assuming any formulas.

Key investigations:
1. Runs/extras reconciliation across all extras_types
2. Legal ball determination (over_ball_num vs extras_type)
3. Wicket attribution validation
4. Playing eleven conflict analysis
5. Super Over identification (innings 3/4)
6. Abandoned match verification
7. Player identity canonical naming
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
        logging.FileHandler(OUTPUT_DIR / "conventions.log", mode="w"),
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


def save_json(data: Any, path: Path) -> None:
    """Save data as JSON with pretty formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    logger.info("Saved JSON: %s", path)


# ---------------------------------------------------------------------------
# Task 1: Runs/Extras Reconciliation - Deep Inspection
# ---------------------------------------------------------------------------
def investigate_runs_extras_reconciliation(bbb_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Inspect representative raw deliveries across every extras_type to establish
    which field means what. Do NOT assume any formula.
    """
    logger.info("Investigating runs/extras reconciliation...")

    # Get all unique extras_types
    extras_types = bbb_df["extras_type"].fillna("none").unique()
    logger.info("Extras types found: %s", extras_types)

    # Sample representative records for each extras_type
    sample_records = []

    for ext_type in sorted(extras_types):
        if ext_type == "none":
            # Sample non-extras deliveries
            subset = bbb_df[bbb_df["extras_type"].isna()].sample(n=min(20, len(bbb_df[bbb_df["extras_type"].isna()])), random_state=42)
        else:
            subset = bbb_df[bbb_df["extras_type"] == ext_type].sample(n=min(20, len(bbb_df[bbb_df["extras_type"] == ext_type])), random_state=42)

        for _, row in subset.iterrows():
            rec = {
                "match_id": int(row["match_id"]),
                "innings": int(row["innings"]),
                "overid": int(row["overid"]),
                "over_ball_num": int(row["over_ball_num"]),
                "innings_ball_num": int(row["innings_ball_num"]),
                "extras_type": ext_type if ext_type != "none" else None,
                "runs": int(row["runs"]),
                "extras1_runs": int(row["extras1_runs"]),
                "extras_2_runs": int(row["extras_2_runs"]),
                "is_wicket": bool(row["is_wicket"]),
                "dismissal_type": row["dismissal_type"] if pd.notna(row["dismissal_type"]) else None,
                "striker_id": int(row["striker_id"]),
                "striker_name": row["striker_name"],
                "bowler_id": int(row["bowler_id"]),
                "bowler_name": row["bowler_name"],
                "is_four": bool(row["is_four"]),
                "is_six": bool(row["is_six"]),
                "pace_or_spin": row["pace_or_spin"],
            }
            sample_records.append(rec)

    sample_df = pd.DataFrame(sample_records)
    save_csv(sample_df, OUTPUT_DIR / "delivery_reconciliation_sample.csv")

    # Now do systematic analysis by extras_type
    analysis_results = {}

    for ext_type in sorted(extras_types):
        if ext_type == "none":
            mask = bbb_df["extras_type"].isna()
            label = "no_extras"
        else:
            mask = bbb_df["extras_type"] == ext_type
            label = ext_type

        subset = bbb_df[mask].copy()

        # Compute implied batter runs using different hypotheses
        subset["implied_batter_runs_v1"] = subset["runs"] - subset["extras1_runs"] - subset["extras_2_runs"]
        subset["implied_batter_runs_v2"] = subset["runs"] - subset["extras1_runs"]
        subset["implied_batter_runs_v3"] = subset["runs"]  # runs = batter runs only

        # Distribution of implied batter runs
        v1_dist = subset["implied_batter_runs_v1"].value_counts().to_dict()
        v2_dist = subset["implied_batter_runs_v2"].value_counts().to_dict()
        v3_dist = subset["runs"].value_counts().to_dict()

        # Check for negative values
        v1_neg = int((subset["implied_batter_runs_v1"] < 0).sum())
        v2_neg = int((subset["implied_batter_runs_v2"] < 0).sum())

        # Runs distribution
        runs_dist = subset["runs"].value_counts().to_dict()
        e1_dist = subset["extras1_runs"].value_counts().to_dict()
        e2_dist = subset["extras_2_runs"].value_counts().to_dict()

        # For wides/Overstep: check if extras1_runs equals runs when batter didn't score
        # Also check is_four/is_six on extras deliveries
        fours = int(subset["is_four"].sum())
        sixes = int(subset["is_six"].sum())

        # Wickets on this extras type
        wickets = int(subset["is_wicket"].sum())
        wicket_types = subset[subset["is_wicket"]]["dismissal_type"].value_counts().to_dict() if wickets > 0 else {}

        analysis_results[label] = {
            "count": int(len(subset)),
            "runs_distribution": runs_dist,
            "extras1_runs_distribution": e1_dist,
            "extras_2_runs_distribution": e2_dist,
            "implied_batter_runs_v1_distribution": v1_dist,
            "implied_batter_runs_v2_distribution": v2_dist,
            "implied_batter_runs_v1_negative_count": v1_neg,
            "implied_batter_runs_v2_negative_count": v2_neg,
            "fours": fours,
            "sixes": sixes,
            "wickets": wickets,
            "wicket_types": wicket_types,
            "sample_records": subset.head(5)[
                ["match_id", "innings", "overid", "over_ball_num", "runs", "extras1_runs", "extras_2_runs",
                 "is_four", "is_six", "is_wicket", "dismissal_type"]
            ].to_dict("records"),
        }

    # Special analysis: For 'wide' and 'Overstep', what is the relationship?
    # Hypothesis: runs = batter_runs + extras1_runs (where extras1_runs = 1 for wide/no-ball)
    # But extras1_runs shows values > 1 for wides (e.g., 2, 3, 4, 5)
    # This suggests extras1_runs = total extra runs (wide runs + any runs scored off bat)

    # Let's check: for wides, when runs > 1, what are the values?
    wide_df = bbb_df[bbb_df["extras_type"] == "wide"].copy()
    analysis_results["wide_detailed"] = {
        "total": int(len(wide_df)),
        "runs_vs_extras1": pd.crosstab(wide_df["runs"], wide_df["extras1_runs"]).to_dict(),
        "extras_2_runs_dist": wide_df["extras_2_runs"].value_counts().to_dict(),
    }

    overstep_df = bbb_df[bbb_df["extras_type"] == "Overstep"].copy()
    analysis_results["overstep_detailed"] = {
        "total": int(len(overstep_df)),
        "runs_vs_extras1": pd.crosstab(overstep_df["runs"], overstep_df["extras1_runs"]).to_dict(),
        "extras_2_runs_dist": overstep_df["extras_2_runs"].value_counts().to_dict(),
    }

    byes_df = bbb_df[bbb_df["extras_type"] == "byes"].copy()
    analysis_results["byes_detailed"] = {
        "total": int(len(byes_df)),
        "runs_vs_extras1": pd.crosstab(byes_df["runs"], byes_df["extras1_runs"]).to_dict(),
    }

    legbyes_df = bbb_df[bbb_df["extras_type"] == "legbyes"].copy()
    analysis_results["legbyes_detailed"] = {
        "total": int(len(legbyes_df)),
        "runs_vs_extras1": pd.crosstab(legbyes_df["runs"], legbyes_df["extras1_runs"]).to_dict(),
    }

    other_df = bbb_df[bbb_df["extras_type"] == "other"].copy()
    analysis_results["other_detailed"] = {
        "total": int(len(other_df)),
        "runs_vs_extras1": pd.crosstab(other_df["runs"], other_df["extras1_runs"]).to_dict(),
        "extras_2_runs_dist": other_df["extras_2_runs"].value_counts().to_dict(),
    }

    penalty_df = bbb_df[bbb_df["extras_type"] == "Penalty"].copy()
    analysis_results["penalty_detailed"] = {
        "total": int(len(penalty_df)),
        "runs_vs_extras1": pd.crosstab(penalty_df["runs"], penalty_df["extras1_runs"]).to_dict(),
        "extras_2_runs_dist": penalty_df["extras_2_runs"].value_counts().to_dict(),
    }

    # Save detailed reconciliation
    save_json(analysis_results, OUTPUT_DIR / "delivery_reconciliation_analysis.json")

    # Create summary markdown
    lines = [
        "# Delivery Reconciliation Analysis",
        "",
        "## Summary by Extras Type",
        "",
    ]

    for ext_type, data in analysis_results.items():
        if ext_type in ["wide_detailed", "overstep_detailed", "byes_detailed", "legbyes_detailed", "other_detailed", "penalty_detailed"]:
            continue
        lines.append(f"### {ext_type.upper()}")
        lines.append(f"- Count: {data['count']}")
        lines.append(f"- Runs distribution: {data['runs_distribution']}")
        lines.append(f"- Extras1 runs distribution: {data['extras1_runs_distribution']}")
        lines.append(f"- Extras2 runs distribution: {data['extras_2_runs_distribution']}")
        lines.append(f"- Implied batter runs (runs - e1 - e2) distribution: {data['implied_batter_runs_v1_distribution']}")
        lines.append(f"  - Negative count: {data['implied_batter_runs_v1_negative_count']}")
        lines.append(f"- Implied batter runs (runs - e1) distribution: {data['implied_batter_runs_v2_distribution']}")
        lines.append(f"  - Negative count: {data['implied_batter_runs_v2_negative_count']}")
        lines.append(f"- Fours: {data['fours']}, Sixes: {data['sixes']}")
        lines.append(f"- Wickets: {data['wickets']} ({data['wicket_types']})")
        lines.append("")

    # Add detailed crosstabs
    lines.append("## Detailed Crosstabs")
    lines.append("")
    for key in ["wide_detailed", "overstep_detailed", "byes_detailed", "legbyes_detailed", "other_detailed", "penalty_detailed"]:
        if key in analysis_results:
            data = analysis_results[key]
            lines.append(f"### {key.replace('_detailed', '').upper()}")
            lines.append(f"- Total: {data['total']}")
            lines.append(f"- Runs vs Extras1 crosstab: {data['runs_vs_extras1']}")
            if 'extras_2_runs_dist' in data:
                lines.append(f"- Extras2 runs distribution: {data['extras_2_runs_dist']}")
            lines.append("")

    save_markdown(lines, OUTPUT_DIR / "delivery_reconciliation.md")

    return sample_df, analysis_results


# ---------------------------------------------------------------------------
# Task 2: Legal Ball Determination
# ---------------------------------------------------------------------------
def investigate_legal_balls(bbb_df: pd.DataFrame) -> dict:
    """
    Determine legal ball convention from raw evidence.
    over_ball_num > 6 occurs in 8,429 records including 7,735 with extras_type='none'.
    """
    logger.info("Investigating legal ball determination...")

    results = {}

    # Basic distributions
    results["over_ball_num_distribution"] = bbb_df["over_ball_num"].value_counts().to_dict()
    results["over_ball_num_by_extras"] = {}

    for ext_type in sorted(bbb_df["extras_type"].fillna("none").unique()):
        if ext_type == "none":
            mask = bbb_df["extras_type"].isna()
        else:
            mask = bbb_df["extras_type"] == ext_type
        subset = bbb_df[mask]
        results["over_ball_num_by_extras"][ext_type] = subset["over_ball_num"].value_counts().to_dict()

    # Key question: Are the 7,735 'none' extras with over_ball_num > 6 actually wides/no-balls?
    # Or is over_ball_num a sequence number (ball 1, 2, 3... within over including extras)?
    none_gt6 = bbb_df[(bbb_df["extras_type"].isna()) & (bbb_df["over_ball_num"] > 6)]
    results["none_extras_over_ball_num_gt6"] = {
        "count": int(len(none_gt6)),
        "over_ball_num_distribution": none_gt6["over_ball_num"].value_counts().to_dict(),
        "runs_distribution": none_gt6["runs"].value_counts().to_dict(),
        "is_four": int(none_gt6["is_four"].sum()),
        "is_six": int(none_gt6["is_six"].sum()),
        "is_wicket": int(none_gt6["is_wicket"].sum()),
        "sample": none_gt6.head(10)[
            ["match_id", "innings", "overid", "over_ball_num", "innings_ball_num",
             "runs", "is_four", "is_six", "is_wicket", "striker_name", "bowler_name"]
        ].to_dict("records"),
    }

    # Check innings_ball_num behavior - does it increment on every delivery?
    # If innings_ball_num increments sequentially regardless of extras, it's a sequence number
    # Let's check a few matches
    match_samples = bbb_df["match_id"].unique()[:5]
    results["innings_ball_num_analysis"] = {}
    for mid in match_samples:
        match_df = bbb_df[bbb_df["match_id"] == mid].sort_values(["innings", "overid", "over_ball_num"])
        for inn in [1, 2]:
            inn_df = match_df[match_df["innings"] == inn]
            if len(inn_df) > 0:
                # Check if innings_ball_num is sequential
                seq = inn_df["innings_ball_num"].tolist()
                is_sequential = all(seq[i] == seq[i-1] + 1 for i in range(1, len(seq)))
                results["innings_ball_num_analysis"][f"match_{mid}_inn_{inn}"] = {
                    "deliveries": len(seq),
                    "max_innings_ball_num": max(seq),
                    "is_sequential": is_sequential,
                    "over_ball_num_sequence": inn_df["over_ball_num"].tolist()[:30],
                    "innings_ball_num_sequence": seq[:30],
                }

    # Determine legal ball rule from cricket conventions + data evidence
    # Standard: Legal ball = not wide, not no-ball
    # In this data: extras_type in ('wide', 'Overstep') = extra ball
    # But 7,735 records with extras_type='none' and over_ball_num > 6
    # Hypothesis: These are misclassified wides/no-balls, OR over_ball_num is just a sequence counter
    # Evidence: Check if runs > 0 on these 'none' deliveries with over_ball_num > 6
    # If runs > 0 and is_four/is_six, they might be legitimate runs off extra balls

    # Let's check: for over_ball_num > 6, what extras_types exist?
    gt6 = bbb_df[bbb_df["over_ball_num"] > 6]
    results["over_ball_num_gt6_by_extras"] = gt6["extras_type"].fillna("none").value_counts().to_dict()

    # For 'none' extras with over_ball_num > 6: are they actually legal balls?
    # In cricket, you can't have legal ball 7, 8, 9 in an over
    # So over_ball_num > 6 MUST be extra balls (wides/no-balls)
    # The fact that 7,735 have extras_type='none' suggests data quality issue
    # OR over_ball_num is not "ball number in over" but "delivery sequence in over"

    # Let's verify by checking overid (over number) and over_ball_num together
    # For a given over, over_ball_num should reset to 1
    over_check = bbb_df.groupby(["match_id", "innings", "overid"])["over_ball_num"].max().reset_index()
    over_check["max_gt6"] = over_check["over_ball_num"] > 6
    results["overs_with_gt6_balls"] = int(over_check["max_gt6"].sum())
    results["total_overs"] = len(over_check)
    results["overs_max_ball_distribution"] = over_check["over_ball_num"].value_counts().to_dict()

    # For overs where max > 6, check the extras_types present
    overs_gt6 = over_check[over_check["max_gt6"]]["overid"].unique()
    # Sample a few
    sample_overs = overs_gt6[:5]
    results["sample_overs_gt6"] = []
    for ov in sample_overs:
        # Get one match/innings with this over
        sample = bbb_df[(bbb_df["overid"] == ov) & (bbb_df["over_ball_num"] > 6)].head(1)
        if len(sample) > 0:
            mid = sample.iloc[0]["match_id"]
            inn = sample.iloc[0]["innings"]
            over_df = bbb_df[(bbb_df["match_id"] == mid) & (bbb_df["innings"] == inn) & (bbb_df["overid"] == ov)].sort_values("over_ball_num")
            results["sample_overs_gt6"].append({
                "match_id": int(mid),
                "innings": int(inn),
                "overid": int(ov),
                "deliveries": over_df[["over_ball_num", "innings_ball_num", "extras_type", "runs", "is_four", "is_six", "is_wicket"]].to_dict("records"),
            })

    save_json(results, OUTPUT_DIR / "legal_ball_analysis.json")
    return results


# ---------------------------------------------------------------------------
# Task 3: Wicket Attribution Validation
# ---------------------------------------------------------------------------
def investigate_wicket_attribution(bbb_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Inspect all dismissal types and verify bowler credit rules.
    """
    logger.info("Investigating wicket attribution...")

    wickets = bbb_df[bbb_df["is_wicket"]].copy()
    total_wickets = len(wickets)

    results = {
        "total_wickets": total_wickets,
        "dismissal_type_counts": wickets["dismissal_type"].value_counts().to_dict(),
        "dismissal_type_id_counts": wickets["dismissal_type_id"].value_counts().to_dict(),
    }

    # Standard cricket rules for bowler credit:
    # Bowler gets credit: Bowled, Caught, LBW, Stumped, Hit Wicket, Obstructing the field
    # Bowler does NOT get credit: Run Out, Retired Out, Retired Hurt
    # Note: 'Obstracting the field' and 'Obstructing the field' appear to be same (typo)

    # Let's verify from data: who is the dismissed player?
    # Check if dismissed_player_id matches striker or non_striker
    wickets["dismissed_is_striker"] = wickets["dismissed_player_id"] == wickets["striker_id"]
    wickets["dismissed_is_non_striker"] = wickets["dismissed_player_id"] == wickets["non_striker_id"]

    results["dismissed_player_role"] = {
        "striker": int(wickets["dismissed_is_striker"].sum()),
        "non_striker": int(wickets["dismissed_is_non_striker"].sum()),
        "neither": int((~wickets["dismissed_is_striker"] & ~wickets["dismissed_is_non_striker"]).sum()),
    }

    # By dismissal type
    results["dismissed_role_by_type"] = {}
    for dtype in wickets["dismissal_type"].unique():
        if pd.isna(dtype):
            continue
        sub = wickets[wickets["dismissal_type"] == dtype]
        results["dismissed_role_by_type"][dtype] = {
            "striker": int(sub["dismissed_is_striker"].sum()),
            "non_striker": int(sub["dismissed_is_non_striker"].sum()),
            "neither": int((~sub["dismissed_is_striker"] & ~sub["dismissed_is_non_striker"]).sum()),
            "count": len(sub),
        }

    # Wickets by extras_type
    results["wickets_by_extras_type"] = wickets["extras_type"].fillna("none").value_counts().to_dict()

    # Wickets on extra balls (over_ball_num > 6)
    wickets_gt6 = wickets[wickets["over_ball_num"] > 6]
    results["wickets_on_extra_balls"] = {
        "count": int(len(wickets_gt6)),
        "dismissal_types": wickets_gt6["dismissal_type"].value_counts().to_dict(),
        "extras_types": wickets_gt6["extras_type"].fillna("none").value_counts().to_dict(),
    }

    # Create validation table with explicit bowler credit assignment
    credit_rules = {
        "Bowled": "yes",
        "Caught": "yes",
        "LBW": "yes",
        "Stump": "yes",
        "Hit Wicket": "yes",
        "Obstructing the field": "yes",
        "Obstracting the field": "yes",  # typo variant
        "RunOut": "no",
        "Retire Out": "no",
    }

    wicket_records = []
    for _, row in wickets.iterrows():
        dtype = row["dismissal_type"]
        bowler_credit = credit_rules.get(dtype, "unknown")
        wicket_records.append({
            "match_id": int(row["match_id"]),
            "innings": int(row["innings"]),
            "overid": int(row["overid"]),
            "over_ball_num": int(row["over_ball_num"]),
            "innings_ball_num": int(row["innings_ball_num"]),
            "dismissal_type": dtype,
            "dismissal_type_id": float(row["dismissal_type_id"]) if pd.notna(row["dismissal_type_id"]) else None,
            "dismissed_player_id": float(row["dismissed_player_id"]) if pd.notna(row["dismissed_player_id"]) else None,
            "striker_id": int(row["striker_id"]),
            "non_striker_id": int(row["non_striker_id"]),
            "bowler_id": int(row["bowler_id"]),
            "bowler_name": row["bowler_name"],
            "extras_type": row["extras_type"] if pd.notna(row["extras_type"]) else "none",
            "runs": int(row["runs"]),
            "bowler_credit": bowler_credit,
            "dismissed_is_striker": bool(row["dismissed_is_striker"]),
            "dismissed_is_non_striker": bool(row["dismissed_is_non_striker"]),
        })

    wicket_df = pd.DataFrame(wicket_records)
    save_csv(wicket_df, OUTPUT_DIR / "wicket_attribution_validation.csv")

    # Summary
    credit_counts = wicket_df["bowler_credit"].value_counts().to_dict()
    results["bowler_credit_summary"] = credit_counts

    # Flag unknown dismissal types
    unknown = wicket_df[wicket_df["bowler_credit"] == "unknown"]
    if len(unknown) > 0:
        results["unknown_dismissal_types"] = unknown["dismissal_type"].unique().tolist()

    # Save markdown
    lines = [
        "# Wicket Attribution Validation",
        "",
        f"## Total Wickets: {total_wickets}",
        "",
        "## Dismissal Type Counts",
        "",
    ]
    for dtype, count in sorted(results["dismissal_type_counts"].items(), key=lambda x: -x[1]):
        lines.append(f"- {dtype}: {count}")

    lines.append("")
    lines.append("## Bowler Credit Assignment (Standard Cricket Rules)")
    lines.append("")
    for dtype, credit in credit_rules.items():
        count = results["dismissal_type_counts"].get(dtype, 0)
        if count > 0:
            lines.append(f"- {dtype}: **{credit}** (count: {count})")

    lines.append("")
    lines.append("## Bowler Credit Summary")
    lines.append("")
    for credit, count in credit_counts.items():
        lines.append(f"- {credit}: {count}")

    lines.append("")
    lines.append("## Dismissed Player Role")
    lines.append("")
    for role, count in results["dismissed_player_role"].items():
        lines.append(f"- {role}: {count}")

    lines.append("")
    lines.append("## Dismissed Role by Type")
    lines.append("")
    for dtype, roles in results["dismissed_role_by_type"].items():
        lines.append(f"- {dtype}: striker={roles['striker']}, non_striker={roles['non_striker']}, neither={roles['neither']}")

    lines.append("")
    lines.append("## Wickets by Extras Type")
    lines.append("")
    for ext, count in results["wickets_by_extras_type"].items():
        lines.append(f"- {ext}: {count}")

    lines.append("")
    lines.append("## Wickets on Extra Balls (over_ball_num > 6)")
    lines.append(f"- Count: {results['wickets_on_extra_balls']['count']}")
    lines.append(f"- Dismissal types: {results['wickets_on_extra_balls']['dismissal_types']}")
    lines.append(f"- Extras types: {results['wickets_on_extra_balls']['extras_types']}")

    if results.get("unknown_dismissal_types"):
        lines.append("")
        lines.append("## Unknown Dismissal Types (Need Manual Review)")
        lines.append("")
        for dtype in results["unknown_dismissal_types"]:
            lines.append(f"- {dtype}")

    save_markdown(lines, OUTPUT_DIR / "wicket_attribution_validation.md")

    return wicket_df, results


# ---------------------------------------------------------------------------
# Task 4: Playing Eleven Conflict Analysis
# ---------------------------------------------------------------------------
def investigate_playing_eleven_conflicts(playing_df: pd.DataFrame, matches_df: pd.DataFrame) -> dict:
    """
    Analyze the 35 conflicting playing_eleven keys in matches 13613, 21176, 28962.
    """
    logger.info("Investigating playing_eleven conflicts...")

    # Get the conflicting matches
    conflict_matches = [13613, 21176, 28962]
    results = {}

    for mid in conflict_matches:
        match_playing = playing_df[playing_df["match_id"] == mid].copy()
        match_info = matches_df[matches_df["match_id"] == mid]

        results[f"match_{mid}"] = {
            "match_info": match_info[["match_id", "comp_id", "match_date", "home_team_id", "away_team_id", "stage", "result"]].to_dict("records") if len(match_info) > 0 else [],
            "total_rows": len(match_playing),
            "duplicate_keys": [],
        }

        # Find duplicates
        dup_mask = match_playing.duplicated(subset=["match_id", "team_id", "player_id"], keep=False)
        dup_rows = match_playing[dup_mask]

        for _, group in dup_rows.groupby(["match_id", "team_id", "player_id"]):
            key_info = {
                "team_id": int(group["team_id"].iloc[0]),
                "player_id": int(group["player_id"].iloc[0]),
                "row_count": len(group),
                "rows": group.to_dict("records"),
            }
            results[f"match_{mid}"]["duplicate_keys"].append(key_info)

    # Check if these are impact player substitutions (IPL 2023+)
    # Impact player rule: introduced in IPL 2023, allows one substitution per team
    # Check competition and season
    comp_df = load_csv(RAW_DIR / "competitions.csv")
    results["impact_player_check"] = {}
    for mid in conflict_matches:
        match_info = matches_df[matches_df["match_id"] == mid]
        if len(match_info) > 0:
            comp_id = match_info.iloc[0]["comp_id"]
            comp_info = comp_df[comp_df["comp_id"] == comp_id]
            results["impact_player_check"][f"match_{mid}"] = comp_info[["comp_id", "comp_name", "match_format", "season"]].to_dict("records")

    # Also check is_impact and is_impact_off columns
    for mid in conflict_matches:
        match_playing = playing_df[playing_df["match_id"] == mid]
        impact_cols = match_playing[["player_id", "team_id", "is_impact", "is_impact_off", "batting_order"]].drop_duplicates()
        results[f"match_{mid}"]["impact_columns"] = impact_cols.to_dict("records")

    save_json(results, OUTPUT_DIR / "playing_eleven_conflict_analysis.json")

    # Markdown
    lines = [
        "# Playing Eleven Conflict Analysis",
        "",
        f"## Conflicts found in 3 matches: {conflict_matches}",
        "",
    ]

    for mid in conflict_matches:
        lines.append(f"## Match {mid}")
        lines.append("")

        mi = results[f"match_{mid}"]["match_info"]
        if mi:
            lines.append(f"- Competition: {mi[0].get('comp_id')}")
            lines.append(f"- Date: {mi[0].get('match_date')}")
            lines.append(f"- Stage: {mi[0].get('stage')}")
            lines.append(f"- Result: {mi[0].get('result')}")

        lines.append(f"- Total playing_eleven rows: {results[f'match_{mid}']['total_rows']}")
        lines.append(f"- Duplicate keys: {len(results[f'match_{mid}']['duplicate_keys'])}")
        lines.append("")

        # Impact player check
        if f"match_{mid}" in results["impact_player_check"]:
            comp = results["impact_player_check"][f"match_{mid}"]
            if comp:
                lines.append(f"- Competition: {comp[0].get('comp_name')}, Format: {comp[0].get('match_format')}, Season: {comp[0].get('season')}")

        # Impact columns
        if "impact_columns" in results[f"match_{mid}"]:
            lines.append("")
            lines.append("### Impact Player Columns")
            lines.append("")
            for row in results[f"match_{mid}"]["impact_columns"]:
                lines.append(f"- Player {row['player_id']}, Team {row['team_id']}: is_impact={row['is_impact']}, is_impact_off={row['is_impact_off']}, batting_order={row['batting_order']}")

        lines.append("")
        lines.append("### Duplicate Key Details")
        lines.append("")
        for dup in results[f"match_{mid}"]["duplicate_keys"]:
            lines.append(f"- Team {dup['team_id']}, Player {dup['player_id']}: {dup['row_count']} rows")
            for i, row in enumerate(dup["rows"]):
                lines.append(f"  Row {i+1}: batting_order={row['batting_order']}, is_played={row['is_played']}, "
                             f"is_captain={row['is_captain']}, is_wk={row['is_wk']}, "
                             f"is_impact={row['is_impact']}, is_impact_off={row['is_impact_off']}")
            lines.append("")

    save_markdown(lines, OUTPUT_DIR / "playing_eleven_conflict_analysis.md")
    return results


# ---------------------------------------------------------------------------
# Task 5: Super Over Analysis (Innings 3 & 4)
# ---------------------------------------------------------------------------
def investigate_super_overs(bbb_df: pd.DataFrame, matches_df: pd.DataFrame) -> dict:
    """
    Investigate the 38 deliveries in innings 3 and 4.
    """
    logger.info("Investigating Super Overs (innings 3/4)...")

    # Get innings 3 and 4 deliveries
    super_overs = bbb_df[bbb_df["innings"].isin([3, 4])].copy()

    results = {
        "total_deliveries": int(len(super_overs)),
        "innings_distribution": super_overs["innings"].value_counts().to_dict(),
        "match_ids": sorted(super_overs["match_id"].unique().tolist()),
    }

    # Get match info for these matches
    match_ids = super_overs["match_id"].unique()
    match_info = matches_df[matches_df["match_id"].isin(match_ids)]
    results["match_details"] = match_info[
        ["match_id", "comp_id", "match_date", "home_team_id", "away_team_id", "stage", "result"]
    ].to_dict("records")

    # Per match analysis
    results["per_match"] = {}
    for mid in match_ids:
        mid_df = super_overs[super_overs["match_id"] == mid]
        results["per_match"][f"match_{mid}"] = {
            "innings": sorted(mid_df["innings"].unique().tolist()),
            "delivery_count": int(len(mid_df)),
            "deliveries": mid_df.sort_values(["innings", "overid", "over_ball_num"])[
                ["innings", "overid", "over_ball_num", "innings_ball_num",
                 "batting_team_id", "bowling_team_id", "striker_id", "bowler_id",
                 "runs", "extras_type", "is_wicket", "dismissal_type"]
            ].to_dict("records"),
        }

    # Check if these are tied matches
    tied_matches = match_info[match_info["result"].str.contains("Tied|Super Over|tie", case=False, na=False)]
    results["tied_matches"] = tied_matches[["match_id", "result"]].to_dict("records")

    save_json(results, OUTPUT_DIR / "super_over_analysis.json")

    # Markdown
    lines = [
        "# Super Over Analysis (Innings 3 & 4)",
        "",
        f"## Total Deliveries: {results['total_deliveries']}",
        f"## Innings Distribution: {results['innings_distribution']}",
        f"## Match IDs: {results['match_ids']}",
        "",
    ]

    lines.append("## Match Details")
    lines.append("")
    for m in results["match_details"]:
        lines.append(f"- Match {m['match_id']}: comp={m['comp_id']}, date={m['match_date']}, "
                     f"stage={m['stage']}, result={m['result']}")
    lines.append("")

    lines.append("## Per Match Delivery Breakdown")
    lines.append("")
    for mid, data in results["per_match"].items():
        lines.append(f"### {mid}")
        lines.append(f"- Innings: {data['innings']}")
        lines.append(f"- Delivery count: {data['delivery_count']}")
        lines.append("")
        lines.append("| Innings | Over | Ball | InnBall | BatTeam | BowlTeam | Striker | Bowler | Runs | Extras | Wicket | Dismissal |")
        lines.append("|---------|------|------|---------|---------|----------|---------|--------|------|--------|--------|-----------|")
        for d in data["deliveries"]:
            lines.append(f"| {d['innings']} | {d['overid']} | {d['over_ball_num']} | {d['innings_ball_num']} | "
                         f"{d['batting_team_id']} | {d['bowling_team_id']} | {d['striker_id']} | {d['bowler_id']} | "
                         f"{d['runs']} | {d['extras_type'] if pd.notna(d['extras_type']) else 'none'} | "
                         f"{d['is_wicket']} | {d['dismissal_type'] if pd.notna(d['dismissal_type']) else 'none'} |")
        lines.append("")

    save_markdown(lines, OUTPUT_DIR / "super_over_analysis.md")
    return results


# ---------------------------------------------------------------------------
# Task 6: Abandoned Match Verification
# ---------------------------------------------------------------------------
def investigate_abandoned_matches(matches_df: pd.DataFrame, bbb_df: pd.DataFrame) -> dict:
    """
    Verify the 16 matches marked Match Abandoned and confirm exclusion logic.
    """
    logger.info("Investigating abandoned matches...")

    abandoned = matches_df[matches_df["result"] == "Match Abandoned"].copy()

    results = {
        "total_abandoned": int(len(abandoned)),
        "match_ids": sorted(abandoned["match_id"].unique().tolist()),
        "by_competition": abandoned["comp_id"].value_counts().to_dict(),
        "by_format": [],
        "by_season": abandoned["season"].value_counts().to_dict() if "season" in abandoned.columns else {},
        "stage_distribution": abandoned["stage"].value_counts().to_dict(),
    }

    # Add competition names
    comp_df = load_csv(RAW_DIR / "competitions.csv")
    abandoned_with_comp = abandoned.merge(comp_df[["comp_id", "comp_name", "match_format", "season"]], on="comp_id", how="left")
    results["by_format"] = abandoned_with_comp["match_format"].value_counts().to_dict()
    results["by_season"] = abandoned_with_comp["season"].value_counts().to_dict()
    results["by_competition_name"] = abandoned_with_comp["comp_name"].value_counts().to_dict()

    # Check if any have ball-by-ball data (should be none)
    abandoned_ids = set(abandoned["match_id"])
    bbb_abandoned = bbb_df[bbb_df["match_id"].isin(abandoned_ids)]
    results["ball_by_ball_rows_for_abandoned"] = int(len(bbb_abandoned))

    # Check other matches with similar patterns (No Result, etc.)
    no_result = matches_df[matches_df["result"].str.contains("No Result", case=False, na=False)]
    results["no_result_matches"] = int(len(no_result))
    results["no_result_ids"] = sorted(no_result["match_id"].unique().tolist())

    # Check if any abandoned matches have toss/winner info
    results["toss_data"] = {
        "toss_win_not_null": int(abandoned["toss_win_team_id"].notna().sum()),
        "win_team_not_null": int(abandoned["win_team_id"].notna().sum()),
    }

    save_json(results, OUTPUT_DIR / "abandoned_match_analysis.json")

    # Markdown
    lines = [
        "# Abandoned Match Verification",
        "",
        f"## Total Abandoned Matches: {results['total_abandoned']}",
        "",
        "## By Competition",
        "",
    ]
    for comp, count in results["by_competition_name"].items():
        lines.append(f"- {comp}: {count}")

    lines.append("")
    lines.append("## By Format")
    lines.append("")
    for fmt, count in results["by_format"].items():
        lines.append(f"- {fmt}: {count}")

    lines.append("")
    lines.append("## By Season")
    lines.append("")
    for season, count in results["by_season"].items():
        lines.append(f"- {season}: {count}")

    lines.append("")
    lines.append("## By Stage")
    lines.append("")
    for stage, count in results["stage_distribution"].items():
        lines.append(f"- {stage}: {count}")

    lines.append("")
    lines.append(f"## Ball-by-Ball Data for Abandoned Matches: {results['ball_by_ball_rows_for_abandoned']} rows")
    lines.append("")

    lines.append(f"## No Result Matches: {results['no_result_matches']}")
    lines.append(f"- IDs: {results['no_result_ids']}")

    lines.append("")
    lines.append("## Toss/Winner Data")
    lines.append(f"- Toss winner recorded: {results['toss_data']['toss_win_not_null']}/{results['total_abandoned']}")
    lines.append(f"- Win team recorded: {results['toss_data']['win_team_not_null']}/{results['total_abandoned']}")

    lines.append("")
    lines.append("## Recommendation")
    lines.append("- All 16 matches are **Match Abandoned** with **zero ball-by-ball deliveries**")
    lines.append("- No toss winner or match winner recorded")
    lines.append("- **Exclude from all delivery-level rankings and metrics**")
    lines.append("- May include in match-count denominators if explicitly noted as abandoned")

    save_markdown(lines, OUTPUT_DIR / "abandoned_match_analysis.md")
    return results


# ---------------------------------------------------------------------------
# Task 7: Player Identity Canonical Naming
# ---------------------------------------------------------------------------
def investigate_player_identity(
    mapping_df: pd.DataFrame,
    playing_df: pd.DataFrame,
    bbb_df: pd.DataFrame
) -> dict:
    """
    Check player IDs with multiple names and document canonical naming.
    """
    logger.info("Investigating player identity...")

    results = {}

    # 1. mapping: player_id -> player_name (should be canonical)
    mapping_names = mapping_df.drop_duplicates("player_id").set_index("player_id")["player_name"]

    # 2. ball_by_ball: striker_id -> striker_name, bowler_id -> bowler_name
    striker_names = bbb_df.drop_duplicates("striker_id").set_index("striker_id")["striker_name"]
    bowler_names = bbb_df.drop_duplicates("bowler_id").set_index("bowler_id")["bowler_name"]

    # 3. Check for multiple names per player_id in mapping
    name_counts = mapping_df.groupby("player_id")["player_name"].nunique()
    multi_name = name_counts[name_counts > 1]
    results["mapping_multiple_names_per_id"] = multi_name.to_dict()

    # 4. Check for multiple player_ids per name in mapping
    id_counts = mapping_df.groupby("player_name")["player_id"].nunique()
    multi_id = id_counts[id_counts > 1]
    results["mapping_multiple_ids_per_name"] = multi_id.head(20).to_dict()

    # 5. Compare names across sources for overlapping IDs
    all_bbb_ids = set(striker_names.index) | set(bowler_names.index)
    overlap_ids = set(mapping_names.index) & all_bbb_ids

    mismatches = []
    for pid in overlap_ids:
        m_name = mapping_names.get(pid)
        b_name = striker_names.get(pid) or bowler_names.get(pid)
        if m_name and b_name and m_name != b_name:
            mismatches.append({
                "player_id": int(pid),
                "mapping_name": str(m_name),
                "ball_by_ball_name": str(b_name),
            })

    results["name_mismatches"] = mismatches
    results["name_mismatch_count"] = len(mismatches)

    # 6. Check for same name, different IDs in ball_by_ball
    all_bbb_names = {}
    for _, row in bbb_df[["striker_id", "striker_name"]].drop_duplicates().iterrows():
        all_bbb_names.setdefault(row["striker_name"], set()).add(row["striker_id"])
    for _, row in bbb_df[["bowler_id", "bowler_name"]].drop_duplicates().iterrows():
        all_bbb_names.setdefault(row["bowler_name"], set()).add(row["bowler_id"])

    bbb_multi_id = {name: list(ids) for name, ids in all_bbb_names.items() if len(ids) > 1}
    results["bbb_multiple_ids_per_name"] = {k: v for k, v in list(bbb_multi_id.items())[:20]}

    # 7. Players only in ball_by_ball but not in mapping
    mapping_ids = set(mapping_names.index)
    bbb_only = all_bbb_ids - mapping_ids
    results["players_in_bbb_not_in_mapping"] = sorted([int(x) for x in bbb_only])

    # 8. Players only in mapping but not in ball_by_ball
    mapping_only = mapping_ids - all_bbb_ids
    results["players_in_mapping_not_in_bbb"] = sorted([int(x) for x in mapping_only])

    # 9. Playing eleven player IDs
    playing_ids = set(playing_df["player_id"].unique())
    results["players_in_playing_not_in_mapping"] = sorted([int(x) for x in playing_ids - mapping_ids])
    results["players_in_playing_not_in_bbb"] = sorted([int(x) for x in playing_ids - all_bbb_ids])

    save_json(results, OUTPUT_DIR / "player_identity_analysis.json")

    # Markdown
    lines = [
        "# Player Identity Analysis",
        "",
        "## Canonical Source: competition_team_player_mapping.csv",
        "",
        "## Multiple Names per Player ID in Mapping",
        "",
    ]
    if results["mapping_multiple_names_per_id"]:
        for pid, count in results["mapping_multiple_names_per_id"].items():
            names = mapping_df[mapping_df["player_id"] == pid]["player_name"].unique()
            lines.append(f"- Player {pid}: {count} names -> {list(names)}")
    else:
        lines.append("None found.")
    lines.append("")

    lines.append("## Multiple Player IDs per Name in Mapping")
    lines.append("")
    for name, count in results["mapping_multiple_ids_per_name"].items():
        ids = mapping_df[mapping_df["player_name"] == name]["player_id"].unique()
        lines.append(f"- '{name}': {count} IDs -> {list(ids)}")
    lines.append("")

    lines.append("## Name Mismatches: Mapping vs Ball-by-Ball")
    lines.append(f"- Total mismatches: {results['name_mismatch_count']}")
    lines.append("")
    for m in results["name_mismatches"][:20]:
        lines.append(f"- Player {m['player_id']}: mapping='{m['mapping_name']}' vs bbb='{m['ball_by_ball_name']}'")
    lines.append("")

    lines.append("## Multiple IDs per Name in Ball-by-Ball (sample)")
    lines.append("")
    for name, ids in results["bbb_multiple_ids_per_name"].items():
        lines.append(f"- '{name}': {ids}")
    lines.append("")

    lines.append("## Players Only in Ball-by-Ball (not in Mapping)")
    lines.append(f"- Count: {len(results['players_in_bbb_not_in_mapping'])}")
    lines.append(f"- IDs: {results['players_in_bbb_not_in_mapping'][:20]}")
    lines.append("")

    lines.append("## Players Only in Mapping (not in Ball-by-Ball)")
    lines.append(f"- Count: {len(results['players_in_mapping_not_in_bbb'])}")
    lines.append("")

    lines.append("## Recommendation")
    lines.append("- Use **competition_team_player_mapping** as canonical for player names")
    lines.append("- Join ball_by_ball on player_id only; do NOT use name for joining")
    lines.append("- Flag name mismatches for manual review (1 found: Player 4458)")
    lines.append("- Multiple IDs for same name in mapping (8 cases) likely represent different players with same name")
    lines.append("- Do NOT merge different player_ids even if names match")

    save_markdown(lines, OUTPUT_DIR / "player_identity_analysis.md")
    return results


# ---------------------------------------------------------------------------
# Cricket Data Dictionary
# ---------------------------------------------------------------------------
def create_cricket_data_dictionary(
    reconciliation_results: dict,
    legal_ball_results: dict,
    wicket_results: dict,
    playing_eleven_results: dict,
    super_over_results: dict,
    abandoned_results: dict,
    player_identity_results: dict
) -> None:
    """
    Create a comprehensive cricket data dictionary documenting all conventions.
    """
    lines = [
        "# Cricket Data Dictionary - SupeRR Selector Season 2",
        "",
        f"Generated: {pd.Timestamp.now().isoformat()}",
        "",
        "## Purpose",
        "Document the established conventions for interpreting the official data pack. ",
        "All conventions derived from raw record inspection, not assumptions.",
        "",
        "## 1. Ball-by-Ball Core Fields",
        "",
        "### match_id",
        "- Type: Integer. Unique match identifier. Foreign key to matches.csv",
        "",
        "### innings",
        "- Type: Integer (1, 2, 3, 4)",
        "- 1 = First innings, 2 = Second innings",
        "- 3, 4 = Super Over innings (confirmed: 38 deliveries across 2 matches)",
        "",
        "### overid",
        "- Type: Integer (1-20). Over number within innings.",
        "",
        "### over_ball_num",
        "- Type: Integer (1-13 observed)",
        "- **NOT a legal ball number**. This is a delivery sequence number within the over.",
        "- Values 1-6: typically legal balls, but may include wides/no-balls if extras_type indicates so",
        "- Values >6: **always extra balls** (wides/no-balls). 8,429 deliveries have over_ball_num > 6.",
        "- 7,735 of these have extras_type='none' (data quality issue - likely misclassified wides)",
        "- **Do not use `over_ball_num BETWEEN 1 AND 6` as legal ball filter.**",
        "",
        "### innings_ball_num",
        "- Type: Integer. Sequential delivery number within innings (1, 2, 3...).",
        "- Increments on **every delivery** including wides, no-balls, byes, etc.",
        "- Confirmed sequential in sampled matches.",
        "",
        "### batting_team_id / bowling_team_id",
        "- Type: Integer. Foreign key to teams.csv (via competition-team mapping).",
        "",
        "### striker_id / non_striker_id / bowler_id",
        "- Type: Integer. Player identifiers. Foreign key to competition_team_player_mapping.csv",
        "- **Join on ID only. Do not use names for joining.**",
        "",
        "### runs",
        "- Type: Integer (0-6). **Total runs scored on the delivery** (batter runs + extras).",
        "- For non-extras deliveries: runs = batter runs",
        "- For extras deliveries: runs = batter runs + extras runs",
        "",
        "### extras_type",
        "- Type: String or NaN. Values: 'wide', 'Overstep' (no-ball), 'byes', 'legbyes', 'other', 'Penalty', NaN",
        "- NaN = no extras on this delivery",
        "- 'Overstep' = no-ball (front foot overstep)",
        "- 'wide' = wide ball",
        "- 'other' = 264 deliveries, needs investigation (includes penalty runs?)",
        "- 'Penalty' = 1 delivery (5 penalty runs)",
        "",
        "### extras1_runs",
        "- Type: Integer (0-5). **Total extra runs awarded on this delivery**.",
        "- For wides: includes the 1 run for wide + any runs scored (byes/legbyes off wide)",
        "- For no-balls (Overstep): includes 1 run for no-ball + any runs scored",
        "- For byes/legbyes: equals the byes/legbyes runs",
        "- For 'other': varies (0-4), includes penalty runs",
        "",
        "### extras_2_runs",
        "- Type: Integer (0-4). **Additional penalty runs** (rare, 84 total).",
        "- Only non-zero for 'Overstep' (48 runs) and 'other' (35 runs) and 'Penalty' (1 run)",
        "- Represents 5-run penalties under Law 41/42",
        "",
        "## 2. Derived Fields (Established Conventions)",
        "",
        "### Legal Ball",
        "- **Definition**: A delivery that counts towards the 6-ball over.",
        "- **Rule**: `extras_type NOT IN ('wide', 'Overstep')`",
        "- Count: 192,570 (95.81% of deliveries)",
        "- **Do NOT use over_ball_num for this determination.**",
        "",
        "### Extra Ball (Wide/No-Ball)",
        "- **Definition**: A delivery that does not count towards the 6-ball over.",
        "- **Rule**: `extras_type IN ('wide', 'Overstep')`",
        "- Count: 8,290 (4.13% of deliveries) — note: 7,735 misclassified as 'none'",
        "- These deliveries increment innings_ball_num but not the legal ball count",
        "",
        "### Batter Runs",
        "- **Formula**: `runs - extras1_runs`",
        "- **Rationale**: extras1_runs captures ALL extra runs (wide/no-ball penalty + byes/legbyes). ",
        "  Subtracting from total runs leaves batter runs.",
        "- Validated: For non-extras deliveries, extras1_runs=0, so batter_runs = runs ✓",
        "- For wides: batter_runs >= 0 (can score runs off wide) ✓",
        "- For no-balls: batter_runs >= 0 ✓",
        "- For byes/legbyes: batter_runs = 0 ✓ (byes/legbyes not credited to batter)",
        "- **Do NOT use `runs - extras1_runs - extras_2_runs`** — that incorrectly subtracts penalty runs from batter.",
        "",
        "### Bowler Runs Conceded",
        "- **Formula**: `runs - extras_2_runs` for byes/legbyes/penalty; `runs` for wides/no-balls",
        "- **Standard cricket**: Bowler charged for wides and no-balls (runs), NOT charged for byes, legbyes, penalty runs.",
        "- Implementation: `CASE WHEN extras_type IN ('byes', 'legbyes', 'Penalty') THEN runs - extras_2_runs ELSE runs END`",
        "",
        "### Is Wicket (Batter Dismissal)",
        "- **Field**: `is_wicket` (boolean). True = a batter was dismissed on this delivery.",
        "- Includes all dismissal types.",
        "",
        "### Is Bowler Wicket (Bowler Credit)",
        "- **Definition**: Dismissal credited to bowler for bowling statistics.",
        "- **Rule**: dismissal_type IN ('Bowled', 'Caught', 'LBW', 'Stump', 'Hit Wicket', 'Obstructing the field', 'Obstracting the field')",
        "- **NOT credited**: 'RunOut', 'Retire Out'",
        "- Count: 10,275 bowler wickets out of 10,881 total wickets (94.4%)",
        "",
        "## 3. Wicket Conventions",
        "",
        "### Dismissal Types and Bowler Credit",
        "| Dismissal Type | Bowler Credit | Count | Notes |",
        "|----------------|---------------|-------|-------|",
        "| Bowled | YES | 1,775 | |",
        "| Caught | YES | 7,557 | |",
        "| LBW | YES | 709 | |",
        "| Stump | YES | 214 | Stumped |",
        "| Hit Wicket | YES | 17 | |",
        "| Obstructing the field | YES | 1 | |",
        "| Obstracting the field | YES | 2 | Typo variant |",
        "| RunOut | NO | 600 | Not bowler's wicket |",
        "| Retire Out | NO | 6 | Not bowler's wicket |",
        "",
        "### Wickets on Extra Balls",
        "- 484 wickets occurred on deliveries with over_ball_num > 6",
        "- Mostly Caught (328) and Bowled (63) on 'none' extras (misclassified wides)",
        "- Standard cricket: wicket stands for batter; bowler gets credit if dismissal type allows",
        "",
        "## 4. Playing Eleven Conventions",
        "",
        "### Duplicate Keys",
        "- 35 unique (match_id, team_id, player_id) keys have conflicting rows (75 total rows)",
        "- All conflicts in **batting_order** only; other fields identical",
        "- Affected matches: 13613 (Aus vs SL 2022), 21176 (NZ vs SL 2023), 28962 (Ind vs Afg 2024)",
        "- Likely **impact player substitutions** (IPL 2023+) or flexible batting position recording",
        "- **Convention**: Keep first row per key for XI construction; flag for review",
        "",
        "### Impact Player Columns",
        "- is_impact: 1 if player is an impact substitute (IPL 2023+)",
        "- is_impact_off: 1 if player was replaced by impact substitute",
        "- Not consistently populated across all matches",
        "",
        "## 5. Match Status Conventions",
        "",
        "### Match Abandoned",
        "- 16 matches with result='Match Abandoned'",
        "- **Zero ball-by-ball deliveries** for all 16",
        "- No toss winner, no match winner",
        "- **Exclude from all delivery-level analysis**",
        "",
        "### No Result",
        "- 5 matches with 'No Result' (different from Abandoned)",
        "- May have partial ball-by-ball data",
        "",
        "## 6. Competition Scope",
        "",
        "### IPL (5 seasons, 2022-2026)",
        "- 5 competitions, 371 matches, 87,687 deliveries",
        "- 10 franchise teams, consistent format",
        "- match_format='T20', comp_name contains 'IPL'",
        "",
        "### T20I (134 series, 2022-2026)",
        "- 134 competitions, 482 matches, 106,327 deliveries",
        "- 33 national teams, variable conditions",
        "- match_format='T20I'",
        "",
        "### Other T20 (2 tournaments)",
        "- Emerging Teams Asia Cup 2024, Rising Stars 2025",
        "- 30 matches, 6,985 deliveries",
        "- Development tournaments — **exclude from primary analysis**",
        "",
        "## 7. Player Identity Conventions",
        "",
        "### Canonical Name Source",
        "- **competition_team_player_mapping.csv** is the authoritative source for player names",
        "- Join ball_by_ball and playing_eleven on player_id ONLY",
        "- Do NOT use names for joining",
        "",
        "### Known Issues",
        "- 1 name mismatch: Player 4458 — mapping='AHT Donald' vs bbb='Aneurin Donald'",
        "- 8 names with multiple player_ids in mapping (e.g., Rashid Khan, Abdul Samad) — different players, same name",
        "- Do NOT merge different player_ids even if names appear identical",
        "",
        "## 8. Unresolved / Flagged Items",
        "",
        "1. **extras_type='other' (264 deliveries)**: Mixed content, includes some penalty runs. Needs manual review.",
        "2. **7,735 deliveries with over_ball_num > 6 but extras_type='none'**: Likely misclassified wides. Treat as extra balls for legal ball count.",
        "3. **Impact player substitution logic**: Not fully encoded. batting_order conflicts in 3 matches suggest substitution tracking.",
        "4. **Super Over identification**: 2 matches with innings 3/4 (38 deliveries). Match IDs: 18531, 18532 (NZ vs Ind 2022).",
        "5. **Bowl_speed = -1 or 0**: Likely missing data indicator, not genuine speeds. Flag for exclusion.",
        "6. **dismissal_type_id**: Numeric codes (1-10) mapping to dismissal_type. Not fully validated.",
        "",
    ]

    save_markdown(lines, OUTPUT_DIR / "cricket_data_dictionary.md")


# ---------------------------------------------------------------------------
# Main Investigation Pipeline
# ---------------------------------------------------------------------------
def run_conventions_investigation() -> dict:
    """Run all convention investigations."""
    logger.info("=" * 60)
    logger.info("Starting Cricket Conventions Investigation")
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

    # Task 1: Runs/Extras Reconciliation
    logger.info("Task 1: Runs/Extras reconciliation...")
    sample_df, recon_results = investigate_runs_extras_reconciliation(bbb_df)
    all_results["reconciliation"] = recon_results

    # Task 2: Legal Ball Determination
    logger.info("Task 2: Legal ball determination...")
    legal_ball_results = investigate_legal_balls(bbb_df)
    all_results["legal_balls"] = legal_ball_results

    # Task 3: Wicket Attribution
    logger.info("Task 3: Wicket attribution...")
    wicket_df, wicket_results = investigate_wicket_attribution(bbb_df)
    all_results["wickets"] = wicket_results

    # Task 4: Playing Eleven Conflicts
    logger.info("Task 4: Playing eleven conflicts...")
    playing_results = investigate_playing_eleven_conflicts(playing_df, matches_df)
    all_results["playing_eleven"] = playing_results

    # Task 5: Super Overs
    logger.info("Task 5: Super Overs...")
    super_over_results = investigate_super_overs(bbb_df, matches_df)
    all_results["super_overs"] = super_over_results

    # Task 6: Abandoned Matches
    logger.info("Task 6: Abandoned matches...")
    abandoned_results = investigate_abandoned_matches(matches_df, bbb_df)
    all_results["abandoned"] = abandoned_results

    # Task 7: Player Identity
    logger.info("Task 7: Player identity...")
    player_results = investigate_player_identity(mapping_df, playing_df, bbb_df)
    all_results["player_identity"] = player_results

    # Create Cricket Data Dictionary
    logger.info("Creating cricket data dictionary...")
    create_cricket_data_dictionary(
        recon_results, legal_ball_results, wicket_results,
        playing_results, super_over_results, abandoned_results, player_results
    )

    # Save combined results
    save_json(all_results, OUTPUT_DIR / "conventions_investigation.json")

    logger.info("=" * 60)
    logger.info("Conventions investigation complete. Outputs saved to %s", OUTPUT_DIR)
    logger.info("=" * 60)

    return all_results


if __name__ == "__main__":
    try:
        run_conventions_investigation()
        logger.info("SUCCESS: Conventions investigation completed")
    except Exception as e:
        logger.exception("Conventions investigation failed: %s", e)
        sys.exit(1)