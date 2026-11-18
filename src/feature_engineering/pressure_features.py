"""
Pressure Feature Engineering Module
Aggregates deliveries into phase-specific rates and pressure performance features.
"""

import pandas as pd
import numpy as np


def compute_batter_phase_rates(deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate batter ball-by-ball deliveries into phase metrics:
    - Strike Rate = runs_off_bat / legal_balls * 100
    - Boundary % = (fours + sixes) / legal_balls * 100
    - Dot Ball % = dot_balls / legal_balls * 100
    """
    grouped = deliveries_df.groupby(['player_id', 'season'])
    agg_df = grouped.agg(
        total_balls=('is_legal_ball', 'sum'),
        total_runs=('runs_off_bat', 'sum'),
        fours=('is_four', 'sum'),
        sixes=('is_six', 'sum'),
        dot_balls=('is_dot', 'sum')
    ).reset_index()

    agg_df['strike_rate'] = np.where(agg_df['total_balls'] > 0, agg_df['total_runs'] / agg_df['total_balls'] * 100.0, 0.0)
    agg_df['boundary_pct'] = np.where(agg_df['total_balls'] > 0, (agg_df['fours'] + agg_df['sixes']) / agg_df['total_balls'] * 100.0, 0.0)
    return agg_df


def compute_bowler_phase_rates(deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate bowler ball-by-ball deliveries into phase metrics:
    - Economy = total_runs_conceded / (legal_balls / 6.0)
    - Wicket Rate = wickets / legal_balls
    - Dot Ball % = dot_balls / legal_balls * 100
    """
    grouped = deliveries_df.groupby(['player_id', 'season'])
    agg_df = grouped.agg(
        total_balls=('is_legal_ball', 'sum'),
        runs_conceded=('total_runs', 'sum'),
        wickets=('is_wicket', 'sum'),
        dot_balls=('is_dot', 'sum')
    ).reset_index()

    agg_df['economy_rate'] = np.where(agg_df['total_balls'] > 0, agg_df['runs_conceded'] / (agg_df['total_balls'] / 6.0), 99.0)
    agg_df['wicket_rate'] = np.where(agg_df['total_balls'] > 0, agg_df['wickets'] / agg_df['total_balls'], 0.0)
    agg_df['dot_ball_pct'] = np.where(agg_df['total_balls'] > 0, agg_df['dot_balls'] / agg_df['total_balls'] * 100.0, 0.0)
    return agg_df

