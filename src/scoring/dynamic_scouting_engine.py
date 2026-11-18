"""
PRESSURE-X Dynamic Scouting Engine
===================================
Configurable multi-dimensional ranking engine for IPL 2027 auction intelligence.
Supports custom weight profiles, missing data policies, and evidence reliability gating.

Default RR Model: 40% Pressure Execution | 30% Age & Development Runway | 20% Skill Ceiling | 10% Current Form
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from enum import Enum


class MissingDataPolicy(Enum):
    """Policy for handling missing dimension scores."""
    ZERO = "zero"                    # Treat missing as 0 (harsh)
    NEUTRAL = "neutral"              # Treat missing as 50 (neutral)
    POPULATION_MEAN = "pop_mean"     # Impute from population mean
    POPULATION_MEDIAN = "pop_median" # Impute from population median
    DIMENSION_WEIGHT_REDISTRIBUTE = "redistribute"  # Redistribute weight to observed dimensions


class WeightProfile(Enum):
    """Pre-defined weight profiles for different scouting philosophies."""
    RR_DEFAULT = "rr_default"           # 40/30/20/10 - Balanced long-term
    PRESSURE_FIRST = "pressure_first"   # 60/15/15/10 - Win-now pressure execution
    YOUTH_FOCUS = "youth_focus"         # 25/50/15/10 - Long-term development
    CEILING_CHASER = "ceiling_chaser"   # 30/20/40/10 - High upside skills
    FORM_WATCHER = "form_watcher"       # 35/20/15/30 - Current form emphasis
    CUSTOM = "custom"                   # User-defined


@dataclass
class DimensionConfig:
    """Configuration for a single scoring dimension."""
    name: str
    key: str
    default_weight: float
    min_weight: float = 0.0
    max_weight: float = 100.0
    missing_policy: MissingDataPolicy = MissingDataPolicy.POPULATION_MEAN
    description: str = ""

    def __post_init__(self):
        # Normalize weight to 0-1 scale for internal use
        self.weight_normalized = self.default_weight / 100.0


@dataclass
class ScoutingWeights:
    """Container for the four dimension weights."""
    dimA_pressure: float = 40.0   # Pressure Execution
    dimB_age_dev: float = 30.0    # Age & Development Runway
    dimC_skill_ceiling: float = 20.0  # Skill Ceiling
    dimD_current_form: float = 10.0   # Current Form

    def __post_init__(self):
        total = self.dimA_pressure + self.dimB_age_dev + self.dimC_skill_ceiling + self.dimD_current_form
        if abs(total - 100.0) > 0.01:
            raise ValueError(f"Weights must sum to 100, got {total}")

    def to_array(self) -> np.ndarray:
        return np.array([self.dimA_pressure, self.dimB_age_dev, self.dimC_skill_ceiling, self.dimD_current_form]) / 100.0

    def to_dict(self) -> Dict[str, float]:
        return {
            'dimA_pressure': self.dimA_pressure,
            'dimB_age_dev': self.dimB_age_dev,
            'dimC_skill_ceiling': self.dimC_skill_ceiling,
            'dimD_current_form': self.dimD_current_form
        }

    @classmethod
    def from_dict(cls, d: Dict[str, float]) -> 'ScoutingWeights':
        return cls(
            dimA_pressure=d.get('dimA_pressure', 40.0),
            dimB_age_dev=d.get('dimB_age_dev', 30.0),
            dimC_skill_ceiling=d.get('dimC_skill_ceiling', 20.0),
            dimD_current_form=d.get('dimD_current_form', 10.0)
        )

    @classmethod
    def from_profile(cls, profile: WeightProfile) -> 'ScoutingWeights':
        profiles = {
            WeightProfile.RR_DEFAULT: cls(40.0, 30.0, 20.0, 10.0),
            WeightProfile.PRESSURE_FIRST: cls(60.0, 15.0, 15.0, 10.0),
            WeightProfile.YOUTH_FOCUS: cls(25.0, 50.0, 15.0, 10.0),
            WeightProfile.CEILING_CHASER: cls(30.0, 20.0, 40.0, 10.0),
            WeightProfile.FORM_WATCHER: cls(35.0, 20.0, 15.0, 30.0),
        }
        return profiles.get(profile, cls(40.0, 30.0, 20.0, 10.0))


@dataclass
class EngineConfig:
    """Full engine configuration."""
    weights: ScoutingWeights
    missing_data_policy: MissingDataPolicy = MissingDataPolicy.POPULATION_MEAN
    min_sample_threshold: int = 30  # Minimum balls for reliable pressure score
    enable_evidence_gating: bool = True  # Gate scores by evidence reliability
    confidence_penalty: float = 0.1  # Penalty multiplier for low confidence
    domestic_bonus: float = 0.0  # Bonus for domestic evidence presence

    # Dimension keys in the candidate dataframe
    dim_keys: Tuple[str, str, str, str] = (
        'dimA_pressure', 'dimB_runway', 'dimC_ceiling', 'dimD_form'
    )

    # Evidence columns
    evidence_balls_key: str = 'evidence_balls'
    has_form_evidence_key: str = 'has_form_evidence'
    has_domestic_evidence_key: str = 'has_domestic_evidence'
    is_shortlisted_key: str = 'is_shortlisted'


class DynamicScoutingEngine:
    """
    Dynamic Scouting Engine for PRESSURE-X.

    Computes configurable multi-dimensional rankings with:
    - Custom weight profiles (40/30/20/10 default)
    - Missing data imputation policies
    - Evidence reliability gating
    - Domestic performance bonuses
    - Sensitivity analysis
    """

    # Default dimension configurations
    DEFAULT_DIMS = [
        DimensionConfig(
            name="Pressure Execution",
            key="dimA_pressure",
            default_weight=40.0,
            description="Bayesian pressure performance in High-Extreme, Death, Chase, Powerplay situations"
        ),
        DimensionConfig(
            name="Age & Development Runway",
            key="dimB_runway",
            default_weight=30.0,
            description="Development runway as of 1 Apr 2027: Emerging<=23:100, YoungDev24-26:85, Prime27-30:65, Exp31+:50"
        ),
        DimensionConfig(
            name="Skill Ceiling",
            key="dimC_ceiling",
            default_weight=20.0,
            description="Physical attributes, bat speed, mystery spin, 3D versatility & tactical squad fit"
        ),
        DimensionConfig(
            name="Current Form",
            key="dimD_form",
            default_weight=10.0,
            description="Audited recent 12-month match logs across international and domestic leagues"
        ),
    ]

    def __init__(self, config: Optional[EngineConfig] = None):
        self.config = config or EngineConfig(weights=ScoutingWeights())
        self._population_stats: Dict[str, Dict[str, float]] = {}
        self._fitted = False

    def fit(self, df: pd.DataFrame) -> 'DynamicScoutingEngine':
        """
        Compute population statistics from the candidate pool for imputation.

        Args:
            df: Candidate pool dataframe with dimension columns

        Returns:
            Self for chaining
        """
        for dim_key in self.config.dim_keys:
            if dim_key in df.columns:
                vals = df[dim_key].dropna()
                if len(vals) > 0:
                    self._population_stats[dim_key] = {
                        'mean': float(vals.mean()),
                        'median': float(vals.median()),
                        'std': float(vals.std()),
                        'min': float(vals.min()),
                        'max': float(vals.max()),
                        'count': len(vals)
                    }
        self._fitted = True
        return self

    def _impute_missing(self, df: pd.DataFrame, dim_key: str) -> pd.Series:
        """Impute missing values for a dimension based on configured policy."""
        policy = self.config.missing_data_policy
        series = df[dim_key].copy()
        missing_mask = series.isna()

        if not missing_mask.any():
            return series

        stats = self._population_stats.get(dim_key, {})
        pop_mean = stats.get('mean', 50.0)
        pop_median = stats.get('median', 50.0)

        if policy == MissingDataPolicy.ZERO:
            series[missing_mask] = 0.0
        elif policy == MissingDataPolicy.NEUTRAL:
            series[missing_mask] = 50.0
        elif policy == MissingDataPolicy.POPULATION_MEAN:
            series[missing_mask] = pop_mean
        elif policy == MissingDataPolicy.POPULATION_MEDIAN:
            series[missing_mask] = pop_median
        elif policy == MissingDataPolicy.DIMENSION_WEIGHT_REDISTRIBUTE:
            # Handled at score computation level
            pass

        return series

    def compute_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute dynamic scouting scores for all candidates.

        Args:
            df: Candidate pool dataframe

        Returns:
            DataFrame with added 'dynamic_scouting_score' and component columns
        """
        if not self._fitted:
            self.fit(df)

        result = df.copy()
        weights = self.config.weights.to_array()
        dim_keys = self.config.dim_keys

        # Prepare dimension scores with imputation
        dim_scores = np.zeros((len(result), 4))
        dim_missing = np.zeros((len(result), 4), dtype=bool)

        for i, dim_key in enumerate(dim_keys):
            if dim_key in result.columns:
                imputed = self._impute_missing(result, dim_key)
                dim_scores[:, i] = imputed.fillna(50.0).values
                dim_missing[:, i] = result[dim_key].isna().values
            else:
                # Dimension not present - use neutral
                dim_scores[:, i] = 50.0
                dim_missing[:, i] = True

        # Handle weight redistribution for missing dimensions
        if self.config.missing_data_policy == MissingDataPolicy.DIMENSION_WEIGHT_REDISTRIBUTE:
            # Redistribute weights from missing dimensions to observed ones per row
            for row_idx in range(len(result)):
                missing = dim_missing[row_idx]
                observed_weights = weights.copy()
                observed_weights[missing] = 0
                weight_sum = observed_weights.sum()
                if weight_sum > 0:
                    observed_weights = observed_weights / weight_sum
                else:
                    observed_weights = np.array([0.25, 0.25, 0.25, 0.25])
                # Compute weighted score
                result.loc[row_idx, 'dynamic_scouting_score'] = np.dot(dim_scores[row_idx], observed_weights)
        else:
            # Standard weighted sum
            result['dynamic_scouting_score'] = np.dot(dim_scores, weights)

        # Store component contributions
        for i, dim_key in enumerate(dim_keys):
            result[f'{dim_key}_contribution'] = dim_scores[:, i] * weights[i]

        # Apply evidence confidence gating
        if self.config.enable_evidence_gating:
            result = self._apply_evidence_gating(result)

        # Apply domestic evidence bonus
        if self.config.domestic_bonus > 0:
            result = self._apply_domestic_bonus(result)

        # Round score
        result['dynamic_scouting_score'] = result['dynamic_scouting_score'].round(2)

        return result

    def _apply_evidence_gating(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply evidence reliability penalty to scores."""
        balls_key = self.config.evidence_balls_key

        if balls_key not in df.columns:
            return df

        balls = df[balls_key].fillna(0)
        threshold = self.config.min_sample_threshold

        # Progressive penalty: full score above threshold, scaled below
        penalty = np.where(
            balls >= threshold,
            1.0,
            1.0 - self.config.confidence_penalty * (1.0 - balls / threshold)
        )
        penalty = np.clip(penalty, 1.0 - self.config.confidence_penalty, 1.0)

        df['dynamic_scouting_score'] = df['dynamic_scouting_score'] * penalty
        df['evidence_confidence_factor'] = penalty.round(3)

        return df

    def _apply_domestic_bonus(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply bonus for domestic evidence presence."""
        dom_key = self.config.has_domestic_evidence_key

        if dom_key not in df.columns:
            return df

        has_dom = df[dom_key].fillna(False)
        df['dynamic_scouting_score'] = df['dynamic_scouting_score'] + (has_dom * self.config.domestic_bonus)
        df['domestic_bonus_applied'] = (has_dom * self.config.domestic_bonus).round(2)

        return df

    def rank_candidates(self, df: pd.DataFrame, ascending: bool = False) -> pd.DataFrame:
        """
        Rank candidates by dynamic scouting score.

        Args:
            df: Candidate pool with computed scores
            ascending: Sort order (False = highest first)

        Returns:
            DataFrame with 'dynamic_rank' column added
        """
        result = df.copy()
        if 'dynamic_scouting_score' not in result.columns:
            result = self.compute_scores(result)

        result = result.sort_values('dynamic_scouting_score', ascending=ascending).reset_index(drop=True)
        result['dynamic_rank'] = range(1, len(result) + 1)

        return result

    def sensitivity_analysis(self, df: pd.DataFrame, weight_range: float = 10.0, steps: int = 5) -> pd.DataFrame:
        """
        Perform sensitivity analysis by varying weights.

        Args:
            df: Candidate pool
            weight_range: ± percentage points to vary each weight
            steps: Number of steps in each direction

        Returns:
            DataFrame with rank stability metrics
        """
        base_weights = self.config.weights.to_dict()
        base_engine = DynamicScoutingEngine(EngineConfig(weights=ScoutingWeights.from_dict(base_weights)))
        base_ranked = base_engine.rank_candidates(df)
        base_ranks = base_ranked.set_index('player_id')['dynamic_rank']

        results = []

        for dim_name, base_w in base_weights.items():
            for delta in np.linspace(-weight_range, weight_range, steps):
                if delta == 0:
                    continue

                # Adjust weights - redistribute delta across other dimensions
                new_weights = base_weights.copy()
                new_weights[dim_name] = max(0, min(100, base_w + delta))

                # Redistribute remaining weight proportionally
                other_dims = [k for k in base_weights if k != dim_name]
                other_total = sum(base_weights[k] for k in other_dims)
                if other_total > 0:
                    for k in other_dims:
                        new_weights[k] = base_weights[k] * (100 - new_weights[dim_name]) / other_total

                # Compute new ranking
                test_engine = DynamicScoutingEngine(EngineConfig(weights=ScoutingWeights.from_dict(new_weights)))
                test_ranked = test_engine.rank_candidates(df)
                test_ranks = test_ranked.set_index('player_id')['dynamic_rank']

                # Compare ranks
                common_ids = set(base_ranks.index) & set(test_ranks.index)
                if common_ids:
                    rank_diffs = {pid: abs(base_ranks[pid] - test_ranks[pid]) for pid in common_ids}
                    avg_rank_shift = np.mean(list(rank_diffs.values()))
                    max_rank_shift = max(rank_diffs.values())
                    top10_stability = sum(1 for pid in common_ids if base_ranks[pid] <= 10 and test_ranks[pid] <= 10) / 10.0
                else:
                    avg_rank_shift = 0
                    max_rank_shift = 0
                    top10_stability = 0

                results.append({
                    'varied_dimension': dim_name,
                    'weight_delta': delta,
                    'new_weight': new_weights[dim_name],
                    'avg_rank_shift': round(avg_rank_shift, 2),
                    'max_rank_shift': max_rank_shift,
                    'top10_stability': round(top10_stability, 3)
                })

        return pd.DataFrame(results)

    def get_dimension_breakdown(self, df: pd.DataFrame, player_id: int) -> Dict[str, Any]:
        """Get detailed dimension breakdown for a specific player."""
        if 'dynamic_scouting_score' not in df.columns:
            df = self.compute_scores(df)

        row = df[df['player_id'] == player_id]
        if row.empty:
            return {}

        row = row.iloc[0]
        weights = self.config.weights.to_dict()

        breakdown = {}
        for dim_key, weight in weights.items():
            if dim_key in row:
                raw_score = row[dim_key]
                contribution = row.get(f'{dim_key}_contribution', raw_score * weight / 100.0)
                breakdown[dim_key] = {
                    'name': dim_key.replace('dimA_', '').replace('dimB_', '').replace('dimC_', '').replace('dimD_', '').replace('_', ' ').title(),
                    'weight': weight,
                    'raw_score': round(float(raw_score), 2) if pd.notna(raw_score) else None,
                    'contribution': round(float(contribution), 2),
                    'weight_pct': weight
                }

        breakdown['total_score'] = round(float(row['dynamic_scouting_score']), 2)
        breakdown['rank'] = int(row.get('dynamic_rank', 0))

        return breakdown

    def export_config(self) -> Dict[str, Any]:
        """Export current engine configuration for reproducibility."""
        return {
            'weights': self.config.weights.to_dict(),
            'missing_data_policy': self.config.missing_data_policy.value,
            'min_sample_threshold': self.config.min_sample_threshold,
            'enable_evidence_gating': self.config.enable_evidence_gating,
            'confidence_penalty': self.config.confidence_penalty,
            'domestic_bonus': self.config.domestic_bonus,
            'population_stats': self._population_stats
        }

    @classmethod
    def from_config(cls, config_dict: Dict[str, Any]) -> 'DynamicScoutingEngine':
        """Create engine from exported configuration."""
        weights = ScoutingWeights.from_dict(config_dict.get('weights', {}))
        config = EngineConfig(
            weights=weights,
            missing_data_policy=MissingDataPolicy(config_dict.get('missing_data_policy', 'pop_mean')),
            min_sample_threshold=config_dict.get('min_sample_threshold', 30),
            enable_evidence_gating=config_dict.get('enable_evidence_gating', True),
            confidence_penalty=config_dict.get('confidence_penalty', 0.1),
            domestic_bonus=config_dict.get('domestic_bonus', 0.0)
        )
        engine = cls(config)
        engine._population_stats = config_dict.get('population_stats', {})
        engine._fitted = bool(engine._population_stats)
        return engine


def create_default_engine() -> DynamicScoutingEngine:
    """Create engine with RR default 40/30/20/10 configuration."""
    return DynamicScoutingEngine(EngineConfig(weights=ScoutingWeights()))


def create_engine_from_profile(profile: WeightProfile, **overrides) -> DynamicScoutingEngine:
    """Create engine from a predefined weight profile with optional overrides."""
    weights = ScoutingWeights.from_profile(profile)

    # Apply overrides
    for key, value in overrides.items():
        if hasattr(weights, key):
            setattr(weights, key, value)

    config = EngineConfig(weights=weights)
    return DynamicScoutingEngine(config)