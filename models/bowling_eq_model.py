"""
Evidence-Qualified (EQ) Bowling Model
=====================================
Specialized bowling evaluation model addressing zero-opportunity pressure phase artifacts.

Core Methodology:
- Audits high-extreme, death, and powerplay opportunity counts for every bowler candidate.
- Replaces shrinkage-imputed population scores with an Evidence-Qualified re-normalization
  over only observed match phases.
- Codifies explicit tactical deployment boundaries to prevent misapplication in IPL matches.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


@dataclass
class BowlerDeploymentGuideline:
    player_id: int
    player_name: str
    primary_phase: str
    restricted_phases: List[str]
    confidence_tier: str
    tactical_rationale: str


class EvidenceQualifiedBowlingModel:
    """
    Evidence-Qualified Bowling Model.
    Ensures zero observed deliveries are treated as UNOBSERVED rather than elite performance.
    """

    # Baseline phase weights when all phases are observed
    DEFAULT_WEIGHTS = {
        'overall_economy': 0.30,
        'high_extreme': 0.25,
        'death': 0.20,
        'powerplay': 0.10,
        'wicket_rate': 0.10,
        'dot_ball_pct': 0.05
    }

    # Codified Tactical Deployment Boundaries
    TACTICAL_GUIDELINES: Dict[int, BowlerDeploymentGuideline] = {
        7935: BowlerDeploymentGuideline(
            player_id=7935,
            player_name="Mohammad Ghazanfar",
            primary_phase="Middle Overs (Overs 7-15)",
            restricted_phases=["Powerplay (Overs 1-6)", "Death Overs (Overs 17-20)"],
            confidence_tier="MEDIUM (Middle-Overs Specialist)",
            tactical_rationale="0 high-extreme deliveries in dataset; unpickable mystery spin suited for middle wicket-taking; prohibited from death/PP deployment in Year 1."
        ),
        6512: BowlerDeploymentGuideline(
            player_id=6512,
            player_name="Michael Bracewell",
            primary_phase="Powerplay & Middle Matchup Overs",
            restricted_phases=["Death Overs (Overs 17-20)"],
            confidence_tier="HIGH (PP/Middle Matchup Specialist)",
            tactical_rationale="0 death overs bowled across qualifying sample; defensive off-spinner effective vs LHB in powerplay; strict prohibition from death overs."
        ),
        4812: BowlerDeploymentGuideline(
            player_id=4812,
            player_name="Harry Tector",
            primary_phase="Middle Containment Overs",
            restricted_phases=["High-Extreme", "Death Overs"],
            confidence_tier="MEDIUM (Part-time / Matchup Spinner)",
            tactical_rationale="0 death and 0 high-extreme deliveries; useful matchup off-spin against top-order LHB; cannot be assigned frontline death responsibility."
        ),
        24767: BowlerDeploymentGuideline(
            player_id=24767,
            player_name="Ripon Mondol",
            primary_phase="Death Overs & Middle Enforcer",
            restricted_phases=[],
            confidence_tier="HIGH (High-Pressure Death Specialist)",
            tactical_rationale="54 verified death-overs deliveries in dataset; proven yorker and slower-ball skills; groomed under Shane Bond as high-pace death asset."
        )
    }

    def __init__(self, min_phase_deliveries: int = 12):
        self.min_phase_deliveries = min_phase_deliveries

    def assess_phase_evidence(self, row: pd.Series) -> Dict[str, str]:
        """
        Determine whether each pressure phase is genuinely OBSERVED or UNOBSERVED.
        """
        evidence_status = {}
        for phase, col in [('he', 'he_balls'), ('death', 'death_balls'), ('pp', 'pp_balls')]:
            count = row.get(col, 0)
            if pd.isna(count) or count < self.min_phase_deliveries:
                evidence_status[phase] = 'UNOBSERVED' if count == 0 else 'LOW_SAMPLE'
            else:
                evidence_status[phase] = 'OBSERVED'
        return evidence_status

    def calculate_evidence_qualified_score(
        self,
        component_scores: Dict[str, float],
        evidence_status: Dict[str, str]
    ) -> Tuple[float, float]:
        """
        Recalculate bowler score by normalizing weights across only observed phases.
        Returns: (eq_score, evidence_coverage_pct)
        """
        active_weights = {}
        weighted_sum = 0.0

        for comp, weight in self.DEFAULT_WEIGHTS.items():
            # Check if this component corresponds to an unobserved phase
            if comp == 'high_extreme' and evidence_status.get('he') == 'UNOBSERVED':
                continue
            if comp == 'death' and evidence_status.get('death') == 'UNOBSERVED':
                continue
            if comp == 'powerplay' and evidence_status.get('pp') == 'UNOBSERVED':
                continue

            active_weights[comp] = weight
            weighted_sum += weight * component_scores.get(comp, 50.0)

        total_active_weight = sum(active_weights.values())
        if total_active_weight > 0:
            eq_score = weighted_sum / total_active_weight
        else:
            eq_score = component_scores.get('overall_economy', 50.0)

        coverage_pct = total_active_weight / sum(self.DEFAULT_WEIGHTS.values()) * 100.0
        return eq_score, coverage_pct

    def get_tactical_guideline(self, player_id: int) -> Optional[BowlerDeploymentGuideline]:
        """Retrieve codified tactical boundaries for a specific bowler."""
        return self.TACTICAL_GUIDELINES.get(int(player_id))

