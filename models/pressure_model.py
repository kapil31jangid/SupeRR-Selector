"""
PRESSURE-X Performance Model
============================
Core statistical pressure performance model for batters and bowlers across T20 competitions.

Methodology:
- Bayesian shrinkage (James-Stein empirical Bayes) towards population mean.
- Competition tier strength adjustment (T1: 1.00, T2: 0.92, T3: 0.84, T4: 0.76, T5: 0.68).
- Multi-phase game state weighting (High-Extreme, Death, Powerplay, Middle/Chase).
- Evidence-Based composite scoring on a 0-100 normalized scale.
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd


@dataclass
class CompetitionTierWeights:
    T1_IPL: float = 1.00
    T2_TOP_LEAGUES: float = 0.92  # BBL, PSL, SA20, The Hundred, ILT20
    T3_EMERGING: float = 0.84     # CPL, BPL, LPL, Super Smash
    T4_ASSOCIATE: float = 0.76    # Associate T20Is
    T5_DOMESTIC: float = 0.68     # Domestic T20 competitions


class PressureModel:
    """
    Evidence-Based Pressure Performance Scoring Engine.
    Evaluates batter and bowler execution under pressure phases.
    """

    def __init__(self, tier_weights: Optional[CompetitionTierWeights] = None):
        self.tier_weights = tier_weights or CompetitionTierWeights()
        
        # Batter Phase Component Weights (Evidence-Based v3)
        self.batter_weights = {
            'overall_sr': 0.30,
            'high_extreme_sr': 0.25,
            'chase_sr': 0.20,
            'powerplay_sr': 0.10,
            'death_sr': 0.10,
            'boundary_pct': 0.05
        }

        # Bowler Phase Component Weights (Evidence-Based v3)
        self.bowler_weights = {
            'overall_economy': 0.30,
            'high_extreme_economy': 0.25,
            'death_economy': 0.20,
            'powerplay_economy': 0.10,
            'wicket_rate': 0.10,
            'dot_ball_pct': 0.05
        }

    @staticmethod
    def apply_shrinkage(
        observed: pd.Series,
        sample_sizes: pd.Series,
        prior_mean: Optional[float] = None,
        k: float = 50.0
    ) -> pd.Series:
        """
        Empirical Bayes shrinkage towards population mean:
        shrunk_value = lambda * observed + (1 - lambda) * prior_mean
        where lambda = sample_size / (sample_size + k)
        """
        if prior_mean is None:
            prior_mean = observed.mean()
        shrinkage_weight = sample_sizes / (sample_sizes + k)
        return shrinkage_weight * observed + (1.0 - shrinkage_weight) * prior_mean

    @staticmethod
    def normalize_metric(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
        """
        Robust quantile normalization to 0-100 scale using 5th and 95th percentiles.
        """
        p5 = series.quantile(0.05)
        p95 = series.quantile(0.95)
        if np.isclose(p95, p5):
            return pd.Series(50.0, index=series.index)
        if higher_is_better:
            scaled = (series - p5) / (p95 - p5) * 100.0
        else:
            scaled = (p95 - series) / (p95 - p5) * 100.0
        return pd.Series(np.clip(scaled, 0.0, 100.0), index=series.index)

    def calculate_batter_pressure_score(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
        """
        Calculate composite batter pressure scores from feature dataframe.
        """
        component_scores = pd.DataFrame(index=df.index)

        # Expected rate columns with shrinkage and competition adjustments
        sr_col = 'strike_rate_comp_adj' if 'strike_rate_comp_adj' in df.columns else 'strike_rate_adj'
        he_col = 'high_extreme_sr_adj' if 'high_extreme_sr_adj' in df.columns else 'high_extreme_sr'
        chase_col = 'chase_strike_rate_adj' if 'chase_strike_rate_adj' in df.columns else 'chase_strike_rate'
        pp_col = 'powerplay_sr_adj' if 'powerplay_sr_adj' in df.columns else 'powerplay_sr'
        death_col = 'death_sr_adj' if 'death_sr_adj' in df.columns else 'death_sr'
        bp_col = 'boundary_pct_comp_adj' if 'boundary_pct_comp_adj' in df.columns else 'boundary_pct_adj'

        component_scores['sr_score'] = self.normalize_metric(df[sr_col], higher_is_better=True)
        component_scores['he_score'] = self.normalize_metric(df[he_col], higher_is_better=True) if he_col in df.columns else 50.0
        component_scores['chase_score'] = self.normalize_metric(df[chase_col], higher_is_better=True) if chase_col in df.columns else 50.0
        component_scores['pp_score'] = self.normalize_metric(df[pp_col], higher_is_better=True) if pp_col in df.columns else 50.0
        component_scores['death_score'] = self.normalize_metric(df[death_col], higher_is_better=True) if death_col in df.columns else 50.0
        component_scores['bp_score'] = self.normalize_metric(df[bp_col], higher_is_better=True) if bp_col in df.columns else 50.0

        composite = (
            self.batter_weights['overall_sr'] * component_scores['sr_score'] +
            self.batter_weights['high_extreme_sr'] * component_scores['he_score'] +
            self.batter_weights['chase_sr'] * component_scores['chase_score'] +
            self.batter_weights['powerplay_sr'] * component_scores['pp_score'] +
            self.batter_weights['death_sr'] * component_scores['death_score'] +
            self.batter_weights['boundary_pct'] * component_scores['bp_score']
        )
        return composite, component_scores

    def calculate_bowler_pressure_score(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
        """
        Calculate composite bowler pressure scores from feature dataframe.
        """
        component_scores = pd.DataFrame(index=df.index)

        econ_col = 'economy_rate_comp_adj' if 'economy_rate_comp_adj' in df.columns else 'economy_rate_adj'
        he_econ_col = 'high_extreme_economy_adj' if 'high_extreme_economy_adj' in df.columns else 'high_extreme_economy'
        death_econ_col = 'death_economy_adj' if 'death_economy_adj' in df.columns else 'death_economy'
        pp_econ_col = 'powerplay_economy_adj' if 'powerplay_economy_adj' in df.columns else 'powerplay_economy'
        wr_col = 'wicket_rate_comp_adj' if 'wicket_rate_comp_adj' in df.columns else 'wicket_rate_adj'
        dot_col = 'dot_ball_pct_comp_adj' if 'dot_ball_pct_comp_adj' in df.columns else 'dot_ball_pct_adj'

        component_scores['econ_score'] = self.normalize_metric(df[econ_col], higher_is_better=False)
        component_scores['he_econ_score'] = self.normalize_metric(df[he_econ_col], higher_is_better=False) if he_econ_col in df.columns else 50.0
        component_scores['death_econ_score'] = self.normalize_metric(df[death_econ_col], higher_is_better=False) if death_econ_col in df.columns else 50.0
        component_scores['pp_econ_score'] = self.normalize_metric(df[pp_econ_col], higher_is_better=False) if pp_econ_col in df.columns else 50.0
        component_scores['wr_score'] = self.normalize_metric(df[wr_col], higher_is_better=True) if wr_col in df.columns else 50.0
        component_scores['dot_score'] = self.normalize_metric(df[dot_col], higher_is_better=True) if dot_col in df.columns else 50.0

        composite = (
            self.bowler_weights['overall_economy'] * component_scores['econ_score'] +
            self.bowler_weights['high_extreme_economy'] * component_scores['he_econ_score'] +
            self.bowler_weights['death_economy'] * component_scores['death_econ_score'] +
            self.bowler_weights['powerplay_economy'] * component_scores['pp_econ_score'] +
            self.bowler_weights['wicket_rate'] * component_scores['wr_score'] +
            self.bowler_weights['dot_ball_pct'] * component_scores['dot_score']
        )
        return composite, component_scores

